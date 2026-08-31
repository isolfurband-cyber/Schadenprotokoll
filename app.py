import streamlit as st
import os
from datetime import datetime
from PIL import Image
from io import BytesIO
from weasyprint import HTML
import base64

st.set_page_config(page_title="KARE-Immobilien Schadensaufnahmeprotokoll", page_icon="📝", layout="wide")

st.title("KARE-Immobilien – Schadensaufnahmeprotokoll")
st.markdown("Erfassung von Mängeln und Schäden mit Bild-Upload und automatisierter PDF-Generierung.")

with st.form("schaden_form"):
    st.header("1. Stammdaten & Objekt")
    col1, col2 = st.columns(2)
    with col1:
        objekt_adresse = st.text_input("Objektadresse / Liegenschaft", "Talstr. 32, 07545 Gera")
        mieter_name = st.text_input("Name des Mieters / Ansprechpartner", "")
        einheit = st.text_input("Wohnungs- / Einheitennummer", "")
    with col2:
        datum = st.date_input("Datum der Aufnahme", datetime.now())
        bearbeiter = st.text_input("Aufgenommen durch (KARE-Immobilien)", "KARE-Immobilien")
        schadensart = st.selectbox("Schadenskategorie", ["Wasserschaden", "Schimmel / Feuchtigkeit", "Elektro / Installation", "Fenster / Türen", "Wand- / Bodenbelag", "Sonstiges"])

    st.header("2. Schadensbeschreibung & Details")
    raum = st.selectbox("Raum / Bereich", ["Wohnzimmer", "Schlafzimmer", "Kinderzimmer", "Küche", "Badezimmer", "Flur / Diele", "Keller / Abstellraum", "Balkon / Terrasse", "Außenbereich / Fassade"])
    beschreibung = st.text_area("Genaue Beschreibung des Schadens / Mangels", placeholder="z.B. Wasserschaden an der Decke im Badezimmer ca. 30x30 cm...")
    
    col_kost, col_ver = st.columns(2)
    with col_kost:
        kostenschätzung = st.text_input("Geschätzte Kosten (€, optional)", "0,00")
    with col_ver:
        verantwortlichkeit = st.selectbox("Vermutliche Verantwortlichkeit", ["Mieter", "Vermieter / Hausverwaltung", "Dritter / Gewährleistung", "Ungeklärt"])

    st.header("3. Fotodokumentation")
    uploaded_files = st.file_uploader("Fotos hochladen (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

    st.header("4. Maßnahme & Fristsetzung")
    massnahme = st.text_area("Erforderliche Sofortmaßnahme / Instandsetzung", "Handwerkertermin vereinbaren und Ursache prüfen.")
    frist = st.date_input("Frist zur Behebung / Rückmeldung", datetime.now())

    submit_button = st.form_submit_button(label="Schadensprotokoll als PDF generieren")

if submit_button:
    images_html = ""
    if uploaded_files:
        images_html = "<h3>Fotodokumentation</h3><div class='photo-grid'>"
        for idx, file in enumerate(uploaded_files):
            img = Image.open(file)
            buffered = BytesIO()
            img.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            images_html += f"""
            <div class='photo-box'>
                <img src='data:image/jpeg;base64,{img_str}' style='width:100%; max-height:200px; object-fit:cover; border-radius:4px;'/>
                <p style='font-size:10pt; color:#555; text-align:center; margin-top:4px;'>Foto {idx+1}: {file.name}</p>
            </div>
            """
        images_html += "</div>"

    html_content = f"""
    <!DOCTYPE html>
    <html lang="de">
    <head>
    <meta charset="UTF-8">
    <style>
        @page {{
            size: A4;
            margin: 15mm;
            background-color: #ffffff;
            @bottom-right {{
                content: "Seite " counter(page) " von " counter(pages);
                font-size: 8pt;
                color: #666;
            }}
            @bottom-left {{
                content: "KARE-Immobilien · Talstr. 32 · 07545 Gera";
                font-size: 8pt;
                color: #666;
            }}
        }}
        body {{
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            color: #333333;
            line-height: 1.4;
            font-size: 10pt;
            margin: 0;
            padding: 0;
        }}
        .header {{
            border-bottom: 2px solid #1e3a8a;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        .header h1 {{
            color: #1e3a8a;
            font-size: 20pt;
            margin: 0 0 5px 0;
        }}
        .header p {{
            margin: 0;
            color: #555;
            font-size: 9pt;
        }}
        h2 {{
            color: #1e3a8a;
            font-size: 13pt;
            border-bottom: 1px solid #cbd5e1;
            padding-bottom: 4px;
            margin-top: 20px;
            margin-bottom: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 15px;
        }}
        th, td {{
            padding: 6px 8px;
            border: 1px solid #cbd5e1;
            vertical-align: top;
        }}
        th {{
            background-color: #f1f5f9;
            color: #1e3a8a;
            text-align: left;
            width: 30%;
        }}
        td {{
            width: 70%;
        }}
        .photo-grid {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 10px;
        }}
        .photo-box {{
            width: 48%;
            border: 1px solid #cbd5e1;
            padding: 5px;
            background: #f8fafc;
            margin-bottom: 10px;
            page-break-inside: avoid;
        }}
        .signature-section {{
            margin-top: 30px;
            page-break-inside: avoid;
        }}
        .sig-box {{
            width: 45%;
            display: inline-block;
            border-top: 1px solid #333;
            margin-top: 40px;
            padding-top: 5px;
            text-align: center;
        }}
    </style>
    </head>
    <body>
        <div class="header">
            <h1>KARE-Immobilien</h1>
            <p>Talstr. 32, 07545 Gera | Tel.: 0365 / 800 49 37 | E-Mail: Info@KARE-Immobilien.de</p>
            <h2 style="border:none; color:#0f172a; margin-top:15px; font-size:16pt;">Schadensaufnahmeprotokoll</h2>
        </div>

        <h2>1. Stammdaten</h2>
        <table>
            <tr><th>Objektadresse</th><td>{objekt_adresse}</td></tr>
            <tr><th>Einheit / Mieter</th><td>{einheit} ({mieter_name})</td></tr>
            <tr><th>Datum der Aufnahme</th><td>{datum.strftime('%d.%m.%Y')}</td></tr>
            <tr><th>Aufgenommen durch</th><td>{bearbeiter}</td></tr>
            <tr><th>Schadenskategorie</th><td>{schadensart}</td></tr>
        </table>

        <h2>2. Schadensbeschreibung</h2>
        <table>
            <tr><th>Betroffener Raum</th><td>{raum}</td></tr>
            <tr><th>Beschreibung des Mangels</th><td>{beschreibung}</td></tr>
            <tr><th>Geschätzte Kosten</th><td>{kostenschätzung} €</td></tr>
            <tr><th>Verantwortlichkeit</th><td>{verantwortlichkeit}</td></tr>
        </table>

        <h2>3. Maßnahme & Frist</h2>
        <table>
            <tr><th>Erforderliche Maßnahme</th><td>{massnahme}</td></tr>
            <tr><th>Frist zur Behebung</th><td>{frist.strftime('%d.%m.%Y')}</td></tr>
        </table>

        {images_html}

        <div class="signature-section">
            <p style="margin-bottom:40px;">Hiermit wird der genannte Zustand bestätigt bzw. die Maßnahme eingeleitet.</p>
            <div style="width: 100%;">
                <div class="sig-box" style="float: left;">Unterschrift Mieter / Anwesender</div>
                <div class="sig-box" style="float: right;">Unterschrift KARE-Immobilien</div>
            </div>
            <div style="clear: both;"></div>
        </div>
    </body>
    </html>
    """

    pdf_path = "schadensprotokoll.pdf"
    HTML(string=html_content).write_pdf(pdf_path)

    with open(pdf_path, "rb") as pdf_file:
        PDFbyte = pdf_file.read()

    st.success("Schadensaufnahmeprotokoll erfolgreich als PDF erstellt!")
    st.download_button(
        label="📄 PDF-Protokoll herunterladen",
        data=PDFbyte,
        file_name=f"Schadensprotokoll_{datum.strftime('%Y%m%d')}.pdf",
        mime="application/octet-stream"
    )