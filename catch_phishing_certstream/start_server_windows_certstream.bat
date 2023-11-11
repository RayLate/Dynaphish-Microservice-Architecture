@echo off

start cmd /k "python server.py"
start cmd /k "python catch_phishing_certstream.py"
start cmd /k "scrapy crawl company"
