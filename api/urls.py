from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.conf.urls.static import static
from api.Views.views import *
from django.conf import settings

router = DefaultRouter()
router.register(r'rolusuario', RolUsuarioViewSet)
router.register(r'usuario', UsuarioViewSet)
router.register(r'rangos', RangosViewSet)
router.register(r'tipolectura', TipoLecturaViewSet)
router.register(r'lectura', LecturaViewSet)
router.register(r'tipoalerta', TipoAlertaViewSet)
router.register(r'alerta', AlertaViewSet)
router.register(r'imagenes', ImagenViewSet)
router.register(r'ejercicio', EjercicioViewSet)
router.register(r'rutina', RutinaViewSet)
router.register(r'rutinaejercicio', RutinaEjercicioViewSet)
router.register(r'resena', ResenaViewSet)
router.register(r'retroalimentacion', retroalimentacionViewSet)
router.register(r'contactoemerg', contactoViewSet)
router.register(r'historial', historialViewSet)
router.register(r'tipotema', tipotemaViewSet)
router.register(r'contenido', contenidoViewSet)
router.register(r'rutinasguardados', rutinasguardadosViewSet)

urlpatterns = [ 
    path('', include(router.urls)), 
    path('register/', RegisterView.as_view(), name='register'), 
    path('login/', LoginView.as_view(), name='login'), 


    path('rutinas_guardadas/<int:usuario_id>/', RutinasGuardadasUsuarioView.as_view()),
    path('rutinas_guardadas/', RutinasGuardadasUsuarioView.as_view()),
    path("rutina_detalle/<int:rutina_id>/", RutinaDetalleAPI.as_view()),
    path("historial_rutina/", CrearHistorialRutinaAPI.as_view(), name="crear_historial"),
    path('rangos_usuario/<int:usuario_id>/', RangosDeUnUsuarioView.as_view()),
    path('lecturas_usuario/<int:usuario_id>/',  LecturasDeUnUsuarioView.as_view()),
    path('ultima_lectura_usuario/<int:usuario_id>/', UltimaLecturaDeUsuarioView.as_view()),
    path("lecturasnuevas/", CrearLecturaUsuarioAPI.as_view(), name="lecturasnuevas"),
    #primero el id del usuario y el numero de accion, va de 1 al 4, en su view se ve cual es cual, no hay relacion con alguna tabla 
    path("simulador/<int:usuario_id>/<int:accion>/", simular_lectura),

    path('recomendacion/lista/<int:usuario_id>/', RutinaRecomendacionListaView.as_view(), name='rutina-recomendacion-lista'),
]


