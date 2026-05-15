import hashlib
import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG


MATERIAS_BASE = [
    "Lenguajes",
    "Saberes y Pensamiento Científico",
    "Ética, Naturaleza y Sociedades",
    "De lo Humano y lo Comunitario",
]


def hash_password(contrasena):
    return hashlib.sha256(contrasena.encode("utf-8")).hexdigest()


def obtener_conexion(con_base=True):
    config = DB_CONFIG.copy()
    if not con_base:
        config.pop("database", None)
    return mysql.connector.connect(**config)


def inicializar_base_datos():
    conexion = obtener_conexion(con_base=False)
    cursor = conexion.cursor()
    cursor.execute(
        "CREATE DATABASE IF NOT EXISTS sarai "
        "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
    )
    cursor.close()
    conexion.close()

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    sentencias = [
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id_usuario INT AUTO_INCREMENT PRIMARY KEY,
            usuario VARCHAR(50) NOT NULL UNIQUE,
            contrasena_hash VARCHAR(255) NOT NULL,
            rol ENUM('Maestro', 'Alumno') NOT NULL,
            activo TINYINT(1) NOT NULL DEFAULT 1,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB
        """,
        """
        CREATE TABLE IF NOT EXISTS docentes (
            id_docente INT AUTO_INCREMENT PRIMARY KEY,
            id_usuario INT NOT NULL UNIQUE,
            nombre VARCHAR(100) NOT NULL,
            grado INT NULL,
            grupo VARCHAR(20) NULL,
            FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
                ON DELETE CASCADE ON UPDATE CASCADE
        ) ENGINE=InnoDB
        """,
        """
        CREATE TABLE IF NOT EXISTS estudiantes (
            id_estudiante INT AUTO_INCREMENT PRIMARY KEY,
            id_usuario INT NOT NULL UNIQUE,
            nombre VARCHAR(100) NOT NULL,
            grado INT NOT NULL,
            grupo VARCHAR(20) NOT NULL,
            telefono_tutor VARCHAR(20) NULL,
            FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
                ON DELETE CASCADE ON UPDATE CASCADE
        ) ENGINE=InnoDB
        """,
        """
        CREATE TABLE IF NOT EXISTS materias (
            id_materia INT AUTO_INCREMENT PRIMARY KEY,
            nombre_materia VARCHAR(100) NOT NULL UNIQUE
        ) ENGINE=InnoDB
        """,
        """
        CREATE TABLE IF NOT EXISTS calificaciones (
            id_calificacion INT AUTO_INCREMENT PRIMARY KEY,
            id_estudiante INT NOT NULL,
            id_materia INT NOT NULL,
            id_docente INT NULL,
            calificacion DECIMAL(4,2) NOT NULL,
            observaciones TEXT NULL,
            fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id_estudiante)
                ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (id_materia) REFERENCES materias(id_materia)
                ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (id_docente) REFERENCES docentes(id_docente)
                ON DELETE SET NULL ON UPDATE CASCADE
        ) ENGINE=InnoDB
        """,
        """
        CREATE TABLE IF NOT EXISTS habitos_estudio (
            id_habito INT AUTO_INCREMENT PRIMARY KEY,
            id_estudiante INT NOT NULL,
            horas_estudio_semana DECIMAL(5,2) NOT NULL DEFAULT 0,
            dias_estudio_semana INT NOT NULL DEFAULT 0,
            horas_sueno DECIMAL(4,2) NOT NULL DEFAULT 0,
            nivel_concentracion ENUM('Bajo', 'Medio', 'Alto') NOT NULL DEFAULT 'Medio',
            dificultad_principal VARCHAR(150) NULL,
            horario_preferido VARCHAR(100) NULL,
            fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id_estudiante)
                ON DELETE CASCADE ON UPDATE CASCADE
        ) ENGINE=InnoDB
        """,
        """
        CREATE TABLE IF NOT EXISTS diagnosticos_ia (
            id_diagnostico INT AUTO_INCREMENT PRIMARY KEY,
            id_estudiante INT NOT NULL,
            promedio DECIMAL(4,2) NOT NULL,
            nivel_riesgo VARCHAR(50) NOT NULL,
            materia_prioritaria VARCHAR(100) NOT NULL,
            resumen TEXT NOT NULL,
            fecha_generada DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id_estudiante)
                ON DELETE CASCADE ON UPDATE CASCADE
        ) ENGINE=InnoDB
        """,
        """
        CREATE TABLE IF NOT EXISTS planes_estudio (
            id_plan INT AUTO_INCREMENT PRIMARY KEY,
            id_diagnostico INT NOT NULL,
            dia VARCHAR(20) NOT NULL,
            materia VARCHAR(100) NOT NULL,
            tiempo_minutos INT NOT NULL,
            actividad TEXT NOT NULL,
            FOREIGN KEY (id_diagnostico) REFERENCES diagnosticos_ia(id_diagnostico)
                ON DELETE CASCADE ON UPDATE CASCADE
        ) ENGINE=InnoDB
        """,
    ]

    for sentencia in sentencias:
        cursor.execute(sentencia)

    conexion.commit()

    for materia in MATERIAS_BASE:
        cursor.execute(
            "INSERT IGNORE INTO materias (nombre_materia) VALUES (%s)",
            (materia,)
        )

    cursor.execute("SELECT id_usuario FROM usuarios WHERE usuario = %s", ("admin",))
    admin = cursor.fetchone()
    if not admin:
        cursor.execute(
            "INSERT INTO usuarios (usuario, contrasena_hash, rol) VALUES (%s, %s, %s)",
            ("admin", hash_password("admin123"), "Maestro")
        )
        id_usuario_admin = cursor.lastrowid
        cursor.execute(
            "INSERT INTO docentes (id_usuario, nombre, grado, grupo) VALUES (%s, %s, %s, %s)",
            (id_usuario_admin, "Docente Administrador", 1, "A")
        )

    cursor.execute("SELECT id_usuario FROM usuarios WHERE usuario = %s", ("alumno1",))
    alumno = cursor.fetchone()
    if not alumno:
        cursor.execute(
            "INSERT INTO usuarios (usuario, contrasena_hash, rol) VALUES (%s, %s, %s)",
            ("alumno1", hash_password("alumno123"), "Alumno")
        )
        id_usuario_alumno = cursor.lastrowid
        cursor.execute(
            "INSERT INTO estudiantes (id_usuario, nombre, grado, grupo, telefono_tutor) VALUES (%s, %s, %s, %s, %s)",
            (id_usuario_alumno, "Alumno de prueba", 1, "A", "9610000000")
        )
        id_estudiante = cursor.lastrowid

        cursor.execute("SELECT id_docente FROM docentes LIMIT 1")
        docente = cursor.fetchone()
        id_docente = docente[0] if docente else None

        calificaciones_demo = {
            "Lenguajes": 8.5,
            "Saberes y Pensamiento Científico": 6.2,
            "Ética, Naturaleza y Sociedades": 7.8,
            "De lo Humano y lo Comunitario": 9.0,
        }

        for materia, nota in calificaciones_demo.items():
            cursor.execute("SELECT id_materia FROM materias WHERE nombre_materia = %s", (materia,))
            id_materia = cursor.fetchone()[0]
            cursor.execute(
                """
                INSERT INTO calificaciones
                (id_estudiante, id_materia, id_docente, calificacion, observaciones)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (id_estudiante, id_materia, id_docente, nota, "Datos de ejemplo iniciales.")
            )

        cursor.execute(
            """
            INSERT INTO habitos_estudio
            (id_estudiante, horas_estudio_semana, dias_estudio_semana, horas_sueno, nivel_concentracion, dificultad_principal, horario_preferido)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (id_estudiante, 3, 2, 6.5, "Bajo", "Se distrae con facilidad", "Tarde")
        )

    conexion.commit()
    cursor.close()
    conexion.close()


def validar_login(usuario, contrasena):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT id_usuario, usuario, rol
        FROM usuarios
        WHERE usuario = %s AND contrasena_hash = %s AND activo = 1
        """,
        (usuario, hash_password(contrasena))
    )
    resultado = cursor.fetchone()
    cursor.close()
    conexion.close()
    return resultado


