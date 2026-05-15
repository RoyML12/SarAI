import serial
import time

try:
    arduino = serial.Serial("COM8", 9600, timeout=1)

    time.sleep(4)

    arduino.write("OK:admin\n".encode("utf-8"))
    arduino.flush()

    print("Mensaje enviado al Arduino")

    time.sleep(3)
    arduino.close()

except Exception as e:
    print("Error al conectar con Arduino:")
    print(e)