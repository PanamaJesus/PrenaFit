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
from datetime import date
from rest_framework.decorators import api_view
from api.utils import enviar_alerta_emergencia # ⬅️ Importar la función de envío

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

    @action(detail=False, methods=['post'], url_path='subir-perfil')
    def subir_perfil(self, request):
        data = request.data.copy()
        data['motivo'] = 'perfil'

        serializer = ImagenesSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Imagen de perfil subida correctamente"}, status=201)

        return Response(serializer.errors, status=400)

    @action(detail=False, methods=['post'], url_path='subir-rutina')
    def subir_rutina(self, request):
        data = request.data.copy()
        data['motivo'] = 'rutina'

        serializer = ImagenesSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Imagen de rutina subida correctamente"}, status=201)

        return Response(serializer.errors, status=400)

    @action(detail=False, methods=['post'], url_path='subir-ejercicio')
    def subir_ejercicio(self, request):
        data = request.data.copy()  
        data['motivo'] = 'ejercicio'

        serializer = ImagenesSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Imagen de registro subida correctamente"}, status=201)

        return Response(serializer.errors, status=400)

    @action(detail=False, methods=['post'], url_path='por-proposito')
    def por_proposito(self, request):
        proposito = request.data.get('proposito', None)
        if not proposito:
            return Response({"error": "Debe proporcionar un parámetro 'proposito'."}, status=400)
        imagenes = Imagen.objects.filter(proposito=proposito)
        serializer = self.get_serializer(imagenes, many=True)
        return Response(serializer.data)



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
    
    @action(detail=False, methods=['get'], url_path='vista_basica')
    def ejercicios_vista_basica(self, request):
        """
        Retorna todos los ejercicios con sus datos
        y la URL del icono (animación) si existe.
        """
        ejercicios = Ejercicio.objects.select_related("animacion").all()
        respuesta = []

        for e in ejercicios:
            data = EjercicioSerializer(e).data

            # URL del icono / animación
            if e.animacion and e.animacion.url:
                data["icono_url"] = e.animacion.url.url
            else:
                data["icono_url"] = None

            respuesta.append(data)

        return Response(respuesta, status=status.HTTP_200_OK)


