from datetime import datetime
import os
from io import BytesIO
import base64
from PIL import Image
import numpy as np
import streamlit as st
from streamlit_drawable_canvas import st_canvas
from weasyprint import HTML

st.set_page_config(
    page_title="KARE-Immobilien Schadensaufnahmeprotokoll",
    page_icon="📝",
    layout="wide",
)

st.title("KARE-Immobilien – Schadensaufnahmeprotokoll")
st.markdown(
    "Erfassung von Mängeln und Schäden mit Bild-Upload, digitaler Unterschrift"
    " und automatisierter PDF-Generierung."
)

with st.form("schaden_form"):
    st.header("1. Stammdaten & Objekt")
    col1, col2 = st.columns(2)
    with col1:
        objekt_adresse = st.text_input(
            "Objektadresse / Liegenschaft", "Talstr. 32, 07545 Gera"
        )
        mieter_name = st.text_input(
            "Name des Mieters / Ansprechpartner", ""
        )
        einheit = st.text_input("Wohnungs- / Einheitennummer", "")
    with col2:
        datum = st.date_input("Datum der Aufnahme", datetime.now())
        bearbeiter = st.text_input(
            "Aufgenommen durch (KARE-Immobilien)", "KARE-Immobilien"
        )
        schadensart = st.selectbox(
            "Schadenskategorie",
            [
                "Wasserschaden",
                "Schimmel / Feuchtigkeit",
                "Elektro / Installation",
                "Fenster / Türen",
                "Wand- / Bodenbelag",
                "Sonstiges",
            ],
        )

    st.header("2. Schadensbeschreibung & Details")
    raum = st.selectbox(
        "Raum / Bereich",
        [
            "Wohnzimmer",
            "Schlafzimmer",
            "Kinderzimmer",
            "Küche",
            "Badezimmer",
            "Flur / Diele",
            "Keller / Abstellraum",
            "Balkon / Terrasse",
            "Außenbereich / Fassade",
        ],
    )
    beschreibung = st.text_area(
        "Genaue Beschreibung des Schadens / Mangels",
        placeholder=(
            "z.B. Wasserschaden an der Decke im Badezimmer ca. 30x30 cm..."
        ),
    )

    col_kost, col_ver = st.columns(2)
    with col_kost:
        kostenschätzung = st.text_input(
            "Geschätzte Kosten (€, optional)", "0,00"
        )
    with col_ver:
        verantwortlichkeit = st.selectbox(
            "Vermutliche Verantwortlichkeit",
            [
                "Mieter",
                "Vermieter / Hausverwaltung",
                "Dritter / Gewährleistung",
                "Ungeklärt",
            ],
        )

    st.header("3. Fotodokumentation")
    uploaded_files = st.file_uploader(
        "Fotos hochladen (PNG, JPG, JPEG)",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True,
    )

    st.header("4. Maßnahme & Fristsetzung")
    massnahme = st.text_area(
        "Erforderliche Sofortmaßnahme / Instandsetzung",
        "Handwerkertermin vereinbaren und Ursache prüfen.",
    )
    frist = st.date_input(
        "Frist zur Behebung / Rückmeldung", datetime.now()
    )

    protokoll_bestätigt = st.checkbox(
        "Hiermit wird die Richtigkeit des Protokolls und der erfassten Mängel"
        " bestätigt."
    )

    submit_button = st.form_submit_button(
        label="Schadensprotokoll als PDF generieren"
    )

# Hinweis: Die Canvas-Unterschriftenfelder müssen außerhalb des st.form liegen,
# da Streamlit Custom Components (wie st_canvas) innerhalb von Formularen Probleme machen können.
st.header("5. Digitale Signaturen")
col_sig_info1, col_sig_info2 = st.columns(2)
with col_sig_info1:
    st.write("**Unterschrift Mieter / Anwesender**")
    canvas_mieter = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",
        stroke_width=2,
        stroke_color="#000000",
        background_color="#f8fafc",
        height=130,
        width=350,
        drawing_mode="freedraw",
        key="canvas_mieter_schaden",
    )
with col_sig_info2:
    st.write("**Unterschrift KARE-Immobilien**")
    canvas_kare = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",
        stroke_width=2,
        stroke_color="#000000",
        background_color="#f8fafc",
        height=130,
        width=350,
        drawing_mode="freedraw",
        key="canvas_kare_schaden",
    )

