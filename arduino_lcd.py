import time

try:
    import serial
except ImportError:
    serial = None


class ArduinoLCD:
    def __init__(self, puerto="COM8", baudrate=9600, activo=True):
        self.puerto = puerto
        self.baudrate = baudrate
        self.activo = activo
        self.conexion = None

    def conectar(self):
        if not self.activo:
            return False

        if serial is None:
            print("pyserial no está instalado. Ejecuta: pip install pyserial")
            return False

        try:
            self.conexion = serial.Serial(self.puerto, self.baudrate, timeout=1)
            # Algunos Arduino se reinician al abrir el puerto serial.
            time.sleep(4)
            return True
        except Exception as error:
            print(f"No se pudo conectar con Arduino en {self.puerto}: {error}")
            self.conexion = None
            return False

    def enviar(self, mensaje):
        if not self.activo:
            return

        try:
            if self.conexion and self.conexion.is_open:
                self.conexion.write((mensaje + "\n").encode("utf-8"))
                self.conexion.flush()
                print(f"Enviado a Arduino: {mensaje}")
        except Exception as error:
            print(f"No se pudo enviar mensaje al Arduino: {error}")

    def cerrar(self):
        try:
            if self.conexion and self.conexion.is_open:
                self.conexion.close()
        except Exception as error:
            print(f"No se pudo cerrar la conexión con Arduino: {error}")
