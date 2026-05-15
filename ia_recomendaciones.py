def calcular_promedio(calificaciones):
    if not calificaciones:
        return 0
    return sum(calificaciones.values()) / len(calificaciones)


def obtener_nivel_riesgo(promedio):
    if promedio < 6:
        return "Riesgo alto"
    if promedio < 7:
        return "Riesgo medio"
    if promedio < 8:
        return "Rendimiento regular"
    if promedio < 9:
        return "Buen rendimiento"
    return "Excelente rendimiento"


def obtener_materia_prioritaria(calificaciones):
    if not calificaciones:
        return None, 0
    materia = min(calificaciones, key=calificaciones.get)
    return materia, calificaciones[materia]


def obtener_materias_bajas(calificaciones, limite=7):
    return {materia: nota for materia, nota in calificaciones.items() if nota < limite}


def actividad_por_materia(materia, calificacion):
    materia_lower = materia.lower()

    if "lenguaje" in materia_lower:
        actividad = "Leer un texto corto, subrayar ideas principales y escribir un resumen."
    elif "saberes" in materia_lower or "cient" in materia_lower:
        actividad = "Resolver ejercicios paso a paso y anotar los temas que causan dudas."
    elif "ética" in materia_lower or "etica" in materia_lower or "sociedades" in materia_lower:
        actividad = "Repasar apuntes, hacer un mapa conceptual y escribir una reflexión breve."
    elif "humano" in materia_lower or "comunitario" in materia_lower:
        actividad = "Relacionar el tema con ejemplos de la vida diaria y hacer una actividad práctica."
    else:
        actividad = "Repasar apuntes, resolver ejercicios y escribir dudas para el docente."

    if calificacion < 6:
        return actividad + " Reforzar desde los conceptos básicos."
    if calificacion < 7:
        return actividad + " Enfocarse en los temas donde hubo errores."
    return actividad


def generar_plan_estudio(calificaciones, habitos):
    if not calificaciones:
        return []

    materias_ordenadas = sorted(calificaciones.items(), key=lambda item: item[1])
    materia_prioritaria, calificacion_prioritaria = materias_ordenadas[0]

    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
    plan = []

    for index, dia in enumerate(dias):
        if index in (0, 2, 4) and calificacion_prioritaria < 8:
            materia, calificacion = materia_prioritaria, calificacion_prioritaria
        else:
            materia, calificacion = materias_ordenadas[index % len(materias_ordenadas)]

        if calificacion < 6:
            tiempo = 50
        elif calificacion < 7:
            tiempo = 40
        elif calificacion < 8:
            tiempo = 30
        else:
            tiempo = 25

        horas_estudio = float(habitos.get("horas_estudio_semana") or 0)
        if horas_estudio < 4 and tiempo < 35:
            tiempo = 35

        plan.append({
            "dia": dia,
            "materia": materia,
            "tiempo_minutos": tiempo,
            "actividad": actividad_por_materia(materia, calificacion)
        })

    return plan


def generar_recomendaciones(calificaciones, habitos, observaciones=""):
    promedio = calcular_promedio(calificaciones)
    nivel_riesgo = obtener_nivel_riesgo(promedio)
    materia_prioritaria, calificacion_baja = obtener_materia_prioritaria(calificaciones)
    materias_bajas = obtener_materias_bajas(calificaciones)

    recomendaciones = []

    if not calificaciones:
        return {
            "promedio": 0,
            "nivel_riesgo": "Sin datos",
            "materia_prioritaria": "Sin datos",
            "recomendaciones": [
                "Aún no hay calificaciones registradas. El docente debe capturar las calificaciones para generar una recomendación."
            ],
            "plan_estudio": []
        }

    if promedio < 6:
        recomendaciones.append("Tu promedio indica riesgo académico alto. Necesitas un plan de estudio intensivo y acompañamiento del docente.")
    elif promedio < 7:
        recomendaciones.append("Tu promedio está en riesgo medio. Puedes mejorar si refuerzas tus materias más bajas y estudias de forma constante.")
    elif promedio < 8:
        recomendaciones.append("Tu rendimiento es regular. Vas avanzando, pero todavía puedes fortalecer tus materias con menor calificación.")
    elif promedio < 9:
        recomendaciones.append("Tienes buen rendimiento. Mantén tus hábitos y refuerza los temas donde tengas más dudas.")
    else:
        recomendaciones.append("Tu rendimiento es excelente. Continúa con tus hábitos actuales y realiza repasos para mantener tu nivel.")

    if materias_bajas:
        detalle = ", ".join([f"{materia} ({nota})" for materia, nota in materias_bajas.items()])
        recomendaciones.append(f"Materias que requieren atención: {detalle}.")

    if materia_prioritaria:
        recomendaciones.append(f"Tu materia prioritaria es {materia_prioritaria}, con calificación de {calificacion_baja}.")

    horas_estudio = float(habitos.get("horas_estudio_semana") or 0)
    dias_estudio = int(habitos.get("dias_estudio_semana") or 0)
    horas_sueno = float(habitos.get("horas_sueno") or 0)
    concentracion = str(habitos.get("nivel_concentracion") or "Medio")
    dificultad = str(habitos.get("dificultad_principal") or "").strip()

    if horas_estudio < 4:
        recomendaciones.append("Estudias pocas horas por semana. Se recomienda estudiar al menos 30 minutos diarios.")
    elif horas_estudio < 7:
        recomendaciones.append("Tu tiempo de estudio es aceptable, pero puede mejorar si estudias un poco todos los días.")
    else:
        recomendaciones.append("Tu tiempo de estudio semanal es bueno. Mantén una rutina constante.")

    if dias_estudio < 3:
        recomendaciones.append("Estudias pocos días a la semana. Es mejor estudiar en sesiones cortas pero frecuentes.")
    elif dias_estudio >= 5:
        recomendaciones.append("Tu frecuencia de estudio es buena. Procura alternar materias para evitar saturarte.")

    if horas_sueno and horas_sueno < 7:
        recomendaciones.append("Dormir menos de 7 horas puede afectar tu concentración y memoria. Intenta mejorar tus horarios de descanso.")

    if concentracion == "Bajo":
        recomendaciones.append("Como tu concentración es baja, usa la técnica Pomodoro: 25 minutos de estudio y 5 minutos de descanso.")
    elif concentracion == "Medio":
        recomendaciones.append("Tu concentración es media. Estudia en un lugar ordenado, sin ruido y sin celular cerca.")
    elif concentracion == "Alto":
        recomendaciones.append("Tu concentración es buena. Aprovecha ese punto fuerte para estudiar primero la materia más difícil.")

    if dificultad:
        recomendaciones.append(f"Dificultad principal reportada por el alumno: {dificultad}.")

    if observaciones:
        recomendaciones.append(f"Observación del docente considerada: {observaciones}")

    plan_estudio = generar_plan_estudio(calificaciones, habitos)

    return {
        "promedio": round(promedio, 2),
        "nivel_riesgo": nivel_riesgo,
        "materia_prioritaria": materia_prioritaria or "Sin datos",
        "recomendaciones": recomendaciones,
        "plan_estudio": plan_estudio
    }
