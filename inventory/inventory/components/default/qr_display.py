import streamlit as st
import os
from PIL import Image
from ...utils.qr_code import generate_qr_code
from ...utils.database import IMAGES_DIR

def qr_display(sku, size=200, download_button=True):
    """
    Display a QR code for a SKU with optional download button.
    
    Args:
        sku (str): The SKU to generate a QR code for
        size (int): The size of the QR code image
        download_button (bool): Whether to show a download button
    """
    # Get or generate QR code path
    qr_path = os.path.join(IMAGES_DIR, f"qr_{sku}.png")
    if not os.path.exists(qr_path):
        qr_path = generate_qr_code(sku)
    
    # Display QR code
    if os.path.exists(qr_path):
        image = Image.open(qr_path)
        st.image(image, width=size, caption=f"QR Code for {sku}")
        
        # Add download button if requested
        if download_button:
            with open(qr_path, "rb") as file:
                qr_bytes = file.read()
                st.download_button(
                    label="Download QR Code",
                    data=qr_bytes,
                    file_name=f"qr_{sku}.png",
                    mime="image/png"
                )
    else:
        st.error(f"QR code for {sku} could not be generated.")