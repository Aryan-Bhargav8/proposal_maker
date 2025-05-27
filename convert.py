import pypandoc
# from docx2pdf import convert
from spire.doc import *
from spire.doc.common import *



document = Document()


def convert_md_to_docx(md_file_path, docx_file_path):
    try:
        # Ensure Pandoc is available
        try:
            pypandoc.get_pandoc_version()
        except OSError:
            print("Pandoc not found. Downloading pandoc...")
            pypandoc.download_pandoc()
        # Convert Markdown to DOCX
        pypandoc.convert_file(
            source_file=md_file_path,
            to="docx",
            outputfile=docx_file_path,
            extra_args=["--standalone"]
        )
        print(f"Conversion successful: {docx_file_path}")
    except Exception as e:
        print(f"Error during conversion: {e}")

def main():
    md_file_path = "output/final_md/refined_proposal.md"
    docx_file_path = "Refined Proposal1.docx"
    convert_md_to_docx(md_file_path, docx_file_path)
    # convert(docx_file_path, r"/Final Proposal.pdf")

    # Convert the DOCX file to PDF
    document.LoadFromFile(docx_file_path)
    document.SaveToFile("Refined Proposal1.pdf", FileFormat.PDF)
    document.Close()

if __name__ == "__main__":
    main()