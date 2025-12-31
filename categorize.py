# categorize.py
import json
import spacy
from spacy.language import Language
from spacy_langdetect import LanguageDetector
from get_corpus import load_corpus
from scrape_filter_link import LinkScraper

DEBUG = True   # set to False to disable debug output

# --------------------------
# Register language detector
# --------------------------
@Language.factory("language_detector")
def create_language_detector(nlp, name):
    return LanguageDetector()

nlp_en = spacy.load("en_core_web_sm")
nlp_en.add_pipe("language_detector", last=True)

nlp_fr = spacy.load("fr_core_news_sm")
nlp_fr.add_pipe("language_detector", last=True)

# --------------------------
# Language detection
# --------------------------
def detect_language(text):
    doc_en = nlp_en(text)
    doc_fr = nlp_fr(text)

    score_en = doc_en._.language.get("score", 0)
    score_fr = doc_fr._.language.get("score", 0)

    if score_en > score_fr and doc_en._.language["language"] == "en":
        return "en"
    if score_fr > score_en and doc_fr._.language["language"] == "fr":
        return "fr"
    return "unknown"

# --------------------------
# Categorization (keyword-based, original spirit)
# --------------------------
def categorize(text, corpus, lang):
    best_category = "unknown"
    max_score = 0

    text_lower = text.lower()

    if DEBUG:
        print("\n--- DEBUG: Categorization ---")
        print(f"Language: {lang}")
        print(f"Text length: {len(text)} characters")

    for category, docs in corpus[lang].items():
        matched = []
        score = 0

        for d in docs:
            if d.lower() in text_lower:
                score += 1
                matched.append(d)

        if DEBUG:
            print(f"\nCategory: {category}")
            print(f"  Score: {score}")
            if matched:
                print(f"  Matched keywords: {matched}")
            else:
                print("  Matched keywords: NONE")

        if score > max_score:
            max_score = score
            best_category = category

    if DEBUG:
        print(f"\n=> Selected category: {best_category} (score={max_score})")
        print("--- END DEBUG ---\n")

    return best_category

# --------------------------
# Main
# --------------------------
if __name__ == "__main__":
    corpus = load_corpus("corpus")

    with open("links.json", encoding="utf-8") as f:
        links = json.load(f)

    results = {}

    for item in links:
        url = item["uri"]
        scraper = LinkScraper(url)
        data = scraper.scrape()
        if DEBUG:
            print("\n--- DEBUG: Scraped Data ---")
            print(f"URL: {url}")
            print(f"Title: {data['title'][:200]}")
            print(f"Description: {data['description'][:200]}")
            print(f"Keywords: {data['keywords']}")
            print(f"Content length: {len(data['content'])}")
            print("--- END DEBUG ---\n")

        # Combine all text sources
        full_text = " ".join([
            data["title"],
            data["description"],
            " ".join(data["keywords"]),
            data["content"]
        ])

        lang = detect_language(full_text)
        if DEBUG:
            print(f"Detected language: {lang}")

        if lang == "unknown":
            category = "unknown"
        else:
            category = categorize(full_text, corpus, lang)

        results[url] = {
            "language": lang,
            "category": category,
            "title": data["title"]
        }

        print(f"{url} → {lang} / {category}")

    with open("result.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
