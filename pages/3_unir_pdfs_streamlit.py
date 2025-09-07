import streamlit as st
from PyPDF2 import PdfMerger
import tempfile
import os

st.set_page_config(page_title="Unir PDFs", page_icon="📎")
st.title("📎 Combinador de PDFs")

uploaded_files = st.file_uploader("Sube los archivos PDF a unir", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    filenames = [file.name for file in uploaded_files]
    order = st.multiselect(
        "Selecciona y ordena los archivos en el orden deseado",
        options=filenames,
        default=filenames,
        key="order",
    )

    if len(order) != len(filenames):
        st.warning("⚠️ Asegúrate de incluir todos los archivos en el orden.")
    else:
        if st.button("🔗 Unir PDFs"):
            with st.spinner("Procesando..."):
                merger = PdfMerger()
                file_map = {file.name: file for file in uploaded_files}

                for name in order:
                    file = file_map[name]
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        tmp.write(file.read())
                        merger.append(tmp.name)

                output_path = os.path.join(tempfile.gettempdir(), "PDF_Combando.pdf")
                merger.write(output_path)
                merger.close()

                with open(output_path, "rb") as f:
                    st.success("✅ PDF combinado exitosamente")
                    st.download_button(
                        label="📥 Descargar PDF combinado",
                        data=f,
                        file_name="PDF_Combinado.pdf",
                        mime="application/pdf"
                    )
