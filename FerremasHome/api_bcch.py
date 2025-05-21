import bcchapi
import pandas as pd
from datetime import datetime, timedelta

def obtener_tipos_cambio():

    siete = bcchapi.Siete("diego321herrera@gmail.com", "Lucholda36")

    hoy = datetime.today().date() #Obtiene la fecha de hoy, sin la hora.
    inicio = (hoy - timedelta(days=7)).strftime("%Y-%m-%d") #Calcula la fecha de hace 7 días
    fin = hoy.strftime("%Y-%m-%d") #Convierte la fecha de hoy (2025-05-21) en string:

    cuadro = siete.cuadro(
        series=[
            "F073.TCO.PRE.Z.D",  # USD
            "F072.CLP.EUR.N.O.D",  # EUR
            "F072.CLP.ARS.N.O.D"   # ARS
        ],
        nombres=["usd", "eur", "ars"],
        desde=inicio,
        hasta=fin,
        frecuencia="D",
        observado={"usd": "last", "eur": "last", "ars": "last"}
    )

    tipo_usd = cuadro["usd"].iloc[-1]
    tipo_eur = cuadro["eur"].iloc[-1]
    tipo_ars = cuadro["ars"].iloc[-1]

    return tipo_usd, tipo_eur, tipo_ars