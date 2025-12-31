# categorize.py
import json
from get_corpus import load_corpus
from scrape_filter_link import LinkScraper
import spacy
from spacy_langdetect import LanguageDetector
from spacy.language import Language

# --------------------------
# Register LanguageDetector
# --------------------------
@Language.factory("language_detector")
def create_language_detector(nlp, name):
    return LanguageDetector()

# Load pipelines
nlp_en = spacy.load("en_core_web_sm")
nlp_en.add_pipe("language_detector", last=True)

nlp_fr = spacy.load("fr_core_news_sm")
nlp_fr.add_pipe("language_detector", last=True)

# --------------------------
# Detect Language Dynamically
# --------------------------
def detect_language(text):
    doc_en = nlp_en(text)
    doc_fr = nlp_fr(text)

    score_en = doc_en._.language.get("score", 0)
    score_fr = doc_fr._.language.get("score", 0)

    if score_en > score_fr and doc_en._.language['language'] == "en":
        return "en"
    elif score_fr > score_en and doc_fr._.language['language'] == "fr":
        return "fr"
    else:
        return "unknown"

# --------------------------
# Categorize bookmark using similarity
# --------------------------
def categorize_bookmark(title, description, corpus):
    text = f"{title} {description}"
    lang = detect_language(text)
    if lang == "unknown":
        return "unknown"
    
    if lang == "en":
        nlp = nlp_en
    else:
        nlp = nlp_fr

    doc_text = nlp(text)
    best_category = "unknown"
    max_score = 0

    for category, docs in corpus[lang].items():
        if not docs:
            continue
        # Compute average similarity with corpus documents
        similarities = [doc_text.similarity(nlp(doc)) for doc in docs]
        avg_sim = sum(similarities) / len(similarities)
        if avg_sim > max_score:
            max_score = avg_sim
            best_category = category

    # Optional: threshold to avoid misclassification
    if max_score < 0.3:
        return "unknown"

    return best_category

# --------------------------
# Main Script
# --------------------------
if __name__ == "__main__":
    corpus = load_corpus("corpus")

    # Load bookmarks
    with open("links.json", encoding="utf-8") as f:
        bookmarks = json.load(f)

    results = {}
    for bm in bookmarks:
        url = bm['uri']
        scraper = LinkScraper(url)
        title, description = scraper.scrape()
        category = categorize_bookmark(title, description, corpus)
        lang = detect_language(title)
        results[url] = {"language": lang, "category": category}
        print(f"URL: {url}, Language: {lang}, Category: {category}")

    # Save results
    with open("result.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
