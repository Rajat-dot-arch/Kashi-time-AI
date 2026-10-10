import os
import wikipedia
import requests

wikipedia.set_lang("en")

# 25 major locations, events, and cultural topics of Kashi
TOPICS = [
    ("kashi_vishwanath_temple", "Kashi Vishwanath Temple"),
    ("dashashwamedh_ghat", "Dashashwamedh Ghat"),
    ("manikarnika_ghat", "Manikarnika Ghat"),
    ("assi_ghat", "Assi Ghat"),
    ("sarnath", "Sarnath"),
    ("ramnagar_fort", "Ramnagar Fort"),
    ("bharat_mata_mandir", "Bharat Mata Mandir"),
    ("ganga_aarti", "Ganga Aarti"),
    ("banaras_hindu_university", "Banaras Hindu University"),
    ("sankat_mochan_temple", "Sankat Mochan Hanuman Temple"),
    ("durga_temple_varanasi", "Durga Mandir, Varanasi"),
    ("tulsi_manas_temple", "Tulsi Manas Mandir"),
    ("kaal_bhairav_temple", "Kaal Bhairav Temple"),
    ("chaukhandi_stupa", "Chaukhandi Stupa"),
    ("bharat_kala_kendra", "Bharat Kala Kendra"),
    ("jantar_mantar_varanasi", "Jantar Mantar, Varanasi"),
    ("chet_singh_ghat", "Chet Singh Ghat"),
    ("scindia_ghat", "Scindia Ghat"),
    ("panchganga_ghat", "Panchganga Ghat"),
    ("gyanvapi_mosque", "Gyanvapi Mosque"),
    ("vishalakshi_temple", "Vishalakshi Temple"),
    ("annapurna_temple", "Annapurna Temple, Varanasi"),
    ("new_vishwanath_temple", "New Vishwanath Temple"),
    ("banarasi_silk", "Banarasi silk"),
    ("varanasi_culture", "Culture of Varanasi"),
]

os.makedirs("data", exist_ok=True)

for slug, title in TOPICS:
    # Skip if we already have the file (like the ones you made manually)
    filepath = f"data/{slug}.txt"
    if os.path.exists(filepath):
        print(f"⏩ Skipping {title} (file already exists)")
        continue

    print(f"Fetching {title}...")
    try:
        page = wikipedia.page(title, auto_suggest=False)
        content = page.content
        
        # Try to get the first image URL
        image_url = ""
        try:
            for img in page.images:
                if any(ext in img.lower() for ext in [".jpg", ".jpeg", ".png"]) and "commons" in img:
                    image_url = img
                    break
        except Exception:
            pass

        # Build a structured file
        text = f"Location: {title}\n"
        if image_url:
            text += f"Image: {image_url}\n"
        text += f"Source: https://en.wikipedia.org/wiki/{title.replace(' ', '_')}\n\n"
        text += content

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"  ✅ Saved {filepath}")
    except Exception as e:
        print(f"  ❌ Failed {title}: {e}")