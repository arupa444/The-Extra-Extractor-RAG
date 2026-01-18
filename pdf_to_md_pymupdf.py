import fitz  # PyMuPDF


def pdf_to_markdown(pdf_path: str, output_md: str):
    doc = fitz.open(pdf_path)

    md_lines = []

    for page in doc:
        blocks = page.get_text("dict")["blocks"]

        for block in blocks:
            if "lines" not in block:
                continue

            for line in block["lines"]:
                line_text = ""
                max_font_size = 0

                for span in line["spans"]:
                    text = span["text"].strip()
                    if not text:
                        continue

                    font_size = span["size"]
                    max_font_size = max(max_font_size, font_size)
                    line_text += text + " "

                line_text = line_text.strip()
                if not line_text:
                    continue

                # ---- HEADING LOGIC ----
                if max_font_size >= 18:
                    md_lines.append(f"# {line_text}")
                elif 15 <= max_font_size < 18:
                    md_lines.append(f"## {line_text}")
                elif 13 <= max_font_size < 15:
                    md_lines.append(f"### {line_text}")
                else:
                    md_lines.append(line_text)

        md_lines.append("\n")

    with open(output_md, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))


if __name__ == "__main__":
    pdf_to_markdown(
        pdf_path="data/apmsmeoneMSME/files/apmsmeone.ap.gov.in_Downloads_GOS_CIRCULARS_NODALOFFICERNODALAGENCY.pdf.pdf",
        output_md="apmsmeone.ap.gov.in_Downloads_RAMP_MSME%20Handbook.md"
    )
