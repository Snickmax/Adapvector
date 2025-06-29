import unicodedata
import os
import random

def normalizar_parametro(texto):
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
    texto = texto.replace(" ", "_")
    return texto

def get_new_db_filename():
    instance_path = os.path.join(os.getcwd(), 'db')
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
    
    existing = [f for f in os.listdir(instance_path) if f.startswith("simulacion_") and f.endswith(".db")]
    nums = [int(f.replace("simulacion_", "").replace(".db", "")) for f in existing if f.replace("simulacion_", "").replace(".db", "").isdigit()]
    next_num = max(nums) + 1 if nums else 1
    return os.path.join(instance_path, f"simulacion_{next_num}.db")

def generar_valor_aleatorio(valor, dist, desv):
    if dist == "NORMAL":
        return random.gauss(valor, desv)
    elif dist == "LOG-NORMAL":
        mu = valor
        sigma = desv
        return random.lognormvariate(mu, sigma)
    else:
        return valor