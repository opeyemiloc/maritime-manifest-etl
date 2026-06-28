from markitdown import MarkItDown
import os
from pathlib import Path

def convert_pdf_to_md(input_pdf_path, output_md_path):
    """
    Dynamically converts any given PDF to Markdown and saves it to the target location.
    """
    input_pdf_path = Path(input_pdf_path)
    output_md_path = Path(output_md_path)

    # Ensure the target md output directory exists
    os.makedirs(output_md_path.parent, exist_ok=True)

    print(f"Starting conversion for: {input_pdf_path.name}...")
    md = MarkItDown()
    
    try:
        # Convert the PDF (passing the path as a string)
        result = md.convert_local(str(input_pdf_path))

        # Save to the specified output directory
        with open(output_md_path, "w", encoding="utf-8") as f:
            f.write(result.text_content)

        print(f"✅ Done! Markdown saved to: \n{output_md_path}")
        return output_md_path
        
    except FileNotFoundError:
        print(f"❌ Error: Could not find the input file at:\n{input_pdf_path}")
        raise # Rethrow the error so the main pipeline knows it failed
    except Exception as e:
        print(f"❌ An error occurred during conversion: {e}")
        raise

if __name__ == "__main__":
    # This allows you to still run it standalone if you want to!
    root_dir = Path(__file__).resolve().parent.parent
    test_input = root_dir / "data" / "inputs" / "MSC ANA CAMILA III ZA622A TINCAN  PDF.pdf"
    test_output = root_dir / "data" / "outputs" / "md" / "output_msc.md"
    convert_pdf_to_md(test_input, test_output)