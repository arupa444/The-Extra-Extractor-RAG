import scrapy
import os
from urllib.parse import urlparse, urljoin, urldefrag
from scrapy_playwright.page import PageMethod


class FullWebsiteSpider(scrapy.Spider):
    name = "full_website"

    def __init__(self, start_url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.start_url = start_url
        self.allowed_domain = urlparse(start_url).netloc
        self.start_urls = [start_url]

        # =====================
        # DIRECTORY SETUP
        # =====================
        self.base_dir = os.path.join("storeCurlData", self.allowed_domain)
        self.html_dir = os.path.join(self.base_dir, "html")
        self.files_dir = os.path.join(self.base_dir, "files")

        os.makedirs(self.html_dir, exist_ok=True)
        os.makedirs(self.files_dir, exist_ok=True)

        # Track visited URLs manually (SPA-safe)
        self.seen = set()

    # =====================
    # START REQUEST (JS ENABLED)
    # =====================
    def start_requests(self):
        yield scrapy.Request(
            self.start_url,
            callback=self.parse,
            meta={
                "playwright": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_load_state", "networkidle"),
                ],
            },
        )

    # =====================
    # PARSER
    # =====================
    def parse(self, response):
        url = response.url

        # Normalize URL (remove fragments)
        url, _ = urldefrag(url)

        if url in self.seen:
            return
        self.seen.add(url)

        content_type = response.headers.get("Content-Type", b"").decode()

        safe_name = (
            url.replace("https://", "")
            .replace("http://", "")
            .replace("/", "_")
            .replace("?", "_")
            .replace("&", "_")
        )

        # =====================
        # HTML PAGE
        # =====================
        if "text/html" in content_type:
            path = os.path.join(self.html_dir, f"{safe_name}.html")

            with open(path, "w", encoding="utf-8") as f:
                f.write(response.text)

            self.logger.info(f"HTML saved: {path}")

            # Extract links AFTER JS execution
            links = response.css("a::attr(href)").getall()

            for link in links:
                absolute = urljoin(url, link)
                absolute, _ = urldefrag(absolute)

                parsed = urlparse(absolute)

                if parsed.netloc != self.allowed_domain:
                    continue

                if absolute in self.seen:
                    continue

                yield scrapy.Request(
                    absolute,
                    callback=self.parse,
                    meta={
                        "playwright": True,
                        "playwright_page_methods": [
                            PageMethod("wait_for_load_state", "networkidle"),
                        ],
                    },
                    dont_filter=True,  # we manage dedup manually
                )

        # =====================
        # NON-HTML FILE
        # =====================
        else:
            ext = content_type.split("/")[-1].split(";")[0]
            path = os.path.join(self.files_dir, f"{safe_name}.{ext}")

            with open(path, "wb") as f:
                f.write(response.body)

            self.logger.info(f"FILE saved: {path}")
