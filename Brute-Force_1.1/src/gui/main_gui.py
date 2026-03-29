import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import time
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import threading
import os

from src.brute_manager import FuerzaBrutaManager, StoppableEvent
from src.core.config import SERVICIOS
from src.core.utils import parse_headers, parse_post_data
from src.core.password_ai import rank_passwords, simple_markov
from src.modules.wifi_crack import crack_handshake_aircrack, crack_handshake_hashcat
from src.modules import hash_crack
from tools.export_report import generar_reporte_pdf

class FuerzaBrutaGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Brute-Force_1.1 - GUI Pro")
        self.root.geometry("1260x1020")
        self.root.configure(bg='#23272e')
        self.en_ejecucion = False
        self.control_event = StoppableEvent()
        self.total_intentos = 0
        self.exitos = 0
        self.progreso_val = tk.DoubleVar(value=0)
        self.label_intentos = None
        self.label_exitos = None
        self.label_errores = None
        self.label_eta = None
        self.label_tasa = None

        self.graf_data_t = []
        self.graf_data_intentos = []
        self.graf_data_exitos = []
        self.graf_fig = None
        self.graf_ax = None
        self.graf_canvas = None
        self.graf_linea_intentos = None
        self.graf_linea_exitos = None
        self.brute_start_time = None
        self.brute_total = 0
        self.brute_exitos = 0
        self.brute_errores = 0

        self.stats_vars = {
            "intentos": 0,
            "total": 0,
            "exitos": 0,
            "errores": 0,
            "eta": "-",
            "por_hilo": {},
            "exitos_hilo": {},
            "errores_hilo": {}
        }

        self.setup_tabs()
        

    def setup_tabs(self):
        self.notebook = ttk.Notebook(self.root)
        self.tab_brute = ttk.Frame(self.notebook)
        self.tab_wifi = ttk.Frame(self.notebook)
        self.tab_report = ttk.Frame(self.notebook)
        self.tab_hash = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_brute, text="Ataques Multi-servicio")
        self.notebook.add(self.tab_wifi, text="Crack WPA2/WPA3")
        self.notebook.add(self.tab_report, text="Exportar Reporte")
        self.notebook.add(self.tab_hash, text="Crackeo de Hashes")
        self.notebook.pack(expand=1, fill='both')

        self.crear_widgets_brute()
        self.crear_widgets_wifi()
        self.crear_widgets_report()
        self.crear_widgets_hash_crack()

    # ========== TAB 1: ATAQUES MULTI-SERVICIO ==========
    def crear_widgets_brute(self):
        f = self.tab_brute

        frame_top = ttk.Frame(f)
        frame_top.pack(pady=7, padx=6, anchor="nw")

        ttk.Label(frame_top, text="Servicio:").grid(row=0, column=0, sticky="w", padx=4)
        self.servicio_var = tk.StringVar(value=list(SERVICIOS.keys())[0])
        servicio_menu = ttk.Combobox(frame_top, textvariable=self.servicio_var, values=list(SERVICIOS.keys()), width=13, state="readonly")
        servicio_menu.grid(row=0, column=1, padx=4)
        ttk.Label(frame_top, text="IP/Host:").grid(row=0, column=2, sticky="w", padx=7)
        self.objetivo_var = tk.StringVar()
        ttk.Entry(frame_top, textvariable=self.objetivo_var, width=18).grid(row=0, column=3, padx=2)
        ttk.Label(frame_top, text="Puerto:").grid(row=0, column=4, sticky="w", padx=7)
        self.puerto_var = tk.StringVar()
        ttk.Entry(frame_top, textvariable=self.puerto_var, width=7).grid(row=0, column=5, padx=2)
        ttk.Label(frame_top, text="Usuarios:").grid(row=0, column=6, sticky="w", padx=7)
        self.usuarios_var = tk.StringVar()
        ttk.Entry(frame_top, textvariable=self.usuarios_var, width=15).grid(row=0, column=7, padx=2)
        ttk.Button(frame_top, text="...", width=3, command=self.cargar_usuarios).grid(row=0, column=8, padx=2)
        ttk.Label(frame_top, text="Passwords:").grid(row=0, column=9, sticky="w", padx=7)
        self.passwords_var = tk.StringVar()
        ttk.Entry(frame_top, textvariable=self.passwords_var, width=15).grid(row=0, column=10, padx=2)
        ttk.Button(frame_top, text="...", width=3, command=self.cargar_passwords).grid(row=0, column=11, padx=2)

        ttk.Label(frame_top, text="Hilos:").grid(row=0, column=12, sticky="w", padx=7)
        self.hilos_var = tk.StringVar(value="6")
        ttk.Entry(frame_top, textvariable=self.hilos_var, width=6).grid(row=0, column=13, padx=2)

        ttk.Label(frame_top, text="IA:").grid(row=0, column=14, sticky="w", padx=7)
        self.ia_var = tk.BooleanVar()
        ttk.Checkbutton(frame_top, variable=self.ia_var).grid(row=0, column=15, padx=2)
        ttk.Label(frame_top, text="Aleatorio:").grid(row=0, column=16, sticky="w", padx=7)
        self.aleatorio_var = tk.BooleanVar()
        ttk.Checkbutton(frame_top, variable=self.aleatorio_var).grid(row=0, column=17, padx=2)

        ttk.Button(frame_top, text="INICIAR", command=self.iniciar_brute, bootstyle="success").grid(row=0, column=18, padx=9)
        ttk.Button(frame_top, text="DETENER", command=self.detener_brute, bootstyle="danger").grid(row=0, column=19, padx=2)

        self.text_brute = tk.Text(f, height=17, width=170, bg="#181c1f", fg="#79ffce", font=("Consolas", 11))
        self.text_brute.pack(pady=10, padx=8, fill="both", expand=True)
                # --- Progreso General ---
        barra_frame = ttk.Frame(f)
        barra_frame.pack(fill="x", padx=8, pady=(0,10))
        ttk.Label(barra_frame, text="Progreso General:").pack(side="left", padx=6)
        barra = ttk.Progressbar(barra_frame, variable=self.progreso_val, maximum=100, length=350)
        barra.pack(side="left", padx=8, fill="x", expand=True)
        self.label_intentos = ttk.Label(barra_frame, text="Intentos: 0")
        self.label_intentos.pack(side="left", padx=14)
        self.label_exitos = ttk.Label(barra_frame, text="Éxitos: 0")
        self.label_exitos.pack(side="left", padx=14)
        self.label_errores = ttk.Label(barra_frame, text="Errores: 0")
        self.label_errores.pack(side="left", padx=14)
        self.label_tasa = ttk.Label(barra_frame, text="Tasa: 0/s")
        self.label_tasa.pack(side="left", padx=14)
        self.label_eta = ttk.Label(barra_frame, text="ETA: -")
        self.label_eta.pack(side="left", padx=14)

        # --- Gráfica en tiempo real ---
        self.graf_fig, self.graf_ax = plt.subplots(figsize=(6.5,2.2))
        self.graf_ax.set_title("Intentos y Éxitos en Tiempo Real")
        self.graf_ax.set_xlabel("Tiempo (s)")
        self.graf_ax.set_ylabel("Cantidad")
        self.graf_linea_intentos, = self.graf_ax.plot([], [], label="Intentos", color='deepskyblue')
        self.graf_linea_exitos, = self.graf_ax.plot([], [], label="Éxitos", color='lime')
        self.graf_ax.legend()
        self.graf_canvas = FigureCanvasTkAgg(self.graf_fig, master=f)
        self.graf_canvas.draw()
        self.graf_canvas.get_tk_widget().pack(fill="x", padx=8, pady=3)
    def actualizar_progreso_brute(self, total, exitos, errores, max_total):
        if self.brute_start_time is None:
            self.brute_start_time = time.time()
            self.graf_data_t = [0]
            self.graf_data_intentos = [0]
            self.graf_data_exitos = [0]
        t_now = time.time() - self.brute_start_time
        self.graf_data_t.append(t_now)
        self.graf_data_intentos.append(total)
        self.graf_data_exitos.append(exitos)

        self.progreso_val.set((total / max_total) * 100 if max_total else 0)
        self.label_intentos.config(text=f"Intentos: {total}")
        self.label_exitos.config(text=f"Éxitos: {exitos}")
        self.label_errores.config(text=f"Errores: {errores}")
        tasa = int(total / t_now) if t_now > 0 else 0
        self.label_tasa.config(text=f"Tasa: {tasa}/s")
        eta = int((max_total - total) / tasa) if tasa > 0 else "-"
        self.label_eta.config(text=f"ETA: {eta if isinstance(eta, int) else '-'}s")

        self.graf_linea_intentos.set_data(self.graf_data_t, self.graf_data_intentos)
        self.graf_linea_exitos.set_data(self.graf_data_t, self.graf_data_exitos)
        self.graf_ax.relim()
        self.graf_ax.autoscale_view()
        self.graf_canvas.draw_idle()
   
    def cargar_usuarios(self):
        f = filedialog.askopenfilename(title="Seleccionar archivo de usuarios")
        if f: self.usuarios_var.set(f)
    def cargar_passwords(self):
        f = filedialog.askopenfilename(title="Seleccionar archivo de passwords")
        if f: self.passwords_var.set(f)

    def iniciar_brute(self):
        self.text_brute.delete("1.0", tk.END)
        self.text_brute.insert(tk.END, "Ataque iniciado...\n")
        # Implementa aquí tu lógica real
    def detener_brute(self):
        self.text_brute.insert(tk.END, "Ataque detenido por usuario.\n")

    # ========== TAB 2: CRACKEO WPA2/WPA3 ==========
    def crear_widgets_wifi(self):
        f = self.tab_wifi

        frame_wifi = ttk.Frame(f)
        frame_wifi.pack(pady=9, padx=6, anchor="nw")

        ttk.Label(frame_wifi, text="Archivo .cap/.hccapx:").grid(row=0, column=0, sticky="w", padx=4)
        self.wifi_handshake_var = tk.StringVar()
        ttk.Entry(frame_wifi, textvariable=self.wifi_handshake_var, width=32).grid(row=0, column=1, padx=4)
        ttk.Button(frame_wifi, text="...", width=3, command=self.cargar_handshake).grid(row=0, column=2, padx=2)
        ttk.Label(frame_wifi, text="Diccionario:").grid(row=0, column=3, sticky="w", padx=8)
        self.wifi_wordlist_var = tk.StringVar()
        ttk.Entry(frame_wifi, textvariable=self.wifi_wordlist_var, width=28).grid(row=0, column=4, padx=2)
        ttk.Button(frame_wifi, text="...", width=3, command=self.cargar_wordlist).grid(row=0, column=5, padx=2)

        ttk.Label(frame_wifi, text="Motor:").grid(row=0, column=6, sticky="w", padx=8)
        self.wifi_motor_var = tk.StringVar()
        motor_cb = ttk.Combobox(frame_wifi, textvariable=self.wifi_motor_var, width=12, state="readonly")
        motor_cb['values'] = ["aircrack-ng", "hashcat"]
        motor_cb.set("aircrack-ng")
        motor_cb.grid(row=0, column=7, padx=2)

        ttk.Button(frame_wifi, text="INICIAR", command=self.iniciar_wifi_crack, bootstyle="success").grid(row=0, column=8, padx=15)

        self.text_wifi = tk.Text(f, height=16, width=170, bg="#181c1f", fg="#adffd4", font=("Consolas", 11))
        self.text_wifi.pack(pady=10, padx=8, fill="both", expand=True)

    def cargar_handshake(self):
        f = filedialog.askopenfilename(title="Seleccionar archivo .cap/.hccapx")
        if f: self.wifi_handshake_var.set(f)
    def cargar_wordlist(self):
        f = filedialog.askopenfilename(title="Seleccionar diccionario")
        if f: self.wifi_wordlist_var.set(f)

    def iniciar_wifi_crack(self):
        self.text_wifi.delete("1.0", tk.END)
        self.text_wifi.insert(tk.END, "Crackeo iniciado...\n")
        # Implementa aquí tu lógica real
    # ========== TAB 3: EXPORTAR REPORTE ==========
    def crear_widgets_report(self):
        f = self.tab_report

        frame_report = ttk.Frame(f)
        frame_report.pack(pady=15, padx=8, anchor="nw")
        ttk.Label(frame_report, text="Archivo CSV de resultados:").grid(row=0, column=0, sticky="w", padx=4)
        self.report_csv_var = tk.StringVar()
        ttk.Entry(frame_report, textvariable=self.report_csv_var, width=40).grid(row=0, column=1, padx=3)
        ttk.Button(frame_report, text="...", width=3, command=self.cargar_csv_reporte).grid(row=0, column=2, padx=2)
        ttk.Label(frame_report, text="Resumen del reporte:").grid(row=0, column=3, sticky="w", padx=8)
        self.report_resumen_var = tk.StringVar()
        ttk.Entry(frame_report, textvariable=self.report_resumen_var, width=35).grid(row=0, column=4, padx=3)
        ttk.Button(frame_report, text="Exportar a PDF", command=self.exportar_pdf).grid(row=0, column=5, padx=18)

        self.text_report = tk.Text(f, height=12, width=170, bg="#181c1f", fg="#ffd182", font=("Consolas", 11))
        self.text_report.pack(pady=12, padx=8, fill="both", expand=True)

    def cargar_csv_reporte(self):
        f = filedialog.askopenfilename(title="Seleccionar archivo CSV")
        if f: self.report_csv_var.set(f)

    def exportar_pdf(self):
        path_csv = self.report_csv_var.get()
        resumen = self.report_resumen_var.get()
        if not os.path.isfile(path_csv):
            messagebox.showerror("Error", "Selecciona un archivo CSV válido.")
            return
        save_path = filedialog.asksaveasfilename(defaultextension=".pdf", title="Guardar PDF")
        if not save_path:
            return
        try:
            generar_reporte_pdf(path_csv, save_path, resumen)
            self.text_report.insert(tk.END, f"Reporte exportado exitosamente: {save_path}\n")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar a PDF:\n{e}")

    # ========== TAB 4: CRACKEO DE HASHES ==========
    def crear_widgets_hash_crack(self):
        frame_hash = ttk.Frame(self.tab_hash)
        frame_hash.pack(pady=14, fill='x')

        ttk.Label(frame_hash, text="Archivo de hashes:").pack(side='left', padx=5)
        self.hash_file = tk.StringVar()
        self.entry_hash = ttk.Entry(frame_hash, textvariable=self.hash_file, width=38)
        self.entry_hash.pack(side='left', padx=4)
        ttk.Button(frame_hash, text="Seleccionar", command=self.seleccionar_hashfile).pack(side='left', padx=3)

        ttk.Label(frame_hash, text="Diccionario:").pack(side='left', padx=7)
        self.hash_dict_file = tk.StringVar()
        self.entry_hash_dict = ttk.Entry(frame_hash, textvariable=self.hash_dict_file, width=38)
        self.entry_hash_dict.pack(side='left', padx=4)
        ttk.Button(frame_hash, text="Seleccionar", command=self.seleccionar_hashdict).pack(side='left', padx=3)

        ttk.Label(frame_hash, text="Tipo de hash (opcional):").pack(side='left', padx=7)
        self.hash_type = tk.StringVar()
        self.entry_hashtype = ttk.Entry(frame_hash, textvariable=self.hash_type, width=14)
        self.entry_hashtype.pack(side='left', padx=4)
        ttk.Button(frame_hash, text="Autodetectar", command=self.autodetectar_hashtype).pack(side='left', padx=3)

        ttk.Label(frame_hash, text="Motor:").pack(side='left', padx=7)
        self.hash_motor = tk.StringVar()
        self.combo_hash_motor = ttk.Combobox(frame_hash, textvariable=self.hash_motor, width=12, state="readonly")
        self.combo_hash_motor['values'] = ['hashcat', 'john']
        self.combo_hash_motor.pack(side='left', padx=4)
        self.combo_hash_motor.set('hashcat')

        ttk.Button(frame_hash, text="Iniciar crack", command=self.iniciar_hash_crack).pack(side='left', padx=15)

        self.text_hash_result = tk.Text(self.tab_hash, height=12, width=170, bg='#16181a', fg='#ff65fd', font=('Consolas', 11))
        self.text_hash_result.pack(pady=18, padx=8)
        ttk.Button(self.tab_hash, text="Exportar resultados a CSV", command=self.exportar_hashes_csv).pack(pady=5)
        ttk.Button(self.tab_hash, text="Exportar resultados a PDF", command=self.exportar_hashes_pdf).pack(pady=2)

    def seleccionar_hashfile(self):
        filename = filedialog.askopenfilename(title="Selecciona archivo de hashes")
        if filename:
            self.entry_hash.delete(0, tk.END)
            self.entry_hash.insert(0, filename)

    def seleccionar_hashdict(self):
        filename = filedialog.askopenfilename(title="Selecciona diccionario de passwords")
        if filename:
            self.entry_hash_dict.delete(0, tk.END)
            self.entry_hash_dict.insert(0, filename)

    def autodetectar_hashtype(self):
        from src.modules.hash_crack import detect_hash_type
        filepath = self.hash_file.get().strip()
        if not filepath or not os.path.isfile(filepath):
            messagebox.showerror("Error", "Selecciona un archivo de hashes válido.")
            return
        with open(filepath, 'r') as f:
            hashline = f.readline().strip()
        try:
            hashmode = detect_hash_type(hashline)
            if hashmode:
                self.hash_type.set(str(hashmode))
                messagebox.showinfo("Detectado", f"Tipo hashcat: {hashmode}")
            else:
                messagebox.showwarning("No detectado", "No se pudo detectar el tipo de hash.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def iniciar_hash_crack(self):
        from src.modules import hash_crack
        hashfile = self.hash_file.get().strip()
        wordlist = self.hash_dict_file.get().strip()
        hashmode = self.hash_type.get().strip() or None
        motor = self.hash_motor.get()
        if not hashfile or not os.path.isfile(hashfile):
            messagebox.showerror("Error", "Selecciona un archivo de hashes válido.")
            return
        if not wordlist or not os.path.isfile(wordlist):
            messagebox.showerror("Error", "Selecciona un diccionario válido.")
            return
        self.text_hash_result.delete('1.0', tk.END)
        self.text_hash_result.insert(tk.END, "Crackeando hashes...\n")
        self.tab_hash.update_idletasks()
        def run_crack():
            try:
                if motor == "hashcat":
                    resultados = hash_crack.crack_hashcat(hashfile, wordlist, hashmode)
                else:
                    resultados = hash_crack.crack_john(hashfile, wordlist)
                if resultados:
                    for h, p in resultados.items():
                        self.text_hash_result.insert(tk.END, f"{h} : {p}\n")
                    self.hash_cracked_data = resultados
                else:
                    self.text_hash_result.insert(tk.END, "No se crackeó ningún hash.\n")
                    self.hash_cracked_data = {}
            except Exception as e:
                self.text_hash_result.insert(tk.END, f"Error: {e}\n")
                self.hash_cracked_data = {}
        threading.Thread(target=run_crack, daemon=True).start()

    def exportar_hashes_csv(self):
        if not hasattr(self, "hash_cracked_data") or not self.hash_cracked_data:
            messagebox.showerror("Error", "No hay resultados para exportar.")
            return
        file = filedialog.asksaveasfilename(defaultextension=".csv", title="Guardar resultados como CSV")
        if not file:
            return
        import csv
        with open(file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Hash", "Password"])
            for h, p in self.hash_cracked_data.items():
                writer.writerow([h, p])
        messagebox.showinfo("Exportación completa", "Resultados exportados a CSV correctamente.")

    def exportar_hashes_pdf(self):
        if not hasattr(self, "hash_cracked_data") or not self.hash_cracked_data:
            messagebox.showerror("Error", "No hay resultados para exportar.")
            return
        file = filedialog.asksaveasfilename(defaultextension=".pdf", title="Guardar resultados como PDF")
        if not file:
            return
        import csv
        import tempfile
        from tools.export_report import generar_reporte_pdf
        with tempfile.NamedTemporaryFile('w+', delete=False, suffix='.csv') as tf:
            writer = csv.writer(tf)
            writer.writerow(["Hash", "Password"])
            for h, p in self.hash_cracked_data.items():
                writer.writerow([h, p])
            tf.flush()
            temp_csv = tf.name
        try:
            resumen = "Hash cracking results"
            generar_reporte_pdf(temp_csv, file, resumen)
            messagebox.showinfo("Exportación completa", "Resultados exportados a PDF correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar a PDF:\n{e}")
        finally:
            os.remove(temp_csv)

