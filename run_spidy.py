import sys
from scrapy.crawler import CrawlerProcess
from utils.spider import FullWebsiteSpider

target_url = sys.argv[1]

process = CrawlerProcess({
    "LOG_LEVEL": "INFO",

    # Playwright config
    "DOWNLOAD_HANDLERS": {
        "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    },
    "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
    "PLAYWRIGHT_BROWSER_TYPE": "chromium",
    "PLAYWRIGHT_CONTEXTS": {
        "default": {
            "java_script_enabled": True,
            "ignore_https_errors": True,
        }
    },


    # Performance tuning
    "CONCURRENT_REQUESTS": 4,
    "DOWNLOAD_DELAY": 0.5,
})


process.crawl(
    FullWebsiteSpider,
    start_url=target_url
)

process.start()
