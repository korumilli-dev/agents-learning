import os

import faiss
import numpy as np

from sentence_transformers import SentenceTransformer


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DOCUMENTS_PATH = os.path.join(
    BASE_DIR,
    "..",
    "02_rag",
    "documents"
)

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

model = SentenceTransformer(
    EMBEDDING_MODEL
)


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


def chunk_text(text):

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    chunks = []

    for i in range(0, len(lines), 2):

        chunk = "\n".join(
            lines[i:i + 2]
        )

        chunks.append(chunk)

    return chunks


def build_knowledge_base():

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

    texts = [
        chunk["content"]
        for chunk in chunks
    ]

    embeddings = model.encode(texts)

    embeddings = np.array(
        embeddings
    ).astype("float32")

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(
        dimension
    )

    index.add(embeddings)

    return chunks, index


chunks, index = build_knowledge_base()


def search_knowledge_base(query, top_k=3):

    query_embedding = model.encode(
        [query]
    )

    query_embedding = np.array(
        query_embedding
    ).astype("float32")

    distances, indices = index.search(
        query_embedding,
        top_k
    )

    results = []

    for distance, index_id in zip(
        distances[0],
        indices[0]
    ):

        results.append({
            "filename": chunks[index_id]["filename"],
            "content": chunks[index_id]["content"],
            "distance": float(distance)
        })

    return results