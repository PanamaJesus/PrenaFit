from django.db import models
from django.contrib.auth.hashers import make_password
from datetime import date, timedelta


class RolUsuario(models.Model):
    rol = models.CharField(max_length=20)
    descripcion = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'rol_usuario'

    def _str_(self):
        return self.rol

# class Imagen(models.Model):
#     url = models.ImageField(upload_to='iconos_perfil/')  
#     proposito = models.CharField(max_length=100, null=True, blank=True)
#     class Meta:
#         db_table = 'imagenes'

#     def __str__(self):
#         return self.url.url if self.url else "
def ruta_por_proposito(instance, filename):
    proposito = (instance.proposito or "").lower()

    if proposito == "perfil":
        carpeta = "iconos_perfil"
    elif proposito == "rutina":
        carpeta = "iconos_rutinas"
    elif proposito == "ejercicio":
        carpeta = "ejercicios"
    else:
        carpeta = "otros"

    return f"{carpeta}/{filename}"


class Imagen(models.Model):
    url = models.ImageField(upload_to=ruta_por_proposito)
    proposito = models.CharField(max_length=100, null=True, blank=True)


    class Meta:
        db_table = 'imagenes'

    def __str__(self):
        return self.url.url if self.url else ""



class Usuario(models.Model):
    nombre = models.CharField(max_length=50)
    ap_pat = models.CharField(max_length=50)
    ap_mat = models.CharField(max_length=50)
    correo = models.EmailField(max_length=254, unique=True)
    semana_embarazo = models.SmallIntegerField(null=True, blank=True)
    rol = models.ForeignKey(RolUsuario, on_delete=models.SET_NULL, null=True)
    codigo_vinculacion = models.CharField(max_length=10, null=True, blank=True)
    estado = models.BooleanField(default=False)
    contrasena = models.CharField(max_length=128, null=True)
    imagen_perfil = models.ForeignKey(Imagen, on_delete=models.SET_NULL, null=True,blank=True
    )
    fecha_nacimiento = models.DateField(null=True, blank=True)
    # ✅ Nuevo campo FIJO para la lógica
    fecha_inicio_embarazo = models.DateField(
        null=True, 
        blank=True,
        help_text="Fecha estimada de inicio del embarazo (Semana 0 + 0 días)."
    )

    class Meta:
        db_table = 'usuario'

    @property
    def semana_embarazo_actual(self):
        """Calcula la semana de embarazo actual en tiempo real."""
        if not self.fecha_inicio_embarazo:
            return self.semana_embarazo if self.semana_embarazo is not None else 0
        # ^ Si la nueva FIE no existe, usa el valor estático viejo como fallback
        
        hoy = date.today()
        dias_transcurridos = (hoy - self.fecha_inicio_embarazo).days

        if dias_transcurridos < 0:
            return 0 

        semana_actual = dias_transcurridos // 7
        return semana_actual
    
    # 📌 Getter para interceptar llamadas antiguas a 'semana_embarazo'
    #    Esto NO es un @property. Se llamaría: usuario.semana_actual_calculada
    
    def get_semana_calculada(self):
        """Método que las APIs pueden llamar en lugar del campo directo."""
        return self.semana_embarazo_actual # Llama a la propiedad calculada

    def __str__(self):
        return f"{self.nombre} {self.ap_pat} {self.ap_mat}"

    def set_password(self, raw_password):
        print("Hasheando contraseña...")
        """Hashea y guarda la contraseña."""
        self.contrasena = make_password(raw_password)
        print("Contraseña hasheada:", self.contrasena)

