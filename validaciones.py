import re


def texto_valido(valor):
    valor = str(valor or "").strip()
    if len(valor) < 2:
        return False
    return bool(re.match(r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü\s]+$", valor))


def usuario_valido(valor):
    valor = str(valor or "").strip()
    return bool(re.match(r"^[A-Za-z0-9_.-]{3,30}$", valor))


def contrasena_valida(valor):
    return len(str(valor or "")) >= 4


def nota_valida(valor):
    try:
        nota = float(valor)
        return 0 <= nota <= 10
    except ValueError:
        return False


def numero_decimal_valido(valor, minimo=0, maximo=100):
    try:
        numero = float(valor)
        return minimo <= numero <= maximo
    except ValueError:
        return False


def entero_valido(valor, minimo=0, maximo=100):
    try:
        numero = int(valor)
        return minimo <= numero <= maximo
    except ValueError:
        return False
