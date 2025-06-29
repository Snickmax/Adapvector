import sqlite3
import statistics

def analisis_frecuencia_dominancia(db_name):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    # Borra resultados previos
    c.execute("DELETE FROM dominancia_estrategias")

    # Obtén los datos de simulación
    c.execute("""
        SELECT van_expandir, van_suspender, van_vender, van_abandonar
        FROM simulacion_estrategias
    """)
    rows = c.fetchall()
    total = len(rows)
    if total == 0:
        conn.close()
        return []

    estrategias = ["Expandir", "Suspender", "Vender", "Abandonar"]
    n = len(estrategias)
    counts = [0] * n
    perdidas = [0] * n
    empates = [0] * n

    for row in rows:
        vals = [v if v is not None else float('-inf') for v in row]
        max_val = max(vals)
        if max_val == float('-inf'):
            continue  # ignora fila inválida
        ganadores = [i for i, v in enumerate(vals) if v == max_val]
        for i in range(n):
            if vals[i] == max_val:
                if len(ganadores) == 1:
                    counts[i] += 1
                else:
                    empates[i] += 1
            else:
                perdidas[i] += 1

    resultados = []
    for i in range(n):
        porc_gana = counts[i] / total
        porc_pierde = perdidas[i] / total
        porc_empate = empates[i] / total
        c.execute("""
            INSERT INTO dominancia_estrategias 
            (estrategia, veces_gana, porc_gana, veces_pierde, porc_pierde, porc_empate)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (estrategias[i], counts[i], porc_gana, perdidas[i], porc_pierde, porc_empate))
        resultados.append({
            "estrategia": estrategias[i],
            "veces_gana": counts[i],
            "porc_gana": porc_gana,
            "veces_pierde": perdidas[i],
            "porc_pierde": porc_pierde,
            "porc_empate": porc_empate
        })

    conn.commit()
    conn.close()
    return resultados

def calcular_estadisticas(vans):
    vans_sorted = sorted(vans)
    n = len(vans)
    media = statistics.mean(vans)
    mediana = statistics.median(vans)
    desv = statistics.stdev(vans)
    varianza = statistics.variance(vans)
    cv = desv / media if media != 0 else 0
    rango = max(vans) - min(vans)
    iqr = statistics.median_high(vans_sorted[n//4*3:]) - statistics.median_low(vans_sorted[:n//4])
    var_5 = vans_sorted[int(0.05 * n)]
    cvar_5 = sum(v for v in vans if v <= var_5) / len([v for v in vans if v <= var_5])
    prob_perdida = len([v for v in vans if v < 0]) / n
    prob_meta = len([v for v in vans if v > 50000000]) / n

    return {
        "Media": media,
        "Mediana": mediana,
        "Máximo": max(vans),
        "Mínimo": min(vans),
        "Rango": rango,
        "Observaciones": n,
        "Desviacion": desv,
        "Varianza": varianza,
        "CoefVariacion": cv,
        "IQR": iqr,
        "VaR_5": var_5,
        "CVaR_5": cvar_5,
        "ProbPerdida": prob_perdida,
        "ProbMeta": prob_meta,
        "RentAjustada": media / desv if desv != 0 else 0,
        "P10": vans_sorted[int(0.10 * n)],
        "P50 (Mediana)": mediana,
        "P90": vans_sorted[int(0.90 * n)]
    }
    
def generar_tabla_frecuencia_y_guardar(db_name, numero_intervalos=100):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("SELECT van FROM resultados")
    datos = [row[0] for row in c.fetchall()]
    total_obs = len(datos)
    if total_obs == 0:
        conn.close()
        return []
    minimo_van = min(datos)
    maximo_van = max(datos)
    rango_total = maximo_van - minimo_van
    ancho_intervalo = rango_total / numero_intervalos
    freq_abs = [0] * numero_intervalos
    resultados_frec = []
    for van in datos:
        idx = min(int((van - minimo_van) / ancho_intervalo), numero_intervalos - 1)
        freq_abs[idx] += 1
    acum_abs = 0
    for i in range(numero_intervalos):
        marca = minimo_van + (i + 0.5) * ancho_intervalo
        acum_abs += freq_abs[i]
        rel = freq_abs[i] / total_obs
        rel_acum = acum_abs / total_obs
        rel_acum_inv = 1 - rel_acum
        c.execute("""
            INSERT INTO frecuencia (marca_clase, freq_abs, freq_abs_acum, freq_rel, freq_rel_acum, freq_rel_acum_inv)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (marca, freq_abs[i], acum_abs, rel, rel_acum, rel_acum_inv))
        resultados_frec.append({
            "marca_clase": marca,
            "freq_abs": freq_abs[i],
            "freq_abs_acum": acum_abs,
            "freq_rel": rel,
            "freq_rel_acum": rel_acum,
            "freq_rel_acum_inv": rel_acum_inv
        })
    conn.commit()
    conn.close()
    return resultados_frec

