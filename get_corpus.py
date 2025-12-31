# get_corpus.py
import os
import json
from collections import defaultdict

def load_corpus(base_dir="corpus"):
    """
    Supports:
    - {"text": "string"}
    - {"text": ["string1", "string2"]}
    - ["string1", "string2"]
    """
    corpus = defaultdict(lambda: defaultdict(list))

    for lang in ("en", "fr"):
        lang_dir = os.path.join(base_dir, lang)
        if not os.path.isdir(lang_dir):
            continue

        for category in os.listdir(lang_dir):
            cat_dir = os.path.join(lang_dir, category)
            if not os.path.isdir(cat_dir):
                continue

            for filename in os.listdir(cat_dir):
                if not filename.endswith(".json"):
                    continue

                path = os.path.join(cat_dir, filename)
                try:
                    with open(path, encoding="utf-8") as f:
                        data = json.load(f)

                    # Original project format
                    if isinstance(data, dict) and "text" in data:
                        if isinstance(data["text"], list):
                            corpus[lang][category].extend(data["text"])
                        else:
                            corpus[lang][category].append(data["text"])

                    # New simplified format
                    elif isinstance(data, list):
                        corpus[lang][category].extend(data)

                except Exception as e:
                    print(f"Skipping {path}: {e}")

    return corpus