if submit_button:
    if not protokoll_bestätigt:
        st.error(
            "Bitte bestätigen Sie das Protokoll über die Checkbox, bevor Sie"
            " das PDF generieren."
        )
    else:
        temp_files = []
        images_html = ""
        if uploaded_files:
            images_html = "<h3>Fotodokumentation</h3><div class='photo-grid'>"
            for idx, file in enumerate(uploaded_files):
                img = Image.open(file)
                if img.mode in ("RGBA", "LA") or (
                    img.mode == "P" and "transparency" in img.info
                ):
                    img = img.convert("RGB")

                buffered = BytesIO()
                img.save(buffered, format="JPEG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                images_html += f"""
                <div class='photo-box'>
                    <img src='data:image/jpeg;base64,{img_str}' style='width:100%; max-height:180px; object-fit:cover; border-radius:4px;'/>
                    <p style='font-size:9pt; color:#555; text-align:center; margin-top:4px;'>Foto {idx+1}: {file.name}</p>
                </div>
                """
            images_html += "</div>"

        # Unterschriften in temporäre PNGs konvertieren falls vorhanden
        sig_mieter_html = "____________________________________<br>Mieter / Anwesender"
        if (
            canvas_mieter.image_data is not None
            and canvas_mieter.json_data["objects"]
        ):
            sig_img_data1 = canvas_mieter.image_data.astype(np.uint8)
            sig_pil1 = Image.fromarray(sig_img_data1).convert("RGBA")
            # Weiß zu transparent konvertieren
            datas = sig_pil1.getdata()
            new_data = []
            for item in datas:
                if item[0] > 240 and item[1] > 240 and item[2] > 240:
                    new_data.append((255, 255, 255, 0))
                else:
                    new_data.append(item)
            sig_pil1.putdata(new_data)

            sig_buf1 = BytesIO()
            sig_pil1.save(sig_buf1, format="PNG")
            sig_str1 = base64.b64encode(sig_buf1.getvalue()).decode()
            sig_mieter_html = f"<img src='data:image/png;base64,{sig_str1}' style='max-height:60px;'/><br>____________________________________<br>Mieter / Anwesender"

        sig_kare_html = (
            "____________________________________<br>KARE-Immobilien"
        )
        if (
            canvas_kare.image_data is not None
            and canvas_kare.json_data["objects"]
        ):
            sig_img_data2 = canvas_kare.image_data.astype(np.uint8)
            sig_pil2 = Image.fromarray(sig_img_data2).convert("RGBA")
            datas2 = sig_pil2.getdata()
            new_data2 = []
            for item in datas2:
                if item[0] > 240 and item[1] > 240 and item[2] > 240:
                    new_data2.append((255, 255, 255, 0))
                else:
                    new_data2.append(item)
            sig_pil2.putdata(new_data2)

            sig_buf2 = BytesIO()
            sig_pil2.save(sig_buf2, format="PNG")
            sig_str2 = base64.b64encode(sig_buf2.getvalue()).decode()
            sig_kare_html = f"<img src='data:image/png;base64,{sig_str2}' style='max-height:60px;'/><br>____________________________________<br>KARE-Immobilien"

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
                font-size: 12pt;
                border-bottom: 1px solid #cbd5e1;
                padding-bottom: 4px;
                margin-top: 15px;
                margin-bottom: 8px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 10px;
            }}
            th, td {{
                padding: 5px 8px;
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
                margin-top: 25px;
                page-break-inside: avoid;
            }}
            .sig-box {{
                width: 45%;
                display: inline-block;
                margin-top: 20px;
                text-align: center;
            }}
        </style>
        </head>
        <body>
            <div class="header">
                <h1>KARE-Immobilien</h1>
                <p>Talstr. 32, 07545 Gera | Tel.: 0365 / 800 49 37 | E-Mail: Info@KARE-Immobilien.de</p>
                <h2 style="border:none; color:#0f172a; margin-top:10px; font-size:15pt;">Schadensaufnahmeprotokoll</h2>
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
                <p style="margin-bottom:15px; font-size:9pt;">Hiermit wird der genannte Zustand bestätigt bzw. die Maßnahme eingeleitet.</p>
                <div style="width: 100%;">
                    <div class="sig-box" style="float: left;">
                        {sig_mieter_html}
                    </div>
                    <div class="sig-box" style="float: right;">
                        {sig_kare_html}
                    </div>
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

        st.success(
            "Schadensaufnahmeprotokoll erfolgreich als PDF erstellt und mit"
            " Unterschriften versehen!"
        )
        st.download_button(
            label="📄 PDF-Protokoll herunterladen",
            data=PDFbyte,
            file_name=f"Schadensprotokoll_{datum.strftime('%Y%m%d')}.pdf",
            mime="application/octet-stream",
        )
