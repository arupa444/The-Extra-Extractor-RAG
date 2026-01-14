from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from playwright.sync_api import sync_playwright

source = "https://the-little-journal.com/"


def get_dynamic_html(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_timeout(5000)
        html_content = page.content()
        browser.close()
        return html_content


# 1. Get the rendered HTML string
rendered_html = get_dynamic_html(source)

# 2. Convert the string using Docling
converter = DocumentConverter()

result = converter.convert_string(rendered_html, InputFormat.HTML)

print(result.document.export_to_markdown())