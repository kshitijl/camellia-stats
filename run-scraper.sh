#!/usr/bin/env sh

cd $(dirname $0)
./webcomic_stats_scraper/scrape-camellia-stats.py --config /config/camellia-scraper-production-repo.json download-and-measure
