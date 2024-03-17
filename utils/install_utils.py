import subprocess
import os
import sys
from parameter_store import app_config


def inline_install(packages):
    for package in packages:
        if os.path.exists(f"/tmp/lib/site-packages/{package}") is False:
            subprocess.check_call([sys.executable.split("/")[-1], "-m", "pip", "install", package, "--no-deps", "-t", "/tmp/lib/site-packages", "--no-cache-dir"])
    sys.path.insert(1, "/tmp/lib/site-packages")