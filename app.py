from datetime import datetime
import os
from io import BytesIO
import base64
from PIL import Image as PILImage
import numpy as np
import streamlit as st
from streamlit_drawable_canvas import st_canvas

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, KeepTogether

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
        mieter_kontakt = st.text_input(
            "Kontaktdaten (Telefonnummer oder E-Mail)", ""
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

st.header("5. Digitale Signaturen")
col_sig_info1, col_sig_info2 = st.columns(2)
with col_sig_info1:
    st.write("**Unterschrift Mieter / Anwesender**")
    canvas_mieter = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",
        stroke_width=2,
        stroke_color="#000000",
        background_color="#ffffff",
        height=130,
        width=350,
        drawing_mode="freedraw",
        update_streamlit=True,
        return_image_data=True,
        key="canvas_mieter_schaden",
    )
    if canvas_mieter.image_data is not None and np.any(canvas_mieter.image_data[:, :, 3] > 0):
        st.session_state["saved_mieter_sig"] = canvas_mieter.image_data
    else:
        st.session_state["saved_mieter_sig"] = None

with col_sig_info2:
    st.write("**Unterschrift KARE-Immobilien**")
    canvas_kare = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",
        stroke_width=2,
        stroke_color="#000000",
        background_color="#ffffff",
        height=130,
        width=350,
        drawing_mode="freedraw",
        update_streamlit=True,
        return_image_data=True,
        key="canvas_kare_schaden",
    )
    if canvas_kare.image_data is not None and np.any(canvas_kare.image_data[:, :, 3] > 0):
        st.session_state["saved_kare_sig"] = canvas_kare.image_data
    else:
        st.session_state["saved_kare_sig"] = None

