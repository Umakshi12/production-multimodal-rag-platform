"""Production-ready RAG Chatbot backend with streaming and conversation history"""

import os
import json
from typing import List, Tuple
# from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_mistralai import ChatMistralAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from logger import get_logger
from config import (
    VECTOR_DB_PATH, RETRIEVER_K, SYSTEM_PROMPT, MISTRAL_AI_MODEL, MISTRAL_AI_API_KEY,
    OPENAI_MODEL, LLM_MODEL, EMBEDDING_MODEL, TEMPERATURE, MAX_TOKENS,
    SOURCE_URL_MAPPING
)

logger = get_logger(__name__)

class OceaniaRAGChatbot:
    """Production-ready RAG chatbot for Oceanic6 Solutionz"""
    
    def __init__(self, vector_db_path: str = VECTOR_DB_PATH):
        """Initialize the chatbot with vector store and LLM"""
        logger.info("Initializing Oceania RAG Chatbot...")
        
        # Load embeddings
        # self.embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
        self.embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        
        # Load vector store
        try:
            self.vectorstore = Chroma(
                persist_directory=vector_db_path,
                embedding_function=self.embeddings
            )
            logger.info(f"Loaded vector store from {vector_db_path}")
        except Exception as e:
            logger.error(f"Error loading vector store: {e}")
            raise
        
        # Create retriever
        self.retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": RETRIEVER_K}
        )
        
        # # Initialize LLM
        # self.llm = ChatOpenAI(
        #     model=OPENAI_MODEL,
        #     temperature=TEMPERATURE,
        #     max_tokens=MAX_TOKENS
        # )
        # 4. Initialize LLM (Mistral via LangChain)
        # Ensure 'mistral-large-latest' or 'mistral-small' is set as LLM_MODEL in config
        if not MISTRAL_AI_API_KEY:
             raise ValueError("MISTRAL_API_KEY is missing from config.")

        self.llm = ChatMistralAI(
            model=LLM_MODEL,
            temperature=TEMPERATURE,
            api_key=MISTRAL_AI_API_KEY
        )
        
        # Conversation history
        self.conversation_history: List[BaseMessage] = []
        
        # Load structured products
        self.products = []
        try:
            with open("products.json", "r") as f:
                self.products = json.load(f)
            logger.info(f"Loaded {len(self.products)} structured products")
        except Exception as e:
            logger.warning(f"Could not load products.json: {e}")

        # Create rewriter prompt for resolving coreferences
        self.rewrite_prompt = ChatPromptTemplate.from_messages([
            ("system", "Given a conversation history and a follow-up question, rephrase the follow-up question to be a standalone question that can be understood without the context. If it's already standalone or a new topic, return it as is. DO NOT ANSWER the question, just rephrase it."),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{question}")
        ])
        self.rewriter = self.rewrite_prompt | self.llm | StrOutputParser()

        # Create prompt template with history support
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="history"),
            ("human", "Context: {context}\n\nQuestion: {question}")
        ])
        
        logger.info("Chatbot initialized successfully")

    def _get_product_context(self, query: str) -> Tuple[str, List[str]]:
        """Check if query matches a product and return curated context + image"""
        matched_context = ""
        matched_images = []
        
        query_lower = query.lower()
        for p in self.products:
            if p["name"].lower() in query_lower:
                matched_context += f"\n[STRUCTURED PRODUCT DATA]\nProduct: {p['name']}\nDescription: {p['description']}\n"
                for key, val in p.get("specs", {}).items():
                    matched_context += f"{key}: {val}\n"
                if p.get("image_path"):
                    matched_images.append(p["image_path"])
        
        return matched_context, matched_images
    
    def format_docs(self, docs) -> str:
        """Format retrieved documents for context"""
        return "\n\n".join([f"[Source: {doc.metadata.get('source', 'Unknown')}]\n{doc.page_content}" for doc in docs])
    
    def get_sources_and_images(self, docs) -> Tuple[List[str], List[str]]:
        """Extract unique sources (Mapped to URLs) and image paths from retrieved documents"""
        import re
        sources = set()
        images = set()
        
        for doc in docs:
            # Extract source and map to URL if possible
            if "source" in doc.metadata:
                source_path = doc.metadata["source"]
                filename = os.path.basename(source_path)
                
                # Strip out any (Page X) or similar suffixes to match mapping
                clean_filename = re.sub(r'\s*\([^)]*\)', '', filename).strip()
                
                if clean_filename in SOURCE_URL_MAPPING:
                    formatted_name = clean_filename.replace('_', ' ').replace('.pdf', '').replace(' slab cut to size catalog', '').strip().title()
                    sources.add(f"Oceanic6 Website - {formatted_name}: {SOURCE_URL_MAPPING[clean_filename]}")
                else:
                    sources.add(filename)
            
            # Extract image path
            if doc.metadata.get("image_path"):
                images.add(doc.metadata["image_path"])
        
        return sorted(list(sources)), sorted(list(images))
    
    def add_to_history(self, role: str, content: str):
        """Add message to conversation history with length capping"""
        if role == "user":
            self.conversation_history.append(HumanMessage(content=content))
        elif role == "assistant":
            self.conversation_history.append(AIMessage(content=content))
        
        # Cap history to maintain context window (MAX_HISTORY pairs = 20 messages)
        from config import MAX_HISTORY
        max_msgs = MAX_HISTORY * 2
        if len(self.conversation_history) > max_msgs:
            self.conversation_history = self.conversation_history[-max_msgs:]
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        logger.info("Conversation history cleared")
    
    def get_history(self) -> List[dict]:
        """Get formatted conversation history"""
        history = []
        for msg in self.conversation_history:
            if isinstance(msg, HumanMessage):
                history.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                history.append({"role": "assistant", "content": msg.content})
        return history
    
    def chat(self, query: str, image_base64: str = None, include_sources: bool = True) -> dict:
        """Chat with the bot and get response with metadata"""
        logger.info(f"User Query: {query}")
        
        # Add user message to history
        self.add_to_history("user", query)
        
        # 1. Rewriting query if history exists...
        search_query = query
        if len(self.conversation_history) > 1: # Only rewrite if there is at least one round-trip
            try:
                search_query = self.rewriter.invoke({
                    "history": self.conversation_history,
                    "question": query
                })
                logger.info(f"Rewritten Search Query: {search_query}")
            except Exception as e:
                logger.warning(f"Failed to rewrite query: {e}")
        
        # 2. Retrieve relevant documents using the rewritten query
        retrieved_docs = self.retriever.invoke(search_query)
        context = self.format_docs(retrieved_docs)
        
        # 3. Check for structured products using rewritten query for better mapping
        prod_context, prod_images = self._get_product_context(search_query)
        if prod_context:
            context = prod_context # Override entirely to avoid RAG noise
        
        # Get sources and any images found directly in the retrieved RAG documents
        sources, retrieved_images = self.get_sources_and_images(retrieved_docs)
        
        # Priority: Only show curated images from our product database.
        images = list(set(prod_images)) if prod_images else []
        
        # 4. Prepare inputs for LLM including history
        input_data = {
            "history": self.conversation_history,
            "context": context,
            "question": query # Use original query for final response generation
        }

        # Handle image-based queries
        if image_base64:
            message_content = [
                {"type": "text", "text": f"Context: {context}\n\nQuestion: {query}"}
            ]
            message_content.append({
                "type": "image_url",
                "image_url": {"url": image_base64}
            })
            
            messages = [
                ("system", SYSTEM_PROMPT),
                MessagesPlaceholder(variable_name="history"),
                HumanMessage(content=message_content)
            ]
            response = self.llm.invoke(messages)
        else:
            response = (self.prompt_template | self.llm).invoke(input_data)
        
        # Add assistant response to history
        self.add_to_history("assistant", response.content)
        
        # Extract curated images based on exact product mentions in the query or the LLM's own response
        final_images = list(set(prod_images)) if prod_images else []
        response_lower = response.content.lower()
        query_lower = query.lower()
        
        for p in self.products:
            # Clean up the product name to its core identity to ensure matches even if LLM drops generic terms
            core_name = p["name"].lower().replace(" granite", "").replace(" quartz", "").replace(" slab", "").replace(" slabs", "").strip()
            
            # If the LLM discusses a product (or the user asked for it indirectly), show its image
            if p["name"].lower() in response_lower or core_name in response_lower or core_name in query_lower:
                if p.get("image_path") and p["image_path"] not in final_images:
                    final_images.append(p["image_path"])
                    
        # Fallback: if no curated products were matched, but the retrieved docs *did* have an image, 
        # ONLY show it if the user explicitly asked to see an image.
        image_keywords = ["image", "picture", "photo", "show me", "look like"]
        wants_image = any(kw in query.lower() for kw in image_keywords)
        
        if not final_images and retrieved_images and wants_image:
            final_images = list(retrieved_images)
            
        images = final_images
        
        # Format response
        result = {
            "answer": response.content,
            "sources": sources if include_sources else [],
            "images": images,
            "retrieved_chunks": len(retrieved_docs),
            "conversation_turn": len(self.conversation_history) // 2
        }
        
        logger.info(f"Response: {response.content[:100]}...")
        logger.info(f"Sources: {len(sources)}, Images: {len(images)}")
        
        return result
    
    def stream_chat(self, query: str):
        """Stream chat response token by token with history support"""
        logger.info(f"Streaming query: {query}")
        
        # Add user message to history
        self.add_to_history("user", query)
        
        # 1. Rewriting query for context
        search_query = query
        if len(self.conversation_history) > 1:
            try:
                search_query = self.rewriter.invoke({
                    "history": self.conversation_history[:-1], # History WITHOUT current query
                    "question": query
                })
                logger.info(f"Rewritten Search Query (Stream): {search_query}")
            except Exception as e:
                logger.warning(f"Failed to rewrite query in stream: {e}")

        # 2. Retrieve relevant documents
        retrieved_docs = self.retriever.invoke(search_query)
        context = self.format_docs(retrieved_docs)
        
        # 3. Check for structured products
        prod_context, _ = self._get_product_context(search_query)
        if prod_context:
            context = prod_context
        
        # 4. Prepare chain inputs
        input_data = {
            "history": self.conversation_history[:-1], # Pass history WITHOUT current query
            "context": context,
            "question": query
        }
        
        # Stream the response
        full_response = ""
        for chunk in (self.prompt_template | self.llm).stream(input_data):
            if hasattr(chunk, 'content'):
                token = chunk.content
                full_response += token
                yield token
        
        # Add assistant response to history
        self.add_to_history("assistant", full_response)
    
    def get_retrieval_details(self, query: str) -> dict:
        """Get detailed retrieval information for debugging"""
        retrieved_docs = self.retriever.invoke(query)
        
        details = {
            "query": query,
            "num_retrieved": len(retrieved_docs),
            "documents": []
        }
        
        for i, doc in enumerate(retrieved_docs, 1):
            details["documents"].append({
                "rank": i,
                "source": doc.metadata.get("source", "Unknown"),
                "source_type": doc.metadata.get("source_type", "Unknown"),
                "preview": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
            })
        
        return details
    
    def batch_chat(self, queries: List[str], image_base64: str = None) -> List[dict]:
        """Process multiple queries in batch"""
        results = []
        for query in queries:
            result = self.chat(query, image_base64=image_base64)
            results.append(result)
        return results


def create_chatbot() -> OceaniaRAGChatbot:
    """Factory function to create and return a chatbot instance"""
    return OceaniaRAGChatbot()


if __name__ == "__main__":
    # Example usage
    chatbot = create_chatbot()
    
    print("\n" + "=" * 60)
    print("OCEANIA RAG CHATBOT")
    print("=" * 60)
    print("Type 'quit' to exit, 'history' to see conversation, 'clear' to clear history\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if not user_input:
            continue
        
        if user_input.lower() == "quit":
            print("Goodbye! ")
            break
        
        if user_input.lower() == "history":
            history = chatbot.get_history()
            print("\nConversation History:")
            for msg in history:
                print(f"  {msg['role'].upper()}: {msg['content'][:100]}...")
            print()
            continue
        
        if user_input.lower() == "clear":
            chatbot.clear_history()
            print("History cleared\n")
            continue
        
        # Get response
        response = chatbot.chat(user_input)
        
        print(f"\nOceania: {response['answer']}\n")
        
        if response['sources']:
            print("Sources:")
            for source in response['sources'][:3]:
                print(f"  - {source}")
        
        if response['images']:
            print("\nRelated Images:")
            for img in response['images'][:2]:
                print(f"  - {img}")
        
        print()
