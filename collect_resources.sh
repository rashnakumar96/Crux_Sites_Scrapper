
if [ -z "$1" ]; then
  echo "❌ Usage: $0 <COUNTRY_CODE>"
  exit 1
fi

country="$1"
echo "Running HAR capture for $country"
VPN_COUNTRY=$country \
NORDVPN_TOKEN="" \
docker-compose up --build --force-recreate --abort-on-container-exit
