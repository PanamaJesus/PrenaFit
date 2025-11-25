from rest_framework import serializers
from api.models import *
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password

 
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

class ImagenesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Imagen
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

class CrearRutinaWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrearRutina
        fields = ['series', 'repeticiones', 'tiempo_seg', 'ejercicio']

class RutinaWriteSerializer(serializers.ModelSerializer):
    ejercicios = CrearRutinaWriteSerializer(many=True)  # ahora writeable

    class Meta:
        model = Rutina
        fields = ['nombre', 'descripcion', 'sug_semanas_em', 'usuario', 'ejercicios']

    def create(self, validated_data):
        ejercicios_data = validated_data.pop('ejercicios', [])
        rutina = Rutina.objects.create(**validated_data)
        for ej in ejercicios_data:
            CrearRutina.objects.create(rutina=rutina, **ej)
        return rutina

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
        fields = ['id', 'nombre', 'ap_pat', 'ap_mat', 'correo', 'contrasena', 'rol']
        extra_kwargs = {'contrasena': {'write_only': True}}

    def create(self, validated_data):
        validated_data['contrasena'] = make_password(validated_data['contrasena'])
        return Usuario.objects.create(**validated_data)


class LoginSerializer(serializers.Serializer):
    correo = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            user = Usuario.objects.get(correo=data['correo'])
        except Usuario.DoesNotExist:
            raise serializers.ValidationError("Usuario no encontrado")

        if not check_password(data['contrasena'], user.password):
            raise serializers.ValidationError("Contraseña incorrecta")

        return user

##############################################################################################################
class RutinasGuardadasUsuarioSerializer(serializers.ModelSerializer): 
    NombreRutina = serializers.CharField(source='rutina.nombre', read_only=True)
    Descripcion = serializers.CharField(source='rutina.descripcion', read_only=True)
    SugSemanas = serializers.IntegerField(source='rutina.sug_semanas_em', read_only=True)
    RutinaId = serializers.IntegerField(source='rutina.id', read_only=True)
    Usuario = serializers.IntegerField(source='usuario.id', read_only=True)

    class Meta:
        model = RutinasGuardados
        fields = [
            'id',
            'fecha_guardado',
            'RutinaId',
            'Usuario',
            'NombreRutina',
            'Descripcion',
            'SugSemanas'
        ]

class EjercicioDetalleSerializer(serializers.ModelSerializer):
    Ejercicio = serializers.CharField(source='ejercicio.nombre', read_only=True)
    Descripcion = serializers.CharField(source='ejercicio.descripcion', read_only=True)
    NivelEsfuerzo = serializers.IntegerField(source='ejercicio.nivel_esfuerzo', read_only=True)
    Series = serializers.IntegerField(source='series', read_only=True)
    Repeticiones = serializers.IntegerField(source='repeticiones', read_only=True)
    TiempoAprox = serializers.IntegerField(source='tiempo_seg', read_only=True)
    AnimacionId = serializers.IntegerField(source='ejercicio.animacion_id', read_only=True)

    Url = serializers.SerializerMethodField()

    def get_Url(self, obj):
        try:
            return obj.ejercicio.animacion.url.url
        except:
            return None

    class Meta:
        model = CrearRutina
        fields = [
            'Ejercicio',
            'Descripcion',
            'NivelEsfuerzo',
            'Series',
            'Repeticiones',
            'TiempoAprox',
            'AnimacionId',
            'Url'
        ]
    
class HistorialRutinaSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistorialRutina
        fields = '__all__'
#########################################################################################