def obtener_docente_por_usuario(id_usuario):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM docentes WHERE id_usuario = %s",
        (id_usuario,)
    )
    resultado = cursor.fetchone()
    cursor.close()
    conexion.close()
    return resultado


def obtener_estudiante_por_usuario(id_usuario):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT e.*, u.usuario
        FROM estudiantes e
        JOIN usuarios u ON u.id_usuario = e.id_usuario
        WHERE e.id_usuario = %s
        """,
        (id_usuario,)
    )
    resultado = cursor.fetchone()
    cursor.close()
    conexion.close()
    return resultado


def obtener_estudiantes():
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT e.id_estudiante, e.nombre, e.grado, e.grupo, e.telefono_tutor, u.usuario
        FROM estudiantes e
        JOIN usuarios u ON u.id_usuario = e.id_usuario
        ORDER BY e.nombre ASC
        """
    )
    resultados = cursor.fetchall()
    cursor.close()
    conexion.close()
    return resultados


def obtener_materias():
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT id_materia, nombre_materia FROM materias ORDER BY id_materia ASC")
    resultados = cursor.fetchall()
    cursor.close()
    conexion.close()
    return resultados


def crear_estudiante(nombre, usuario, contrasena, grado, grupo, telefono_tutor):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    try:
        cursor.execute(
            "INSERT INTO usuarios (usuario, contrasena_hash, rol) VALUES (%s, %s, %s)",
            (usuario, hash_password(contrasena), "Alumno")
        )
        id_usuario = cursor.lastrowid
        cursor.execute(
            """
            INSERT INTO estudiantes (id_usuario, nombre, grado, grupo, telefono_tutor)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (id_usuario, nombre, grado, grupo, telefono_tutor)
        )
        conexion.commit()
        return cursor.lastrowid
    except Error:
        conexion.rollback()
        raise
    finally:
        cursor.close()
        conexion.close()


def guardar_calificaciones(id_estudiante, id_docente, calificaciones, observaciones):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    try:
        cursor.execute("DELETE FROM calificaciones WHERE id_estudiante = %s", (id_estudiante,))
        for nombre_materia, nota in calificaciones.items():
            cursor.execute("SELECT id_materia FROM materias WHERE nombre_materia = %s", (nombre_materia,))
            fila = cursor.fetchone()
            if not fila:
                cursor.execute("INSERT INTO materias (nombre_materia) VALUES (%s)", (nombre_materia,))
                id_materia = cursor.lastrowid
            else:
                id_materia = fila[0]

            cursor.execute(
                """
                INSERT INTO calificaciones
                (id_estudiante, id_materia, id_docente, calificacion, observaciones)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (id_estudiante, id_materia, id_docente, nota, observaciones)
            )

        conexion.commit()
    except Error:
        conexion.rollback()
        raise
    finally:
        cursor.close()
        conexion.close()


