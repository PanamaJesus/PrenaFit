from rest_framework import serializers
from api.models import *
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password

 
class RolUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolUsuario
        fields = '__all__'

class UsuarioSerializer(serializers.ModelSerializer):
    semana_embarazo = serializers.SerializerMethodField()
    class Meta:
        model = Usuario
        fields = '__all__'

        extra_kwargs = {
            'contrasena': {'write_only': True} 
        }

    def get_semana_embarazo(self, obj):
        return obj.semana_embarazo_actual

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
    ejercicios = CrearRutinaWriteSerializer(many=True)

    class Meta:
        model = Rutina
        fields = ['nombre', 'descripcion', 'sug_semanas_em', 'usuario', 'ejercicios']

    def create(self, validated_data):
        ejercicios_data = validated_data.pop('ejercicios', [])
        rutina = Rutina.objects.create(**validated_data)
        
        for ej in ejercicios_data:
            # CORRECCIÓN: Eliminar la clave 'id' si existe
            if 'id' in ej:
                del ej['id']
            
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

# class RegisterSerializer(serializers.ModelSerializer):
#     imagen_perfil = serializers.PrimaryKeyRelatedField(
#         queryset=Imagen.objects.all(),
#         required=False,
#         allow_null=True
#     )

#     fecha_nacimiento = serializers.DateField(
#         required=False,
#         allow_null=True
#     )
#     class Meta:
#         model = Usuario
#         fields = ['id', 'nombre', 'ap_pat', 'ap_mat', 'correo', 'contrasena',
#                 'rol', 'semana_embarazo', 'estado', 'imagen_perfil', 'fecha_nacimiento']
#         extra_kwargs = {'contrasena': {'write_only': True}}

#     def create(self, validated_data):
#         validated_data['contrasena'] = make_password(validated_data['contrasena'])
#         return Usuario.objects.create(**validated_data)
class RegisterSerializer(serializers.ModelSerializer):
   # 📌 1. CAMPO DE ENTRADA (INPUT): Solo para recibir el valor en el POST
    #     ¡IMPORTANTE! Este campo NO debe llamarse 'semana_embarazo' o entrarás en conflicto.
    semana_inicial_registro = serializers.IntegerField(write_only=True) 

    # 📌 2. CAMPO DE SALIDA (OUTPUT): Este es el que usa la lógica dinámica
    semana_embarazo = serializers.SerializerMethodField()

    imagen_perfil = serializers.PrimaryKeyRelatedField(
        queryset=Imagen.objects.all(),
        required=False,
        allow_null=True
    )

    fecha_nacimiento = serializers.DateField(
        required=False,
        allow_null=True
    )

    # Campos para Rangos
    rbpm_inferior = serializers.IntegerField(required=False, allow_null=True)
    rbpm_superior = serializers.IntegerField(required=False, allow_null=True)
    rox_inferior = serializers.DecimalField(max_digits=5, decimal_places=2, required=False, allow_null=True)
    rox_superior = serializers.DecimalField(max_digits=5, decimal_places=2, required=False, allow_null=True)

    # Campos para ContactoEmerg
    contacto_nombre = serializers.CharField(required=False, allow_null=True)
    contacto_ap_pat = serializers.CharField(max_length=50, required=False, allow_null=True)
    contacto_ap_mat = serializers.CharField(max_length=50, required=False, allow_null=True)
    contacto_correo = serializers.EmailField(required=False, allow_null=True)

    class Meta:
        model = Usuario
        fields = [
            'id', 'nombre', 'ap_pat', 'ap_mat', 'correo', 'contrasena',
            'rol', 'semana_embarazo', 'estado',
            'imagen_perfil', 'fecha_nacimiento',
            # Campos de rangos
            'rbpm_inferior', 'rbpm_superior', 'rox_inferior', 'rox_superior',
            # Campos de contacto de emergencia
            'contacto_nombre', 'contacto_ap_pat', 'contacto_ap_mat', 'contacto_correo',
            'semana_inicial_registro', # <-- Usamos este para el input
            'semana_embarazo',
        ]
        extra_kwargs = {
            'contrasena': {'write_only': True}
        }
    def get_semana_embarazo(self, obj):
        # Asegúrate de que obj.semana_embarazo_actual esté definido en tu modelo Usuario
        return obj.semana_embarazo_actual

    def create(self, validated_data):
        semana_inicial = validated_data.pop('semana_inicial_registro', None)
        
        # 1. Calcular la fecha de inicio del embarazo (FIE)
        fecha_inicio = None
        if semana_inicial is not None and semana_inicial > 0:
            dias_pasados = semana_inicial * 7
            fecha_inicio = date.today() - timedelta(days=dias_pasados)
            
        # 2. Inyectar la FIE en los datos validados
        validated_data['fecha_inicio_embarazo'] = fecha_inicio

        # Extraer los campos que no pertenecen al modelo Usuario
        rbpm_inferior = validated_data.pop('rbpm_inferior', None)
        rbpm_superior = validated_data.pop('rbpm_superior', None)
        rox_inferior = validated_data.pop('rox_inferior', None)
        rox_superior = validated_data.pop('rox_superior', None)
        
        contacto_nombre = validated_data.pop('contacto_nombre', None)
        contacto_ap_pat = validated_data.pop('contacto_ap_pat', None)
        contacto_ap_mat = validated_data.pop('contacto_ap_mat', None)
        contacto_correo = validated_data.pop('contacto_correo', None)

        # Hashear la contraseña
        validated_data['contrasena'] = make_password(validated_data['contrasena'])

        # Crear el usuario
        usuario = Usuario.objects.create(**validated_data)

        # Crear los rangos si se proporcionaron todos los campos necesarios
        if all([rbpm_inferior is not None, rbpm_superior is not None, 
                rox_inferior is not None, rox_superior is not None]):
            Rangos.objects.create(
                usuario=usuario,
                rbpm_inferior=rbpm_inferior,
                rbpm_superior=rbpm_superior,
                rox_inferior=rox_inferior,
                rox_superior=rox_superior
            )

        # Crear el contacto de emergencia si se proporcionaron todos los campos necesarios
        if all([contacto_nombre, contacto_ap_pat, contacto_ap_mat, contacto_correo]):
            ContactoEmerg.objects.create(
                usuario=usuario,
                nombre=contacto_nombre,
                ap_pat=contacto_ap_pat,
                ap_mat=contacto_ap_mat,
                correo=contacto_correo
            )

        return usuario
        

    fecha_nacimiento = serializers.DateField(
        required=False,
        allow_null=True
    )


    


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

