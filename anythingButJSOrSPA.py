from docling.document_converter import DocumentConverter

source = "Screenshot 2025-12-19 at 8.17.50 PM.png"  # document per local path or URL
converter = DocumentConverter()
result = converter.convert(source)
print(result.document.export_to_markdown())  # output: "## Docling Technical Report[...]"