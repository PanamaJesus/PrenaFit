import os
import pandas as pd
import joblib
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_squared_error

# --- 1. CONFIGURACIÓN DE ARCHIVOS ---
MODELO_DIR = 'modelos' 
MODELO_NOMBRE = 'random_forest_regresor_rutinas_OPTIMIZADO.pkl' # Nuevo nombre para distinguir
CSV_NOMBRE = 'dataset_regresion_rutinas.csv'
CSV_PATH = os.path.join(os.getcwd(), CSV_NOMBRE) 
MODELO_PATH = os.path.join(os.getcwd(), MODELO_DIR, MODELO_NOMBRE)

FEATURE_COLUMNS = [
    'semana_embarazo', 'sug_semanas_em', 'rbpm_inferior', 'rbpm_superior', 
    'rox_inferior', 'avg_bpm', 'avg_oxigeno', 'alerta_generada', 
    'rutina_esfuerzo_promedio'
]
TARGET_COLUMN = 'score_idoneidad'

# Crear la carpeta 'modelos' si no existe
os.makedirs(MODELO_DIR, exist_ok=True)

# --- 2. CARGA Y PREPARACIÓN DE DATOS ---
try:
    df = pd.read_csv(CSV_PATH)
    # Filtrar solo las columnas necesarias
    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

except FileNotFoundError:
    print(f"❌ Error: El archivo {CSV_NOMBRE} no fue encontrado.")
    exit()

# Dividir para Cross-Validation (usaremos todo el set para Grid Search)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# --- 3. OPTIMIZACIÓN DE HIPERPARÁMETROS (Grid Search) ---
print("\n⚙️ Iniciando Grid Search para optimización de hiperparámetros...")

# Definición del rango de hiperparámetros a probar
param_grid = {
    # Número de árboles: un rango más amplio que 100 por defecto
    'n_estimators': [100, 200, 300], 
    # Profundidad máxima del árbol: importante para evitar sobreajuste
    'max_depth': [5, 10, 15, None], 
    # Mínimo de muestras requeridas para dividir un nodo
    'min_samples_split': [2, 5],
}

# Inicializar el modelo base
rf = RandomForestRegressor(random_state=42, n_jobs=-1)

# Inicializar Grid Search (usando 5-fold cross-validation)
# Scoring: MSE (error cuadrático medio), pero GridSearchCV busca maximizar, así que usamos 'neg_mean_squared_error'
grid_search = GridSearchCV(
    estimator=rf, 
    param_grid=param_grid, 
    cv=5, 
    scoring='neg_mean_squared_error', 
    verbose=2, 
    n_jobs=-1
)

# Ejecutar la búsqueda
grid_search.fit(X_train, y_train)

# --- 4. EVALUACIÓN Y GUARDADO DEL MEJOR MODELO ---
best_rf_model = grid_search.best_estimator_

print("\n--- Resultados de Optimización ---")
print(f"✅ Mejor Score (MSE Negativo): {grid_search.best_score_:.4f}")
print(f"⚙️ Mejores Hiperparámetros: {grid_search.best_params_}")

# Evaluación del mejor modelo en el conjunto de prueba
y_pred = best_rf_model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
print(f"✅ MSE (Error Cuadrático Medio) con modelo optimizado: {mse:.4f}")

# Guardar el modelo optimizado
try:
    joblib.dump(best_rf_model, MODELO_PATH)
    print(f"\n💾 Modelo OPTIMIZADO guardado exitosamente en: {MODELO_PATH}")
    print("¡Listo! Tu modelo está mucho más robusto.")
except Exception as e:
    print(f"❌ Error al guardar el modelo: {e}")