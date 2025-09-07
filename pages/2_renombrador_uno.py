import streamlit as st
import re
from bs4 import BeautifulSoup

st.title("📄 Renombrador de Pedido (1 archivo)")

uploaded_file = st.file_uploader("Subí un archivo .htm", type=["htm"])

def extract(text, pat, default=""):
    m = re.search(pat, text, re.IGNORECASE)
    if not m:
        return default
    return m.group(1).strip() if m.lastindex else m.group(0).strip()

def safe_filename(name):
    return re.sub(r'[\\/:*?"<>|]+', "_", name)

if uploaded_file:
    content = uploaded_file.read().decode("utf-8", errors="ignore")
    soup = BeautifulSoup(content, "html.parser")
    text = soup.get_text(separator="\n")

    pedido = extract(text, r"Pedido de compra\s*.*\n.*\n(EP\d+)")
    sitio_linea = extract(text, r"Sitio\s+Tienda\s+([A-ZÀ-ÿ ]+).*-?\s*Entidad\s*(\d+)")
    tienda = sitio_linea.split()[0] if sitio_linea else "Tienda"
    numero_tienda = extract(text, r"Sitio\s+(\d{4})")
    pac = extract(text, r"PAC\s*(\d+/\d+)").replace("/", "-")
    descripcion = extract(text, r"(honorarios.*PAC.*)")
    descripcion = re.sub(r"honorarios\s+ingenieria\s+", "", descripcion, flags=re.IGNORECASE)
    descripcion = descripcion.strip().lower().replace("  ", " ")

    if not (numero_tienda or pedido or pac):
        nuevo_nombre = f"{uploaded_file.name} (no renombrado).htm"
    else:
        nuevo_nombre = f"{numero_tienda} {tienda.upper()} PAC {pac} pedido {pedido} {descripcion}.htm"

    nuevo_nombre = safe_filename(nuevo_nombre)

    st.success(f"✅ Archivo procesado. Nuevo nombre: {nuevo_nombre}")

    st.download_button(
        label="📥 Descargar archivo renombrado",
        data=content,
        file_name=nuevo_nombre,
        mime="text/html"
    )