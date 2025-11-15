from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, viewsets

from api.models import *
from api.db_serializers import *
# nuevas 
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken

class RolUsuarioViewSet(viewsets.ModelViewSet):
    queryset = RolUsuario.objects.all()
    serializer_class = RolUsuarioSerializer

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

class RangosViewSet(viewsets.ModelViewSet):
    queryset = Rangos.objects.all()
    serializer_class = RangosSerializer

class TipoLecturaViewSet(viewsets.ModelViewSet):
    queryset = TipoLectura.objects.all()
    serializer_class = TipoLecturaSerializer

class LecturaViewSet(viewsets.ModelViewSet):
    queryset = Lectura.objects.all()
    serializer_class = LecturaSerializer

class TipoAlertaViewSet(viewsets.ModelViewSet):
    queryset = TipoAlerta.objects.all()
    serializer_class = TipoAlertaSerializer

class AlertaViewSet(viewsets.ModelViewSet):
    queryset = Alerta.objects.all()
    serializer_class = AlertaSerializer

class AnimacionViewSet(viewsets.ModelViewSet):
    queryset = Animacion.objects.all()
    serializer_class = AnimacionSerializer

class EjercicioViewSet(viewsets.ModelViewSet):
    queryset = Ejercicio.objects.all()
    serializer_class = EjercicioSerializer

    #obtener los ejercicios de una categoria 
    @action(detail=False, methods=['get'], url_path='categoria')
    def by_categoria(self, request):
        categoria = request.query_params.get('categoria', None)

        if not categoria:
            return Response({"error": "Debe especificar una categoría como parámetro (?categoria=Cardio)"}, status=400)

        ejercicios = Ejercicio.objects.filter(categoria__iexact=categoria)
        serializer = self.get_serializer(ejercicios, many=True)
        return Response(serializer.data)
    
    #Actualizar un ejercicio por su id
    @action(detail=False, methods=['put'], url_path='actualizar_ejercicio')
    def actualizar_ejercicio(self, request):
        ejercicio_id = request.data.get('id_ejercicio')
        #obtener el id del body
        if not ejercicio_id:
            return Response({'error': 'Debes enviar el campo "id" en el body.'},
                            status=status.HTTP_400_BAD_REQUEST) 
        try:
            #busca el ejercicio por su id
            ejercicio_actulizar = Ejercicio.objects.get(id=ejercicio_id)
        except Ejercicio.DoesNotExist:
            return Response({'error': 'Ejercicio no encontrado.'},
                            status=status.HTTP_404_NOT_FOUND)
        #crear el serializer con los datos nuevos
        serializer = self.get_serializer(ejercicio_actulizar, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #Elimina un ejercicio por su id
    @action(detail=False, methods=['delete'], url_path='eliminar_ejercicio')
    def eliminar_ejercicio(self, request):
        ejercicio_id = request.data.get('id_ejercicio')
        #obtener el id del body
        if not ejercicio_id:
            return Response({'error': 'Debes enviar el campo "id" en el body.'},
                            status=status.HTTP_400_BAD_REQUEST) 
        try:
            #busca el ejercicio por su id
            ejercicio_eliminar= Ejercicio.objects.get(id=ejercicio_id)
        except Ejercicio.DoesNotExist:
            return Response({'error': 'Ejercicio no encontrado.'},
                            status=status.HTTP_404_NOT_FOUND)
        #elimiinar el ejercicio
        ejercicio_eliminar.delete()

        return Response({'mensaje': f'Ejercicio con id {ejercicio_id} eliminado correctamente.'},
                    status=status.HTTP_200_OK)
    
    #Vista detallada de un ejercicio con comentarios
    @action(detail=False, methods=['get'], url_path='vista_detallada_comentarios')
    def vista_detallada_comentarios(self, request):
        ejercicio_id = request.data.get('ejercicio_id')

        if not ejercicio_id:
            return Response({"error": "Debe especificar un ejercicio_id"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            ejercicio = Ejercicio.objects.get(id=ejercicio_id)
        except Ejercicio.DoesNotExist:
            return Response({"error": "Ejercicio no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        ejercicio_serializer = EjercicioDetalleSerializer(ejercicio)

        return Response({
            "ejercicio": ejercicio_serializer.data,
        }, status=status.HTTP_200_OK)
    


class RutinaViewSet(viewsets.ModelViewSet):
    queryset = Rutina.objects.all()
    serializer_class = RutinaSerializer

class RutinaEjercicioViewSet(viewsets.ModelViewSet):
    queryset = CrearRutina.objects.all()
    serializer_class = RutinaEjercicioSerializer

class ResenaViewSet(viewsets.ModelViewSet):
    queryset = Resena.objects.all()
    serializer_class = ResenaSerializer

    #Buscar comentarios de un ejercicio por su id
    @action(detail=False, methods=['post'], url_path='comentarios_ejercicio')
    def comentarios_ejercicio(self, request):
        ejercicio_id = request.data.get('ejercicio_id', None)

        if not ejercicio_id:
            return Response({"error": "Debe especificar un ejercicio_id como parámetro"}, status=400)

        comentarios = Resena.objects.filter(ejercicio__id=ejercicio_id)
        serializer = self.get_serializer(comentarios, many=True)
        return Response(serializer.data)

    #Actualizar un comentario por su id
    @action(detail=False, methods=['put'], url_path='actualizar_comentario')
    def actualizar_comentario(self, request):
        id_comentario = request.data.get('id_comentario')
        #obtener el id del body
        if not id_comentario:
            return Response({'error': 'Debes enviar el campo "id" en el body.'},
                            status=status.HTTP_400_BAD_REQUEST) 
        try:
            #busca el comentario por su id
            comentario_actulizar = Resena.objects.get(id=id_comentario)
        except Ejercicio.DoesNotExist:
            return Response({'error': 'Comentario no encontrado.'},
                            status=status.HTTP_404_NOT_FOUND)
        #crear el serializer con los datos nuevos
        serializer = self.get_serializer(comentario_actulizar, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #Elimina un ejercicio por su id
    @action(detail=False, methods=['delete'], url_path='eliminar_comentario')
    def eliminar_comentario(self, request):
        id_comentario = request.data.get('id_comentario')
        #obtener el id del body
        if not id_comentario:
            return Response({'error': 'Debes enviar el campo "id" en el body.'},
                            status=status.HTTP_400_BAD_REQUEST) 
        try:
            #busca el comentario por su id
            comentario_eliminar= Resena.objects.get(id=id_comentario)
        except Resena.DoesNotExist:
            return Response({'error': 'Comentario no encontrado.'},
                            status=status.HTTP_404_NOT_FOUND)
        #elimiinar el ejercicio
        comentario_eliminar.delete()

        return Response({'mensaje': f'Comentario con id {id_comentario} eliminado correctamente.'},
                    status=status.HTTP_200_OK)


class retroalimentacionViewSet(viewsets.ModelViewSet):
    queryset = Retroalimentacion.objects.all()
    serializer_class = retroalimentacionSerializer

class contactoViewSet(viewsets.ModelViewSet):
    queryset = ContactoEmerg.objects.all()
    serializer_class = ContactoSerializer

class historialViewSet(viewsets.ModelViewSet):
    queryset = HistorialRutina.objects.all()
    serializer_class = HistorialSerializer

class tipotemaViewSet(viewsets.ModelViewSet):
    queryset = TipoTema.objects.all()
    serializer_class = TipoTemaSerializer

class contenidoViewSet(viewsets.ModelViewSet):
    queryset = ContenidoEducativo.objects.all()
    serializer_class = ContenidoSerializer

class rutinasguardadosViewSet(viewsets.ModelViewSet):
    queryset = RutinasGuardados.objects.all()
    serializer_class = RutinasGuardadosSerializer

class RegisterView(APIView):
    def post(self, request):
        data = request.data

        # Validar si el correo ya existe
        if Usuario.objects.filter(correo=data.get('correo')).exists():
            return Response({'error': 'Este correo ya está registrado.'}, status=status.HTTP_400_BAD_REQUEST)

        # Crear el objeto sin guardar aún
        usuario = Usuario(
            nombre=data.get('nombre'),
            ap_pat=data.get('ap_pat'),
            ap_mat=data.get('ap_mat'),
            correo=data.get('correo'),
            semana_embarazo=data.get('semana_embarazo'),
            rol_id=data.get('rol')
        )

        # 🔥 Hashear la contraseña antes de guardar
        usuario.set_password(data.get('contrasena'))

        # 🔥 Guardar el usuario (ahora sí)
        usuario.save()

        print(">>> Usuario guardado con contraseña hasheada:", usuario.contrasena)

        serializer = UsuarioSerializer(usuario)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# class LoginView(APIView):
#     def post(self, request):
#         correo = request.data.get('correo')

#         try:
#             usuario = Usuario.objects.get(correo=correo)
#             serializer = UsuarioSerializer(usuario)
#             return Response({
#                 'message': 'Inicio de sesión exitoso',
#                 'usuario': serializer.data
#             }, status=status.HTTP_200_OK)

#         except Usuario.DoesNotExist:
#             return Response({'error': 'Correo no registrado'}, status=status.HTTP_404_NOT_FOUND)

class LoginView(APIView):
    def post(self, request):
        correo = request.data.get('correo')
        contrasena = request.data.get('contrasena')

        try:
            usuario = Usuario.objects.get(correo=correo)
        except Usuario.DoesNotExist:
            return Response({'error': 'Correo no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        if not check_password(contrasena, usuario.contrasena):
            return Response({'error': 'Contraseña incorrecta'}, status=status.HTTP_400_BAD_REQUEST)

        if not usuario.estado:
            return Response({'error': 'El usuario no está activo'}, status=status.HTTP_403_FORBIDDEN)

        # Generar tokens
        refresh = RefreshToken.for_user(usuario)

        # Serializar datos del usuario
        user_data = {
            'id': usuario.id,
            'nombre_completo': f"{usuario.nombre} {usuario.ap_pat} {usuario.ap_mat}",
            'nombre': usuario.nombre,
            'ap_pat': usuario.ap_pat,
            'ap_mat': usuario.ap_mat,
            'correo': usuario.correo,
            'rol': usuario.rol_id,
            'semana_embarazo': usuario.semana_embarazo,
            # Agrega otros campos que desees incluir
        }

        return Response({
            'message': 'Inicio de sesión exitoso',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'usuario': user_data
        }, status=status.HTTP_200_OK)
###################################################################################################
class RutinasGuardadasUsuarioView(APIView):

    def get(self, request, usuario_id=None):
        if usuario_id:
            registros = RutinasGuardados.objects.filter(usuario_id=usuario_id)
        else:
            registros = RutinasGuardados.objects.all()

        serializer = RutinasGuardadasUsuarioSerializer(registros, many=True)
        return Response(serializer.data)
    
class RutinaDetalleAPI(APIView):
    def get(self, request, rutina_id):

        ejercicios = CrearRutina.objects.filter(
            rutina_id=rutina_id
        ).select_related("ejercicio", "rutina")

        serializer = EjercicioDetalleSerializer(ejercicios, many=True)

        return Response(serializer.data)
    
class CrearHistorialRutinaAPI(APIView):
    def post(self, request):
        serializer = HistorialRutinaSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)



#################################################################################################################