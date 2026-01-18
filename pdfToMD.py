from docling.document_converter import DocumentConverter

# Initialize the converter once
converter = DocumentConverter()


def pdf_to_markdown(file_path: str) -> str:
    # docling detects the format automatically from the file extension
    result = converter.convert(file_path)
    return result.document.export_to_markdown()


# ---------------------------------------------------------
# HOW TO USE IT
# ---------------------------------------------------------

pdf_path = "data/apmsmeoneMSME/files/apmsmeone.ap.gov.in_Data_ExistingPolicy_2025INDS_35747_MS28_E.pdf.pdf"  # <--- Change this to your PDF file path

try:
    # 1. Pass the FILE PATH directly (not the file content)
    markdown_output = pdf_to_markdown(pdf_path)

    # 2. Print or Save the result
    print(markdown_output[:500])  # Preview first 500 chars

    with open("output.md", "w", encoding="utf-8") as f:
        f.write(markdown_output)
        print("\n--- Saved output to 'output.md' ---")

except Exception as e:
    print(f"An error occurred: {e}")