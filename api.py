"""
Entry point kept for docker-compose (python api.py) and uvicorn api:app.
The REST API lives in websites_monitor/adapters/http.py.
"""
import os

import uvicorn

from checks.check_domainsblacklists_blacklist import prefetch_blacklist
from websites_monitor.adapters.http import create_app
from websites_monitor.bootstrap import build_service

# The domain blacklist takes 20-30 s to download: fetch it at startup, not
# inside the first scan, where it would hit the check timeout.
app = create_app(build_service(), on_startup=prefetch_blacklist)

if __name__ == "__main__":
    # Reloading restarts the server whenever a file under the app changes,
    # and drops every request in flight: development only.
    reload = os.environ.get("API_RELOAD", "").lower() in ("1", "true", "yes")
    uvicorn.run("api:app", host=os.environ.get("API_HOST", "0.0.0.0"),
                port=int(os.environ.get("API_PORT", "8000")), reload=reload)
