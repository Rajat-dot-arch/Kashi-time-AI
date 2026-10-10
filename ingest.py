import os
import glob
import chromadb
from sentence_transformers import SentenceTransformer

CHROMA_PATH = "vectorstore"
COLLECTION_NAME = "kashi"
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"

print("Loading embedder...")
embed_model = SentenceTransformer(EMBED_MODEL_NAME)
print("✅ Embedder loaded.")


def chunk_text(text, chunk_size=800, overlap=100):
    paragraphs = text.split("\n\n")
    chunks = []
    current = ""
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        if len(current) + len(p) + 2 <= chunk_size:
            current = (current + "\n\n" + p) if current else p
        else:
            if current:
                chunks.append(current)
            if len(p) > chunk_size:
                step = chunk_size - overlap
                for i in range(0, len(p), step):
                    chunks.append(p[i:i + chunk_size])
                current = ""
            else:
                current = p
    if current:
        chunks.append(current)
    return chunks


def ingest():
    chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
    try:
        chroma_client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = chroma_client.get_or_create_collection(COLLECTION_NAME)

    files = glob.glob("data/*.txt")
    print(f"Found {len(files)} files.")

    all_chunks, all_metadatas, all_ids = [], [], []

    for filepath in files:
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
        chunks = chunk_text(text)
        fname = os.path.basename(filepath)
        for i, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            all_metadatas.append({"source": fname})
            all_ids.append(f"{fname}_{i}")
        print(f"  {fname}: {len(chunks)} chunks")

    if not all_chunks:
        print("No chunks found.")
        return

    print(f"Embedding {len(all_chunks)} chunks with {EMBED_MODEL_NAME}...")
    embeddings = embed_model.encode(all_chunks, show_progress_bar=True, convert_to_numpy=True).tolist()

    collection.add(
        documents=all_chunks,
        embeddings=embeddings,
        metadatas=all_metadatas,
        ids=all_ids
    )
    print(f"✅ Stored {len(all_chunks)} chunks.")


if __name__ == "__main__":
    ingest()