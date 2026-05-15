import tkinter as tk
from tkinter import ttk

FONT = "Segoe UI"

COLORS = {
    "bg": "#FFFFFF",
    "surface": "#FFFFFF",
    "surface_alt": "#F2F2F2",
    "border": "#BDBDBD",
    "text": "#222222",
    "muted": "#555555",
    "primary": "#1F4E79",
    "success": "#2E7D32",
    "danger": "#B00020",
    "warning": "#8A5A00",
}


def configurar_estilos(root=None):
    if root is not None:
        root.configure(bg=COLORS["bg"])

    style = ttk.Style()
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure("TNotebook", background=COLORS["bg"])
    style.configure("TNotebook.Tab", padding=(8, 4), font=(FONT, 9))

    style.configure(
        "Treeview",
        font=(FONT, 9),
        rowheight=24,
        background=COLORS["surface"],
        fieldbackground=COLORS["surface"],
        foreground=COLORS["text"],
    )
    style.configure("Treeview.Heading", font=(FONT, 9, "bold"))


def boton(parent, texto, comando, color="normal", ancho=None):
    """Botón sencillo de Tkinter."""
    if color == "primary":
        return tk.Button(parent, text=texto, command=comando, width=ancho, bg=COLORS["primary"], fg="white", font=(FONT, 9))
    if color == "danger":
        return tk.Button(parent, text=texto, command=comando, width=ancho, bg=COLORS["danger"], fg="white", font=(FONT, 9))
    if color == "success":
        return tk.Button(parent, text=texto, command=comando, width=ancho, bg=COLORS["success"], fg="white", font=(FONT, 9))
    return tk.Button(parent, text=texto, command=comando, width=ancho, font=(FONT, 9))
