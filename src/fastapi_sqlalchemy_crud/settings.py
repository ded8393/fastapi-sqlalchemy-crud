import os

from platformdirs import user_cache_path

DEBUG = os.environ.get("DEBUG", "").lower() not in {"", "0", "false"}

CACHE_DIR = user_cache_path("boh_app")
