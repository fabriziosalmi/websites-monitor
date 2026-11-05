"""The web UI's locale files are complete, consistent and used."""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
APP_JS = (DOCS / "assets" / "app.js").read_text(encoding="utf-8")
INDEX = (DOCS / "index.html").read_text(encoding="utf-8")
LOCALES = {
    path.stem: json.loads(path.read_text(encoding="utf-8"))
    for path in sorted((DOCS / "assets" / "locales").glob("*.json"))
}
PLACEHOLDER = re.compile(r"\{(\w+)\}")


def placeholders(value):
    if isinstance(value, dict):
        return {form: set(PLACEHOLDER.findall(text)) for form, text in value.items()}
    return set(PLACEHOLDER.findall(value))


def ids(pattern):
    block = APP_JS[APP_JS.index(pattern):]
    block = block[:block.index("];")]
    return re.findall(r"^\s*\[?\{?\s*(?:id: )?'([a-z_]+)'", block, re.M)


def used_keys():
    keys = set(re.findall(r"""\bt[x]?\(\s*'([a-zA-Z0-9_.]+)'""", APP_JS))
    keys |= set(re.findall(r"'((?:nav|history|scan|settings|results|catalog|toast|err|time)\.[a-zA-Z]+)'", APP_JS))
    keys |= set(re.findall(r'data-i18n="([^"]+)"', INDEX))
    for attr in re.findall(r'data-i18n-attr="([^"]+)"', INDEX):
        keys |= {pair.split(":")[1] for pair in attr.split(";")}
    checks = ids("const CHECKS = [")
    categories = ids("const CATEGORIES = [")
    statuses = re.findall(r"^\s*(\w+): \{ badge:", APP_JS, re.M)
    keys |= {f"check.{c}.{part}" for c in checks for part in ("name", "hint")}
    keys |= {f"category.{c}" for c in categories}
    keys |= {f"status.{s}" for s in statuses}
    return keys


def test_english_and_italian_are_both_there():
    assert set(LOCALES) == {"en", "it"}


def test_every_language_has_the_same_keys():
    english = set(LOCALES["en"])
    for lang, strings in LOCALES.items():
        assert set(strings) == english, (
            f"{lang}.json: missing {sorted(english - set(strings))}, extra {sorted(set(strings) - english)}"
        )


def test_translations_keep_the_placeholders_and_plural_forms():
    for key, value in LOCALES["en"].items():
        for lang, strings in LOCALES.items():
            other = strings[key]
            assert type(other) is type(value), f"{lang}.json {key}: plural form mismatch"
            if isinstance(value, dict):
                assert set(other) >= {"one", "other"}, f"{lang}.json {key}: needs one and other"
                assert placeholders(other)["other"] == placeholders(value)["other"], f"{lang}.json {key}"
            else:
                assert placeholders(other) == placeholders(value), f"{lang}.json {key}: placeholders differ"


def test_english_has_no_empty_string():
    assert [k for k, v in LOCALES["en"].items() if v == ""] == []


def test_every_key_the_ui_uses_exists_and_every_key_is_used():
    used = used_keys()
    defined = set(LOCALES["en"])
    assert sorted(used - defined) == [], "keys used by the UI but missing from en.json"
    assert sorted(defined - used) == [], "keys in en.json that nothing uses"


def test_every_check_and_category_has_its_own_name():
    english = LOCALES["en"]
    for c in ids("const CHECKS = ["):
        assert english.get(f"check.{c}.name") and english.get(f"check.{c}.hint"), c
    for c in ids("const CATEGORIES = ["):
        assert english.get(f"category.{c}"), c


def test_the_asset_version_in_the_script_matches_the_page():
    version = re.search(r"const ASSET_VERSION = '(\w+)'", APP_JS).group(1)
    assert f"assets/app.js?v={version}" in INDEX
    assert f"assets/app.css?v={version}" in INDEX


def test_the_italian_text_has_no_em_dash():
    text = json.dumps(LOCALES["it"], ensure_ascii=False)
    assert "—" not in text
