"""
Embed all images in data/images.json using CLIP and store in ChromaDB.
Run AFTER scripts/fetch_images.py.
"""
import io
import json
import os
import requests
import chromadb
from PIL import Image
from sentence_transformers import SentenceTransformer

CHROMA_PATH = "vectorstore"
COLLECTION = "kashi_images"

print("Loading CLIP model (first run downloads ~600MB)...")
model = SentenceTransformer("clip-ViT-B-32")
print("✅ Model loaded.")

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
try:
    chroma_client.delete_collection(COLLECTION)
    print("Deleted old image collection.")
except Exception:
    pass
collection = chroma_client.get_or_create_collection(COLLECTION)

with open("data/images.json", "r", encoding="utf-8") as f:
    records = json.load(f)

print(f"Processing {len(records)} images...\n")

added = 0
skipped = 0

for i, rec in enumerate(records):
    try:
        r = requests.get(
            rec["url"], timeout=15,
            headers={"User-Agent": "KashiTimeAI/1.0 (educational)"}
        )
        r.raise_for_status()
        img = Image.open(io.BytesIO(r.content)).convert("RGB")

        # Embed image
        img_emb = model.encode(img, convert_to_numpy=True).tolist()

        # Embed caption text — same space as image via CLIP
        text_for_embed = f"{rec['caption']} {' '.join(rec['tags'])}"
        txt_emb = model.encode(text_for_embed, convert_to_numpy=True).tolist()

        # Average of both — better matching on either query type
        combined = [(a + b) / 2 for a, b in zip(img_emb, txt_emb)]

        collection.add(
            embeddings=[combined],
            documents=[rec["caption"]],
            metadatas=[{
                "url": rec["url"],
                "caption": rec["caption"][:300],
                "entities": ", ".join(rec.get("entities", [])),
                "source": rec.get("source", "Wikimedia Commons"),
                "license": rec.get("license", "unknown"),
            }],
            ids=[rec["id"]]
        )
        added += 1

        if added % 10 == 0:
            print(f"  ✅ {added} embedded ({i+1}/{len(records)})")

    except Exception as e:
        skipped += 1
        print(f"  ⚠️  skip {rec['id']}: {str(e)[:80]}")

print(f"\n✅ Done. Embedded: {added}, Skipped: {skipped}")
print(f"   Collection '{COLLECTION}' now contains {collection.count()} images.")