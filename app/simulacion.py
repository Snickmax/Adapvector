import sqlite3
from .helpers import generar_valor_aleatorio
from .analisis import (
    calcular_estadisticas,
    generar_tabla_frecuencia_y_guardar,
    evaluar_opciones_reales,
    analisis_comparativo_estrategico,
    analisis_frecuencia_dominancia,
    ranking_estrategias
)

def correr_simulacion_y_guardar(db_name):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    def obtener_param(clave_base):
        c.execute("SELECT valor, dist, desv FROM parametros WHERE clave = ?", (clave_base,))
        row = c.fetchone()
        if row:
            valor, dist, desv = row
            valor = float(valor) if valor else 0
            desv = float(desv) if desv else 0
            return valor, dist, desv
        return 0, '', 0

    precio_cobre, dist_precio, desv_precio = obtener_param("Precio_esperado_del_cobre")
    ley, dist_ley, desv_ley = obtener_param("Ley_del_mineral")
    costo_mina, dist_mina, desv_mina = obtener_param("Costo_mina")
    costo_planta, dist_planta, desv_planta = obtener_param("Costo_planta")
    produccion, _, _ = obtener_param("Produccion_mina_anual")
    recuperacion, _, _ = obtener_param("Recuperacion_metalurgica")
    costos_fijos, _, _ = obtener_param("Costos_fijos_anuales")
    tasa_descuento, _, _ = obtener_param("Tasa_de_descuento")
    horizonte, _, _ = obtener_param("Horizonte_del_proyecto")
    n_sim, _, _ = obtener_param("Numero_de_simulaciones")

    tasa_descuento /= 100
    tasa_factor = 1 / ((1 + tasa_descuento) ** horizonte) if horizonte > 0 else 1

    van_list = []
    for i in range(1, int(n_sim) + 1):
        p = generar_valor_aleatorio(precio_cobre, dist_precio, desv_precio)
        l = generar_valor_aleatorio(ley, dist_ley, desv_ley)
        cm = generar_valor_aleatorio(costo_mina, dist_mina, desv_mina)
        cp = generar_valor_aleatorio(costo_planta, dist_planta, desv_planta)

        ingreso = produccion * l * recuperacion * p * 2204.62
        costo_total = cm * produccion + cp * produccion + costos_fijos
        flujo = ingreso - costo_total
        van = flujo * tasa_factor
        van_list.append(van)

        c.execute("INSERT INTO resultados (simulacion, van, precio, ley, costo_mina, costo_planta) VALUES (?, ?, ?, ?, ?, ?)",
                  (i, van, p, l, cm, cp))

    resumen = calcular_estadisticas(van_list)
    for k, v in resumen.items():
        c.execute("INSERT INTO estadisticas (indicador, valor) VALUES (?, ?)", (k, v))

    conn.commit()
    conn.close()

    tabla_frec = generar_tabla_frecuencia_y_guardar(db_name)
    opciones = evaluar_opciones_reales(db_name)
    analisis = analisis_comparativo_estrategico(db_name)
    simular_opciones_estrategicas(db_name)
    dominancia = analisis_frecuencia_dominancia(db_name)
    ranking = ranking_estrategias(db_name)

    return resumen, tabla_frec, opciones, analisis, dominancia, ranking


def get_param_dist(cursor, clave):
    row = cursor.execute("SELECT valor, dist, desv FROM parametros WHERE clave=?", (clave,)).fetchone()
    if row:
        valor = float(row[0]) if row[0] else 0
        dist = row[1] if row[1] else ''
        desv = float(row[2]) if row[2] else 0
        return valor, dist, desv
    return 0, '', 0

def simular_opciones_estrategicas(db_name):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    # Borra simulaciones previas
    c.execute("DELETE FROM simulacion_estrategias")

    # Obtener parámetros necesarios
    def get(clave): 
        row = c.execute("SELECT valor FROM parametros WHERE clave=?", (clave,)).fetchone()
        return float(row[0]) if row else 0

    tasa = get("Tasa_de_descuento") / 100
    añoD = int(get("Ano_decision_estrategica"))
    añosE = int(get("Anos_de_expansion"))
    añosS = int(get("Anos_de_suspension"))
    hor = int(get("Horizonte_del_proyecto"))
    tVenta = get("Valor_de_venta_proyectado")
    capex = get("Capex_de_expansion")
    costoS = get("Costo_por_suspender")
    cierre = get("Costos_de_cierre")
    produccion = get("Produccion_mina_anual")
    recuperacion = get("Recuperacion_metalurgica")
    costosFijos = get("Costos_fijos_anuales")
    nSim = int(get("Numero_de_simulaciones"))

    precio_base, dist_precio, desv_precio = get_param_dist(c, "Precio_esperado_del_cobre")
    ley_base, dist_ley, desv_ley = get_param_dist(c, "Ley_del_mineral")
    costo_mina_base, dist_cm, desv_cm = get_param_dist(c, "Costo_mina")
    costo_planta_base, dist_cp, desv_cp = get_param_dist(c, "Costo_planta")

    for i in range(1, nSim + 1):
        rndPrecio = generar_valor_aleatorio(precio_base, dist_precio, desv_precio)
        rndLey = generar_valor_aleatorio(ley_base, dist_ley, desv_ley)
        rndCM = generar_valor_aleatorio(costo_mina_base, dist_cm, desv_cm)
        rndCP = generar_valor_aleatorio(costo_planta_base, dist_cp, desv_cp)

        ingreso = produccion * rndLey * recuperacion * rndPrecio * 2204.62
        costo_total = (rndCM + rndCP) * produccion + costosFijos
        flujo = ingreso - costo_total

        van_expandir = -capex / ((1 + tasa) ** añoD) + flujo * (1 - (1 + tasa) ** -añosE) / tasa / ((1 + tasa) ** añoD)

        añosResto = hor - añoD - añosS
        if añosResto > 0:
            van_suspender = -costoS / ((1 + tasa) ** añoD) + flujo * (1 - (1 + tasa) ** -añosResto) / tasa / ((1 + tasa) ** (añoD + añosS))
        else:
            van_suspender = -costoS / ((1 + tasa) ** añoD)

        van_vender = tVenta / ((1 + tasa) ** añoD)
        van_abandonar = -cierre / ((1 + tasa) ** añoD)

        c.execute("""
            INSERT INTO simulacion_estrategias (simulacion, van_expandir, van_suspender, van_vender, van_abandonar,
                                                precio_cobre, ley_mineral, costo_mina, costo_planta)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (i, van_expandir, van_suspender, van_vender, van_abandonar,
              rndPrecio, rndLey, rndCM, rndCP))

    conn.commit()
    conn.close()