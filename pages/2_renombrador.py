import streamlit as st
import zipfile
import re
import io
import csv
from bs4 import BeautifulSoup

st.header("📄 Renombrador de pedidos ALCAMPO")

st.write("Subí tus archivos `.htm` de pedidos y descargá todo ya renombrado.")

uploaded_files = st.file_uploader("Seleccioná los archivos .htm", type="htm", accept_multiple_files=True)

if uploaded_files:
    csv_rows = [("Nombre original", "Nuevo nombre")]
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        for file in uploaded_files:
            original_name = file.name
            content = file.read().decode("utf-8", errors="ignore")
            soup = BeautifulSoup(content, "html.parser")
            text = soup.get_text(separator="\n")

            def extract(pat, default=""):
                m = re.search(pat, text, re.IGNORECASE)
                return m.group(1).strip() if m else default

            pedido = extract(r"Pedido de compra\s*.*\n.*\n(EP\d+)")
            sitio_linea = extract(r"Sitio\s+Tienda\s+([A-ZÀ-ÿ ]+).*-?\s*Entidad\s*(\d+)")
            tienda = sitio_linea.split()[0] if sitio_linea else "Tienda"
            numero_tienda = extract(r"Sitio\s+(\d{4})")
            pac = extract(r"PAC\s*(\d+/\d+)").replace("/", "-")
            descripcion = extract(r"honorarios.*PAC.*")
            descripcion = re.sub(r"honorarios\s+ingenieria\s+", "", descripcion, flags=re.IGNORECASE)
            descripcion = descripcion.strip().lower().replace("  ", " ")

            if not (numero_tienda and pedido and pac):
                continue

            nuevo_nombre = f"{numero_tienda} {tienda.upper()} PAC {pac} pedido {pedido} {descripcion}.htm"
            nuevo_nombre = nuevo_nombre.replace("\n", " ").replace("\r", " ")

            zipf.writestr(nuevo_nombre, content)
            csv_rows.append((original_name, nuevo_nombre))

        # CSV dentro del ZIP
        csv_content = io.StringIO()
        csv_writer = csv.writer(csv_content)
        csv_writer.writerows(csv_rows)
        zipf.writestr("renombrados.csv", csv_content.getvalue())

    st.download_button(
        label="📦 Descargar archivos renombrados (.zip)",
        data=zip_buffer.getvalue(),
        file_name="renombrados.zip",
        mime="application/zip"
    )
