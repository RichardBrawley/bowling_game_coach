import os
from haystack_integrations.document_stores.pgvector import PGVectorDocumentStore
from haystack.components.retrievers import EmbeddingRetriever
from haystack_integrations.components.generators.openai import OpenAIGenerator
from haystack import Pipeline

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 1️⃣ Connect to PGVector in Postgres
document_store = PGVectorDocumentStore(
    connection_string="postgresql+psycopg2://postgres:postgres@localhost:5432/bowling",
    table_name="documents",
    embedding_dim=1536,  # depends on the embedding model
    recreate_table=False
)

# 2️⃣ Retriever (embeddings)
retriever = EmbeddingRetriever(
    document_store=document_store,
    embedding_model="text-embedding-3-small"  # OpenAI small embedding model
)

# 3️⃣ Generator (LLM)
generator = OpenAIGenerator(
    api_key=OPENAI_API_KEY,
    model="gpt-4o-mini"
)

# 4️⃣ Build pipeline
rag_pipeline = Pipeline()
rag_pipeline.add_component("retriever", retriever)
rag_pipeline.add_component("generator", generator)

rag_pipeline.connect("retriever", "generator")

# 5️⃣ Insert starter docs if empty
if document_store.count_documents() == 0:
    docs = [
        {"content": "In bowling, a strike means knocking down all 10 pins in the first roll."},
        {"content": "A spare means you knocked down all remaining pins in the second roll."},
        {"content": "In the 10th frame, players may roll up to 3 times if they score a strike or spare."},
        {"content": "Spare conversion consistency is key for improving your bowling score."}
    ]
    document_store.write_documents(docs)
    document_store.update_embeddings(retriever)
