import streamlit as st
import pdfplumber
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io

def main():
    st.title("PDF Scraper")

    st.write(
        "Upload a PDF to extract text and/or images. "
        "For scanned PDFs, enable OCR if you need text from images."
    )

    # Let user select whether to apply OCR (for scanned PDFs)
    use_ocr = st.checkbox("Use OCR for scanned pages (slower)")

    # Upload PDF
    uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])

    # We only proceed if a PDF is uploaded
    if uploaded_pdf:
        # Convert the uploaded file to a bytes object
        pdf_bytes = uploaded_pdf.read()
        
        # Buttons to choose which action to take
        if st.button("Extract Text"):
            extracted_text = extract_text(pdf_bytes, use_ocr=use_ocr)
            st.subheader("Extracted Text")
            st.text_area("", extracted_text, height=300)

        if st.button("Extract Images"):
            image_list = extract_images(pdf_bytes)
            st.subheader("Extracted Images")
            if image_list:
                for idx, img in enumerate(image_list):
                    st.image(img, caption=f"Image #{idx+1}")
            else:
                st.write("No images found in this PDF.")

def extract_text(pdf_bytes, use_ocr=False):
    """
    Extracts text from PDF bytes. If use_ocr is True,
    each page is rendered as an image and then passed through Tesseract.
    """
    text_content = []
    
    if not use_ocr:
        # Simple direct text extraction with pdfplumber
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_content.append(page_text)
    else:
        # OCR each page with pdfplumber + pytesseract
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for idx, page in enumerate(pdf.pages):
                # Render page to image
                pil_image = page.to_image(resolution=300).original
                # OCR
                ocr_text = pytesseract.image_to_string(pil_image)
                text_content.append(f"Page {idx+1}:\n{ocr_text}\n")
    
    return "\n".join(text_content)

def extract_images(pdf_bytes):
    """
    Extracts images from the PDF as PIL images in a list.
    """
    images = []
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    for page_index in range(len(doc)):
        page = doc[page_index]
        image_list = page.get_images(full=True)
        
        for img_info in image_list:
            xref = img_info[0]
            base_image = doc.extract_image(xref)
            image_data = base_image["image"]
            # Convert to PIL image
            pil_img = Image.open(io.BytesIO(image_data))
            images.append(pil_img)

    return images

if __name__ == "__main__":
    main()

