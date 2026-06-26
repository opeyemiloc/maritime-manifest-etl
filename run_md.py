from markitdown import MarkItDown

md = MarkItDown()
result = md.convert_local("MSC ANA CAMILA III ZA622A TINCAN  PDF.pdf")

with open("output_msc.md", "w", encoding="utf-8") as f:
    f.write(result.text_content)

print("Done. Saved to output_msc.md")