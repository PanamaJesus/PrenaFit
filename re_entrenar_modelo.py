import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import joblib
import os
import sys

# Definición de rutas y archivos
# Asume que este script se encuentra en el mismo directorio que el CSV y el PKL final.
CSV_FILENAME = 'dataset_regresion_rutinas.csv'
MODEL_FILENAME = 'random_forest_regresor_rutinas_OPTIMIZADO.pkl'

FEATURE_COLUMNS = [
    'semana_embarazo', 'sug_semanas_em', 'rbpm_inferior', 'rbpm_superior',
    'rox_inferior', 'avg_bpm', 'avg_oxigeno', 'alerta_generada',
    'rutina_esfuerzo_promedio'
]
TARGET_COLUMN = 'score_idoneidad'

print("--- Iniciando Re-entrenamiento del Modelo ML ---")

# 1. Carga de datos
try:
    df = pd.read_csv(CSV_FILENAME)
    print(f"Datos cargados desde {CSV_FILENAME}. Filas: {len(df)}")
except FileNotFoundError:
    print(f"ERROR: No se encontró el archivo CSV en la ruta: {CSV_FILENAME}")
    sys.exit(1)

# 2. Preparación de datos (usando las columnas que el modelo espera)
X = df[FEATURE_COLUMNS]
y = df[TARGET_COLUMN]

# División para entrenamiento (aunque re-entrenaremos con gran parte de los datos)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. Entrenamiento del modelo
# Usamos un número razonable de estimadores (100) para un modelo robusto
MODELO_RF = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1, max_depth=10)
print("Re-entrenando RandomForestRegressor...")
MODELO_RF.fit(X_train, y_train)
print("Re-entrenamiento completo.")

# 4. Guardar el modelo (sobrescribiendo el anterior)
try:
    joblib.dump(MODELO_RF, MODEL_FILENAME)
    print(f"\n✅ Modelo guardado exitosamente con la versión actual de Scikit-learn.")
    print(f"Archivo: {MODEL_FILENAME}")
except Exception as e:
    print(f"ERROR al guardar el modelo: {e}")
    sys.exit(1)

print("--- Proceso de Re-entrenamiento finalizado ---")