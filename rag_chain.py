import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import chromadb

load_dotenv()

CHROMA_PATH = "vectorstore"
CHAT_MODEL = "llama3.2"

# Detect mode: if GROQ_API_KEY is set, we're on the cloud
USE_GROQ = bool(os.getenv("GROQ_API_KEY"))

if USE_GROQ:
    from groq import Groq
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    print("☁️ Running in Cloud Mode (Groq API)")
else:
    import ollama
    print("💻 Running in Local Mode (Ollama)")

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
text_collection = chroma_client.get_or_create_collection("kashi")
image_collection = chroma_client.get_or_create_collection("kashi_images")

_clip_model = None

def get_clip():
    global _clip_model
    if _clip_model is None:
        print("Loading CLIP for image retrieval...")
        _clip_model = SentenceTransformer("clip-ViT-B-32")
    return _clip_model

def embed_query(text):
    """Embed text for the text collection."""
    if USE_GROQ:
        # Groq doesn't offer embeddings, so we use a local small model instead
        # This is lightweight enough to run on free cloud tiers
        model = SentenceTransformer("all-MiniLM-L6-v2")
        return model.encode(text, convert_to_numpy=True).tolist()
    else:
        resp = ollama.embeddings(model="nomic-embed-text", prompt=text)
        return resp["embedding"]

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
            model=CHAT_MODEL,
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