"""
Fetch images of Kashi locations from Wikimedia Commons API.
Outputs: data/images.json
"""
import json
import os
import requests

# Make sure data/ exists
os.makedirs("data", exist_ok=True)

# Search terms — each will fetch up to 15 images
SEARCHES = [
    "Kashi Vishwanath Temple",
    "Dashashwamedh Ghat",
    "Manikarnika Ghat",
    "Assi Ghat",
    "Sarnath",
    "Ramnagar Fort Varanasi",
    "Ganga Aarti Varanasi",
    "Banaras Hindu University",
    "Sankat Mochan Hanuman Temple",
    "Durga Mandir Varanasi",
    "Tulsi Manas Temple",
    "Chet Singh Ghat",
    "Scindia Ghat",
    "Panchganga Ghat",
    "Kaal Bhairav Temple Varanasi",
    "Bharat Mata Mandir Varanasi",
    "Gyanvapi Mosque",
    "Varanasi Ghats",
    "Varanasi street",
    "Varanasi boats Ganga",
]

WIKI_API = "https://commons.wikimedia.org/w/api.php"
records = []
seen_urls = set()

for query in SEARCHES:
    print(f"Searching: {query}")
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": f"filetype:bitmap {query}",
        "gsrlimit": 15,
        "gsrnamespace": 6,
        "prop": "imageinfo",
        "iiprop": "url|extmetadata|size",
        "iiurlwidth": 800,
    }
    try:
        r = requests.get(WIKI_API, params=params, timeout=30,
                        headers={"User-Agent": "KashiTimeAI/1.0 (educational project)"})
        data = r.json()
    except Exception as e:
        print(f"  ❌ request failed: {e}")
        continue

    pages = data.get("query", {}).get("pages", {})
    added = 0
    for pid, page in pages.items():
        info_list = page.get("imageinfo", [])
        if not info_list:
            continue
        info = info_list[0]
        url = info.get("thumburl") or info.get("url")
        if not url or url in seen_urls:
            continue

        meta = info.get("extmetadata", {})
        caption = meta.get("ImageDescription", {}).get("value", query)
        # Strip HTML from caption
        import re
        caption = re.sub(r"<[^>]+>", "", caption).strip()
        if len(caption) > 200:
            caption = caption[:200] + "..."

        records.append({
            "id": f"img_{len(records):04d}",
            "url": url,
            "caption": caption or query,
            "entities": [query],
            "tags": query.lower().split(),
            "source": "Wikimedia Commons",
            "license": meta.get("LicenseShortName", {}).get("value", "unknown"),
        })
        seen_urls.add(url)
        added += 1

    print(f"  ✅ +{added} images")

with open("data/images.json", "w", encoding="utf-8") as f:
    json.dump(records, f, indent=2, ensure_ascii=False)

print(f"\n✅ Total collected: {len(records)} images → data/images.json")