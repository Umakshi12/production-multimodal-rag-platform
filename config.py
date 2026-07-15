"""Configuration file for Oceanic RAG Chatbot"""

import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-api-key")
# MISTRAL_AI_API_KEY = os.getenv("MISTRAL_AI_API_KEY", "your-mistral-api-key")
MISTRAL_AI_API_KEY = os.getenv("MISTRAL_AI_API_KEY", "your-mistral-api-key")
# Toggle: set to True to use OpenAI (production). For local/free testing leave False.
USE_OPENAI = os.getenv("USE_OPENAI", "False").lower() in ("1", "true", "yes")

# When USE_OPENAI=True these will be used. For local testing we default to local backends below.
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")
MISTRAL_AI_MODEL = os.getenv("MISTRAL_AI_MODEL", "pixtral-12b-2409")

# Embedding model to use when USE_OPENAI=True
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")


# Local / free-testing defaults
# Use Sentence-Transformers model for embeddings
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
# Use a Hugging Face Mistral-family model identifier for local testing (requires HF access and resources)
LLM_MODEL = os.getenv("LLM_MODEL", "mistral-small-latest")

# Database Configuration
VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./chroma_db")
DATA_DIR = os.getenv("DATA_DIR", "./company_data")
IMAGE_OUTPUT_DIR = os.getenv("IMAGE_OUTPUT_DIR", "./extracted_images")

# Website Configuration
WEBSITE_URLS = [
    # Main Pages
    "https://www.oceanic6solutionz.com/",
    "https://www.oceanic6solutionz.com/aboutus.html",
    "https://www.oceanic6solutionz.com/products.html",
    "https://www.oceanic6solutionz.com/export.html",
    "https://www.oceanic6solutionz.com/projects.html",
    "https://www.oceanic6solutionz.com/blogs.html",
    "https://www.oceanic6solutionz.com/contact-us.html",
    
    # Operational & Info Pages
    "https://www.oceanic6solutionz.com/manufacturing-natural-stone.html",
    "https://www.oceanic6solutionz.com/factory-natural-stone.html",
    "https://www.oceanic6solutionz.com/packaging.html",
    "https://www.oceanic6solutionz.com/quality-control.html",
    "https://www.oceanic6solutionz.com/delivery.html",

    # Product Categories
    "https://www.oceanic6solutionz.com/granite-slabs.html",
    "https://www.oceanic6solutionz.com/engineered-quartz.html",
    "https://www.oceanic6solutionz.com/quartz-countertops.html",
    "https://www.oceanic6solutionz.com/limestone.html",
    "https://www.oceanic6solutionz.com/sandstone.html",
    "https://www.oceanic6solutionz.com/porcelain-slabs.html",
    "https://www.oceanic6solutionz.com/quartzite.html",
    "https://www.oceanic6solutionz.com/outdoor-paver-tiles.html",
    "https://www.oceanic6solutionz.com/sandstone-cobbles.html",

    # Granite Applications
    "https://www.oceanic6solutionz.com/granite-kitchen-countertops.html",
    "https://www.oceanic6solutionz.com/granite-vanity-tops.html",
    "https://www.oceanic6solutionz.com/granite-paver-stones.html",

    # Specific Granite Products
    "https://www.oceanic6solutionz.com/crystal-blue.html",
    "https://www.oceanic6solutionz.com/crystal-yellow.html",
    "https://www.oceanic6solutionz.com/s-white.html",
    "https://www.oceanic6solutionz.com/china-white.html",
    "https://www.oceanic6solutionz.com/oceanic-blue.html",
    "https://www.oceanic6solutionz.com/cheema-pink.html",
    "https://www.oceanic6solutionz.com/desert-brown.html",
    "https://www.oceanic6solutionz.com/malwara-gold.html",
    "https://www.oceanic6solutionz.com/p-white.html",
    "https://www.oceanic6solutionz.com/burgandy-white-1.html",
    "https://www.oceanic6solutionz.com/burgandy-white-2.html",
    "https://www.oceanic6solutionz.com/cheda-white.html",
    "https://www.oceanic6solutionz.com/chiana-white.html",
    "https://www.oceanic6solutionz.com/colonial-white.html",
    "https://www.oceanic6solutionz.com/moon-white.html",
    "https://www.oceanic6solutionz.com/parda-gold.html",
    "https://www.oceanic6solutionz.com/river-white-1.html",
    "https://www.oceanic6solutionz.com/river-white-2.html",
    "https://www.oceanic6solutionz.com/river-white-3.html",
    "https://www.oceanic6solutionz.com/river-white-4.html",
    "https://www.oceanic6solutionz.com/royal-gold.html",
    "https://www.oceanic6solutionz.com/royal-white.html",
    "https://www.oceanic6solutionz.com/sk-blue.html",
    "https://www.oceanic6solutionz.com/tan-black.html",
    "https://www.oceanic6solutionz.com/tan-brown.html",
    "https://www.oceanic6solutionz.com/thunder-white-1.html",
    "https://www.oceanic6solutionz.com/thunder-white-2.html",
    "https://www.oceanic6solutionz.com/burgandy-pink.html",
    "https://www.oceanic6solutionz.com/burgandy-river.html",
    "https://www.oceanic6solutionz.com/burgandy.html",
    "https://www.oceanic6solutionz.com/river-gold.html",
    "https://www.oceanic6solutionz.com/sparkle-white.html",
    "https://www.oceanic6solutionz.com/black-galaxy.html",
    "https://www.oceanic6solutionz.com/black-pearl.html",
    "https://www.oceanic6solutionz.com/new-viscon-white.html",
    "https://www.oceanic6solutionz.com/steel-grey.html",
    "https://www.oceanic6solutionz.com/viscon-white.html",
    "https://www.oceanic6solutionz.com/desert-black.html",
    "https://www.oceanic6solutionz.com/sweed-green.html",
    "https://www.oceanic6solutionz.com/mani-white.html",
    "https://www.oceanic6solutionz.com/silver-streak.html",
    "https://www.oceanic6solutionz.com/titanium-black.html",
    "https://www.oceanic6solutionz.com/river-brown.html",
    "https://www.oceanic6solutionz.com/rajasthan-black.html",
    "https://www.oceanic6solutionz.com/desert-grey.html",
    "https://www.oceanic6solutionz.com/marine-black-leather.html",
    "https://www.oceanic6solutionz.com/marine-black-honed.html",
    "https://www.oceanic6solutionz.com/marine-black-polished.html",

    # Quartz Products
    "https://www.oceanic6solutionz.com/ice-white.html",
    "https://www.oceanic6solutionz.com/calacatta-almond.html",
    "https://www.oceanic6solutionz.com/nazrana.html"
]