class Rangos(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    rbpm_inferior = models.SmallIntegerField()
    rbpm_superior = models.SmallIntegerField()
    rox_inferior = models.DecimalField(max_digits=5, decimal_places=2)
    rox_superior = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        db_table = 'rangos'

    def _str_(self):
        return f"Rangos de {self.usuario}"


class TipoLectura(models.Model):
    tipo = models.CharField(max_length=50)
    descripcion = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'tipo_lectura'

    def _str_(self):
        return self.tipo


class Lectura(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    lectura_bpm = models.SmallIntegerField()
    lectura_ox = models.DecimalField(max_digits=5, decimal_places=2)
    temperatura = models.DecimalField(max_digits=5, decimal_places=2)
    tipo = models.ForeignKey(TipoLectura, on_delete=models.SET_NULL, null=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    class Meta:
        db_table = 'lecturas'

    def _str_(self):
        return f"Lectura {self.id} de {self.usuario}"


class TipoAlerta(models.Model):
    tipo = models.CharField(max_length=50)
    descripcion = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'tipos_alertas'

    def _str_(self):
        return self.tipo


class Alerta(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    descripcion = models.TextField()
    fecha_alerta = models.DateTimeField(auto_now_add=True)
    tipo = models.ForeignKey(TipoAlerta, on_delete=models.SET_NULL, null=True)
    lectura = models.ForeignKey(Lectura, on_delete=models.CASCADE)

    class Meta:
        db_table = 'alertas'

    def _str_(self):
        return f"Alerta {self.id} - {self.tipo}"

class Ejercicio(models.Model):
    nombre = models.CharField(max_length=50)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    animacion = models.ForeignKey(Imagen, on_delete=models.SET_NULL, null=True)
    descripcion = models.TextField(null=True, blank=True)
    nivel_esfuerzo = models.SmallIntegerField()
    sug_semanas = models.SmallIntegerField()
    categoria = models.CharField(max_length=50, null=True)
    series_default = models.SmallIntegerField(null=True, blank=True)
    repeticiones_default = models.SmallIntegerField(null=True, blank=True)
    tiempo_seg_default = models.SmallIntegerField(null=True, blank=True)

    class Meta:
        db_table = 'ejercicios'

    def _str_(self):
        return self.nombre


class Rutina(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(null=True, blank=True)
    sug_semanas_em = models.SmallIntegerField()
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    icono = models.ForeignKey(Imagen, on_delete=models.SET_NULL,null=True, blank=True)
    es_publica = models.BooleanField(default=False)

    class Meta:
        db_table = 'rutina'

    def _str_(self):
        return self.nombre


class CrearRutina(models.Model):
    series = models.SmallIntegerField()
    repeticiones = models.SmallIntegerField()
    tiempo_seg = models.SmallIntegerField()
    ejercicio = models.ForeignKey(Ejercicio, on_delete=models.CASCADE)
    rutina = models.ForeignKey(Rutina, on_delete=models.CASCADE)

    class Meta:
        db_table = 'crear_rutina'

    def _str_(self):
        return f"{self.rutina} - {self.ejercicio}"


class Resena(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    ejercicio = models.ForeignKey(Ejercicio, on_delete=models.CASCADE)
    descripcion = models.TextField()

    class Meta:
        db_table = 'resenas'

    def _str_(self):
        return f"Resena {self.id} - {self.usuario}"


class Retroalimentacion(models.Model):
    rutina = models.ForeignKey(Rutina, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    comentario = models.TextField()

    class Meta:
        db_table = 'retroalimentacion'

    def _str_(self):
        return f"Feedback de {self.usuario} - {self.rutina}"


class ContactoEmerg(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=50)
    ap_pat = models.CharField(max_length=50)
    ap_mat = models.CharField(max_length=50)
    correo = models.EmailField(max_length=254)

    class Meta:
        db_table = 'contacto_emerg'

    def _str_(self):
        return f"Contacto: {self.nombre} {self.ap_Pat}"


class HistorialRutina(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    rutina = models.ForeignKey(Rutina, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    finalizada = models.BooleanField(default=False)
    avg_oxigeno = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    avg_bpm = models.SmallIntegerField(null=True, blank=True)
    temperatura = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    tiempo = models.IntegerField(null=True, blank=True)
    estado = models.CharField(max_length=50)

    class Meta:
        db_table = 'historial_rutina'

    def _str_(self):
        return f"Historial {self.rutina} de {self.usuario}"


class TipoTema(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'tipo_tema'

    def _str_(self):
        return self.nombre


class ContenidoEducativo(models.Model):
    titulo = models.CharField(max_length=50)
    texto = models.TextField()
    tema = models.ForeignKey(TipoTema, on_delete=models.CASCADE)
    urls_img = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'contenido_educativo'

    def _str_(self):
        return self.titulo

class RutinasGuardados(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    rutina = models.ForeignKey(Rutina, on_delete=models.CASCADE)
    fecha_guardado = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'rutina_guardados'

    def __str__(self):
        return f"{self.usuario} guardó {self.ejercicio}"