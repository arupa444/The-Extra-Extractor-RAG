import sys
from scrapy.crawler import CrawlerProcess
from utils.spider import FullWebsiteSpider

target_url = sys.argv[1]

process = CrawlerProcess({
    "LOG_LEVEL": "INFO",
    "DOWNLOAD_HANDLERS": {
        "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    },
    "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
    "PLAYWRIGHT_BROWSER_TYPE": "chromium",
})

process.crawl(
    FullWebsiteSpider,
    start_url=target_url
)

process.start()
