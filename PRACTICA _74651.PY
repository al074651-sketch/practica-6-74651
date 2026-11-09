import tkinter as tk
from tkinter import ttk, messagebox
import math

# ==========================================
# CONSTANTES DE DISEÑO Y PALETA DE COLORES
# ==========================================
COLOR_BG_MAIN = "#18151D"       # Carbón obsidiana profundo
COLOR_CARD_BG = "#211D28"       # Superficie de tarjetas
COLOR_CARD_BORDER = "#332C3D"   # Bordes sutiles
COLOR_ACCENT = "#C48B9F"        # Rosa empolvado (Dusty Rose)
COLOR_ACCENT_HOVER = "#A66E81"  # Malva intenso
COLOR_TEXT = "#F3E6EA"          # Texto principal (Rosa perla claro)
COLOR_TEXT_MUTED = "#A89A9F"    # Texto secundario

# Estados de Corrosión
COLOR_SAFE = "#88AB94"          # Verde menta empolvado (<10%)
COLOR_WARN = "#D4A373"          # Ocre cálido (10% - 15%)
COLOR_CRIT = "#B84A62"          # Carmesí borgoña (>15%)

# ==========================================
# MÓDULO LOGICO (MODELADO DE CORROSIÓN)
# ==========================================
class CorrosionModel:
    """Clase encargada de representar la matriz de acero y realizar los cálculos físicos."""
    def __init__(self, rows=4, cols=4):
        self.rows = rows
        self.cols = cols
        self.d0 = 16.0  # Diámetro inicial nominal en mm (ej. Varilla #5)
        self.critical_limit = 15.0  # % límite de pérdida tolerable
        
        # Matriz NxM con la velocidad de corrosión local (mm/año) en cada zona
        # Inicializada por defecto con ambiente urbano (0.02 mm/año)
        self.matrix_vc = [[0.02 for _ in range(cols)] for _ in range(rows)]

    def set_environment_preset(self, rate):
        """Asigna una tasa base a toda la matriz."""
        for r in range(self.rows):
            for c in range(self.cols):
                self.matrix_vc[r][c] = rate

    def calculate_cell_status(self, r, c, years):
        """Calcula el estado actual de una celda específica a los 'years' años."""
        vc = self.matrix_vc[r][c]
        delta_d = vc * years  # Pérdida de diámetro acumulada (mm)
        d_actual = max(0.0, self.d0 - delta_d)
        
        # Áreas transversales (mm²)
        area_0 = (math.pi * (self.d0 ** 2)) / 4.0
        area_actual = (math.pi * (d_actual ** 2)) / 4.0
        
        loss_pct = ((area_0 - area_actual) / area_0) * 100.0 if area_0 > 0 else 100.0
        
        if loss_pct < 10.0:
            status = "SEGURO"
            color = COLOR_SAFE
        elif loss_pct <= self.critical_limit:
            status = "ALERTA"
            color = COLOR_WARN
        else:
            status = "CRÍTICO"
            color = COLOR_CRIT
            
        return {
            "vc": vc,
            "d_actual": d_actual,
            "area_actual": area_actual,
            "loss_pct": loss_pct,
            "status": status,
            "color": color
        }

    def evaluate_structure(self, years):
        """Genera las estadísticas globales de la matriz."""
        max_loss = -1.0
        max_coord = (0, 0)
        total_loss = 0.0
        critical_count = 0
        
        for r in range(self.rows):
            for c in range(self.cols):
                cell_info = self.calculate_cell_status(r, c, years)
                loss = cell_info["loss_pct"]
                total_loss += loss
                
                if loss > max_loss:
                    max_loss = loss
                    max_coord = (r, c)
                
                if cell_info["status"] == "CRÍTICO":
                    critical_count += 1
                    
        total_cells = self.rows * self.cols
        avg_loss = total_loss / total_cells
        
        return {
            "avg_loss": avg_loss,
            "max_loss": max_loss,
            "max_coord": max_coord,
            "critical_count": critical_count,
            "total_cells": total_cells
        }

