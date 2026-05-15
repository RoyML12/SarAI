import tkinter as tk
from tkinter import ttk, messagebox
from mysql.connector import Error

from database import (
    crear_estudiante,
    obtener_docente_por_usuario,
    obtener_estudiantes,
    obtener_materias,
    guardar_calificaciones,
    guardar_habitos,
    guardar_diagnostico_ia,
    obtener_calificaciones_estudiante,
    obtener_ultimo_habito,
    obtener_observaciones_estudiante,
)
from ia_recomendaciones import generar_recomendaciones
from validaciones import (
    texto_valido,
    usuario_valido,
    contrasena_valida,
    nota_valida,
    numero_decimal_valido,
    entero_valido,
)
from ui_styles import COLORS, FONT, configurar_estilos, boton


def abrir_panel_maestro(ventana_login, usuario_actual):
    panel = tk.Toplevel()
    panel.title("Panel de Maestro - sarAI")
    panel.geometry("1000x690")
    panel.minsize(900, 650)
    configurar_estilos(panel)

    docente = obtener_docente_por_usuario(usuario_actual["id_usuario"])
    id_docente = docente["id_docente"] if docente else None

    materias = obtener_materias()
    estudiantes_cache = []
    entradas_calificaciones = {}

    def cerrar_sesion():
        panel.destroy()
        ventana_login.deiconify()

    panel.protocol("WM_DELETE_WINDOW", cerrar_sesion)

    encabezado = tk.Frame(panel, bg=COLORS["bg"])
    encabezado.pack(fill="x", padx=10, pady=8)

    tk.Label(encabezado, text="Panel de Maestro", bg=COLORS["bg"], fg=COLORS["text"], font=(FONT, 13, "bold")).pack(side="left")
    tk.Label(encabezado, text="  |  Registro, evaluación y recomendaciones", bg=COLORS["bg"], fg=COLORS["muted"], font=(FONT, 9)).pack(side="left")
    boton(encabezado, "Cerrar sesión", cerrar_sesion, ancho=13).pack(side="right")

    contenido = tk.Frame(panel, bg=COLORS["bg"])
    contenido.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    notebook = ttk.Notebook(contenido)
    notebook.pack(fill="both", expand=True)

    tab_registro = tk.Frame(notebook, bg=COLORS["bg"])
    tab_evaluacion = tk.Frame(notebook, bg=COLORS["bg"])
    notebook.add(tab_registro, text="Registrar alumno")
    notebook.add(tab_evaluacion, text="Evaluación e IA")

    caja_registro = tk.LabelFrame(tab_registro, text="Datos del alumno", bg=COLORS["surface"], font=(FONT, 9, "bold"), padx=12, pady=10)
    caja_registro.pack(fill="x", padx=10, pady=10)

    campos_registro = {}

    def agregar_campo(texto, fila, clave, mostrar=None):
        tk.Label(caja_registro, text=texto, bg=COLORS["surface"], font=(FONT, 9)).grid(row=fila, column=0, sticky="w", padx=8, pady=5)
        entrada = tk.Entry(caja_registro, width=35, show=mostrar, font=(FONT, 9))
        entrada.grid(row=fila, column=1, sticky="w", padx=8, pady=5)
        campos_registro[clave] = entrada

    agregar_campo("Nombre completo:", 0, "nombre")
    agregar_campo("Usuario:", 1, "usuario")
    agregar_campo("Contraseña:", 2, "contrasena", "*")
    agregar_campo("Grado:", 3, "grado")
    agregar_campo("Grupo:", 4, "grupo")
    agregar_campo("Teléfono del tutor:", 5, "telefono")

    botones_registro = tk.Frame(caja_registro, bg=COLORS["surface"])
    botones_registro.grid(row=6, column=0, columnspan=2, sticky="w", padx=8, pady=(12, 4))

    def limpiar_registro():
        for entrada in campos_registro.values():
            entrada.delete(0, tk.END)

    def registrar_alumno():
        nombre = campos_registro["nombre"].get().strip()
        usuario = campos_registro["usuario"].get().strip()
        contrasena = campos_registro["contrasena"].get().strip()
        grado = campos_registro["grado"].get().strip()
        grupo = campos_registro["grupo"].get().strip()
        telefono = campos_registro["telefono"].get().strip()

        if not texto_valido(nombre):
            messagebox.showerror("Error", "El nombre debe contener solo letras y espacios.")
            return
        if not usuario_valido(usuario):
            messagebox.showerror("Error", "El usuario debe tener de 3 a 30 caracteres y no usar espacios.")
            return
        if not contrasena_valida(contrasena):
            messagebox.showerror("Error", "La contraseña debe tener al menos 4 caracteres.")
            return
        if not entero_valido(grado, 1, 6):
            messagebox.showerror("Error", "El grado debe ser un número entre 1 y 6.")
            return
        if not grupo:
            messagebox.showerror("Error", "El grupo es obligatorio.")
            return

        try:
            crear_estudiante(nombre, usuario, contrasena, int(grado), grupo.upper(), telefono)
            messagebox.showinfo("Éxito", "Alumno registrado correctamente.")
            limpiar_registro()
            cargar_estudiantes()
            notebook.select(tab_evaluacion)
        except Error as error:
            messagebox.showerror("Error", f"No se pudo registrar el alumno.\n\nDetalle: {error}")

    boton(botones_registro, "Registrar", registrar_alumno, color="primary", ancho=15).pack(side="left")
    boton(botones_registro, "Limpiar", limpiar_registro, ancho=12).pack(side="left", padx=8)

    caja_nota = tk.LabelFrame(tab_registro, text="Nota", bg=COLORS["surface"], font=(FONT, 9, "bold"), padx=12, pady=10)
    caja_nota.pack(fill="x", padx=10, pady=(0, 10))
    tk.Label(
        caja_nota,
        text="Después de registrar al alumno, entra a la pestaña Evaluación e IA para capturar sus calificaciones y hábitos.",
        bg=COLORS["surface"],
        fg=COLORS["muted"],
        font=(FONT, 9),
        wraplength=850,
        justify="left",
    ).pack(anchor="w")

    tab_evaluacion.columnconfigure(0, weight=1)
    tab_evaluacion.rowconfigure(1, weight=1)

    caja_alumno = tk.LabelFrame(tab_evaluacion, text="Alumno", bg=COLORS["surface"], font=(FONT, 9, "bold"), padx=10, pady=8)
    caja_alumno.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

    tk.Label(caja_alumno, text="Seleccionar alumno:", bg=COLORS["surface"], font=(FONT, 9)).grid(row=0, column=0, padx=6, pady=5, sticky="w")
    combo_alumnos = ttk.Combobox(caja_alumno, width=48, state="readonly")
    combo_alumnos.grid(row=0, column=1, padx=6, pady=5, sticky="w")
    boton(caja_alumno, "Recargar", lambda: cargar_estudiantes(), ancho=12).grid(row=0, column=2, padx=6, pady=5)

    datos = tk.Frame(tab_evaluacion, bg=COLORS["bg"])
    datos.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
    datos.columnconfigure(0, weight=1)
    datos.columnconfigure(1, weight=1)
    datos.rowconfigure(2, weight=1)

    caja_calif = tk.LabelFrame(datos, text="Calificaciones", bg=COLORS["surface"], font=(FONT, 9, "bold"), padx=10, pady=8)
    caja_calif.grid(row=0, column=0, sticky="nsew", padx=(0, 6), pady=(0, 8))

    for index, materia in enumerate(materias):
        nombre_materia = materia["nombre_materia"]
        tk.Label(caja_calif, text=f"{nombre_materia}:", bg=COLORS["surface"], font=(FONT, 9)).grid(row=index, column=0, sticky="w", padx=6, pady=5)
        entrada = tk.Entry(caja_calif, width=10, justify="center", font=(FONT, 9))
        entrada.grid(row=index, column=1, sticky="w", padx=6, pady=5)
        entradas_calificaciones[nombre_materia] = entrada

    caja_habitos = tk.LabelFrame(datos, text="Hábitos de estudio", bg=COLORS["surface"], font=(FONT, 9, "bold"), padx=10, pady=8)
    caja_habitos.grid(row=0, column=1, sticky="nsew", padx=(6, 0), pady=(0, 8))

    tk.Label(caja_habitos, text="Horas/semana:", bg=COLORS["surface"], font=(FONT, 9)).grid(row=0, column=0, sticky="w", padx=6, pady=5)
    entrada_horas_estudio = tk.Entry(caja_habitos, width=10, font=(FONT, 9))
    entrada_horas_estudio.grid(row=0, column=1, sticky="w", padx=6, pady=5)

    tk.Label(caja_habitos, text="Días/semana:", bg=COLORS["surface"], font=(FONT, 9)).grid(row=1, column=0, sticky="w", padx=6, pady=5)
    entrada_dias_estudio = tk.Entry(caja_habitos, width=10, font=(FONT, 9))
    entrada_dias_estudio.grid(row=1, column=1, sticky="w", padx=6, pady=5)

    tk.Label(caja_habitos, text="Horas de sueño:", bg=COLORS["surface"], font=(FONT, 9)).grid(row=2, column=0, sticky="w", padx=6, pady=5)
    entrada_horas_sueno = tk.Entry(caja_habitos, width=10, font=(FONT, 9))
    entrada_horas_sueno.grid(row=2, column=1, sticky="w", padx=6, pady=5)

    tk.Label(caja_habitos, text="Concentración:", bg=COLORS["surface"], font=(FONT, 9)).grid(row=3, column=0, sticky="w", padx=6, pady=5)
    combo_concentracion = ttk.Combobox(caja_habitos, values=["Bajo", "Medio", "Alto"], width=12, state="readonly")
    combo_concentracion.set("Medio")
    combo_concentracion.grid(row=3, column=1, sticky="w", padx=6, pady=5)

    tk.Label(caja_habitos, text="Dificultad:", bg=COLORS["surface"], font=(FONT, 9)).grid(row=0, column=2, sticky="w", padx=6, pady=5)
    entrada_dificultad = tk.Entry(caja_habitos, width=22, font=(FONT, 9))
    entrada_dificultad.grid(row=0, column=3, sticky="w", padx=6, pady=5)

    tk.Label(caja_habitos, text="Horario:", bg=COLORS["surface"], font=(FONT, 9)).grid(row=1, column=2, sticky="w", padx=6, pady=5)
    entrada_horario = tk.Entry(caja_habitos, width=22, font=(FONT, 9))
    entrada_horario.grid(row=1, column=3, sticky="w", padx=6, pady=5)

    caja_obs = tk.LabelFrame(datos, text="Observaciones del docente", bg=COLORS["surface"], font=(FONT, 9, "bold"), padx=10, pady=8)
    caja_obs.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 8))
    txt_observaciones = tk.Text(caja_obs, height=3, wrap="word", font=(FONT, 9))
    txt_observaciones.pack(fill="x")

    caja_resultado = tk.LabelFrame(datos, text="Resultado generado por sarAI", bg=COLORS["surface"], font=(FONT, 9, "bold"), padx=10, pady=8)
    caja_resultado.grid(row=2, column=0, columnspan=2, sticky="nsew")
    caja_resultado.columnconfigure(0, weight=1)
    caja_resultado.rowconfigure(1, weight=1)

    txt_resultado = tk.Text(caja_resultado, height=6, wrap="word", font=(FONT, 9))
    txt_resultado.grid(row=0, column=0, sticky="ew", pady=(0, 8))

    tabla_plan = ttk.Treeview(caja_resultado, columns=("Dia", "Materia", "Tiempo", "Actividad"), show="headings", height=5)
    tabla_plan.heading("Dia", text="Día")
    tabla_plan.heading("Materia", text="Materia")
    tabla_plan.heading("Tiempo", text="Tiempo")
    tabla_plan.heading("Actividad", text="Actividad")
    tabla_plan.column("Dia", width=80, anchor="center")
    tabla_plan.column("Materia", width=190)
    tabla_plan.column("Tiempo", width=80, anchor="center")
    tabla_plan.column("Actividad", width=500)
    tabla_plan.grid(row=1, column=0, sticky="nsew")

    acciones = tk.Frame(tab_evaluacion, bg=COLORS["bg"])
    acciones.grid(row=2, column=0, sticky="w", padx=10, pady=(0, 10))

    def obtener_id_estudiante_seleccionado():
        seleccion = combo_alumnos.get()
        if not seleccion:
            return None
        return int(seleccion.split(" - ")[0])

    def cargar_estudiantes():
        nonlocal estudiantes_cache
        estudiantes_cache = obtener_estudiantes()
        valores = [f"{est['id_estudiante']} - {est['nombre']} ({est['usuario']})" for est in estudiantes_cache]
        combo_alumnos["values"] = valores
        if valores:
            combo_alumnos.set(valores[0])
            cargar_datos_alumno()

    def limpiar_resultado():
        txt_resultado.delete("1.0", tk.END)
        for item in tabla_plan.get_children():
            tabla_plan.delete(item)

    def limpiar_formulario_evaluacion():
        for entrada in entradas_calificaciones.values():
            entrada.delete(0, tk.END)
        entrada_horas_estudio.delete(0, tk.END)
        entrada_dias_estudio.delete(0, tk.END)
        entrada_horas_sueno.delete(0, tk.END)
        entrada_dificultad.delete(0, tk.END)
        entrada_horario.delete(0, tk.END)
        combo_concentracion.set("Medio")
        txt_observaciones.delete("1.0", tk.END)
        limpiar_resultado()

    def cargar_datos_alumno(event=None):
        id_estudiante = obtener_id_estudiante_seleccionado()
        if not id_estudiante:
            return

        limpiar_formulario_evaluacion()
        calificaciones = obtener_calificaciones_estudiante(id_estudiante)
        habitos = obtener_ultimo_habito(id_estudiante)
        observaciones = obtener_observaciones_estudiante(id_estudiante)

        for materia, nota in calificaciones.items():
            if materia in entradas_calificaciones:
                entradas_calificaciones[materia].insert(0, str(nota))

        entrada_horas_estudio.insert(0, str(habitos.get("horas_estudio_semana", 0)))
        entrada_dias_estudio.insert(0, str(habitos.get("dias_estudio_semana", 0)))
        entrada_horas_sueno.insert(0, str(habitos.get("horas_sueno", 0)))
        combo_concentracion.set(habitos.get("nivel_concentracion", "Medio"))
        entrada_dificultad.insert(0, habitos.get("dificultad_principal", "") or "")
        entrada_horario.insert(0, habitos.get("horario_preferido", "") or "")
        txt_observaciones.insert("1.0", observaciones)

    combo_alumnos.bind("<<ComboboxSelected>>", cargar_datos_alumno)

    def mostrar_resultado_ia(resultado):
        limpiar_resultado()
        texto = (
            f"Promedio: {resultado['promedio']}\n"
            f"Nivel de riesgo: {resultado['nivel_riesgo']}\n"
            f"Materia prioritaria: {resultado['materia_prioritaria']}\n\n"
            "Recomendaciones:\n"
        )
        for recomendacion in resultado["recomendaciones"]:
            texto += f"- {recomendacion}\n"
        txt_resultado.insert("1.0", texto)

        for fila in resultado["plan_estudio"]:
            tabla_plan.insert("", "end", values=(fila["dia"], fila["materia"], f"{fila['tiempo_minutos']} min", fila["actividad"]))

    def guardar_evaluacion():
        id_estudiante = obtener_id_estudiante_seleccionado()
        if not id_estudiante:
            messagebox.showerror("Error", "Selecciona un alumno.")
            return

        calificaciones = {}
        for materia, entrada in entradas_calificaciones.items():
            valor = entrada.get().strip()
            if not nota_valida(valor):
                messagebox.showerror("Error", f"La calificación de {materia} debe estar entre 0 y 10.")
                return
            calificaciones[materia] = float(valor)

        if not numero_decimal_valido(entrada_horas_estudio.get(), 0, 80):
            messagebox.showerror("Error", "Las horas de estudio deben estar entre 0 y 80.")
            return
        if not entero_valido(entrada_dias_estudio.get(), 0, 7):
            messagebox.showerror("Error", "Los días de estudio deben estar entre 0 y 7.")
            return
        if not numero_decimal_valido(entrada_horas_sueno.get(), 0, 24):
            messagebox.showerror("Error", "Las horas de sueño deben estar entre 0 y 24.")
            return

        habitos = {
            "horas_estudio_semana": float(entrada_horas_estudio.get()),
            "dias_estudio_semana": int(entrada_dias_estudio.get()),
            "horas_sueno": float(entrada_horas_sueno.get()),
            "nivel_concentracion": combo_concentracion.get(),
            "dificultad_principal": entrada_dificultad.get().strip(),
            "horario_preferido": entrada_horario.get().strip(),
        }
        observaciones = txt_observaciones.get("1.0", tk.END).strip()

        try:
            guardar_calificaciones(id_estudiante, id_docente, calificaciones, observaciones)
            guardar_habitos(id_estudiante, habitos)
            resultado = generar_recomendaciones(calificaciones, habitos, observaciones)
            guardar_diagnostico_ia(id_estudiante, resultado)
            mostrar_resultado_ia(resultado)
            messagebox.showinfo("Éxito", "Evaluación guardada y recomendación generada.")
        except Error as error:
            messagebox.showerror("Error", f"No se pudo guardar la evaluación.\n\nDetalle: {error}")

    boton(acciones, "Guardar evaluación y generar IA", guardar_evaluacion, color="primary", ancho=30).pack(side="left")
    boton(acciones, "Limpiar", limpiar_formulario_evaluacion, ancho=12).pack(side="left", padx=8)

    cargar_estudiantes()
