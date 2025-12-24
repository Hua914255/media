
import PyPDF2
import sys

def read_pdf(path):
    try:
        reader = PyPDF2.PdfReader(path)
        print(f"Total Pages: {len(reader.pages)}")
        for i, page in enumerate(reader.pages):
            print(f"--- Page {i+1} ---")
            print(page.extract_text())
            print("\n")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    read_pdf(r"d:/STUDY/SchoolLearning/level3/Interactive_media_technology/lab/故事演化公式定义.pdf")
