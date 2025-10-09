from rest_framework import serializers
from api.models import *

class RolUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolUsuario
        fields = '__all__'

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = '__all__'

class RangosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rangos
        fields = '__all__'

class TipoLecturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoLectura
        fields = '__all__'

class LecturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lectura
        fields = '__all__'

class TipoAlertaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoAlerta
        fields = '__all__'

class AlertaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alerta
        fields = '__all__'

class AnimacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Animacion
        fields = '__all__'

class EjercicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ejercicio
        fields = '__all__'
    
class RutinaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rutina
        fields = '__all__'

class RutinaEjercicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrearRutina
        fields = '__all__'

class ResenaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resena
        fields = '__all__'  

class retroalimentacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Retroalimentacion
        fields = '__all__'

class ContactoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactoEmerg
        fields = '__all__'

class HistorialSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistorialRutina
        fields = '__all__'

class TipoTemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoTema
        fields = '__all__'

class ContenidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContenidoEducativo
        fields = '__all__'
