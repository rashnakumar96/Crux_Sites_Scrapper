import os
import json
from multiprocessing import Process
from playwright.sync_api import sync_playwright
from concurrent.futures import ProcessPoolExecutor
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

DATA_DIR = "/app/data"
HAR_ROOT = os.path.join(DATA_DIR, "har_files")
TOP_SITES_FILE = os.path.join(DATA_DIR, "top_sites_per_country.json")

def load_top_sites_from_json(country_code):
    with open(TOP_SITES_FILE, "r") as f:
        country_sites = json.load(f)
    return country_sites.get(country_code.upper(), [])

def process_site_batch(country, site_list,max_workers=4):
    har_dir = os.path.join(HAR_ROOT, country)
    os.makedirs(har_dir, exist_ok=True)
    number_of_sites = len(site_list)

    def run_site(site, idx):
        tid = threading.get_ident()
        thread_id = f"W{tid % 100:02d}"  
        domain = site.replace("https://", "").replace("http://", "").replace("/", "_")
        har_path = os.path.join(har_dir, f"{domain}.har")

        if os.path.exists(har_path):
            print(f"⏭️ (Worker {thread_id}) Skipping {site} (HAR already exists)", flush=True)
            return
        print(f"🌐 (Worker {thread_id}) Capturing HAR for {site} ({idx}/{number_of_sites})", flush=True)
        try:
            subprocess.run(
                ["python", "scripts/process_single_site.py", site, har_path],
                timeout=30
            )
        except subprocess.TimeoutExpired:
            print(f"❌ Subprocess timed out for {site}", flush=True)
            if os.path.exists(har_path):
                try:
                    os.remove(har_path)
                    print("🗑️ Deleted timed-out HAR", flush=True)
                except:
                    print("⚠️ Failed to delete after timeout", flush=True)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(run_site, site, idx) for idx, site in enumerate(site_list)]
        for future in as_completed(futures):
            try:
                future.result()  # Raise exceptions if any
            except Exception as e:
                print(f"⚠️ Exception during site capture: {e}", flush=True)