def evaluar_opciones_reales(db_name):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("DELETE FROM opciones")
    p10 = c.execute("SELECT valor FROM estadisticas WHERE indicador = 'P10'").fetchone()[0]
    p50 = c.execute("SELECT valor FROM estadisticas WHERE indicador = 'P50 (Mediana)'").fetchone()[0]
    p90 = c.execute("SELECT valor FROM estadisticas WHERE indicador = 'P90'").fetchone()[0]
    def get(clave): 
        row = c.execute("SELECT valor FROM parametros WHERE clave=?", (clave,)).fetchone()
        return float(row[0]) if row else 0
    tasa = get("Tasa_de_descuento") / 100
    tVenta = get("Valor_de_venta_proyectado")
    capex = get("Capex_de_expansion")
    añosE = get("Anos_de_expansion")
    añosS = get("Anos_de_suspension")
    costoS = get("Costo_por_suspender")
    añoD = get("Ano_decision_estrategica")
    cierre = get("Costos_de_cierre")
    hor = get("Horizonte_del_proyecto")
    resultados = []
    for flujo_van, esc_txt in [ (p10, "P10 (Pesimista)"), (p50, "P50 (Base)"), (p90, "P90 (Optimista)")]:
        flujo_anual = flujo_van / ((1 - (1 + tasa) ** -hor) / tasa) if tasa != 0 else flujo_van / hor
        van_expandir = -capex / ((1 + tasa) ** añoD) + flujo_anual * (1 - (1 + tasa) ** -añosE) / tasa / ((1 + tasa) ** añoD)
        van_suspender = -costoS / ((1 + tasa) ** añoD)
        años_resto = hor - añoD - añosS
        if años_resto > 0:
            van_suspender += flujo_anual * (1 - (1 + tasa) ** -años_resto) / tasa / ((1 + tasa) ** (añoD + añosS))
        van_vender = tVenta / ((1 + tasa) ** añoD)
        van_abandonar = -cierre / ((1 + tasa) ** añoD)
        for estrategia, val in [
            ("Expandir", van_expandir),
            ("Suspender", van_suspender),
            ("Vender", van_vender),
            ("Abandonar", van_abandonar)
        ]:
            c.execute("INSERT INTO opciones (estrategia, escenario, van_esperado) VALUES (?, ?, ?)", (estrategia, esc_txt, val))
            resultados.append({"estrategia": estrategia, "escenario": esc_txt, "van_esperado": val})
    conn.commit()
    conn.close()
    return resultados

