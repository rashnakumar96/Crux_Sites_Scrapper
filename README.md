## Prerequisites

1. Docker and Docker Compose installed.
2. A NordVPN token with a valid subscription. Add your NordVPN token in collect_resources.sh
3. Python 3.x if you plan to run any helper scripts outside Docker.


# HAR Capture & Resource Collection

This repository provides tools to collect HAR files of websites and extract their resources for analysis.

## Usage

Run the collection script with a two-letter country code:

```bash
./collect_resources.sh CC
```

where CC is the ISO country code (e.g., US, IN, FR).

---

## How It Works

- Reads the top 1,000 CrUX sites for the specified country from the **cached file**:
`data/top_sites_per_country.json`

- Connects to **NordVPN** using the provided country code (`CC`).

- Collects HAR (HTTP Archive) files for each site and stores them in:  
  `data/har_files/CC/`

- Extracts resources from the HAR files and saves them in:  
  `data/resources/CC_resources.json`

  This file is structured **per CrUX site**, mapping each site to the list of resources observed.

