## Summary

In this repository, I implement a customized scrapy crawler to crawl a list of
URLs with its HTML, screenshot, information.

## Environment setup [! We find that the scrapy crawler only works with python version 3.7.10]

```
conda create --name py37-fixed python=3.7.10
conda activate py37-fixed
pip install -r requirement.txt
```
if pip install fail, please install dependency one by one

## Step 1: Start Splash Server in Docker

```
cd phishing-splashserver
docker-compose up
docker-start-stop.sh
```

## Step 2: Start URL feeding, feed obtained from Certstream

- For windows

```
cd ../
start_server_windows_certstream.bat
```

- For Linux

```
cd ../
bash ./start_server_linux_certstream.sh
```

## Step 3: Run scrapy crawler

- Change the USER_AGENT in companycrawl/settings.py to your own user agent
- Change the output_folder in companycrawl/spider/example.py to where you want
  to save the scraped results

```
scrapy crawl company
```
