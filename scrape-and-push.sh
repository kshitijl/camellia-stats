./webcomic_stats_scraper/scrape-camellia-stats.py --config /home/kslauria/production-config.json download-and-measure
./webcomic_stats_scraper/scrape-camellia-stats.py --config /home/kslauria/production-config.json generate-report
git commit -am "Scheduled scrape"
git push
