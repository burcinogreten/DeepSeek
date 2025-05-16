import streamlit as st
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
import os
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def add_notes_to_pdf(pdf_bytes, notes_text):
    """PDF'e not ekler"""
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    
    # Notları PDF'in altına ekleyelim
    can.setFont("Helvetica", 10)
    text = can.beginText(40, 40)
    text.textLines(notes_text)
    can.drawText(text)
    can.save()
    
    packet.seek(0)
    notes_pdf = PdfReader(packet)
    
    original_pdf = PdfReader(BytesIO(pdf_bytes))
    output = PdfWriter()
    
    for page in original_pdf.pages:
        page.merge_page(notes_pdf.pages[0])
        output.add_page(page)
    
    output_stream = BytesIO()
    output.write(output_stream)
    return output_stream.getvalue()

def merge_pdfs(pdf1_bytes, pdf2_bytes, mode='side_by_side'):
    """İki PDF'i birleştirir"""
    pdf1 = PdfReader(BytesIO(pdf1_bytes))
    pdf2 = PdfReader(BytesIO(pdf2_bytes))
    
    output = PdfWriter()
    
    if mode == 'side_by_side':
        # Yan yana birleştirme (basit bir yaklaşım)
        for page1, page2 in zip(pdf1.pages, pdf2.pages):
            page1.merge_page(page2)
            output.add_page(page1)
    else:  # üst üste
        for page in pdf1.pages:
            output.add_page(page)
        for page in pdf2.pages:
            output.add_page(page)
    
    output_stream = BytesIO()
    output.write(output_stream)
    return output_stream.getvalue()

def main():
    st.title("PDF Karşılaştırma Aracı")
    st.subheader("Çizim PDF'lerini Karşılaştırın")
    
    # PDF yükleme
    uploaded_files = st.file_uploader("PDF Dosyalarını Yükleyin", type="pdf", accept_multiple_files=True)
    
    if not uploaded_files:
        st.warning("Lütfen en az iki PDF dosyası yükleyin.")
        return
    
    if len(uploaded_files) < 2:
        st.warning("Karşılaştırma yapabilmek için en az iki PDF dosyası gerekli.")
        return
    
    # PDF seçimi
    file_names = [file.name for file in uploaded_files]
    col1, col2 = st.columns(2)
    
    with col1:
        pdf1_choice = st.selectbox("Birinci PDF'i seçin", file_names)
    with col2:
        # İkinci seçenekte birinci seçilen hariç diğerleri
        remaining_files = [name for name in file_names if name != pdf1_choice]
        pdf2_choice = st.selectbox("İkinci PDF'i seçin", remaining_files)
    
    # Seçilen PDF'leri bul
    pdf1_bytes = None
    pdf2_bytes = None
    for file in uploaded_files:
        if file.name == pdf1_choice:
            pdf1_bytes = file.read()
        elif file.name == pdf2_choice:
            pdf2_bytes = file.read()
    
    # Not ekleme
    st.subheader("Not Ekleme")
    notes1 = st.text_area(f"{pdf1_choice} için notlar", height=100)
    notes2 = st.text_area(f"{pdf2_choice} için notlar", height=100)
    
    # PDF'leri notlarla güncelle
    if notes1:
        pdf1_bytes = add_notes_to_pdf(pdf1_bytes, notes1)
    if notes2:
        pdf2_bytes = add_notes_to_pdf(pdf2_bytes, notes2)
    
    # Birleştirme modu
    merge_mode = st.radio("Birleştirme Modu", ["Yan Yana", "Üst Üste"])
    
    # Önizleme butonu
    if st.button("PDF'leri Birleştir ve Göster"):
        if pdf1_bytes and pdf2_bytes:
            merged_pdf = merge_pdfs(
                pdf1_bytes, 
                pdf2_bytes, 
                mode='side_by_side' if merge_mode == "Yan Yana" else 'stacked'
            )
            
            # Önizleme göster
            st.success("PDF'ler başarıyla birleştirildi!")
            
            # PDF'i indirme butonu
            st.download_button(
                label="Birleştirilmiş PDF'i İndir",
                data=merged_pdf,
                file_name="birlestirilmis_pdf.pdf",
                mime="application/pdf"
            )
            
            # PDF'i göster (sınırlı destek)
            st.write("PDF Önizleme (sınırlı destek):")
            base64_pdf = base64.b64encode(merged_pdf).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
        else:
            st.error("PDF'ler yüklenirken bir hata oluştu.")

if __name__ == "__main__":
    import base64
    main()