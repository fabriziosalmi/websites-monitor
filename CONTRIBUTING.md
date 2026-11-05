# Contributing

Thanks for helping. This file covers the setup, the tests, how a check is written and registered, and how changes are proposed.

## Setup

Python 3.11, the version the Docker image and CI use:

```bash
git clone https://github.com/fabriziosalmi/websites-monitor.git
cd websites-monitor
python3.11 -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt
python api.py               # API and web UI on http://127.0.0.1:8000/
```

`API_RELOAD=1 python api.py` restarts the server when a file changes. Do not use it in production: a restart drops the requests in progress.

## Tests

```bash
python -m pytest -q
```

The tests do not touch the network: checks are exercised with fake responses. A bug fix comes with a test that fails without the fix; check that it does by reverting the fix once before you open the pull request.

CI runs the same suite on Python 3.11, then builds the Docker image, starts it with the 256 MB memory limit of `docker-compose.yml` and calls the API.

## Writing a check

A check is a function in `checks/check_<id>.py`:

```python
import logging

import requests

logger = logging.getLogger(__name__)


def check_example(website: str) -> str:
    """
    One line saying what the check looks at.

    Args:
        website (str): A domain such as "example.com". Accept a URL too.

    Returns:
        str: the verdict, optionally followed by a detail in parentheses.
    """
    url = website if website.startswith(("http://", "https://")) else f"https://{website}"
    try:
        response = requests.get(url, timeout=10)
    except requests.RequestException as e:
        logger.warning(f"Could not fetch {url}: {e}")
        return "\u26AA (site unreachable)"           # no verdict
    if "x-example" in response.headers:
        return "\U0001F7E2"                          # pass
    return "\U0001F534 (x-example header missing)"   # fail
```

Rules:

- Return a string that starts with the verdict: `\U0001F7E2` pass, `\U0001F7E1` or `\U0001F7E0` warning, `\U0001F534` fail, `\u26AA` no verdict. Anything after it, in parentheses, is shown next to the verdict in the web UI and the report.
- Never raise. When the check cannot decide (the site does not answer, a key is missing, there is nothing to check), return no verdict with the reason, for example `"\u26AA (no PageSpeed API key)"`. Not having a feature is a verdict only when the check is about that feature.
- Take one positional argument, `website`. Read optional keys from the environment (`os.environ.get("NAME")`) and list them in `.env.example` and in the README.
- Bound every network call with a timeout. The API also stops waiting after the check's timeout, but a thread that keeps running still holds memory.
- Keep memory flat: the containers have 256 MB. Stream large downloads to disk instead of loading them.

## Registering a check

1. `api.py`: add the module to `CHECK_MODULES` and the category to `CHECK_CATEGORIES`.
2. `main.py`: add it to `WebsiteMonitor._initialize_check_functions` so the scheduled report runs it.
3. `docs/assets/app.js`: add it to `CHECKS` with the same category; `tests/test_ui_catalog.py` fails while the web UI and the API disagree. Add `check.<id>.name` and `check.<id>.hint` to every file in `docs/assets/locales/`; `tests/test_ui_locales.py` fails while a language lacks them.
4. Run `python scripts/export_openapi.py`. `tests/test_openapi_snapshot.py` fails while `docs/openapi.json` is out of date.
5. Add the check to the table in `README.md`.

## Interface text

Every string of the web UI is in `docs/assets/locales/en.json` and `it.json`, read through `t()` in `app.js` (static text in `index.html` through `data-i18n` attributes). To change or add text, edit both files: the tests fail when a key exists in one language only, when a translation drops a `{placeholder}`, or when a key is unused. After changing `app.js`, `app.css` or a locale file, bump `ASSET_VERSION` in `app.js` and the `?v=` in `index.html` together, or browsers keep the cached files.

## Commits and pull requests

- Branch from `main` and open a pull request against it.
- Commit messages follow Conventional Commits with a scope, and the subject says what changes for the user: `fix(checks): dnssec reads the signature from an A query instead of a refused RRSIG query`.
- Say in the pull request what you measured: the output of the check before and after on a real site, and the test that fails without the change.

## Reporting bugs and security issues

Open an issue with the check ID, the site you tested (if you can share it), the output you got and the output you expected.

Report security issues privately, as described in [SECURITY.md](SECURITY.md).
