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
from django.db import transaction
from django.db.models import Avg
from django.db.models.functions import ExtractMonth

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

    @action(detail=False, methods=['post'], url_path='ultimaLectura',)
    def ultimaLectura(self, request):
    
        """
        Retorna la última lectura de un usuario y sus rangos según el usuario_id enviado en el body.
        """
        usuario_id = request.data.get("usuario_id")

        if not usuario_id:
            return Response(
                {"error": "Debe enviar usuario_id en el body."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Obtener la última lectura
        lectura = Lectura.objects.filter(usuario_id=usuario_id).order_by('-fecha').first()

        if not lectura:
            return Response(
                {"message": "No se encontraron lecturas para este usuario."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Obtener los rangos del usuario
        rangos = Rangos.objects.filter(usuario_id=usuario_id).first()
        rangos_data = None
        if rangos:
            rangos_data = {
                "rbpm_inferior": rangos.rbpm_inferior,
                "rbpm_superior": rangos.rbpm_superior,
                "rox_inferior": str(rangos.rox_inferior),
                "rox_superior": str(rangos.rox_superior),
            }

        serializer = LecturaSerializer(lectura)

        # Devolver lectura y rangos juntos
        return Response(
            {
                "lectura": serializer.data,
                "rangos": rangos_data
            },
            status=status.HTTP_200_OK
        )    
    @action(detail=False, methods=['post'], url_path='usuario-mes')
    def lecturas_mes(self, request):
        """
        Retorna promedios de un tipo de lectura para un usuario en un mes específico.
        body: {
            "usuario_id": 1,
            "tipo": "bpm",  # opciones: "bpm", "ox", "temperatura"
            "mes": 5        # mes del 1 al 12
        }
        """
        usuario_id = request.data.get("usuario_id")
        tipo = request.data.get("tipo")
        mes = request.data.get("mes")

        if not usuario_id or not tipo or not mes:
            return Response({"error": "Debe enviar usuario_id, tipo y mes en el body."},
                            status=status.HTTP_400_BAD_REQUEST)

        if tipo not in ["bpm", "ox", "temperatura"]:
            return Response({"error": "Tipo no válido. Debe ser 'bpm', 'ox' o 'temperatura'."},
                            status=status.HTTP_400_BAD_REQUEST)

        campo = {
            "bpm": "lectura_bpm",
            "ox": "lectura_ox",
            "temperatura": "temperatura"
        }[tipo]

        # Filtrar por usuario y mes
        datos = (
            Lectura.objects.filter(usuario_id=usuario_id)
            .annotate(mes=ExtractMonth('fecha'))
            .filter(mes=mes)
            .values('fecha')
            .annotate(valor=Avg(campo))
            .order_by('fecha')
        )

        resultado = [{"fecha": d['fecha'], "valor": float(d['valor']) if d['valor'] is not None else None} for d in datos]

        return Response({
            "tipo": tipo,
            "mes": mes,
            "datos": resultado
        }, status=status.HTTP_200_OK)
    

class TipoAlertaViewSet(viewsets.ModelViewSet):
    queryset = TipoAlerta.objects.all()
    serializer_class = TipoAlertaSerializer

class AlertaViewSet(viewsets.ModelViewSet):
    queryset = Alerta.objects.all()
    serializer_class = AlertaSerializer

class ImagenViewSet(viewsets.ModelViewSet):
    queryset = Imagen.objects.all()
    serializer_class = ImagenesSerializer

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
    
    @action(detail=False, methods=['get'], url_path='con-ejercicios')
    def rutinas_con_ejercicios(self, request):
        """
        Retorna todas las rutinas con sus ejercicios,
        incluyendo número total de ejercicios y duración total de la rutina.
        """
        rutinas = Rutina.objects.all()

        respuesta = []

        for rutina in rutinas:
            rutina_data = RutinaSerializer(rutina).data

            # Obtener ejercicios dentro de esta rutina
            crear_items = CrearRutina.objects.filter(rutina=rutina)

            ejercicios_data = []
            duracion_total = 0  # en segundos

            for item in crear_items:
                ejercicios_data.append({
                    "id": item.id,
                    "series": item.series,
                    "repeticiones": item.repeticiones,
                    "tiempo_seg": item.tiempo_seg,
                    "ejercicio": EjercicioSerializer(item.ejercicio).data
                })

                if item.tiempo_seg:
                    duracion_total += item.tiempo_seg

            # Convertir segundos a minutos (decimal)
            duracion_minutos = duracion_total / 60

            rutina_data["ejercicios"] = ejercicios_data
            rutina_data["total_ejercicios"] = len(ejercicios_data)
            rutina_data["duracion_total_segundos"] = duracion_total
            rutina_data["duracion_total_minutos"] = round(duracion_minutos, 2)

            respuesta.append(rutina_data)

        return Response(respuesta, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='crear-con-ejercicios')
    def crear_con_ejercicios(self, request):
        serializer = RutinaWriteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Rutina creada correctamente"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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

    @action(detail=False, methods=['post'], url_path='usuario')
    def historial_usuario(self, request):
        """
        Retorna todas las rutinas de un usuario con sus nombres, desempeño y rangos.
        """
        usuario_id = request.data.get("usuario_id")
        if not usuario_id:
            return Response({"error": "Debe enviar usuario_id en el body."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Obtener todas las rutinas del usuario
        rutinas = HistorialRutina.objects.filter(usuario_id=usuario_id).order_by('-fecha')

        # Preparar datos para el frontend
        rutinas_data = []
        for r in rutinas:
            # Nombre de la rutina
            nombre_rutina = r.rutina.nombre if r.rutina else "—"

            # Tiempo en mm:ss
            minutos = r.tiempo // 60 if r.tiempo else 0
            segundos = r.tiempo % 60 if r.tiempo else 0
            tiempo_str = f"{minutos:02d}:{segundos:02d}"

            rutinas_data.append({
                "id": r.id,
                "nombre": nombre_rutina,
                "fecha": r.fecha.strftime("%Y-%m-%d"),
                "promedioOxigenacion": r.avg_oxigeno,
                "promedioFrecuencia": r.avg_bpm,
                "promedioPresion": "—",  # Si luego agregas presión media, reemplazar aquí
                "promedioTemperatura": "—", # Si agregas temperatura media
                "tiempo": tiempo_str,
                "finalizada": r.finalizada,
                "estado": r.estado,
                "calorias": r.calorias
            })

        # Obtener rangos del usuario
        rangos = Rangos.objects.filter(usuario_id=usuario_id).first()
        rangos_data = None
        if rangos:
            rangos_data = {
                "rbpm_inferior": rangos.rbpm_inferior,
                "rbpm_superior": rangos.rbpm_superior,
                "rox_inferior": str(rangos.rox_inferior),
                "rox_superior": str(rangos.rox_superior),
            }

        return Response({
            "rutinas": rutinas_data,
            "rangos": rangos_data
        }, status=status.HTTP_200_OK)
    


class tipotemaViewSet(viewsets.ModelViewSet):
    queryset = TipoTema.objects.all()
    serializer_class = TipoTemaSerializer

class contenidoViewSet(viewsets.ModelViewSet):
    queryset = ContenidoEducativo.objects.all()
    serializer_class = ContenidoSerializer

class rutinasguardadosViewSet(viewsets.ModelViewSet):
    queryset = RutinasGuardados.objects.all()
    serializer_class = RutinasGuardadosSerializer

    @action(detail=False, methods=['post'], url_path='guardadas-usuario')
    def rutinas_guardadas_usuario(self, request):
        """
        Retorna las rutinas guardadas por un usuario,
        incluyendo ejercicios, total de ejercicios y duración total en minutos.
        """
        usuario_id = request.data.get("usuario_id")

        if not usuario_id:
            return Response(
                {"error": "usuario_id es requerido"},
                status=status.HTTP_400_BAD_REQUEST
            )

        guardadas = RutinasGuardados.objects.filter(usuario_id=usuario_id)

        respuesta = []

        for item in guardadas:
            rutina = item.rutina

            rutina_data = RutinaSerializer(rutina).data

            # Obtener ejercicios con datos
            crear_items = CrearRutina.objects.filter(rutina=rutina)

            ejercicios_data = []
            duracion_total_seg = 0

            for e in crear_items:
                ejercicios_data.append({
                    "id": e.id,
                    "series": e.series,
                    "repeticiones": e.repeticiones,
                    "tiempo_seg": e.tiempo_seg,
                    "ejercicio": EjercicioSerializer(e.ejercicio).data
                })

                duracion_total_seg += e.tiempo_seg if e.tiempo_seg else 0

            # Agregar datos extra
            rutina_data["ejercicios"] = ejercicios_data
            rutina_data["total_ejercicios"] = len(ejercicios_data)
            rutina_data["duracion_min"] = round(duracion_total_seg / 60, 2)

            respuesta.append(rutina_data)

        return Response(respuesta, status=status.HTTP_200_OK)

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
        ).select_related("ejercicio", "rutina", "ejercicio__animacion")

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