import pandas as pd
import os

CSV_FILENAME = 'dataset_regresion_rutinas.csv'
CSV_PATH = os.path.join(os.getcwd(), CSV_FILENAME) 
TARGET_COLUMN = 'score_idoneidad'

print(f"--- 📊 Verificación de Distribución de Scores en {CSV_FILENAME} ---")

try:
    df = pd.read_csv(CSV_PATH)
    
    if TARGET_COLUMN not in df.columns:
        print(f"❌ ERROR: La columna '{TARGET_COLUMN}' no se encontró en el archivo CSV.")
        exit()
        
    total_filas = len(df)
    
    # 1. Contar valores perfectos (1.0)
    count_perfectos = len(df[df[TARGET_COLUMN] >= 0.999])
    
    # 2. Contar valores altos (cercanos a 1.0)
    count_altos = len(df[df[TARGET_COLUMN] >= 0.8])
    
    # 3. Contar valores muy bajos (cercanos a 0.0)
    count_bajos = len(df[df[TARGET_COLUMN] <= 0.2])
    
    # 4. Estadísticas descriptivas
    stats = df[TARGET_COLUMN].describe().round(3)
    
    print("\n--- RESUMEN ESTADÍSTICO DE 'score_idoneidad' ---")
    print(stats)
    print("\n------------------------------------------------")
    print(f"Total de muestras en el Dataset: {total_filas}")
    print(f"Muestras con Score PERFECTO (>= 0.999): {count_perfectos}")
    print(f"Muestras con Score ALTO (>= 0.8): {count_altos}")
    print(f"Muestras con Score BAJO (<= 0.2): {count_bajos}")
    print("------------------------------------------------\n")

    if count_perfectos == 0:
        print("🚨 ALERTA: No se encontraron scores de 1.0. Esto debe corregirse manualmente en el CSV para que el modelo pueda predecir alto.")
    elif count_perfectos < (total_filas * 0.05):
        print(f"⚠️ ADVERTENCIA: Solo el {count_perfectos/total_filas * 100:.2f}% de los datos es perfecto. Considera añadir más filas de 1.0.")
    else:
        print("✅ CONCLUSIÓN: El dataset tiene suficientes ejemplos de idoneidad alta. Procede con el reentrenamiento avanzado.")

except FileNotFoundError:
    print(f"❌ ERROR: El archivo {CSV_FILENAME} no fue encontrado. Asegúrate de que el nombre sea correcto.")
except Exception as e:
    print(f"❌ Ocurrió un error al procesar el archivo: {e}")