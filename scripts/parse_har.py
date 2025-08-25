import os
import json
import socket
from urllib.parse import urlparse
import time
import dns.resolver
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
# import check_govt_in_top_sites
import sys


HAR_ROOT = "/app/data/har_files"
OUT_DIR = "/app/data/resources"
os.makedirs(OUT_DIR, exist_ok=True)
IP_DIR = "/app/data/ips"
os.makedirs(IP_DIR, exist_ok=True)

def extract_resources(har_path):
    with open(har_path, 'r') as f:
        har_data = json.load(f)
    entries = har_data.get('log', {}).get('entries', [])
    resources = []
    for entry in entries:
        url = entry.get('request', {}).get('url')
        resources.append(url)
    return resources

def process_country_har(country):
    har_dir = os.path.join(HAR_ROOT, country)
    out_path = os.path.join(OUT_DIR, f"{country}_resources.json")
    all_resources = {}

    for fname in os.listdir(har_dir):
        if fname.endswith(".har"):
            domain = fname.replace(".har", "")
            path = os.path.join(har_dir, fname)
            print(f"Parsing {domain}")
            all_resources[domain] = extract_resources(path)

    with open(out_path, "w") as f:
        json.dump(all_resources, f, indent=2)

def extract_fqdn(url):
    try:
        return urlparse(url).hostname
    except:
        return None
    
def extract_unique_domains(country):
    out_path = os.path.join(OUT_DIR, f"{country}_resources.json")
    with open(out_path) as f:
        json_data = json.load(f)
    fqdns = set()
    # _,govt_topsite_match=check_govt_in_top_sites.label_gov_fqdns(country)
    for site, site_data in json_data.items():
        # if site in govt_topsite_match:
        #     continue
        for url in site_data:
            fqdn = extract_fqdn(url)
            if fqdn:
                fqdns.add(fqdn)
    return list(fqdns)

def robust_resolve(domain, retries=3, delay=0.3):
    """Attempt to resolve a domain with retries and fallback to dnspython."""
    for attempt in range(retries):
        try:
            return socket.gethostbyname(domain)
        except socket.gaierror:
            time.sleep(delay)
    try:
        answer = dns.resolver.resolve(domain, 'A', lifetime=2)
        return answer[0].to_text()
    except Exception:
        return None

def resolve_and_get_asn(domain):
    try:
        ip = robust_resolve(domain)
        return domain, ip
    except Exception as e:
        print(f"IP resolution failed for {domain}: {e}")
    return domain, None, None

def build_domain_map(country,max_threads=100):
    """Build a domain-to-IP-to-ASN map using parallel DNS resolution with retries."""
    domain_list=extract_unique_domains(country)
    domain_map = {}

    total = len(domain_list)
    completed = 0

    print(f"🔍 Resolving {total} domains for {country}...")

    with ThreadPoolExecutor(max_threads) as executor:
        futures = {executor.submit(resolve_and_get_asn, d): d for d in domain_list}
        for future in tqdm(as_completed(futures), total=total, desc=f"🔄 Resolving"):
            try:
                domain, ip = future.result()
                if ip:
                    domain_map[domain] = {"ip": ip}
            except Exception as e:
                print(f"⚠️ Resolution error: {e}")
            completed += 1
            if completed % 100 == 0 or completed == total:
                print(f"✅ Completed {completed}/{total}", flush=True)

    out_path = os.path.join(IP_DIR, f"{country}_domain_ip_map.json")
    with open(out_path, "w") as f:
        json.dump(domain_map, f, indent=2)
    print(f"📦 Saved {len(domain_map)} resolved domains to {out_path}")

if __name__ == "__main__":
    # main()
    if len(sys.argv) < 2:
        print("❌ Usage: python your_script.py <COUNTRY_CODE>")
        sys.exit(1)
    country = sys.argv[1]
    # process_country_har(country)
    build_domain_map(country,max_threads=100)