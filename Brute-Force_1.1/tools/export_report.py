# tools/export_report.py

from fpdf import FPDF

def generar_reporte_pdf(resultado_csv, archivo_pdf, resumen="", detalles=None):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, "Reporte de Auditoría - Brute-Force_1.1", ln=True, align="C")
    pdf.ln(6)
    if resumen:
        pdf.multi_cell(0, 8, resumen)
    pdf.ln(4)
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 8, "Resultados:", ln=True)
    with open(resultado_csv, encoding="utf-8") as f:
        for line in f:
            pdf.cell(0, 7, line.strip(), ln=True)
    if detalles:
        pdf.ln(10)
        pdf.set_font("Arial", size=9)
        pdf.multi_cell(0, 6, detalles)
    pdf.output(archivo_pdf)

