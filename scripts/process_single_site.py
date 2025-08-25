# scripts/process_single_site.py
import sys
import os
from playwright.sync_api import sync_playwright

site = sys.argv[1]
har_path = sys.argv[2]

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(record_har_path=har_path, record_har_content="omit")
        page = context.new_page()
        page.goto(site, wait_until="load", timeout=20000)
        context.close()
        browser.close()
except Exception as e:
    print(f"⚠️ Failed for {site}: {e}", flush=True)
    if os.path.exists(har_path):
        try:
            os.remove(har_path)
            print("🗑️ Deleted incomplete HAR", flush=True)
        except Exception as de:
            print(f"⚠️ Failed to delete: {de}", flush=True)
