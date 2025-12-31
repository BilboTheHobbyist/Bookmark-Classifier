# get_corpus.py
import os
import json
from collections import defaultdict

def load_corpus(base_dir="corpus"):
    """Load corpus split by language and category."""
    corpus = defaultdict(lambda: defaultdict(list))
    for lang in ["en", "fr"]:
        lang_dir = os.path.join(base_dir, lang)
        if not os.path.exists(lang_dir):
            continue
        for category in os.listdir(lang_dir):
            cat_dir = os.path.join(lang_dir, category)
            if not os.path.isdir(cat_dir):
                continue
            for file in os.listdir(cat_dir):
                if file.endswith(".json"):
                    path = os.path.join(cat_dir, file)
                    with open(path, encoding="utf-8") as f:
                        try:
                            data = json.load(f)
                            corpus[lang][category].extend(data)
                        except json.JSONDecodeError:
                            print(f"Skipping invalid JSON file: {path}")
    return corpus
