import os

import faiss
import numpy as np

from sentence_transformers import SentenceTransformer
from openai import OpenAI
from dotenv import load_dotenv


# ============================================================
# Configuration
# ============================================================

DOCUMENTS_PATH = "documents"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
TOP_K = 3


# ============================================================
# OpenAI setup
# ============================================================

load_dotenv()

client = OpenAI()


# ============================================================
# Load embedding model
# ============================================================

print("Loading embedding model...")

model = SentenceTransformer(
    EMBEDDING_MODEL
)


# ============================================================
# Load documents
# ============================================================

def load_documents():

    documents = []

    for filename in os.listdir(DOCUMENTS_PATH):

        path = os.path.join(
            DOCUMENTS_PATH,
            filename
        )

        if not os.path.isfile(path):
            continue

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as f:

            content = f.read()

        documents.append({
            "filename": filename,
            "content": content
        })

    return documents


# ============================================================
# Chunk documents
# ============================================================

def chunk_text(text):

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    chunks = []

    current_chunk = []

    for line in lines:

        current_chunk.append(line)

        # Create a chunk when we reach a sentence-ending line
        if line.endswith("."):

            chunks.append(
                "\n".join(current_chunk)
            )

            current_chunk = []

    if current_chunk:

        chunks.append(
            "\n".join(current_chunk)
        )

    return chunks


# ============================================================
# Build chunk collection
# ============================================================

documents = load_documents()

chunks = []

for document in documents:

    document_chunks = chunk_text(
        document["content"]
    )

    for chunk in document_chunks:

        chunks.append({
            "filename": document["filename"],
            "content": chunk
        })


print(f"\nLoaded {len(chunks)} chunks")


# ============================================================
# Create embeddings
# ============================================================

texts = [
    chunk["content"]
    for chunk in chunks
]

embeddings = model.encode(
    texts
)

embeddings = np.array(
    embeddings
).astype("float32")


print(
    "Embedding shape:",
    embeddings.shape
)


# ============================================================
# Create FAISS vector index
# ============================================================

dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(
    dimension
)

index.add(embeddings)


print(
    "Vectors in index:",
    index.ntotal
)


# ============================================================
# User question
# ============================================================

query = "How should users authenticate?"


# ============================================================
# Embed the question
# ============================================================

query_embedding = model.encode(
    [query]
)

query_embedding = np.array(
    query_embedding
).astype("float32")


# ============================================================
# Retrieve relevant chunks
# ============================================================

distances, indices = index.search(
    query_embedding,
    TOP_K
)


retrieved_chunks = []


print("\nTop retrieval results:\n")


for distance, index_id in zip(
    distances[0],
    indices[0]
):

    chunk = chunks[index_id]

    print(
        f"File: {chunk['filename']}"
    )

    print(
        f"Distance: {distance:.4f}"
    )

    print(
        f"Content: {chunk['content']}"
    )

    print("-" * 60)

    retrieved_chunks.append(
        chunk["content"]
    )


# ============================================================
# Build context for the LLM
# ============================================================

context = "\n\n---\n\n".join(
    retrieved_chunks
)


# ============================================================
# Generate answer using OpenAI
# ============================================================

response = client.responses.create(

    model="gpt-5.6-luna",

    instructions="""
You are a company knowledge assistant.

Answer the user's question using ONLY
the provided knowledge base context.

If the answer is not contained in the
provided context, say:

"I could not find this information
in the knowledge base."

Do not invent company policies.
""",

    input=f"""
Knowledge base context:

{context}


User question:

{query}
"""
)


# ============================================================
# Final answer
# ============================================================

print("\nFinal answer:\n")

print(
    response.output_text
)