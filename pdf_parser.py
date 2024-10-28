import re
import fitz  # PyMuPDF

def clean_text(text):
    """Function to clean text by removing unwanted characters, extra spaces, and redundant newlines."""
    text = re.sub(r'\s+', ' ', text)
    text = text.replace("\n", " ").replace("\r", " ")
    return text.strip()

def extract_text_from_pdf(pdf_path):
    """Extracts text from the given PDF, cleaning it and splitting into chunks."""
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Error opening PDF: {e}")
        return []

    text_chunks = []

    for page_num in range(doc.page_count):
        try:
            page = doc.load_page(page_num)
            text = page.get_text("text").strip()
            cleaned_text = clean_text(text)

            if cleaned_text:
                sentence_chunks = re.split(r'(?<=[.!?]) +', cleaned_text)
                for sentence in sentence_chunks:
                    if sentence.strip():
                        text_chunks.append({
                            "text": sentence.strip(),
                            "page_number": page_num + 1
                        })
        except Exception as e:
            print(f"Error processing page {page_num + 1}: {e}")

    return text_chunks