class RutinaViewSet(viewsets.ModelViewSet):
    queryset = Rutina.objects.all()
    serializer_class = RutinaSerializer
    @action(detail=False, methods=['get'], url_path='vista_basica')
    def rutinas_con_ejercicios_vista_basica(self, request):

        """
        Retorna todas las rutinas con:
        - total de ejercicios
        - duración total
        Pero SIN enviar la lista de ejercicios.
        """

        rutinas = Rutina.objects.all()
        respuesta = []

        for rutina in rutinas:

            rutina_data = RutinaSerializer(rutina).data

            # ============================
            #  🔥 URL del icono
            # ============================
            if rutina.icono and rutina.icono.url:
                rutina_data["icono_url"] = rutina.icono.url.url
            else:
                rutina_data["icono_url"] = None

            # ============================
            #  🔥 Creado por (admin o usuario)
            # ============================
            usuario = rutina.usuario

            es_admin = (
                usuario.rol and 
                usuario.rol.rol.lower() == "admin"
            )

            if es_admin:
                rutina_data["creado_por"] = "PregnFit"
            else:
                rutina_data["creado_por"] = f"{usuario.nombre} {usuario.ap_pat} {usuario.ap_mat}"

            # ============================
            #  🔥 Obtener items sin enviarlos
            # ============================
            crear_items = CrearRutina.objects.filter(rutina=rutina)

            total_ejercicios = crear_items.count()

            duracion_total = sum(
                item.tiempo_seg for item in crear_items if item.tiempo_seg
            )

            duracion_minutos = duracion_total / 60

            # Agregar cálculos
            rutina_data["total_ejercicios"] = total_ejercicios
            rutina_data["duracion_total_segundos"] = duracion_total
            rutina_data["duracion_total_minutos"] = round(duracion_minutos, 2)

            # Agregar a respuesta
            respuesta.append(rutina_data)

        return Response(respuesta, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='detalle-rutina')
    def detalle_rutina(self, request):

        """
        Retorna TODA la información de UNA rutina:
        - ejercicios
        - total de ejercicios
        - duración total
        - URL del icono
        - nombre del creador (usuario o PregnFit si es admin)
        - reseñas (retroalimentaciones)
        Recibe: rutina_id
        """

        rutina_id = request.data.get("rutina_id")

        if not rutina_id:
            return Response({"error": "Falta rutina_id"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rutina = Rutina.objects.get(id=rutina_id)
        except Rutina.DoesNotExist:
            return Response({"error": "La rutina no existe"}, status=status.HTTP_404_NOT_FOUND)

        rutina_data = RutinaSerializer(rutina).data

        # ----------------------------
        # ICONO URL
        # ----------------------------
        if rutina.icono and rutina.icono.url:
            rutina_data["icono_url"] = rutina.icono.url.url
        else:
            rutina_data["icono_url"] = None

        # ----------------------------
        # QUIÉN LA CREÓ
        # ----------------------------
        usuario = rutina.usuario

        es_admin = (
            usuario.rol and 
            usuario.rol.rol.lower() == "admin"
        )

        if es_admin:
            rutina_data["creado_por"] = "PregnFit"
        else:
            rutina_data["creado_por"] = f"{usuario.nombre} {usuario.ap_pat} {usuario.ap_mat}"

       
        # ----------------------------
        # EJERCICIOS
        # ----------------------------
        crear_items = CrearRutina.objects.filter(rutina=rutina)

        ejercicios_data = []
        duracion_total = 0

        for item in crear_items:

            # URL del icono (animación) del ejercicio
            if (
                item.ejercicio and 
                item.ejercicio.animacion and 
                item.ejercicio.animacion.url
            ):
                icono_ejercicio_url = item.ejercicio.animacion.url.url
            else:
                icono_ejercicio_url = None

            ejercicios_data.append({
                "id": item.id,
                "series": item.series,
                "repeticiones": item.repeticiones,
                "tiempo_seg": item.tiempo_seg,
                "ejercicio": EjercicioSerializer(item.ejercicio).data,
                "icono_url": icono_ejercicio_url
            })

            if item.tiempo_seg:
                duracion_total += item.tiempo_seg


        duracion_minutos = round(duracion_total / 60, 2)

        rutina_data["ejercicios"] = ejercicios_data
        rutina_data["total_ejercicios"] = len(ejercicios_data)
        rutina_data["duracion_total_segundos"] = duracion_total
        rutina_data["duracion_total_minutos"] = duracion_minutos

        # ----------------------------
        # RESEÑAS
        # ----------------------------
        resenas = Retroalimentacion.objects.filter(rutina=rutina).order_by("-fecha")

        rutina_data["reseñas"] = [
            {
                "usuario": str(r.usuario),
                "comentario": r.comentario,
                "fecha": r.fecha,
            }
            for r in resenas
        ]

        rutina_data["total_reseñas"] = len(rutina_data["reseñas"])

        # ----------------------------
        # RESPUESTA FINAL
        # ----------------------------
        return Response(rutina_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='crear-con-ejercicios')
    def crear_con_ejercicios(self, request):
        serializer = RutinaWriteSerializer(data=request.data)
        if serializer.is_valid():
            rutina = serializer.save()
            return Response({
                "message": "Rutina creada correctamente",
                "rutina_id": rutina.id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], url_path='buscar-por-nombre')
    def buscar_por_nombre(self, request):
        """
        Busca una rutina por nombre y retorna:
        - datos básicos de la rutina
        - lista de ejercicios (con sus datos)
        - totales (ejercicios y duración)
        - icono_url
        - creador
        - reseñas
        Recibe: nombre (string)
        """
        nombre = request.data.get("nombre")

        if not nombre:
            return Response({"error": "Falta el campo 'nombre'"}, status=status.HTTP_400_BAD_REQUEST)

        # Puedes cambiar __icontains por __iexact si quieres coincidencia exacta
        rutina = Rutina.objects.filter(nombre__icontains=nombre).first()

        if not rutina:
            return Response({"error": "No se encontró ninguna rutina con ese nombre"},
                            status=status.HTTP_404_NOT_FOUND)

        rutina_data = RutinaSerializer(rutina).data

        # ----------------------------
        # ICONO URL (usando el objeto, no el _id)
        # ----------------------------
        if rutina.icono and rutina.icono.url:
            rutina_data["icono_url"] = rutina.icono.url.url
        else:
            rutina_data["icono_url"] = None

        # ----------------------------
        # QUIÉN LA CREÓ
        # ----------------------------
        usuario = rutina.usuario
        es_admin = (
            usuario.rol and 
            usuario.rol.rol.lower() == "admin"
        )

        if es_admin:
            rutina_data["creado_por"] = "PregnFit"
        else:
            rutina_data["creado_por"] = f"{usuario.nombre} {usuario.ap_pat} {usuario.ap_mat}"

        # ----------------------------
        # EJERCICIOS
        # ----------------------------
        crear_items = CrearRutina.objects.filter(rutina=rutina)

        ejercicios_data = []
        duracion_total = 0

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

        duracion_minutos = round(duracion_total / 60, 2)

        rutina_data["ejercicios"] = ejercicios_data
        rutina_data["total_ejercicios"] = len(ejercicios_data)
        rutina_data["duracion_total_segundos"] = duracion_total
        rutina_data["duracion_total_minutos"] = duracion_minutos

        # ----------------------------
        # RESEÑAS
        # ----------------------------
        resenas = Retroalimentacion.objects.filter(rutina=rutina).order_by("-fecha")

        rutina_data["reseñas"] = [
            {
                "usuario": str(r.usuario),
                "comentario": r.comentario,
                "fecha": r.fecha,
            }
            for r in resenas
        ]
        rutina_data["total_reseñas"] = len(rutina_data["reseñas"])

        # ----------------------------
        # RESPUESTA FINAL
        # ----------------------------
        return Response(rutina_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='de-usuario')
    def rutinas_de_usuario(self, request):
        """
        Retorna las rutinas:
        - creadas por un usuario
        - guardadas por un usuario
        Recibe: usuario_id (en el body)
        """
        usuario_id = request.data.get("usuario_id")

        if not usuario_id:
            return Response(
                {"error": "Debe enviar usuario_id en el body."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ------------------------------------
        # 1) Rutinas creadas por el usuario
        # ------------------------------------
        creadas_qs = Rutina.objects.filter(usuario_id=usuario_id)
        creadas = []

        for rutina in creadas_qs:
            rutina_data = RutinaSerializer(rutina).data

            # Icono
            if rutina.icono and rutina.icono.url:
                rutina_data["icono_url"] = rutina.icono.url.url
            else:
                rutina_data["icono_url"] = None

            # Ejercicios + duración
            crear_items = CrearRutina.objects.filter(rutina=rutina)
            ejercicios_data = []
            duracion_total = 0

            for item in crear_items:
                ejercicios_data.append({
                    "id": item.id,
                    "series": item.series,
                    "repeticiones": item.repeticiones,
                    "tiempo_seg": item.tiempo_seg,
                    "ejercicio": EjercicioSerializer(item.ejercicio).data,
                })
                if item.tiempo_seg:
                    duracion_total += item.tiempo_seg

            rutina_data["ejercicios"] = ejercicios_data
            rutina_data["total_ejercicios"] = len(ejercicios_data)
            rutina_data["duracion_total_segundos"] = duracion_total
            rutina_data["duracion_total_minutos"] = round(duracion_total / 60, 2) if duracion_total else 0

            creadas.append(rutina_data)

        # ------------------------------------
        # 2) Rutinas guardadas por el usuario
        # ------------------------------------
        guardadas_qs = RutinasGuardados.objects.filter(usuario_id=usuario_id)
        guardadas = []

        for item in guardadas_qs:
            rutina = item.rutina
            rutina_data = RutinaSerializer(rutina).data

            rutina_data["guardado_id"] = item.id
            # Icono
            if rutina.icono and rutina.icono.url:
                rutina_data["icono_url"] = rutina.icono.url.url
            else:
                rutina_data["icono_url"] = None

            # Ejercicios + duración
            crear_items = CrearRutina.objects.filter(rutina=rutina)
            ejercicios_data = []
            duracion_total = 0

            for e in crear_items:
                ejercicios_data.append({
                    "id": e.id,
                    "series": e.series,
                    "repeticiones": e.repeticiones,
                    "tiempo_seg": e.tiempo_seg,
                    "ejercicio": EjercicioSerializer(e.ejercicio).data,
                })
                if e.tiempo_seg:
                    duracion_total += e.tiempo_seg

            rutina_data["ejercicios"] = ejercicios_data
            rutina_data["total_ejercicios"] = len(ejercicios_data)
            rutina_data["duracion_total_segundos"] = duracion_total
            rutina_data["duracion_total_minutos"] = round(duracion_total / 60, 2) if duracion_total else 0

            guardadas.append(rutina_data)

        # ------------------------------------
        # Respuesta
        # ------------------------------------
        return Response(
            {
                "creadas": creadas,
                "guardadas": guardadas,
            },
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['put'], url_path='actualizar-rutina')
    def actualizar_rutina(self, request):
        """
        Actualiza una rutina creada por un usuario.
        Permite cambiar: nombre, descripcion, icono, es_publica
        y agregar / eliminar ejercicios.

        Body esperado:
        {
            "rutina_id": 23,
            "usuario_id": 27,

            "nombre": "Nuevo nombre opcional",
            "descripcion": "Nueva descripción opcional",
            "icono_id": 9,           # opcional, puede ser null para quitar
            "es_publica": true,      # opcional

            "ejercicios_eliminar": [60, 61],   # IDs de CrearRutina
            "ejercicios_agregar": [
                {
                    "ejercicio_id": 24,
                    "series": 15,
                    "repeticiones": 3,
                    "tiempo_seg": 30
                }
            ]
        }
        """
        rutina_id = request.data.get("rutina_id")
        usuario_id = request.data.get("usuario_id")

        if not rutina_id or not usuario_id:
            return Response(
                {"error": "Debe enviar rutina_id y usuario_id."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Asegurarse de que la rutina pertenezca a ese usuario
        try:
            rutina = Rutina.objects.get(id=rutina_id, usuario_id=usuario_id)
        except Rutina.DoesNotExist:
            return Response(
                {"error": "Rutina no encontrada o no pertenece a este usuario."},
                status=status.HTTP_404_NOT_FOUND
            )

        # -----------------------------
        # Actualizar campos básicos
        # -----------------------------
        nombre = request.data.get("nombre")
        descripcion = request.data.get("descripcion")
        icono_id = request.data.get("icono_id")
        es_publica = request.data.get("es_publica")

        if nombre is not None:
            rutina.nombre = nombre

        if descripcion is not None:
            rutina.descripcion = descripcion

        if es_publica is not None:
            rutina.es_publica = bool(es_publica)

        if icono_id is not None:
            if icono_id == "" or icono_id is False or icono_id is None:
                rutina.icono = None
            else:
                try:
                    icono = Imagen.objects.get(id=icono_id)
                    rutina.icono = icono
                except Imagen.DoesNotExist:
                    return Response(
                        {"error": "El icono_id especificado no existe."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

        rutina.save()

        # -----------------------------
        # Eliminar ejercicios
        # -----------------------------
        ejercicios_eliminar = request.data.get("ejercicios_eliminar", [])
        if isinstance(ejercicios_eliminar, list) and ejercicios_eliminar:
            CrearRutina.objects.filter(
                id__in=ejercicios_eliminar,
                rutina=rutina
            ).delete()

        # -----------------------------
        # Agregar ejercicios
        # -----------------------------
        ejercicios_agregar = request.data.get("ejercicios_agregar", [])
        if isinstance(ejercicios_agregar, list):
            for ej in ejercicios_agregar:
                ejercicio_id = ej.get("ejercicio_id")
                series = ej.get("series")
                repeticiones = ej.get("repeticiones")
                tiempo_seg = ej.get("tiempo_seg")

                if not ejercicio_id:
                    continue  # puedes poner validación más estricta si quieres

                CrearRutina.objects.create(
                    rutina=rutina,
                    ejercicio_id=ejercicio_id,
                    series=series or 0,
                    repeticiones=repeticiones or 0,
                    tiempo_seg=tiempo_seg or 0,
                )

        # -----------------------------
        # Armar respuesta final
        # -----------------------------
        rutina_data = RutinaSerializer(rutina).data

        # Icono URL
        if rutina.icono and rutina.icono.url:
            rutina_data["icono_url"] = rutina.icono.url.url
        else:
            rutina_data["icono_url"] = None

        # Ejercicios actuales de la rutina
        crear_items = CrearRutina.objects.filter(rutina=rutina)
        ejercicios_data = []
        duracion_total = 0

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

        rutina_data["ejercicios"] = ejercicios_data
        rutina_data["total_ejercicios"] = len(ejercicios_data)
        rutina_data["duracion_total_segundos"] = duracion_total
        rutina_data["duracion_total_minutos"] = round(duracion_total / 60, 2) if duracion_total else 0

        return Response(rutina_data, status=status.HTTP_200_OK)### Cómo llamarlo

    @action(detail=False, methods=['delete'], url_path='eliminar-rutina')
    def eliminar_rutina(self, request):
        """
        Elimina una rutina creada por un usuario.
        Solo el usuario que creó la rutina puede eliminarla.
        Al eliminar la rutina, se eliminan automáticamente:
        - Los ejercicios asociados (CrearRutina)
        - Las retroalimentaciones (Retroalimentacion)
        - Los historiales relacionados (HistorialRutina)
        
        Body esperado:
        {
            "rutina_id": 23,
            "usuario_id": 27
        }
        """
        rutina_id = request.data.get("rutina_id")
        usuario_id = request.data.get("usuario_id")

        if not rutina_id or not usuario_id:
            return Response(
                {"error": "Debe enviar rutina_id y usuario_id en el body."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verificar que la rutina existe y pertenece al usuario
        try:
            rutina = Rutina.objects.get(id=rutina_id, usuario_id=usuario_id)
        except Rutina.DoesNotExist:
            return Response(
                {"error": "Rutina no encontrada o no pertenece a este usuario."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Guardar el ID antes de eliminar para la respuesta
        rutina_id_eliminada = rutina.id
        nombre_rutina = rutina.nombre

        # Eliminar la rutina (Django eliminará automáticamente los registros relacionados en cascada)
        rutina.delete()

        return Response(
            {
                "message": "Rutina eliminada correctamente",
                "rutina_id": rutina_id_eliminada,
                "nombre": nombre_rutina
            },
            status=status.HTTP_200_OK
        )

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
                "temperatura": r.temperatura
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

            rutina_data["guardado_id"] = item.id
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

    @action(detail=False, methods=['delete'], url_path='eliminar-guardada')
    def eliminar_rutina_guardada(self, request):
        """
        Elimina el registro de una rutina guardada por un usuario.
        Solo elimina el registro de RutinasGuardados, NO la rutina en sí.
        
        Body esperado:
        {
            "rutina_id": 23,
            "usuario_id": 27
        }
        """
        rutina_id = request.data.get("rutina_id")
        usuario_id = request.data.get("usuario_id")

        if not rutina_id or not usuario_id:
            return Response(
                {"error": "Debe enviar rutina_id y usuario_id en el body."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Buscar el registro específico
        try:
            registro = RutinasGuardados.objects.get(
                id=rutina_id,
                usuario=usuario_id
            )
        except RutinasGuardados.DoesNotExist:
            return Response(
                {"error": "No se encontró la rutina guardada para este usuario."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Eliminar solo el registro (no la rutina)
        registro.delete()

        return Response(
            {
                "message": "Rutina eliminada de guardadas correctamente",
                "rutina_id": rutina_id,
                "usuario_id": usuario_id
            },
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['post'], url_path='crear-guardada')
    def crear_rutina_guardada(self, request):
        """
        Guarda una rutina para un usuario si no ha sido guardada previamente.
        Requiere 'usuario_id' y 'rutina_id' en el cuerpo de la solicitud (request.data).
        """
        usuario_id = request.data.get("usuario_id")
        rutina_id = request.data.get("rutina_id")

        # 1. Validación de datos de entrada
        if not usuario_id or not rutina_id:
            return Response(
                {"error": "Tanto 'usuario_id' como 'rutina_id' son requeridos."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Opcional: Verificar que la rutina exista
        try:
            rutina = Rutina.objects.get(pk=rutina_id)
        except Rutina.DoesNotExist:
            return Response(
                {"error": f"La rutina con ID {rutina_id} no existe."},
                status=status.HTTP_404_NOT_FOUND
            )

        # 2. Verificar si la rutina ya ha sido guardada por el usuario
        # Usa filter().exists() para una consulta eficiente.
        ya_guardada = RutinasGuardados.objects.filter(
            usuario_id=usuario_id, 
            rutina_id=rutina_id
        ).exists()

        if ya_guardada:
            return Response(
                {"mensaje": "Esta rutina ya ha sido guardada por el usuario."},
                status=status.HTTP_409_CONFLICT  # Código 409: Conflicto
            )

        # 3. Guardar la rutina
        try:
            rutina_guardada = RutinasGuardados.objects.create(
                usuario_id=usuario_id,
                rutina=rutina # Usamos el objeto rutina recuperado o rutina_id
            )
            
            # Puedes serializar el objeto guardado para devolver los datos completos
            serializer = RutinasGuardadosSerializer(rutina_guardada)
            
            return Response(
                {"mensaje": "Rutina guardada exitosamente.", "data": serializer.data},
                status=status.HTTP_201_CREATED  # Código 201: Creado
            )

        except Exception as e:
            # Captura errores en caso de que el usuario_id no sea válido (si no se validó antes)
            # o cualquier otro error de la base de datos.
            return Response(
                {"error": f"Ocurrió un error al guardar la rutina: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            usuario = serializer.save()
            return Response(RegisterSerializer(usuario).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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

        if usuario.imagen_perfil and usuario.imagen_perfil.url:
            imagen_relativa = usuario.imagen_perfil.url.url  # /media/...
            imagen_url_completa = request.build_absolute_uri(usuario.imagen_perfil.url.url)
        else:
            imagen_relativa = None
            imagen_url_completa = None

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
            'imagen_perfil': imagen_relativa,          # /media/fotos/perfil.jpg
            'imagen_perfil_url': imagen_url_completa 
        }

        return Response({
            'message': 'Inicio de sesión exitoso',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'usuario': user_data
        }, status=status.HTTP_200_OK)
##########################################################################
# vista del select de los rangos de un usuario
class RangosDeUnUsuarioView(APIView):
    def get(self, request, usuario_id=None):
        if usuario_id:
            registros =Rangos.objects.filter(usuario_id=usuario_id)
        else:
            registros = Rangos.objects.all()

        serializer =  RangosDeUnUsuarioSerializer(registros, many=True)
        return Response(serializer.data)
# vista del select de las lecturas de un usuario
class LecturasDeUnUsuarioView(APIView):
    def get(self, request, usuario_id=None):
        if usuario_id:
            registros =Lectura.objects.filter(usuario_id=usuario_id)
        else:
            registros = Lectura.objects.all()

        serializer = LecturasDeUnUsuarioSerializer(registros, many=True)
        return Response(serializer.data)
# vista del select de la ultima lecturas de un usuario
class UltimaLecturaDeUsuarioView(APIView):
    def get(self, request, usuario_id=None):
        if not usuario_id:
            return Response({"error": "Debe especificar usuario_id"}, status=400)
        
        try:
            ultima_lectura = Lectura.objects.filter(usuario_id=usuario_id).latest("id")
        except Lectura.DoesNotExist:
            return Response({"error": "No se encontró ninguna lectura para este usuario"}, status=404)
        
        serializer = LecturasDeUnUsuarioSerializer(ultima_lectura)
        return Response(serializer.data)
# Vista Rutinas guardadas de un usuario        
class RutinasGuardadasUsuarioView(APIView):
    def get(self, request, usuario_id=None):
        if usuario_id:
            registros = RutinasGuardados.objects.filter(usuario_id=usuario_id)
        else:
            registros = RutinasGuardados.objects.all()

        serializer = RutinasGuardadasUsuarioSerializer(registros, many=True)
        return Response(serializer.data)
#vista de los ejercicios de una rutina relacionada a un usuario    
class RutinaDetalleAPI(APIView):
    def get(self, request, rutina_id):

        ejercicios = CrearRutina.objects.filter(
            rutina_id=rutina_id
        ).select_related("ejercicio", "rutina", "ejercicio__animacion")

        serializer = EjercicioDetalleSerializer(ejercicios, many=True)

        return Response(serializer.data)
# Vista del post de historial de rutinas
class CrearHistorialRutinaAPI(APIView):
    def post(self, request):
        serializer = HistorialRutinaSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)
# vista del post de lecturas
class CrearLecturaUsuarioAPI(APIView):
    def post(self, request):
        serializer = LecturaSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)
    
# class CrearAlertasUsuarioAPI(APIView):
#     def post(self, request):
#         serializer = AlertaSerializer(data=request.data)

#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=201)

#         return Response(serializer.errors, status=400)



def calcular_edad(fecha_nac):
    hoy = date.today()
    return hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))


@api_view(["POST"])
def simular_lectura(request, usuario_id, accion):

    # 1-normal / 2-bajo / 3-medio / 4-alto
    mapa_acciones = {
        "1": "normal",
        "2": "bajo",
        "3": "medio",
        "4": "alto"
    }

    accion = str(accion)
    if accion not in mapa_acciones:
        return Response({"error": "Acción inválida (usa 1,2,3,4)"}, status=400)

    accion = mapa_acciones[accion]
    try:
        user = Usuario.objects.get(id=usuario_id)
    except Usuario.DoesNotExist:
        return Response({"error": "Usuario no encontrado"}, status=404)

    #   Rangos de las lecturas en base a la accion
    acciones_cfg = {
        "normal": {
            "bpm": (80, 90),
            "ox": (97.0, 100.0),
            "temp": (36.3, 36.8)
        },
        "bajo": {
            "bpm": (90, 110),
            "ox": (96.0, 98.0),
            "temp": (36.7, 37.1)
        },
        "medio": {
            "bpm": (110, 135),
            "ox": (95.0, 97.0),
            "temp": (37.0, 37.4)
        },
        "alto": {
            "bpm": (135, 160),
            "ox": (93.0, 96.0),
            "temp": (37.3, 38.0)
        },
    }
    #Genera la lecura
    cfg = acciones_cfg[accion]
    nuevo_bpm = random.randint(cfg["bpm"][0], cfg["bpm"][1])
    nuevo_ox = round(random.uniform(cfg["ox"][0], cfg["ox"][1]), 2)
    nueva_temp = round(random.uniform(cfg["temp"][0], cfg["temp"][1]), 2)
    
    # GUARDAR LECTURA EN BD
    data = {
        "usuario": user.id,
        "lectura_bpm": nuevo_bpm,
        "lectura_ox": nuevo_ox,
        "temperatura": nueva_temp,
        "tipo": None
    }

    serializer = LecturaSerializer(data=data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    lectura = serializer.save()  # guardar lectura

    #   VALIDAR RANGOS Y GENERAR ALERTAS
    try:
        rangos = Rangos.objects.get(usuario=user)
    except Rangos.DoesNotExist:
        rangos = None  # si no hay rangos simplemente no hay alertas

    if rangos:
        alertas_generadas = []

        # ------------------ BPM ------------------
        if nuevo_bpm < rangos.rbpm_inferior or nuevo_bpm > rangos.rbpm_superior:
            tipo = TipoAlerta.objects.filter(tipo="BPM").first()
            Alerta.objects.create(
                usuario=user,
                descripcion=f"Frecuencia cardíaca fuera de rango: {nuevo_bpm} bpm",
                tipo=tipo,
                lectura=lectura
            )
            alertas_generadas.append("bpm")

        # ------------------ SpO2 ------------------
        if nuevo_ox < float(rangos.rox_inferior) or nuevo_ox > float(rangos.rox_superior):
            tipo = TipoAlerta.objects.filter(tipo="OX").first()
            Alerta.objects.create(
                usuario=user,
                descripcion=f"Nivel de oxigenación fuera de rango: {nuevo_ox}%",
                tipo=tipo,
                lectura=lectura
            )
            alertas_generadas.append("ox")
        # 🟢 NUEVA LÓGICA DE ENVÍO DE CORREO 🟢
        # Si se generó ALGUNA alerta, intentamos enviar el correo.
        if alertas_generadas:
            try:
                # 1. Obtener el objeto de Contacto de Emergencia
                # Usamos el related_name por defecto (contactoemerg_set) y tomamos el primero.
                contacto = user.contactoemerg_set.first() 
                
                if contacto:
                    # 2. Enviar el correo
                    envio_exitoso = enviar_alerta_emergencia(user, contacto)
                    
                    if not envio_exitoso:
                        print(f"ATENCIÓN: FALLÓ EL ENVÍO DE ALERTA por correo para {user.correo}")
                else:
                    # Caso en que el usuario no tiene contactos registrados
                    print(f"ADVERTENCIA: Usuario {user.id} no tiene contactos de emergencia registrados.")
                    
            except Exception as e:
                # Cualquier otro error, como un problema de conexión SMTP
                print(f"ERROR FATAL DE ENVÍO DE CORREO: {e}")
                
    # ------------------ FIN DE ALERTA ------------------

    return Response(LecturaSerializer(lectura).data, status=status.HTTP_201_CREATED)

#################################################################################################################
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Avg, Sum, Count
import pandas as pd 
from datetime import date # <--- ¡IMPORTANTE: Nuevo Import!
from .utils import get_ml_model_context 


class RutinaRecomendacionListaView(APIView):
    """
    Retorna una lista de rutinas recomendadas basándose en el cálculo dinámico 
    de las semanas de embarazo usando 'fecha_inicio_embarazo'.
    """
    def get(self, request, usuario_id):
        # 1. Cargar el modelo y features
        MODELO_RF, FEATURE_COLUMNS = get_ml_model_context()
        if not MODELO_RF:
            return Response({"error": "Modelo de recomendación no cargado en el servidor."}, status=500)
            
        try:
            usuario = Usuario.objects.get(pk=usuario_id)
            rangos = Rangos.objects.filter(usuario=usuario).first()
            
            # Verificaciones críticas
            if not rangos:
                return Response({"error": "Rangos del usuario no definidos."}, status=400)
            if not usuario.fecha_inicio_embarazo: # Usamos el campo confirmado por el usuario
                 return Response({"error": "La fecha de inicio de embarazo no está definida en el perfil del usuario."}, status=400)

        except Usuario.DoesNotExist:
            return Response({"error": "Usuario no encontrado."}, status=404)

        # 2. Obtener Rutinas candidatas y Features Agregados
        rutinas_candidatas_qs = Rutina.objects.filter(es_publica=True)
        
        rutinas_con_esfuerzo = rutinas_candidatas_qs.annotate(
            rutina_esfuerzo_promedio=Avg('crearrutina__ejercicio__nivel_esfuerzo'),
            total_ejercicios=Count('crearrutina'), 
            duracion_total_minutos=Sum('crearrutina__tiempo_seg') / 60.0,
        ).exclude(rutina_esfuerzo_promedio__isnull=True) 

        rutinas_list = list(rutinas_con_esfuerzo)

        # 3. Obtener Historial y Calcular Alerta (Lógica sin cambios)
        ultimo_historial = HistorialRutina.objects.filter(usuario=usuario).order_by('-fecha').first()
        alerta_generada = 0
        historial_data = {}
        
        if ultimo_historial and ultimo_historial.avg_bpm and ultimo_historial.avg_oxigeno:
            alerta_bpm = (ultimo_historial.avg_bpm < rangos.rbpm_inferior) or (ultimo_historial.avg_bpm > rangos.rbpm_superior)
            alerta_ox = (ultimo_historial.avg_oxigeno < rangos.rox_inferior)
            alerta_generada = 1 if alerta_bpm or alerta_ox else 0
            historial_data = {'avg_bpm': ultimo_historial.avg_bpm, 'avg_oxigeno': ultimo_historial.avg_oxigeno}
        else:
            historial_data = {'avg_bpm': rangos.rbpm_inferior + 5, 'avg_oxigeno': 98.0}

        # 4. Preparar DataFrame de Predicción
        datos_prediccion = [] 
        
        # 🔥 CÁLCULO DE SEMANAS DE EMBARAZO (LÓGICA NUEVA) 🔥
        hoy = date.today()
        # Usamos el campo correcto: fecha_inicio_embarazo
        fecha_inicio_embarazo = usuario.fecha_inicio_embarazo 
        
        # Calcular la diferencia de días
        dias_embarazo = (hoy - fecha_inicio_embarazo).days
        
        # Calcular la semana actual (días / 7). 
        # Usamos max(1, ...) para asegurar que siempre sea al menos la semana 1.
        semana_actual = max(1, int(dias_embarazo / 7))
        # 🔥 FIN DEL CÁLCULO 🔥

        for rutina in rutinas_list:
            esfuerzo = rutina.rutina_esfuerzo_promedio if rutina.rutina_esfuerzo_promedio is not None else 0 

            fila = {
                'semana_embarazo': semana_actual, # Alimentamos al ML con el valor calculado
                'sug_semanas_em': rutina.sug_semanas_em,
                'rbpm_inferior': rangos.rbpm_inferior,
                'rbpm_superior': rangos.rbpm_superior,
                'rox_inferior': rangos.rox_inferior,
                **historial_data, 
                'alerta_generada': alerta_generada,
                'rutina_esfuerzo_promedio': esfuerzo 
            }
            datos_prediccion.append(fila)

        if not datos_prediccion:
             return Response([], status=200)

        df_prediccion = pd.DataFrame(datos_prediccion, columns=FEATURE_COLUMNS)

        # 5. Predicción y Creación de Lista Final
        scores_predichos = MODELO_RF.predict(df_prediccion)
        
        lista_recomendada = []
        
        for i, rutina in enumerate(rutinas_list):
            score = scores_predichos[i]
            
            # Filtro de Producción Activado (>= 0.5)
            if score >= 0.5: 
                
                lista_recomendada.append({
                    'id': rutina.id, 'nombre': rutina.nombre, 'descripcion': rutina.descripcion,
                    'sug_semanas_em': rutina.sug_semanas_em,
                    'total_ejercicios': int(getattr(rutina, 'total_ejercicios', 0)), 
                    'duracion_total_minutos': round(float(getattr(rutina, 'duracion_total_minutos', 0)), 0), 
                    'creado_por': rutina.usuario.nombre, 
                    'score_ml': round(score, 3) 
                })

        # 6. Ordenar por score descendente
        lista_recomendada.sort(key=lambda x: x['score_ml'], reverse=True)
        
        return Response(lista_recomendada, status=200)
################################################################