def analisis_comparativo_estrategico(db_name):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS analisis_estrategico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT,
            escenario TEXT,
            estrategia TEXT,
            valor REAL,
            capex REAL,
            ratio REAL,
            segundo TEXT,
            diferencia REAL,
            extra TEXT
        )

    """)

    c.execute("DELETE FROM analisis_estrategico")

    c.execute("SELECT estrategia, escenario, van_esperado FROM opciones")
    rows = c.fetchall()

    if not rows:
        conn.close()
        return []

    escenarios = ["P10 (Pesimista)", "P50 (Base)", "P90 (Optimista)"]
    estrategias = ["Expandir", "Suspender", "Vender", "Abandonar"]
    dict_van = {f"{e}|{s}": v for e, s, v in rows}
    resultado_final = []

    for esc in escenarios:
        ranking = {e: dict_van.get(f"{e}|{esc}", float('-inf')) for e in estrategias}
        ordenado = sorted(ranking.items(), key=lambda x: x[1], reverse=True)
        if len(ordenado) >= 2:
            mejor, mejor_van = ordenado[0]
            segundo, segundo_van = ordenado[1]
            diferencia = mejor_van - segundo_van
            c.execute("""
                INSERT INTO analisis_estrategico (tipo, escenario, estrategia, valor, capex, ratio, segundo, diferencia, extra)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, ("ranking", esc, mejor, mejor_van, None, None, segundo, diferencia, None))

            resultado_final.append({
                "tipo": "ranking",
                "escenario": esc,
                "estrategia": mejor,
                "valor": mejor_van,
                "capex": None,
                "ratio": None,
                "segundo": segundo,
                "diferencia": diferencia,
                "extra": None
            })


    van_aband = dict_van.get("Abandonar|P50 (Base)", 0)
    for e in estrategias:
        van_p50 = dict_van.get(f"{e}|P50 (Base)", 0)
        impacto = van_p50 - van_aband
        c.execute("""
            INSERT INTO analisis_estrategico (tipo, escenario, estrategia, valor, capex, ratio, extra)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ("impacto", "P50 (Base)", e, impacto, None, None, ""))
        resultado_final.append({
            "tipo": "impacto",
            "escenario": "P50 (Base)",
            "estrategia": e,
            "valor": impacto
        })

    def get_param(clave):
        row = c.execute("SELECT valor FROM parametros WHERE clave = ?", (clave,)).fetchone()
        return float(row[0]) if row else 0

    capex_dict = {
        "Expandir": get_param("Capex_de_expansion"),
        "Suspender": get_param("Costo_por_suspender"),
        "Vender": 0,
        "Abandonar": 0
    }

    for e in estrategias:
        v10 = dict_van.get(f"{e}|P10 (Pesimista)", 0)
        v50 = dict_van.get(f"{e}|P50 (Base)", 0)
        v90 = dict_van.get(f"{e}|P90 (Optimista)", 0)
        rev = 0.25 * v10 + 0.5 * v50 + 0.25 * v90
        capex = capex_dict[e]
        if capex:
            ratio = rev / capex
        else:
            ratio = 8 if rev > 0 else -8 if rev < 0 else None
        c.execute("""
            INSERT INTO analisis_estrategico (tipo, escenario, estrategia, valor, capex, ratio, extra)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ("rev", "", e, rev, capex, ratio, ""))
        resultado_final.append({
            "tipo": "rev",
            "escenario": "",
            "estrategia": e,
            "valor": rev,
            "capex": capex,
            "ratio": ratio
        })

    conn.commit()
    conn.close()
    return resultado_final

def ranking_estrategias(db_name):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("DELETE FROM ranking_estrategias")

    # Obtén simulación
    c.execute("""
        SELECT van_expandir, van_suspender, van_vender, van_abandonar,
            precio_cobre, ley_mineral, costo_mina, costo_planta
        FROM simulacion_estrategias
    """)
    rows = c.fetchall()
    if not rows:
        conn.close()
        return []

    n = len(rows)
    estrategias = ["Expandir", "Suspender", "Vender", "Abandonar"]
    suma_van = [0] * 4

    for row in rows:
        for i in range(4):
            suma_van[i] += row[i]

    rev = [s / n for s in suma_van]

    def get_param(clave):
        row = c.execute("SELECT valor FROM parametros WHERE clave=?", (clave,)).fetchone()
        return float(row[0]) if row else 0

    capex_dict = {
        "Expandir": get_param("Capex_de_expansion"),
        "Suspender": get_param("Costo_por_suspender"),
        "Vender": 0.001,  # evita div 0
        "Abandonar": get_param("Costos_de_cierre")
    }

    precio = get_param("Precio_esperado_del_cobre")
    ley = get_param("Ley_del_mineral")
    costo_mina = get_param("Costo_mina")
    costo_planta = get_param("Costo_planta")

    resultados = []
    for i, est in enumerate(estrategias):
        capex = capex_dict[est]
        ratio = rev[i] / capex if capex else 0
        costo_total = costo_mina + costo_planta
        if rev[i] > 0 and ratio > 1:
            recomendacion = "✅ Recomendado en escenarios normales"
        elif rev[i] > 0 and ratio <= 1:
            recomendacion = "⚠️ Solo si el CAPEX es limitado"
        else:
            recomendacion = "❌ Solo en escenarios críticos"

        c.execute("""
            INSERT INTO ranking_estrategias 
            (estrategia, rev, capex, rev_capex, precio_prom, ley_prom, 
             costo_mina, costo_planta, costo_total, recomendacion)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (est, rev[i], capex, ratio, precio, ley, costo_mina, costo_planta, costo_total, recomendacion))

        resultados.append({
            "estrategia": est,
            "rev": rev[i],
            "capex": capex,
            "rev_capex": ratio,
            "precio_prom": precio,
            "ley_prom": ley,
            "costo_mina": costo_mina,
            "costo_planta": costo_planta,
            "costo_total": costo_total,
            "recomendacion": recomendacion
        })

    conn.commit()
    conn.close()
    return resultados