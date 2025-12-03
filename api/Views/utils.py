import joblib
import os
from django.conf import settings

# --- Configuración del Modelo ---
MODELO_PATH = os.path.join(settings.BASE_DIR, 'modelos', 'random_forest_regresor_rutinas_OPTIMIZADO.pkl')
MODELO_RF = None

FEATURE_COLUMNS = [
    'semana_embarazo', 'sug_semanas_em', 'rbpm_inferior', 'rbpm_superior', 
    'rox_inferior', 'avg_bpm', 'avg_oxigeno', 'alerta_generada', 
    'rutina_esfuerzo_promedio'
]

# --- Carga del Modelo ---
try:
    MODELO_RF = joblib.load(MODELO_PATH)
    print("✅ Modelo Random Forest V2 cargado exitosamente.")
except Exception as e:
    print(f"❌ ERROR: Fallo al cargar el modelo de recomendación: {e}")

def get_ml_model_context():
    """Retorna el modelo cargado y las columnas esperadas para usar en views.py."""
    return MODELO_RF, FEATURE_COLUMNS