##########################################################################
from rest_framework.views import APIView
import random
from rest_framework.response import Response

##############################################################################################################
#Select de lecturas de un usuario
class LecturasDeUnUsuarioSerializer(serializers.ModelSerializer): 
    NombreUsuario = serializers.CharField(source='usuario.nombre', read_only=True)
    SemanasEmb = serializers.IntegerField(source='usuario.semana_embarazo', read_only=True)
    FechaNacimiento = serializers.DateField(source='usuario.fecha_nacimiento', read_only=True)
    lecturabpm = serializers.IntegerField(source='lectura_bpm', read_only=True)
    lecturaox = serializers.DecimalField(
        source='lectura_ox',
        read_only=True,
        max_digits=5,
        decimal_places=2
    )
    Temperatura = serializers.DecimalField(
        source='temperatura',
        read_only=True,
        max_digits=5,
        decimal_places=2
    )
    class Meta:
        model = Lectura
        fields = [
            'NombreUsuario',
            'SemanasEmb',
            'FechaNacimiento',
            'lecturabpm',
            'lecturaox',
            'Temperatura'
        ]
#select de los rangos de un usuario
class RangosDeUnUsuarioSerializer(serializers.ModelSerializer): 
    NombreUsuario = serializers.CharField(source='usuario.nombre', read_only=True)
    LatidosInferiores = serializers.IntegerField(source='rbpm_inferior', read_only=True)
    LatidosSuperiores = serializers.IntegerField(source='rbpm_superior', read_only=True)
    OxigenoInferior = serializers.DecimalField(
        source='rox_inferior',
        read_only=True,
        max_digits=5,
        decimal_places=2
    )
    OxigenoSuperior = serializers.DecimalField(
        source='rox_superior',
        read_only=True,
        max_digits=5,
        decimal_places=2
    )
    class Meta:
        model = Rangos
        fields = [
            'NombreUsuario',
            'LatidosInferiores',
            'LatidosSuperiores',
            'OxigenoInferior',
            'OxigenoSuperior'
        ]
#Las rutinas de un usuario
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
#Ejercicios de una rutina vinculada a un uusario
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
        anim = obj.ejercicio.animacion
        if anim and hasattr(anim, "url"):
            try:
                return anim.url.url
            except:
                return None
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
#post para agregar una rutina al historial de rutinas    
class HistorialRutinaSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistorialRutina
        fields = '__all__'
#########################################################################################
