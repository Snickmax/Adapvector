import sqlite3

def init_db(db_name):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS parametros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            clave TEXT,
            valor TEXT,
            dist TEXT,
            desv TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS resultados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            simulacion INTEGER,
            van REAL,
            precio REAL,
            ley REAL,
            costo_mina REAL,
            costo_planta REAL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS estadisticas (
            indicador TEXT,
            valor REAL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS frecuencia (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            marca_clase REAL,
            freq_abs INTEGER,
            freq_abs_acum INTEGER,
            freq_rel REAL,
            freq_rel_acum REAL,
            freq_rel_acum_inv REAL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS opciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            estrategia TEXT,
            escenario TEXT,
            van_esperado REAL
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS simulacion_estrategias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            simulacion INTEGER,
            van_expandir REAL,
            van_suspender REAL,
            van_vender REAL,
            van_abandonar REAL,
            precio_cobre REAL,
            ley_mineral REAL,
            costo_mina REAL,
            costo_planta REAL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS dominancia_estrategias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            estrategia TEXT,
            veces_gana INTEGER,
            porc_gana REAL,
            veces_pierde INTEGER,
            porc_pierde REAL,
            porc_empate REAL
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS ranking_estrategias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            estrategia TEXT,
            rev REAL,
            capex REAL,
            rev_capex REAL,
            precio_prom REAL,
            ley_prom REAL,
            costo_mina REAL,
            costo_planta REAL,
            costo_total REAL,
            recomendacion TEXT
        )
    """)

    conn.commit()
    conn.close()