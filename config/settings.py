import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CHROMEDRIVER_PATH = "chromedriver"  # If it's in the root or in PATH
CHROME_PATH = "/usr/bin/chromium"   # Optional, can be removed if not used
COOKIES_PATH = os.path.join(BASE_DIR, "..", "instagram_cookies.json")
