from rest_framework import viewsets
from api.models import *
from api.db_serializers import *

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

class RutinaViewSet(viewsets.ModelViewSet):
    queryset = Rutina.objects.all()
    serializer_class = RutinaSerializer

class RutinaEjercicioViewSet(viewsets.ModelViewSet):
    queryset = CrearRutina.objects.all()
    serializer_class = RutinaEjercicioSerializer

class ResenaViewSet(viewsets.ModelViewSet):
    queryset = Resena.objects.all()
    serializer_class = ResenaSerializer

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
