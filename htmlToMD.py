from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat


converter = DocumentConverter()


def html_to_markdown(html: str) -> str:
    result = converter.convert_string(html, InputFormat.HTML)
    return result.document.export_to_markdown()


file_path = "data/apmsmeoneMSME/html/apmsmeone.ap.gov.in_.html"  # <--- REPLACE THIS with your file name

try:
    # 2. Open the file and read its contents into a string
    # We use encoding="utf-8" to handle special characters correctly
    with open(file_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    # 3. Send the string to your function
    markdown_output = html_to_markdown(html_content)

    # 4. Print the result or save it to a new file
    print("--- Conversion Successful. Here is the start of the Markdown: ---")
    print(markdown_output[:500]) # Print first 500 characters to preview

    # Optional: Save the result to a Markdown file
    with open("output.md", "w", encoding="utf-8") as f:
        f.write(markdown_output)
        print("\n--- Saved output to 'output.md' ---")

except FileNotFoundError:
    print(f"Error: Could not find the file named '{file_path}'. Make sure the path is correct.")
except Exception as e:
    print(f"An error occurred: {e}")