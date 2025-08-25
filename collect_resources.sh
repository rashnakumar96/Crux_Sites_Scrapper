
if [ -z "$1" ]; then
  echo "❌ Usage: $0 <COUNTRY_CODE>"
  exit 1
fi

country="$1"
echo "Running HAR capture for $country"
VPN_COUNTRY=$country \
NORDVPN_TOKEN="e9f2ab7c6187216b5261e064f6658e697ffd4e8b119bca022a6a97b565e8a228" \
docker-compose up --build --force-recreate --abort-on-container-exit
