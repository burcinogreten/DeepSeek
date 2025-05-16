import streamlit as st
from pdf2image import convert_from_bytes
from PIL import Image, ImageChops, ImageDraw
import io
from datetime import date
import numpy as np

st.set_page_config(page_title="PDF Görsel Karşılaştırıcı", layout="wide")
st.title("📄 PDF Karşılaştırıcı (Görsel + Notlar + Tarih + Görünüm Seçimi)")

uploaded_files = st.file_uploader("PDF dosyalarınızı yükleyin (en fazla 10 tane)", type="pdf", accept_multiple_files=True)

if uploaded_files and len(uploaded_files) >= 2:
    file_names = [f.name for f in uploaded_files]
    file_dict = {f.name: f for f in uploaded_files}

    col1, col2 = st.columns(2)
    with col1:
        file1_name = st.selectbox("📂 Önceki Versiyon", file_names)
    with col2:
        file2_name = st.selectbox("📂 Yeni Versiyon", file_names, index=1)

    st.markdown("---")
    st.subheader("📝 Notlar ve Revizyon Tarihi")
    selected_date = st.date_input("📅 Revizyon Tarihi", value=date.today())
    notes = st.text_area("📌 Notlarınızı yazın (örneğin: ne değişti, kim yaptı)")

    st.markdown("---")
    view_option = st.radio("🖼️ Görüntüleme Şekli", ["Yan Yana", "Üst Üste"], horizontal=True)
    highlight_option = st.checkbox("🔴 Farklılıkları vurgula", value=True)

    if file1_name != file2_name:
        if st.button("🔍 Karşılaştır"):
            pdf1 = file_dict[file1_name].getvalue()
            pdf2 = file_dict[file2_name].getvalue()

            st.subheader("🖼️ Sayfa 1 Görsel Karşılaştırması")
            try:
                # PDF'leri görüntüye çevir
                img1 = convert_from_bytes(pdf1, first_page=1, last_page=1, dpi=200)[0].convert("RGB")
                img2 = convert_from_bytes(pdf2, first_page=1, last_page=1, dpi=200)[0].convert("RGB")

                # Boyutları eşitle (orijinal en-boy oranını koruyarak)
                max_width = 800
                ratio = min(max_width/img1.width, max_width/img2.width)
                new_size = (int(img1.width * ratio), int(img1.height * ratio))
                
                img1 = img1.resize(new_size, Image.LANCZOS)
                img2 = img2.resize(new_size, Image.LANCZOS)

                # Farkları bul
                diff = ImageChops.difference(img1, img2)
                
                # Farkları işaretle (eğer seçiliyse)
                highlighted = img2.copy()
                if highlight_option:
                    diff_array = np.array(diff)
                    if np.any(diff_array > 0):
                        bbox = diff.getbbox()
                        if bbox:
                            draw = ImageDraw.Draw(highlighted)
                            draw.rectangle(bbox, outline="red", width=3)
                    else:
                        st.success("✅ İki PDF arasında görsel fark bulunamadı.")

                if view_option == "Yan Yana":
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.image(img1, caption="Önceki Versiyon", use_column_width=True)
                    with col2:
                        st.image(img2, caption="Yeni Versiyon", use_column_width=True)
                    if highlight_option:
                        with col3:
                            st.image(highlighted, caption="Farklılıklar (Kırmızıyla İşaretli)", use_column_width=True)
                else:
                    st.image(img1, caption="Önceki Versiyon", use_column_width=True)
                    st.image(img2, caption="Yeni Versiyon", use_column_width=True)
                    if highlight_option:
                        st.image(highlighted, caption="Farklılıklar (Kırmızıyla İşaretli)", use_column_width=True)

                # Not ve tarih bilgisi
                st.markdown("---")
                st.success(f"🗓️ Tarih: {selected_date}  \n📝 Not: {notes if notes else 'Not girilmedi'}")

            except Exception as e:
                st.error(f"Görsel karşılaştırma sırasında hata oluştu: {str(e)}")
                st.error("PDF'ler görüntüye dönüştürülemedi. PDF'lerin bozuk olmadığından emin olun.")
else:
    st.info("Lütfen karşılaştırmak için en az iki PDF dosyası yükleyin.")
