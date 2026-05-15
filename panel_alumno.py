import tkinter as tk
from tkinter import ttk, messagebox
from mysql.connector import Error

from database import (
    obtener_estudiante_por_usuario,
    obtener_calificaciones_estudiante,
    obtener_ultimo_habito,
    obtener_observaciones_estudiante,
    obtener_ultimo_diagnostico,
    guardar_diagnostico_ia,
)
from ia_recomendaciones import generar_recomendaciones
from ui_styles import COLORS, FONT, configurar_estilos, boton


def abrir_panel_alumno(ventana_login, usuario_actual):
    estudiante = obtener_estudiante_por_usuario(usuario_actual["id_usuario"])

    if not estudiante:
        messagebox.showerror("Error", "No se encontró información del estudiante.")
        ventana_login.deiconify()
        return

    panel = tk.Toplevel()
    panel.title("Panel de Alumno - sarAI")
    panel.geometry("980x680")
    panel.minsize(900, 620)
    configurar_estilos(panel)

    def cerrar_sesion():
        panel.destroy()
        ventana_login.deiconify()

    panel.protocol("WM_DELETE_WINDOW", cerrar_sesion)

    encabezado = tk.Frame(panel, bg=COLORS["bg"])
    encabezado.pack(fill="x", padx=10, pady=8)

    tk.Label(encabezado, text="Panel de Alumno", bg=COLORS["bg"], fg=COLORS["text"], font=(FONT, 13, "bold")).pack(side="left")
    tk.Label(encabezado, text=f"  |  {estudiante['nombre']}", bg=COLORS["bg"], fg=COLORS["muted"], font=(FONT, 9)).pack(side="left")
    boton(encabezado, "Cerrar sesión", cerrar_sesion, ancho=13).pack(side="right")

    contenido = tk.Frame(panel, bg=COLORS["bg"])
    contenido.pack(fill="both", expand=True, padx=10, pady=(0, 10))
    contenido.columnconfigure(0, weight=1)
    contenido.rowconfigure(3, weight=1)

    caja_resumen = tk.LabelFrame(contenido, text="Resumen", bg=COLORS["surface"], font=(FONT, 9, "bold"), padx=10, pady=8)
    caja_resumen.grid(row=0, column=0, sticky="ew", pady=(0, 8))

    tk.Label(caja_resumen, text="Promedio:", bg=COLORS["surface"], font=(FONT, 9, "bold")).grid(row=0, column=0, sticky="w", padx=6, pady=5)
    lbl_promedio = tk.Label(caja_resumen, text="--", bg=COLORS["surface"], fg=COLORS["primary"], font=(FONT, 10, "bold"))
    lbl_promedio.grid(row=0, column=1, sticky="w", padx=6, pady=5)

    tk.Label(caja_resumen, text="Nivel de riesgo:", bg=COLORS["surface"], font=(FONT, 9, "bold")).grid(row=0, column=2, sticky="w", padx=(30, 6), pady=5)
    lbl_riesgo = tk.Label(caja_resumen, text="--", bg=COLORS["surface"], fg=COLORS["warning"], font=(FONT, 10, "bold"))
    lbl_riesgo.grid(row=0, column=3, sticky="w", padx=6, pady=5)

    tk.Label(caja_resumen, text="Materia prioritaria:", bg=COLORS["surface"], font=(FONT, 9, "bold")).grid(row=0, column=4, sticky="w", padx=(30, 6), pady=5)
    lbl_materia = tk.Label(caja_resumen, text="--", bg=COLORS["surface"], fg=COLORS["text"], font=(FONT, 10, "bold"))
    lbl_materia.grid(row=0, column=5, sticky="w", padx=6, pady=5)

    fila_superior = tk.Frame(contenido, bg=COLORS["bg"])
    fila_superior.grid(row=1, column=0, sticky="nsew", pady=(0, 8))
    fila_superior.columnconfigure(0, weight=1)
    fila_superior.columnconfigure(1, weight=1)

    caja_calificaciones = tk.LabelFrame(fila_superior, text="Calificaciones", bg=COLORS["surface"], font=(FONT, 9, "bold"), padx=10, pady=8)
    caja_calificaciones.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

    tabla_calificaciones = ttk.Treeview(caja_calificaciones, columns=("Materia", "Calificacion"), show="headings", height=6)
    tabla_calificaciones.heading("Materia", text="Materia")
    tabla_calificaciones.heading("Calificacion", text="Calificación")
    tabla_calificaciones.column("Materia", width=350)
    tabla_calificaciones.column("Calificacion", width=100, anchor="center")
    tabla_calificaciones.pack(fill="both", expand=True)

    caja_habitos = tk.LabelFrame(fila_superior, text="Hábitos registrados", bg=COLORS["surface"], font=(FONT, 9, "bold"), padx=10, pady=8)
    caja_habitos.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

    txt_habitos = tk.Text(caja_habitos, height=6, wrap="word", font=(FONT, 9))
    txt_habitos.pack(fill="both", expand=True)

    caja_recomendaciones = tk.LabelFrame(contenido, text="Recomendaciones de sarAI", bg=COLORS["surface"], font=(FONT, 9, "bold"), padx=10, pady=8)
    caja_recomendaciones.grid(row=2, column=0, sticky="ew", pady=(0, 8))

    txt_recomendaciones = tk.Text(caja_recomendaciones, height=8, wrap="word", font=(FONT, 9))
    txt_recomendaciones.pack(fill="x")

    caja_plan = tk.LabelFrame(contenido, text="Plan de estudio sugerido", bg=COLORS["surface"], font=(FONT, 9, "bold"), padx=10, pady=8)
    caja_plan.grid(row=3, column=0, sticky="nsew", pady=(0, 8))
    caja_plan.columnconfigure(0, weight=1)
    caja_plan.rowconfigure(0, weight=1)

    tabla_plan = ttk.Treeview(caja_plan, columns=("Dia", "Materia", "Tiempo", "Actividad"), show="headings", height=7)
    tabla_plan.heading("Dia", text="Día")
    tabla_plan.heading("Materia", text="Materia")
    tabla_plan.heading("Tiempo", text="Tiempo")
    tabla_plan.heading("Actividad", text="Actividad")
    tabla_plan.column("Dia", width=80, anchor="center")
    tabla_plan.column("Materia", width=220)
    tabla_plan.column("Tiempo", width=80, anchor="center")
    tabla_plan.column("Actividad", width=520)
    tabla_plan.grid(row=0, column=0, sticky="nsew")

    acciones = tk.Frame(contenido, bg=COLORS["bg"])
    acciones.grid(row=4, column=0, sticky="e")

    def limpiar_datos():
        for item in tabla_calificaciones.get_children():
            tabla_calificaciones.delete(item)
        for item in tabla_plan.get_children():
            tabla_plan.delete(item)
        txt_habitos.delete("1.0", tk.END)
        txt_recomendaciones.delete("1.0", tk.END)

    def cargar_datos():
        limpiar_datos()

        id_estudiante = estudiante["id_estudiante"]
        calificaciones = obtener_calificaciones_estudiante(id_estudiante)
        habitos = obtener_ultimo_habito(id_estudiante)
        observaciones = obtener_observaciones_estudiante(id_estudiante)

        if not calificaciones:
            lbl_promedio.config(text="Sin datos")
            lbl_riesgo.config(text="Sin datos")
            lbl_materia.config(text="Sin datos")
            txt_recomendaciones.insert("1.0", "Aún no tienes calificaciones registradas. Pide a tu maestro que capture tu evaluación.")
            return

        diagnostico, plan = obtener_ultimo_diagnostico(id_estudiante)

        if not diagnostico:
            resultado = generar_recomendaciones(calificaciones, habitos, observaciones)
            guardar_diagnostico_ia(id_estudiante, resultado)
            diagnostico, plan = obtener_ultimo_diagnostico(id_estudiante)

        for materia, nota in calificaciones.items():
            tabla_calificaciones.insert("", "end", values=(materia, nota))

        lbl_promedio.config(text=f"{diagnostico['promedio']}")
        lbl_riesgo.config(text=f"{diagnostico['nivel_riesgo']}")
        lbl_materia.config(text=f"{diagnostico['materia_prioritaria']}")

        texto_habitos = (
            f"Horas de estudio por semana: {habitos.get('horas_estudio_semana', 0)}\n"
            f"Días de estudio por semana: {habitos.get('dias_estudio_semana', 0)}\n"
            f"Horas de sueño promedio: {habitos.get('horas_sueno', 0)}\n"
            f"Nivel de concentración: {habitos.get('nivel_concentracion', 'Medio')}\n"
            f"Dificultad principal: {habitos.get('dificultad_principal', '') or 'Sin dato'}\n"
            f"Horario preferido: {habitos.get('horario_preferido', '') or 'Sin dato'}"
        )
        txt_habitos.insert("1.0", texto_habitos)
        txt_recomendaciones.insert("1.0", diagnostico["resumen"])

        for fila in plan:
            tabla_plan.insert("", "end", values=(fila["dia"], fila["materia"], f"{fila['tiempo_minutos']} min", fila["actividad"]))

    def cargar_datos_seguro():
        try:
            cargar_datos()
        except Error as error:
            messagebox.showerror("Error", f"No se pudo cargar la información.\n\nDetalle: {error}")

    boton(acciones, "Actualizar información", cargar_datos_seguro, color="primary", ancho=22).pack(side="right")
    cargar_datos_seguro()
