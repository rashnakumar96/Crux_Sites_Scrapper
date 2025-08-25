import os
import requests
from playwright.sync_api import sync_playwright
import har_capture
from parse_har import process_country_har,build_domain_map
import time

def verify_vpn_country(expected_country):
    """Verify external IP geolocation to confirm VPN connection."""
    print("🌐 Verifying VPN connection...")
    try:
        response = requests.get("https://ifconfig.co/json", timeout=10)
        data = response.json()
        actual_country = data.get("country", "UNKNOWN").upper()
        ip = data.get("ip", "UNKNOWN")
        # actual_country = utils.call_ipinfo(ip)
        print(f"✅ VPN is connected to {actual_country} (IP: {ip})")
    except Exception as e:
        raise RuntimeError(f"⚠️ VPN check failed: {e}")


# countryList=["TH","KR","AE","ZA","UY","CR","BR","VN","TW","BD","KZ","MA","NZ","AR"]  
def main():
    start_time = time.time()
    country = os.environ.get("COUNTRY", "US").upper()
    print(f"🚩 Target country (from env): {country}")
    time.sleep(10)
    verify_vpn_country(country)
            
    with sync_playwright() as playwright:
        print(f"🔄 Running HAR capture for {country}")
        site_list=har_capture.load_top_sites_from_json(country)
        har_capture.process_site_batch(country, site_list,max_workers=4)
        print(f"📦 Extracting resources for {country}")
        process_country_har(country)
        build_domain_map(country,max_threads=100)
    
    end_time = time.time()
    duration = end_time - start_time
    minutes, seconds = divmod(duration, 60)
    print(f"✅ Script completed in {int(minutes)} minutes and {seconds:.2f} seconds")

if __name__ == "__main__":
    main()