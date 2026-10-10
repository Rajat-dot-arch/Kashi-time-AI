import os
from dotenv import load_dotenv

# --- Detect environment and load Groq key ---
try:
    import streamlit as st
    GROQ_KEY = st.secrets.get("GROQ_API_KEY", "")
except Exception:
    GROQ_KEY = ""

if not GROQ_KEY:
    load_dotenv()
    GROQ_KEY = os.getenv("GROQ_API_KEY", "")

USE_GROQ = bool(GROQ_KEY)

import chromadb
from sentence_transformers import SentenceTransformer

CHROMA_PATH = "vectorstore"
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"

if USE_GROQ:
    from groq import Groq
    groq_client = Groq(api_key=GROQ_KEY)
    print("☁️ Cloud Mode (Groq)")
else:
    import ollama
    print("💻 Local Mode (Ollama)")

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
text_collection = chroma_client.get_or_create_collection("kashi")
image_collection = chroma_client.get_or_create_collection("kashi_images")

_embed_model = None
_clip_model = None


def get_embedder():
    global _embed_model
    if _embed_model is None:
        _embed_model = SentenceTransformer(EMBED_MODEL_NAME)
    return _embed_model


def get_clip():
    global _clip_model
    if _clip_model is None:
        _clip_model = SentenceTransformer("clip-ViT-B-32")
    return _clip_model


def embed_query(text):
    return get_embedder().encode(text, convert_to_numpy=True).tolist()


def retrieve_text(query, k=4):
    query_embedding = embed_query(query)
    results = text_collection.query(
        query_embeddings=[query_embedding],
        n_results=k
    )
    docs = results["documents"][0]
    metadatas = results["metadatas"][0]
    return list(zip(docs, metadatas))


def retrieve_images(query, k=3):
    # Skip images on cloud to save RAM (CLIP is ~600 MB)
    if USE_GROQ:
        return []
    if image_collection.count() == 0:
        return []
    model = get_clip()
    query_emb = model.encode(query, convert_to_numpy=True).tolist()
    results = image_collection.query(
        query_embeddings=[query_emb],
        n_results=k
    )
    images = []
    for i in range(len(results["ids"][0])):
        meta = results["metadatas"][0][i]
        images.append({
            "url": meta["url"],
            "caption": meta.get("caption", ""),
            "source": meta.get("source", "Wikimedia Commons"),
            "license": meta.get("license", "unknown"),
        })
    return images


def answer(query, chat_history=None):
    if chat_history is None:
        chat_history = []

    docs = retrieve_text(query, k=4)
    context = "\n\n---\n\n".join([d[0] for d in docs])
    sources = sorted(set([d[1]["source"] for d in docs]))
    images = retrieve_images(query, k=3)

    system_prompt = (
        "You are Kashi-Time AI, a heritage guide for Varanasi/Kashi.\n"
        "Use ONLY the context below to answer the question. "
        "If the answer is not in the context, say: "
        "'I don't have that information in my knowledge base.'\n"
        "If the question asks about changes, destructions, or events, "
        "list ALL relevant events from the context with their dates.\n"
        "Keep answers concise, factual, and informative. "
        "Mention the source location when relevant.\n\n"
        f"Context:\n{context}"
    )

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(chat_history[-4:])
    messages.append({"role": "user", "content": query})

    if USE_GROQ:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.2
        )
        answer_text = response.choices[0].message.content
    else:
        response = ollama.chat(
            model="llama3.2",
            messages=messages,
            options={"temperature": 0.2}
        )
        answer_text = response["message"]["content"]

    return {
        "answer": answer_text,
        "sources": sources,
        "images": images,
    }


if __name__ == "__main__":
    history = []
    while True:
        q = input("Ask Kashi-Time AI: ")
        if q.lower() in ["exit", "quit"]:
            break
        result = answer(q, history)
        print("\nAnswer:", result["answer"])
        print("Sources:", result["sources"])
        print("-" * 60)
        history.append({"role": "user", "content": q})
        history.append({"role": "assistant", "content": result["answer"]})