if submit_button:
    # Prüfen, ob beide Unterschriften im Session State hinterlegt sind
    sig_mieter_valid = "saved_mieter_sig" in st.session_state and st.session_state["saved_mieter_sig"] is not None
    sig_kare_valid = "saved_kare_sig" in st.session_state and st.session_state["saved_kare_sig"] is not None

    if not protokoll_bestätigt:
        st.error(
            "Bitte bestätigen Sie das Protokoll über die Checkbox, bevor Sie"
            " das PDF generieren."
        )
    elif not sig_mieter_valid or not sig_kare_valid:
        st.error(
            "Es fehlen Unterschriften! Bitte stellen Sie sicher, dass sowohl der Mieter als auch KARE-Immobilien unterschrieben haben."
        )
    else:
        pdf_path = "schadensprotokoll.pdf"
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=A4,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )
        
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=16,
            textColor=colors.HexColor('#1e3a8a'),
            spaceAfter=4
        )
        
        subtitle_style = ParagraphStyle(
            'DocSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8,
            textColor=colors.HexColor('#555555'),
            spaceAfter=12
        )
        
        h2_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=11,
            textColor=colors.HexColor('#1e3a8a'),
            spaceBefore=10,
            spaceAfter=6,
            keepWithNext=True
        )
        
        cell_style = ParagraphStyle(
            'TableCell',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            textColor=colors.HexColor('#333333')
        )
        
        cell_bold = ParagraphStyle(
            'TableBold',
            parent=cell_style,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#1e3a8a')
        )

        story = []
        
        # Header block
        story.append(Paragraph("KARE-Immobilien", title_style))
        story.append(Paragraph("Talstr. 32, 07545 Gera | Tel.: 0365 / 800 49 37 | E-Mail: Info@KARE-Immobilien.de", subtitle_style))
        story.append(Paragraph("<b>Schadensaufnahmeprotokoll</b>", ParagraphStyle('SubHeader', parent=title_style, fontSize=13, textColor=colors.HexColor('#0f172a'))))
        story.append(Spacer(1, 10))
        
        def create_table(data):
            formatted_data = []
            for row in data:
                formatted_data.append([
                    Paragraph(row[0], cell_bold),
                    Paragraph(row[1], cell_style)
                ])
            t = Table(formatted_data, colWidths=[150, 385])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
                ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
                ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
                ('TOPPADDING', (0,0), (-1,-1), 5),
                ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                ('LEFTPADDING', (0,0), (-1,-1), 6),
                ('RIGHTPADDING', (0,0), (-1,-1), 6),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ]))
            return t

        story.append(Paragraph("1. Stammdaten", h2_style))
        story.append(create_table([
            ["Objektadresse", objekt_adresse],
            ["Einheit / Mieter", f"{einheit} ({mieter_name})"],
            ["Kontaktdaten Mieter", mieter_kontakt],
            ["Datum der Aufnahme", datum.strftime('%d.%m.%Y')],
            ["Aufgenommen durch", bearbeiter],
            ["Schadenskategorie", schadensart]
        ]))
        
        story.append(Paragraph("2. Schadensbeschreibung", h2_style))
        story.append(create_table([
            ["Betroffener Raum", raum],
            ["Beschreibung des Mangels", beschreibung],
            ["Geschätzte Kosten", f"{kostenschätzung} €"],
            ["Verantwortlichkeit", verantwortlichkeit]
        ]))
        
        story.append(Paragraph("3. Maßnahme & Frist", h2_style))
        story.append(create_table([
            ["Erforderliche Maßnahme", massnahme],
            ["Frist zur Behebung", frist.strftime('%d.%m.%Y')]
        ]))

        if uploaded_files:
            story.append(Paragraph("Fotodokumentation", h2_style))
            img_table_data = []
            row_imgs = []
            for idx, file in enumerate(uploaded_files):
                img = PILImage.open(file)
                if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                    img = img.convert("RGB")
                img_io = BytesIO()
                img.save(img_io, format='JPEG')
                img_io.seek(0)
                
                rl_img = RLImage(img_io, width=230, height=150)
                rl_img.hAlign = 'CENTER'
                caption = Paragraph(f"Foto {idx+1}: {file.name}", ParagraphStyle('Cap', parent=cell_style, fontSize=8, alignment=1))
                row_imgs.append([rl_img, caption])
                
                if len(row_imgs) == 2:
                    img_table_data.append(row_imgs)
                    row_imgs = []
            if row_imgs:
                while len(row_imgs) < 2:
                    row_imgs.append(["", ""])
                img_table_data.append(row_imgs)
                
            for r in img_table_data:
                cell_contents = [[cell[0], cell[1]] if isinstance(cell, list) else "" for cell in r]
                # Build side-by-side photo layout
                pass
            
            # Simple list approach for images
            for idx, file in enumerate(uploaded_files):
                img = PILImage.open(file)
                if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                    img = img.convert("RGB")
                img_io = BytesIO()
                img.save(img_io, format='JPEG')
                img_io.seek(0)
                
                rl_img = RLImage(img_io, width=200, height=130)
                rl_img.hAlign = 'CENTER'
                story.append(Spacer(1, 5))
                story.append(rl_img)
                story.append(Paragraph(f"Foto {idx+1}: {file.name}", ParagraphStyle('Cap', parent=cell_style, fontSize=8, alignment=1)))
                story.append(Spacer(1, 5))

        def get_sig_image(state_key):
            if state_key in st.session_state and st.session_state[state_key] is not None:
                img_data = st.session_state[state_key].astype("uint8")
                pil_img = PILImage.fromarray(img_data, mode="RGBA")
                background = PILImage.new("RGB", pil_img.size, (255, 255, 255))
                background.paste(pil_img, mask=pil_img.split()[3])
                buf = BytesIO()
                background.save(buf, format="PNG")
                buf.seek(0)
                return RLImage(buf, width=180, height=50)
            return Paragraph("<br><br>", cell_style)

        sig_mieter_obj = get_sig_image("saved_mieter_sig")
        sig_kare_obj = get_sig_image("saved_kare_sig")

        sig_table_data = [
            [sig_mieter_obj, sig_kare_obj],
            [Paragraph("____________________________________<br/>Mieter / Anwesender", cell_style),
             Paragraph("____________________________________<br/>KARE-Immobilien", cell_style)]
        ]
        
        sig_table = Table(sig_table_data, colWidths=[250, 250])
        sig_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ]))

        story.append(Spacer(1, 15))
        story.append(Paragraph("Hiermit wird der genannte Zustand bestätigt bzw. die Maßnahme eingeleitet.", ParagraphStyle('Note', parent=cell_style, fontSize=9)))
        story.append(Spacer(1, 10))
        story.append(KeepTogether(sig_table))

        def add_footer(canvas_obj, doc_obj):
            canvas_obj.saveState()
            canvas_obj.setFont('Helvetica', 8)
            canvas_obj.setFillColor(colors.HexColor('#666666'))
            canvas_obj.drawString(40, 25, "KARE-Immobilien · Talstr. 32 · 07545 Gera")
            canvas_obj.drawRightString(A4[0] - 40, 25, f"Seite {doc_obj.page}")
            canvas_obj.restoreState()

        doc.build(story, onFirstPage=add_footer, onLaterPages=add_footer)

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
