"""Local model wrappers: HuggingFace embeddings (sentence-transformers) and a simple LLM wrapper
that uses the Hugging Face transformers text-generation pipeline for local Mistral testing.

This file provides lightweight classes to be used when `config.USE_OPENAI` is False.
"""

from typing import List
import logging

try:
    from sentence_transformers import SentenceTransformer
except Exception:
    SentenceTransformer = None

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
except Exception:
    pipeline = None
    AutoTokenizer = None
    AutoModelForCausalLM = None

from config import EMBEDDING_MODEL, LLM_MODEL, TEMPERATURE, MAX_TOKENS

logger = logging.getLogger(__name__)


class LocalEmbeddings:
    """Local embeddings using sentence-transformers (all-MiniLM-L6-v2).

    Usage: emb = LocalEmbeddings(); vector = emb.embed_text(text)
    """

    def __init__(self, model_name: str = EMBEDDING_MODEL):
        if SentenceTransformer is None:
            raise RuntimeError("sentence-transformers is not installed")
        self.model_name = model_name
        logger.info(f"Initializing SentenceTransformer: {model_name}")
        self.model = SentenceTransformer(model_name)

    def embed_text(self, text: str):
        return self.model.encode(text).tolist()

    def embed_documents(self, docs: List[str]):
        return [v.tolist() if hasattr(v, 'tolist') else v for v in self.model.encode(docs)]


class LocalLLM:
    """Simple local LLM wrapper using Hugging Face's text-generation pipeline.

    Note: Running a Mistral-family model locally can require significant resources.
    For small testing, consider using a small CPU-friendly model.
    """

    def __init__(self, model_name: str = LLM_MODEL, temperature: float = TEMPERATURE, max_tokens: int = MAX_TOKENS):
        if pipeline is None:
            raise RuntimeError("transformers is not installed")
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        logger.info(f"Initializing local LLM pipeline: {model_name}")

        # Create a text-generation pipeline; use CPU by default
        try:
            self.pipeline = pipeline(
                "text-generation",
                model=model_name,
                device=-1,
                tokenizer=model_name,
                trust_remote_code=True,
            )
        except Exception as e:
            logger.warning(f"Failed to initialize HF pipeline directly ({e}), attempting AutoModel load")
            # Fallback: try manual tokenizer/model
            try:
                tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
                model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True)
                self.pipeline = pipeline("text-generation", model=model, tokenizer=tokenizer, device=-1)
            except Exception as e2:
                logger.error(f"Unable to initialize local LLM: {e2}")
                raise

    def generate(self, prompt: str) -> str:
        # Use conservative generation params
        outputs = self.pipeline(
            prompt,
            max_new_tokens=self.max_tokens,
            do_sample=False,
            temperature=float(self.temperature),
            return_full_text=False,
        )
        # pipeline returns list of dicts
        if isinstance(outputs, list) and len(outputs) > 0:
            return outputs[0].get('generated_text', outputs[0].get('text', ''))
        return str(outputs)
