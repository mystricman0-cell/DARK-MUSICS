import os
from pathlib import Path

import yaml

languages = {}
languages_present = {}

_LANGS_DIR = Path(__file__).parent / "langs"


def get_string(lang: str):
    if lang in languages:
        return languages[lang]
    return languages.get("en", {})


def get_command(key: str):
    return languages.get("en", {}).get(key, key)


def _load_languages():
    if not _LANGS_DIR.exists():
        print(f"[WARNING] strings/langs/ directory not found at {_LANGS_DIR}")
        languages["en"] = {}
        return

    en_path = _LANGS_DIR / "en.yml"
    if en_path.exists():
        try:
            languages["en"] = yaml.safe_load(en_path.read_text(encoding="utf8")) or {}
            languages_present["en"] = languages["en"].get("name", "English")
        except Exception as e:
            print(f"[WARNING] Failed to load en.yml: {e}")
            languages["en"] = {}

    for filename in os.listdir(_LANGS_DIR):
        if not filename.endswith(".yml") or filename == "en.yml":
            continue
        language_name = filename[:-4]
        try:
            lang_data = yaml.safe_load(
                (_LANGS_DIR / filename).read_text(encoding="utf8")
            ) or {}
            for item in languages.get("en", {}):
                if item not in lang_data:
                    lang_data[item] = languages["en"][item]
            languages[language_name] = lang_data
            languages_present[language_name] = lang_data.get("name", language_name)
        except Exception as e:
            print(f"[WARNING] Skipping language file {filename}: {e}")


_load_languages()