# Text Processing Configuration
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
RETRIEVER_K = 5

# URL Mapping for sources
SOURCE_URL_MAPPING = {
    "granite_slab_cut_to_size_catalog.pdf": "https://www.oceanic6solutionz.com/products/granite/",
    "granite_quote_sheet.pdf": "https://www.oceanic6solutionz.com/products/granite/",
    "quartz_slab_cut_to_size_catalog.pdf": "https://www.oceanic6solutionz.com/products/quartz/",
    "quartz_quote_sheet.pdf": "https://www.oceanic6solutionz.com/products/quartz/",
    "slabs_technical_specs.pdf": "https://www.oceanic6solutionz.com/technical-specifications/"
}

# RAG Configuration
SYSTEM_PROMPT = """You are Oceania, a sharp and professional AI consultant for Oceanic6 Solutionz. 

Core Rules:
1. **PRODUCT FOCUS**: Focus your entire answer on the specific product the user asked about. 
2. **NO MARKDOWN IMAGES**: **NEVER** use `![alt](url)` or `<img>` tags in your response. 
3. **NO SYSTEM LINGO**: Do **NOT** include internal labels like "[STRUCTURED PRODUCT DATA]" in your output. Just write naturally.
4. **NO MANUAL CITATIONS**: Do **NOT** write "Sources:" or provide a list of links in your message content. The system handles this in a separate section automatically.
5. **NO REPETITIVE INTROS**: Jump straight to the answer.
6. **CLARITY**: Be concise. Use bolding and bullet points for specs.
7. **MATERIAL ACCURACY**: If the user asks for Quartz and the RAG also mentions Quartzite, stick to the **Quartz** data.

Status:
- If a user asks a technical question, provide the spec.
- If they ask for price, provide it from the tables.
- DO NOT promise to show an image if you are not discussing a specifically named stone from the catalog.

Formatting:
- Product Specs: Use clean markdown lists.
- Emails/Complex Queries: Suggest sales@oceanic6solutionz.com.

Context from company knowledge base:
{context}

Respond as a helpful, direct expert. No fluff. 
CRITICAL RULE: If the user asks for images of a specific product, you MUST explicitly state the EXACT product name in your text (e.g. "Crystal Blue", "Black Galaxy Granite Slab", "Calcutta Laza") so the backend can fetch it. If you mention it, do NOT say "Here is the image". The system appends images automatically."""

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "./logs/chatbot.log")

# Streamlit Configuration
STREAMLIT_PAGE_TITLE = "Oceanic6 Solutionz - AI Assistant"
STREAMLIT_PAGE_ICON = "🤖"
STREAMLIT_LAYOUT = "wide"

# Chat Configuration
MAX_HISTORY = 10  # Maximum conversation history to keep
TEMPERATURE = float(os.getenv("TEMPERATURE", 0.3))  # Lower temperature for more deterministic responses
MAX_TOKENS = int(os.getenv("MAX_TOKENS", 1000))
