from rest_framework import serializers
from api.models import *
from django.contrib.auth import authenticate
 
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
    contador_resenas = serializers.SerializerMethodField()
    class Meta:
        model = Ejercicio
        fields = '__all__'

    def get_contador_resenas(self, obj):
        return obj.resena_set.count()
    
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

class RutinasGuardadosSerializer(serializers.ModelSerializer):
    class Meta:
        model = RutinasGuardados
        fields = '__all__'

class ResenaSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='usuario.nombre', read_only=True)
    ejercicio_id = serializers.PrimaryKeyRelatedField(
        queryset=Ejercicio.objects.all(), source='ejercicio'
    )

    class Meta:
        model = Resena
        fields = ['id', 'usuario', 'usuario_nombre', 'fecha', 'descripcion', 'ejercicio_id']



class EjercicioDetalleSerializer(serializers.ModelSerializer):
    resenas = ResenaSerializer(many=True, read_only=True, source='resena_set')

    class Meta:
        model = Ejercicio
        fields = [
            'id',
            'nombre',
            'descripcion',
            'nivel_esfuerzo',
            'sug_semanas',
            'categoria',
            'resenas'
        ]

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'password', 'edad', 'rol']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = Usuario.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            edad=validated_data.get('edad', None),
            rol=validated_data.get('rol', 'usuario')
        )
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Credenciales incorrectas")
   