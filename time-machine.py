from datetime import datetime
from calendar import calendar

def get_month(monthNumber):
    month = {
        1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
        5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
        9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
    }
    return month[monthNumber]

def get_activity(dayNumber):
    activity = {
        1: "Saludé a tres personas con las que casi no hablaba",
        2: "Agradecí a alguien por su apoyo y buen trabajo",
        3: "Compartí un consejo o truco útil con el equipo",
        4: "Aprendí algo nuevo en menos de 10 minutos",
        5: "Revisé un proceso que podía mejorarse",
        6: "Reconocí públicamente el esfuerzo de un compañero",
        7: "Organicé mi espacio de trabajo y mis archivos digitales",
        8: "Usé palabras positivas durante las reuniones",
        9: "Propuse una idea para optimizar una tarea del equipo",
        10: "Leí un artículo breve sobre liderazgo y comunicación",
        11: "Escribí tres cosas que me salieron bien durante la semana",
        12: "Pedí retroalimentación sobre mi desempeño",
        13: "Ayudé a un compañero sin que me lo pidiera",
        14: "Escuché activamente en una reunión, sin interrumpir",
        15: "Dediqué tiempo a aprender una nueva función o herramienta",
        16: "Envié un mensaje de motivación al grupo",
        17: "Hice una pausa consciente para respirar y despejarme",
        18: "Compartí una curiosidad o dato interesante con el equipo",
        19: "Ofrecí apoyo a alguien que estaba sobrecargado",
        20: "Reflexioné sobre un error reciente y lo que aprendí de él",
        21: "Celebré un logro del equipo, aunque fuera pequeño",
        22: "Revisé un documento o código y propuse mejoras",
        23: "Participé activamente en una reunión aportando ideas",
        24: "Propuse un tema para un próximo Chapter",
        25: "Escuché música que me motivó antes de empezar el día",
        26: "Organicé mis prioridades de la semana",
        27: "Reconocí una habilidad valiosa de un compañero",
        28: "Anoté algo nuevo que aprendí ese día",
        29: "Sugerí una dinámica para el siguiente encuentro",
        30: "Cerré mi jornada laboral sin dejar pendientes abiertos",
        31: "Escribí un mensaje a un amigo"
    }
    return activity[dayNumber]

def get_climate(monthNumber):
    climate = {
        "enero": "Ventoso con cielos despejados 🗓️ ☀️",
        "febrero": "Lluvias ligeras y tardes nubladas 🗓️ ",
        "marzo": "Calor seco con brisa cálida 🗓️ 🗓️",
        "abril": "Neblina matutina y sol intermitente 🗓️ 🗓️",
        "mayo": "Lluvias intensas y truenos ocasionales ⛈️",
        "junio": "Soleado con noches frescas ☀️ 🗓️",
        "julio": "Tormentas pasajeras y humedad alta 🗓️ 💧",
        "agosto": "Calor sofocante con vientos fuertes 🗓️🗓️ ",
        "septiembre": "Cielos despejados y temperatura templada 🗓️ ",
        "octubre": "Lluvia fina y mañanas frías 🗓️ ❄️",
        "noviembre": "Días nublados con ráfagas de viento 🗓️ 🗓️",
        "diciembre": "Frío intenso con ocasional llovizna ❄️ 🗓️"
    }
    return climate[monthNumber]

def get_date_and_result(date):
    
    
    days = {
        0: "lunes", 1: "martes", 2: "miércoles", 3: "jueves",
        4: "viernes", 5: "sábado", 6: "domingo"
    }

    dateFormat = datetime.strptime(date, '%d/%m/%Y')
    day = dateFormat.day
    month_num = dateFormat.month
    year = dateFormat.year
    day_week = dateFormat.weekday()
    dateText = f"El dia {days[day_week]} del mes de {get_month(month_num)} {get_activity(day)}, {get_climate(get_month(month_num))} y el año de "

    return dateText

def main():
    fecha_input = input("Ingrese una fecha: ").strip()
        
    get_date_and_result(fecha_input)


if __name__ == "__main__":
    main()