# ==========================================
# MÓDULO INTERFAZ GRÁFICA (STEELIA GUI)
# ==========================================
class SteeliaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("STEELIA — Evaluador de Corrosión en Acero")
        self.root.geometry("1100 x 720")
        self.root.configure(bg=COLOR_BG_MAIN)

        self.model = CorrosionModel(rows=4, cols=4)
        self.current_year = tk.IntVar(value=10)
        self.is_playing = False
        
        self.setup_styles()
        self.build_ui()
        self.update_simulation()

    def setup_styles(self):
        """Configura estilos visuales para los widgets ttk."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar colores de sliders y comboboxes
        style.configure("TFrame", background=COLOR_BG_MAIN)
        style.configure("Card.TFrame", background=COLOR_CARD_BG, relief="flat")
        style.configure("TLabel", background=COLOR_CARD_BG, foreground=COLOR_TEXT, font=("Segoe UI", 10))
        style.configure("Header.TLabel", background=COLOR_BG_MAIN, foreground=COLOR_ACCENT, font=("Segoe UI", 18, "bold"))
        style.configure("SubHeader.TLabel", background=COLOR_CARD_BG, foreground=COLOR_ACCENT, font=("Segoe UI", 12, "bold"))
        style.configure("Value.TLabel", background=COLOR_CARD_BG, foreground=COLOR_TEXT, font=("Segoe UI", 14, "bold"))

    def build_ui(self):
        # Header principal
        header_frame = tk.Frame(self.root, bg=COLOR_BG_MAIN, pady=15, padx=25)
        header_frame.pack(fill="x")
        
        lbl_title = tk.Label(header_frame, text="STEELIA", font=("Georgia", 22, "bold"), bg=COLOR_BG_MAIN, fg=COLOR_ACCENT)
        lbl_title.pack(side="left")
        
        lbl_subtitle = tk.Label(header_frame, text=" |  Modelado Matricial de Degradación del Acero", font=("Segoe UI", 11), bg=COLOR_BG_MAIN, fg=COLOR_TEXT_MUTED)
        lbl_subtitle.pack(side="left", fill="y", pady=5)

        # Contenedor Principal (2 columnas: Izquierda Parámetros, Derecha Matriz y Resultados)
        main_container = tk.Frame(self.root, bg=COLOR_BG_MAIN, padx=20, pady=10)
        main_container.pack(fill="both", expand=True)

        # COLUMNA IZQUIERDA: Panel de Control
        left_panel = tk.Frame(main_container, bg=COLOR_CARD_BG, highlightbackground=COLOR_CARD_BORDER, highlightthickness=1, padx=15, pady=15, width=320)
        left_panel.pack(side="left", fill="y", padx=(0, 15))
        left_panel.pack_propagate(False)

        tk.Label(left_panel, text="PARÁMETROS DEL MODELO", font=("Segoe UI", 11, "bold"), bg=COLOR_CARD_BG, fg=COLOR_ACCENT).pack(anchor="w", pady=(0, 15))

        # 1. Diámetro inicial
        tk.Label(left_panel, text="Diámetro Inicial d₀ (mm):", bg=COLOR_CARD_BG, fg=COLOR_TEXT).pack(anchor="w")
        self.ent_d0 = tk.Entry(left_panel, bg=COLOR_BG_MAIN, fg=COLOR_TEXT, insertbackground=COLOR_TEXT, relief="flat", highlightbackground=COLOR_CARD_BORDER, highlightthickness=1)
        self.ent_d0.insert(0, "16.0")
        self.ent_d0.pack(fill="x", pady=(2, 12))

        # 2. Ambiente Exposición
        tk.Label(left_panel, text="Ambiente de Exposición:", bg=COLOR_CARD_BG, fg=COLOR_TEXT).pack(anchor="w")
        self.cmb_env = ttk.Combobox(left_panel, values=["Urbano (0.02 mm/año)", "Industrial (0.06 mm/año)", "Marino (0.12 mm/año)"], state="readonly")
        self.cmb_env.current(0)
        self.cmb_env.pack(fill="x", pady=(2, 12))
        self.cmb_env.bind("<<ComboboxSelected>>", self.on_env_change)

        # 3. Límite Crítico Tolerable
        tk.Label(left_panel, text="Límite Tolerable de Pérdida (%):", bg=COLOR_CARD_BG, fg=COLOR_TEXT).pack(anchor="w")
        self.ent_limit = tk.Entry(left_panel, bg=COLOR_BG_MAIN, fg=COLOR_TEXT, insertbackground=COLOR_TEXT, relief="flat", highlightbackground=COLOR_CARD_BORDER, highlightthickness=1)
        self.ent_limit.insert(0, "15.0")
        self.ent_limit.pack(fill="x", pady=(2, 15))

        # Botón Aplicar Parámetros
        btn_apply = tk.Button(left_panel, text="Actualizar Parámetros", bg=COLOR_ACCENT, fg=COLOR_BG_MAIN, activebackground=COLOR_ACCENT_HOVER, font=("Segoe UI", 9, "bold"), relief="flat", command=self.apply_parameters, cursor="hand2")
        btn_apply.pack(fill="x", pady=(0, 20))

        # Separador sutil
        tk.Frame(left_panel, bg=COLOR_CARD_BORDER, height=1).pack(fill="x", pady=10)

        # Controles de Tiempo (Simulación)
        tk.Label(left_panel, text="SIMULACIÓN TEMPORAL", font=("Segoe UI", 11, "bold"), bg=COLOR_CARD_BG, fg=COLOR_ACCENT).pack(anchor="w", pady=(10, 5))
        
        self.lbl_year = tk.Label(left_panel, text="Tiempo: 10 Años", font=("Segoe UI", 12, "bold"), bg=COLOR_CARD_BG, fg=COLOR_TEXT)
        self.lbl_year.pack(anchor="w", pady=5)

        self.slider_year = ttk.Scale(left_panel, from_=0, to=50, variable=self.current_year, command=lambda e: self.update_simulation())
        self.slider_year.pack(fill="x", pady=5)

        self.btn_play = tk.Button(left_panel, text="▶ Reproducción Animada", bg=COLOR_CARD_BORDER, fg=COLOR_TEXT, activebackground=COLOR_ACCENT_HOVER, font=("Segoe UI", 9), relief="flat", command=self.toggle_play, cursor="hand2")
        self.btn_play.pack(fill="x", pady=10)

        # COLUMNA DERECHA: Matriz visual y Estadísticas
        right_panel = tk.Frame(main_container, bg=COLOR_BG_MAIN)
        right_panel.pack(side="right", fill="both", expand=True)

        # Sub-panel Superior: Matriz Grid
        matrix_card = tk.Frame(right_panel, bg=COLOR_CARD_BG, highlightbackground=COLOR_CARD_BORDER, highlightthickness=1, padx=15, pady=15)
        matrix_card.pack(fill="both", expand=True, pady=(0, 15))

        tk.Label(matrix_card, text="MAPA DE CALOR DE LA PARRILLA DE ACERO (MATRIZ 4x4)", font=("Segoe UI", 11, "bold"), bg=COLOR_CARD_BG, fg=COLOR_ACCENT).pack(anchor="w", pady=(0, 10))
        
        self.matrix_frame = tk.Frame(matrix_card, bg=COLOR_CARD_BG)
        self.matrix_frame.pack(expand=True)
        self.cell_widgets = []
        self.create_matrix_grid()

        # Leyenda de Colores
        legend_frame = tk.Frame(matrix_card, bg=COLOR_CARD_BG)
        legend_frame.pack(fill="x", pady=(10, 0))
        
        self.create_legend_item(legend_frame, COLOR_SAFE, "Seguro (<10%)")
        self.create_legend_item(legend_frame, COLOR_WARN, "Alerta (10-15%)")
        self.create_legend_item(legend_frame, COLOR_CRIT, "Crítico (>15%)")

        # Sub-panel Inferior: Métricas Globales y Recomendación
        metrics_card = tk.Frame(right_panel, bg=COLOR_CARD_BG, highlightbackground=COLOR_CARD_BORDER, highlightthickness=1, padx=15, pady=15)
        metrics_card.pack(fill="x")

        metrics_grid = tk.Frame(metrics_card, bg=COLOR_CARD_BG)
        metrics_grid.pack(fill="x")

        # Tarjeta Métrica 1
        m1 = tk.Frame(metrics_grid, bg=COLOR_BG_MAIN, padx=10, pady=8)
        m1.pack(side="left", fill="both", expand=True, padx=5)
        tk.Label(m1, text="Pérdida Promedio", bg=COLOR_BG_MAIN, fg=COLOR_TEXT_MUTED, font=("Segoe UI", 8)).pack()
        self.lbl_avg_loss = tk.Label(m1, text="0.0%", bg=COLOR_BG_MAIN, fg=COLOR_TEXT, font=("Segoe UI", 14, "bold"))
        self.lbl_avg_loss.pack()

        # Tarjeta Métrica 2
        m2 = tk.Frame(metrics_grid, bg=COLOR_BG_MAIN, padx=10, pady=8)
        m2.pack(side="left", fill="both", expand=True, padx=5)
        tk.Label(m2, text="Pérdida Máxima (Zona)", bg=COLOR_BG_MAIN, fg=COLOR_TEXT_MUTED, font=("Segoe UI", 8)).pack()
        self.lbl_max_loss = tk.Label(m2, text="0.0%", bg=COLOR_BG_MAIN, fg=COLOR_TEXT, font=("Segoe UI", 14, "bold"))
        self.lbl_max_loss.pack()

        # Tarjeta Métrica 3
        m3 = tk.Frame(metrics_grid, bg=COLOR_BG_MAIN, padx=10, pady=8)
        m3.pack(side="left", fill="both", expand=True, padx=5)
        tk.Label(m3, text="Celdas en Estado Crítico", bg=COLOR_BG_MAIN, fg=COLOR_TEXT_MUTED, font=("Segoe UI", 8)).pack()
        self.lbl_crit_count = tk.Label(m3, text="0 / 16", bg=COLOR_BG_MAIN, fg=COLOR_TEXT, font=("Segoe UI", 14, "bold"))
        self.lbl_crit_count.pack()

        # Diagnóstico técnico automatizado
        self.lbl_diag = tk.Label(metrics_card, text="Diagnóstico: Estructura en condiciones óptimas.", font=("Segoe UI", 9, "italic"), bg=COLOR_CARD_BG, fg=COLOR_ACCENT, pady=8)
        self.lbl_diag.pack(anchor="w")

    def create_legend_item(self, parent, color, text):
        f = tk.Frame(parent, bg=COLOR_CARD_BG)
        f.pack(side="left", padx=15)
        box = tk.Frame(f, bg=color, width=14, height=14)
        box.pack(side="left", padx=(0, 5))
        box.pack_propagate(False)
        tk.Label(f, text=text, bg=COLOR_CARD_BG, fg=COLOR_TEXT_MUTED, font=("Segoe UI", 8)).pack(side="left")

    def create_matrix_grid(self):
        """Crea la cuadrícula de botones interactivos para la matriz 4x4."""
        for r in range(self.model.rows):
            row_widgets = []
            for c in range(self.model.cols):
                btn = tk.Button(
                    self.matrix_frame,
                    text=f"({r},{c})\n100%",
                    font=("Consolas", 9, "bold"),
                    width=10, height=3,
                    relief="flat",
                    cursor="hand2",
                    command=lambda row=r, col=c: self.on_cell_click(row, col)
                )
                btn.grid(row=r, column=c, padx=5, pady=5)
                row_widgets.append(btn)
            self.cell_widgets.append(row_widgets)

    def on_env_change(self, event):
        idx = self.cmb_env.current()
        rates = [0.02, 0.06, 0.12]
        self.model.set_environment_preset(rates[idx])
        self.update_simulation()

    def apply_parameters(self):
        try:
            d0_val = float(self.ent_d0.get())
            limit_val = float(self.ent_limit.get())
            if d0_val <= 0 or limit_val <= 0:
                raise ValueError
            self.model.d0 = d0_val
            self.model.critical_limit = limit_val
            self.update_simulation()
        except ValueError:
            messagebox.showerror("Error de Entrada", "Por favor ingresa números válidos mayores a 0.")

    def on_cell_click(self, r, c):
        """Permite editar individualmente la tasa de corrosión de una celda para simular picaduras."""
        cell_info = self.model.calculate_cell_status(r, c, self.current_year.get())
        
        def save_custom_rate():
            try:
                new_rate = float(ent_rate.get())
                self.model.matrix_vc[r][c] = new_rate
                top.destroy()
                self.update_simulation()
            except ValueError:
                messagebox.showerror("Error", "Ingresa una tasa numérica válida.")

        top = tk.Toplevel(self.root)
        top.title(f"Detalle Zona ({r}, {c})")
        top.geometry("280x220")
        top.configure(bg=COLOR_CARD_BG)

        tk.Label(top, text=f"Inspección de Nodo [{r}, {c}]", font=("Segoe UI", 10, "bold"), bg=COLOR_CARD_BG, fg=COLOR_ACCENT).pack(pady=10)
        tk.Label(top, text=f"Diámetro remanente: {cell_info['d_actual']:.2f} mm", bg=COLOR_CARD_BG, fg=COLOR_TEXT).pack()
        tk.Label(top, text=f"Pérdida acumulada: {cell_info['loss_pct']:.1f}%", bg=COLOR_CARD_BG, fg=COLOR_TEXT).pack()

        tk.Label(top, text="Tasa Corrosión (mm/año):", bg=COLOR_CARD_BG, fg=COLOR_TEXT_MUTED).pack(pady=(10, 2))
        ent_rate = tk.Entry(top, bg=COLOR_BG_MAIN, fg=COLOR_TEXT, insertbackground=COLOR_TEXT, relief="flat")
        ent_rate.insert(0, str(cell_info["vc"]))
        ent_rate.pack(fill="x", padx=30)

        tk.Button(top, text="Guardar Cambio", bg=COLOR_ACCENT, fg=COLOR_BG_MAIN, relief="flat", command=save_custom_rate, pady=4).pack(pady=15)

    def update_simulation(self):
        """Actualiza la renderización de la matriz y las métricas en tiempo real."""
        years = self.current_year.get()
        self.lbl_year.config(text=f"Tiempo: {years} Años")

        # Actualizar celdas de la matriz
        for r in range(self.model.rows):
            for c in range(self.model.cols):
                info = self.model.calculate_cell_status(r, c, years)
                btn = self.cell_widgets[r][c]
                
                # Texto en celda
                btn.config(
                    text=f"[{r},{c}]\n{info['d_actual']:.1f} mm\n-{info['loss_pct']:.1f}%",
                    bg=info['color'],
                    fg="#121016" if info['color'] == COLOR_WARN else "#FFFFFF"
                )

        # Actualizar métricas globales
        stats = self.model.evaluate_structure(years)
        self.lbl_avg_loss.config(text=f"{stats['avg_loss']:.1f}%")
        self.lbl_max_loss.config(text=f"{stats['max_loss']:.1f}% en [{stats['max_coord'][0]},{stats['max_coord'][1]}]")
        self.lbl_crit_count.config(text=f"{stats['critical_count']} / {stats['total_cells']}")

        # Actualizar recomendación
        if stats['critical_count'] > 0:
            self.lbl_diag.config(text=f"⚠️ ALERTA: {stats['critical_count']} zona(s) superan el umbral tolerable ({self.model.critical_limit}%). Se sugiere intervención urgente.", fg=COLOR_CRIT)
        elif stats['max_loss'] > 8.0:
            self.lbl_diag.config(text="ℹ️ PRECAUCIÓN: Estructura mostrando desgaste moderado. Planificar mantenimiento preventivo.", fg=COLOR_WARN)
        else:
            self.lbl_diag.config(text="✅ OK: Estructura en óptimas condiciones de resistencia.", fg=COLOR_SAFE)

    def toggle_play(self):
        """Inicia/detiene la animación temporal del slider."""
        self.is_playing = not self.is_playing
        if self.is_playing:
            self.btn_play.config(text="⏸ Pausar Animación", bg=COLOR_ACCENT_HOVER)
            self.animate()
        else:
            self.btn_play.config(text="▶ Reproducción Animada", bg=COLOR_CARD_BORDER)

    def animate(self):
        if self.is_playing:
            curr = self.current_year.get()
            if curr >= 50:
                self.current_year.set(0)
            else:
                self.current_year.set(curr + 1)
            self.update_simulation()
            self.root.after(300, self.animate)

# ==========================================
# PUNTO DE ENTRADA PRINCIPAL
# ==========================================
if __name__ == "__main__":
    root = tk.Tk()
    app = SteeliaApp(root)
    root.mainloop()
