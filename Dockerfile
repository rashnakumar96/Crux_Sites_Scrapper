# Base image with Playwright and Python
# FROM mcr.microsoft.com/playwright/python:v1.52.0-jammy
FROM mcr.microsoft.com/playwright/python:v1.54.0-jammy


# Install system tools
# RUN apt-get update && apt-get install -y curl iputils-ping && apt-get clean

RUN apt-get update \
 && apt-get install -y --no-install-recommends dnsutils curl iputils-ping \
 && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy your code

COPY requirements.txt ./
# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
COPY scripts/ ./scripts/
# ✅ Install Playwright Python bindings and browser binaries
# RUN pip install --no-cache-dir playwright && playwright install --with-deps
# Optional: install only Chromium to reduce image size
# RUN playwright install chromium --with-deps

# ✅ Set increased memory limit for Node.js engine used by Playwright
ENV NODE_OPTIONS=--max-old-space-size=4096

# Set the entrypoint for the container
ENTRYPOINT ["python", "-u", "scripts/run_country.py"]
