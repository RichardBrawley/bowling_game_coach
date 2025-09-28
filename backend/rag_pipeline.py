import os
from dotenv import load_dotenv

from haystack.core.pipeline import Pipeline
from haystack.utils.auth import Secret
from haystack_integrations.document_stores.pgvector import PgvectorDocumentStore
from haystack.components.writers import DocumentWriter
from haystack_integrations.components.retrievers.pgvector import PgvectorEmbeddingRetriever
from haystack.components.generators import OpenAIGenerator
from haystack.components.builders import PromptBuilder
from haystack.components.embedders import SentenceTransformersTextEmbedder, SentenceTransformersDocumentEmbedder

# -------------------------------------------------------------------
# Load env vars
# -------------------------------------------------------------------
load_dotenv()

POSTGRES_URL = os.getenv("POSTGRES_URL", "postgresql://postgres:postgres@localhost:5432/bowling")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

print(POSTGRES_URL)

# -------------------------------------------------------------------
# Document store (shared between pipelines)
# -------------------------------------------------------------------
document_store = PgvectorDocumentStore(
    connection_string=Secret.from_token(POSTGRES_URL),
    table_name="documents", 
    embedding_dimension=384,
)
document_store._ensure_db_setup()  # private, but useful for setup

# -------------------------------------------------------------------
# Indexing pipeline
# -------------------------------------------------------------------
indexing = Pipeline()

indexing_embedder = SentenceTransformersDocumentEmbedder(
    model="sentence-transformers/all-MiniLM-L6-v2"  # free, small & fast
)

writer = DocumentWriter(document_store=document_store)

indexing.add_component("embedder", indexing_embedder)
indexing.add_component("writer", writer)
indexing.connect("embedder.documents", "writer.documents")


# -------------------------------------------------------------------
# RAG pipeline
# -------------------------------------------------------------------
rag_pipeline = Pipeline()

query_embedder = SentenceTransformersTextEmbedder(
    model="sentence-transformers/all-MiniLM-L6-v2"
)

retriever = PgvectorEmbeddingRetriever(document_store=document_store)

prompt_builder = PromptBuilder(
    template="""
    You are a professional sports commentator announcing a bowling match. 
    Use the retrieved documents (player history, past games, scores) to add 
    colorful and exciting context.

    Speak with enthusiasm, energy, and drama, as if you’re on live TV.

    Question (viewer request): {{query}}
    Documents (stats & background): {{documents}}

    Now give a broadcast-style commentary:
    """
)

generator = OpenAIGenerator(
    api_key=Secret.from_token(OPENAI_API_KEY),
    model="gpt-4o-mini",
)

rag_pipeline.add_component("query_embedder", query_embedder)
rag_pipeline.add_component("retriever", retriever)
rag_pipeline.add_component("prompt_builder", prompt_builder)
rag_pipeline.add_component("generator", generator)

# Connect flow
rag_pipeline.connect("query_embedder.embedding", "retriever.query_embedding")
rag_pipeline.connect("retriever", "prompt_builder.documents")
rag_pipeline.connect("prompt_builder.prompt", "generator.prompt")
