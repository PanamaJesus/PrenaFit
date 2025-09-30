from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.Views.views import *  

router = DefaultRouter()
router.register(r'rolusuario', RolUsuarioViewSet)
router.register(r'usuario', UsuarioViewSet)
router.register(r'rangos', RangosViewSet)
router.register(r'tipolectura', TipoLecturaViewSet)
router.register(r'lectura', LecturaViewSet)
router.register(r'tipoalerta', TipoAlertaViewSet)
router.register(r'alerta', AlertaViewSet)
router.register(r'animacion', AnimacionViewSet)
router.register(r'ejercicio', EjercicioViewSet)
router.register(r'rutina', RutinaViewSet)
router.register(r'rutinaejercicio', RutinaEjercicioViewSet)
router.register(r'reseña', ResenaViewSet)
router.register(r'retroalimentacion', retroalimentacionViewSet)
router.register(r'contactoemerg', contactoViewSet)
router.register(r'historial', historialViewSet)
router.register(r'tipotema', tipotemaViewSet)
router.register(r'contenido', contenidoViewSet)



urlpatterns = [
    path('', include(router.urls)),
]