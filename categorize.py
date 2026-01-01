# categorize.py
import json
import spacy
from spacy.language import Language
from spacy_langdetect import LanguageDetector
from get_corpus import load_corpus
from scrape_filter_link import LinkScraper
import os

RESULT_FILE = "result.json"

def load_results():
    if not os.path.exists(RESULT_FILE):
        return []

    if os.path.getsize(RESULT_FILE) == 0:
        return []

    with open(RESULT_FILE, encoding="utf-8") as f:
        data = json.load(f)

    # MIGRATION GUARD
    if isinstance(data, dict):
        print("⚠ result.json is a dict, converting to list format")
        return [
            {"url": url, **value}
            for url, value in data.items()
        ]

    if isinstance(data, list):
        return data

    raise ValueError("Invalid result.json format")

DEBUG = True   # set to False to disable debug output

# add tokenization
def tokenize(text, nlp):
    """
    Returns a set of normalized tokens:
    - lowercase
    - lemmatized
    - alphabetic
    - no stopwords
    """
    doc = nlp(text)
    return {
        token.lemma_.lower()
        for token in doc
        if token.is_alpha and not token.is_stop
    }

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

# Language detection pipeline (language-agnostic)
nlp_langdetect = spacy.blank("xx")
nlp_langdetect.add_pipe("language_detector")

# --------------------------
# Language detection
# --------------------------
def detect_language(text, min_len=200, en_threshold=0.80):
    """
    Deterministic language detection:
    - Defaults to French
    - Switches to English only if confidently detected
    """

    if not text or len(text) < min_len:
        return "fr"

    try:
        doc = nlp_langdetect(text)
        lang = doc._.language.get("language")
        score = doc._.language.get("score", 0)

        if DEBUG:
            print(f"Language detect → {lang} ({score:.2f})")

        if lang == "en" and score >= en_threshold:
            return "en"

        if lang == "fr":
            return "fr"

    except Exception as e:
        if DEBUG:
            print(f"Language detection error: {e}")

    # Default fallback
    return "fr"

def append_result(entry):
    results = load_results()
    results.append(entry)

    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

# --------------------------
# Categorization (keyword-based, original spirit)
# --------------------------
def categorize(text, corpus, lang):
    nlp = nlp_en if lang == "en" else nlp_fr

    text_tokens = tokenize(text, nlp)

    best_category = "unknown"
    max_score = 0

    if DEBUG:
        print("\n--- DEBUG: Token-based categorization ---")
        print(f"Text tokens ({len(text_tokens)}): {sorted(list(text_tokens))[:30]}")

    for category, docs in corpus[lang].items():
        score = 0
        matched_tokens = set()

        for doc in docs:
            doc_tokens = tokenize(doc, nlp)
            overlap = text_tokens & doc_tokens
            score += len(overlap)
            matched_tokens |= overlap

        if DEBUG:
            print(f"\nCategory: {category}")
            print(f"  Score: {score}")
            print(f"  Matched tokens: {sorted(matched_tokens) if matched_tokens else 'NONE'}")

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

        result = {
        "url": url,
        "language": lang,
        "category": category,
        "title": data["title"]
         }

        append_result(result)

