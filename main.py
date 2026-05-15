import tkinter as tk
from tkinter import messagebox
from mysql.connector import Error
import threading

from database import inicializar_base_datos, validar_login
from panel_maestro import abrir_panel_maestro
from panel_alumno import abrir_panel_alumno
from ui_styles import COLORS, FONT, configurar_estilos, boton
from config import ARDUINO_CONFIG
from arduino_lcd import ArduinoLCD


def crear_login():
    ventana = tk.Tk()
    ventana.title("Inicio de Sesión - sarAI")
    ventana.geometry("340x330")
    ventana.resizable(False, False)
    configurar_estilos(ventana)

    arduino = ArduinoLCD(
        puerto=ARDUINO_CONFIG["port"],
        baudrate=ARDUINO_CONFIG["baudrate"],
        activo=ARDUINO_CONFIG["enabled"],
    )

    sistema_listo = {"valor": False}

    def cerrar_aplicacion():
        arduino.enviar("CERRAR")
        arduino.cerrar()
        ventana.destroy()

    ventana.protocol("WM_DELETE_WINDOW", cerrar_aplicacion)

    # Contenedor principal
    frame = tk.Frame(ventana, bg=COLORS["bg"])
    frame.pack(fill="both", expand=True, padx=20, pady=18)

    tk.Label(frame, text="sarAI", font=(FONT, 18, "bold"), bg=COLORS["bg"], fg=COLORS["text"]).pack(pady=(0, 4))
    tk.Label(frame, text="Sistema académico", font=(FONT, 9), bg=COLORS["bg"], fg=COLORS["muted"]).pack(pady=(0, 12))

    formulario = tk.LabelFrame(frame, text="Acceso", bg=COLORS["surface"], font=(FONT, 9, "bold"), padx=12, pady=10)
    formulario.pack(fill="x")

    tk.Label(formulario, text="Usuario:", bg=COLORS["surface"], font=(FONT, 9)).grid(row=0, column=0, sticky="w", pady=5)
    txt_usuario = tk.Entry(formulario, width=24, font=(FONT, 9))
    txt_usuario.grid(row=0, column=1, padx=(10, 0), pady=5)

    tk.Label(formulario, text="Contraseña:", bg=COLORS["surface"], font=(FONT, 9)).grid(row=1, column=0, sticky="w", pady=5)
    txt_contrasena = tk.Entry(formulario, width=24, show="*", font=(FONT, 9))
    txt_contrasena.grid(row=1, column=1, padx=(10, 0), pady=5)

    lbl_estado = tk.Label(
        frame,
        text="Preparando conexión con MySQL...",
        bg=COLORS["bg"],
        fg=COLORS["muted"],
        font=(FONT, 8),
        justify="left",
        wraplength=290,
    )
    lbl_estado.pack(anchor="w", pady=(10, 0))

    def iniciar_sesion():
        if not sistema_listo["valor"]:
            messagebox.showwarning("Sistema no listo", "Aún no está lista la conexión con MySQL.")
            return

        usuario = txt_usuario.get().strip()
        contrasena = txt_contrasena.get().strip()

        if not usuario or not contrasena:
            arduino.enviar("ERROR_DATOS")
            messagebox.showerror("Error", "Ingresa usuario y contraseña.")
            return

        try:
            usuario_db = validar_login(usuario, contrasena)
        except Error as error:
            arduino.enviar("ERROR_BD")
            messagebox.showerror("Error", f"No se pudo validar el acceso.\n\nDetalle: {error}")
            return

        if not usuario_db:
            arduino.enviar("ERROR_USUARIO")
            messagebox.showerror("Error", "Usuario o contraseña incorrectos.")
            return

        arduino.enviar(f"OK:{usuario_db['usuario']}")
        txt_contrasena.delete(0, tk.END)
        ventana.withdraw()

        if usuario_db["rol"] == "Maestro":
            abrir_panel_maestro(ventana, usuario_db)
        elif usuario_db["rol"] == "Alumno":
            abrir_panel_alumno(ventana, usuario_db)

    btn_entrar = boton(formulario, "Entrar", iniciar_sesion, color="primary", ancho=18)
    btn_entrar.grid(row=2, column=0, columnspan=2, pady=(12, 2))
    btn_entrar.config(state="disabled")

    def sistema_correcto():
        sistema_listo["valor"] = True
        btn_entrar.config(state="normal")
        lbl_estado.config(text="Sistema listo. Ingresa tus datos.", fg=COLORS["success"])
        txt_usuario.focus()

    def sistema_error(error):
        sistema_listo["valor"] = False
        btn_entrar.config(state="disabled")
        lbl_estado.config(text="No se pudo conectar con MySQL. Revisa config.py y que MySQL esté encendido.", fg=COLORS["danger"])
        arduino.enviar("ERROR_BD")
        messagebox.showerror("Error de base de datos", f"No se pudo preparar la base de datos.\n\nDetalle: {error}")

    def preparar_sistema():
        try:
            arduino.conectar()
            arduino.enviar("LISTO")
            inicializar_base_datos()
            ventana.after(0, sistema_correcto)
        except Exception as error:
            ventana.after(0, lambda error=error: sistema_error(error))

    ventana.bind("<Return>", lambda event: iniciar_sesion())
    threading.Thread(target=preparar_sistema, daemon=True).start()
    ventana.mainloop()


if __name__ == "__main__":
    crear_login()
