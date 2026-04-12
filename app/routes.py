from flask import Blueprint, render_template, request
from .helpers import normalizar_parametro, get_new_db_filename
from .db_utils import init_db
from .simulacion import correr_simulacion_y_guardar
import pandas as pd
import sqlite3

bp = Blueprint('main', __name__)

@bp.route("/", methods=["GET", "POST"])
def index():
    data = {}
    if request.method == "POST":
        action = request.form.get("action")
        if action == "cargar":
            file = request.files.get("file")
            if file and file.filename.endswith((".xls", ".xlsx")):
                try:
                    df = pd.read_excel(file)
                    for _, row in df.iterrows():
                        nombre_original = str(row["Parámetro"]).strip()
                        clave = normalizar_parametro(nombre_original)
                        valor = row.get("Valor Ejemplo", "")
                        dist = row.get("Distribución", "")
                        desv = row.get("Desv. Est.", "")
                        data[f"{clave}_valor"] = "" if pd.isna(valor) else valor
                        data[f"{clave}_dist"] = "" if pd.isna(dist) else dist
                        data[f"{clave}_desv"] = "" if pd.isna(desv) else desv
                except Exception as e:
                    return f"Error leyendo archivo: {e}"
        else:
            db_name = get_new_db_filename()
            init_db(db_name)
            conn = sqlite3.connect(db_name)
            c = conn.cursor()
            for key in request.form:
                if key.endswith("_valor"):
                    base_key = key.replace("_valor", "")
                    valor = request.form.get(key)
                    dist = request.form.get(f"{base_key}_dist", "")
                    desv = request.form.get(f"{base_key}_desv", "")
                    c.execute("INSERT INTO parametros (clave, valor, dist, desv) VALUES (?, ?, ?, ?)", (base_key, valor, dist, desv))
            conn.commit()
            conn.close()
            resumen, tabla_frec, opciones, analisis, dominancia, ranking = correr_simulacion_y_guardar(db_name)
            bd_name = db_name.split("\ ")[-1]
            return render_template("resultados.html", resumen=resumen, tabla_frec=tabla_frec, opciones=opciones, analisis=analisis, dominancia=dominancia, ranking=ranking, db_name=bd_name)

    return render_template("index.html", data=data)