def guardar_habitos(id_estudiante, habitos):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO habitos_estudio
            (id_estudiante, horas_estudio_semana, dias_estudio_semana, horas_sueno, nivel_concentracion, dificultad_principal, horario_preferido)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                id_estudiante,
                habitos.get("horas_estudio_semana", 0),
                habitos.get("dias_estudio_semana", 0),
                habitos.get("horas_sueno", 0),
                habitos.get("nivel_concentracion", "Medio"),
                habitos.get("dificultad_principal", ""),
                habitos.get("horario_preferido", "")
            )
        )
        conexion.commit()
    except Error:
        conexion.rollback()
        raise
    finally:
        cursor.close()
        conexion.close()


def obtener_calificaciones_estudiante(id_estudiante):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT m.nombre_materia, c.calificacion, c.observaciones
        FROM calificaciones c
        JOIN materias m ON m.id_materia = c.id_materia
        WHERE c.id_estudiante = %s
        ORDER BY m.id_materia ASC
        """,
        (id_estudiante,)
    )
    filas = cursor.fetchall()
    cursor.close()
    conexion.close()
    return {fila["nombre_materia"]: float(fila["calificacion"]) for fila in filas}


def obtener_observaciones_estudiante(id_estudiante):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT observaciones
        FROM calificaciones
        WHERE id_estudiante = %s AND observaciones IS NOT NULL
        ORDER BY fecha_registro DESC
        LIMIT 1
        """,
        (id_estudiante,)
    )
    fila = cursor.fetchone()
    cursor.close()
    conexion.close()
    return fila["observaciones"] if fila and fila["observaciones"] else ""


def obtener_ultimo_habito(id_estudiante):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT *
        FROM habitos_estudio
        WHERE id_estudiante = %s
        ORDER BY fecha_registro DESC
        LIMIT 1
        """,
        (id_estudiante,)
    )
    fila = cursor.fetchone()
    cursor.close()
    conexion.close()

    if not fila:
        return {
            "horas_estudio_semana": 0,
            "dias_estudio_semana": 0,
            "horas_sueno": 0,
            "nivel_concentracion": "Medio",
            "dificultad_principal": "",
            "horario_preferido": "",
        }

    return fila


def guardar_diagnostico_ia(id_estudiante, resultado):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    try:
        resumen = "\n".join(resultado["recomendaciones"])
        cursor.execute(
            """
            INSERT INTO diagnosticos_ia
            (id_estudiante, promedio, nivel_riesgo, materia_prioritaria, resumen)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                id_estudiante,
                resultado["promedio"],
                resultado["nivel_riesgo"],
                resultado["materia_prioritaria"],
                resumen
            )
        )
        id_diagnostico = cursor.lastrowid

        for fila in resultado["plan_estudio"]:
            cursor.execute(
                """
                INSERT INTO planes_estudio
                (id_diagnostico, dia, materia, tiempo_minutos, actividad)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    id_diagnostico,
                    fila["dia"],
                    fila["materia"],
                    fila["tiempo_minutos"],
                    fila["actividad"]
                )
            )

        conexion.commit()
        return id_diagnostico
    except Error:
        conexion.rollback()
        raise
    finally:
        cursor.close()
        conexion.close()


def obtener_ultimo_diagnostico(id_estudiante):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT *
        FROM diagnosticos_ia
        WHERE id_estudiante = %s
        ORDER BY fecha_generada DESC
        LIMIT 1
        """,
        (id_estudiante,)
    )
    diagnostico = cursor.fetchone()

    if not diagnostico:
        cursor.close()
        conexion.close()
        return None, []

    cursor.execute(
        """
        SELECT dia, materia, tiempo_minutos, actividad
        FROM planes_estudio
        WHERE id_diagnostico = %s
        ORDER BY FIELD(dia, 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo')
        """,
        (diagnostico["id_diagnostico"],)
    )
    plan = cursor.fetchall()
    cursor.close()
    conexion.close()
    return diagnostico, plan
