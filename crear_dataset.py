import pandas as pd
import numpy as np
import os

# --- 1. CONFIGURACIÓN ---
NUM_SAMPLES = 800 # Número de filas a generar. Un buen número para empezar.
CSV_FILENAME = 'dataset_regresion_rutinas.csv'

FEATURE_COLUMNS = [
    'semana_embarazo', 'sug_semanas_em', 'rbpm_inferior', 'rbpm_superior', 
    'rox_inferior', 'avg_bpm', 'avg_oxigeno', 'alerta_generada', 
    'rutina_esfuerzo_promedio'
]
TARGET_COLUMN = 'score_idoneidad'

# --- 2. FUNCIÓN DE SIMULACIÓN DE SCORE ---
def calculate_score(row):
    """
    Simula la lógica de idoneidad para generar el target (score_idoneidad).
    Esto es crucial para tener ejemplos de score alto (cercano a 1.0).
    """
    score = 1.0  # Empezamos con el score máximo

    # PENALIZACIONES BASADAS EN SALUD:
    # 1. Penalización fuerte si hay alerta activa (alerta_generada = 1)
    if row['alerta_generada'] == 1:
        score -= 0.6
    
    # 2. Penalización si el BPM promedio está fuera de los límites
    if row['avg_bpm'] > row['rbpm_superior'] + 5 or row['avg_bpm'] < row['rbpm_inferior'] - 5:
        score -= 0.4
    
    # PENALIZACIONES BASADAS EN RUTINA:
    # 3. Penalización si la rutina sugerida no coincide con la semana actual
    semana_diff = np.abs(row['semana_embarazo'] - row['sug_semanas_em'])
    score -= semana_diff * 0.05
    
    # 4. Penalización si el esfuerzo de la rutina es muy alto
    score -= (row['rutina_esfuerzo_promedio'] / 5.0) * 0.2
    
    # Asegurar que el score esté entre 0.0 y 1.0
    score = np.clip(score, 0.0, 1.0)
    
    # Añadir un pequeño ruido para que no sean valores perfectos
    score = score - np.random.uniform(0.0, 0.1)
    
    return np.clip(score, 0.0, 1.0)


# --- 3. GENERACIÓN DE DATOS ---
print(f"Generando {NUM_SAMPLES} muestras...")

data = pd.DataFrame()

# Generar Features con distribución realista
data['semana_embarazo'] = np.random.randint(5, 40, NUM_SAMPLES)
data['sug_semanas_em'] = np.random.randint(5, 40, NUM_SAMPLES)
data['rbpm_inferior'] = np.random.uniform(65, 75, NUM_SAMPLES).round(1)
data['rbpm_superior'] = np.random.uniform(95, 115, NUM_SAMPLES).round(1)
data['rox_inferior'] = np.random.uniform(93.0, 96.0, NUM_SAMPLES).round(1)
data['avg_bpm'] = np.random.uniform(70, 130, NUM_SAMPLES).round(1)
data['avg_oxigeno'] = np.random.uniform(94.0, 100.0, NUM_SAMPLES).round(1)
data['alerta_generada'] = np.random.choice([0, 1], NUM_SAMPLES, p=[0.8, 0.2]) # 80% sin alerta
data['rutina_esfuerzo_promedio'] = np.random.uniform(1.0, 5.0, NUM_SAMPLES).round(1)

# Calcular la Columna Target (score_idoneidad)
data[TARGET_COLUMN] = data.apply(calculate_score, axis=1).round(3)


# --- 4. GUARDAR CSV ---
try:
    data.to_csv(CSV_FILENAME, index=False)
    print(f"✅ Dataset creado exitosamente: {CSV_FILENAME}")
    print(f"Número de scores altos (>0.7): {len(data[data[TARGET_COLUMN] > 0.7])}")
    print(f"Ahora puedes ejecutar 'python entrenar_modelo.py'.")

except Exception as e:
    print(f"❌ Error al guardar el archivo: {e}")