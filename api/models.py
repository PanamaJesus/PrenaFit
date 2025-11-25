from django.db import models
from django.contrib.auth.hashers import make_password


class RolUsuario(models.Model):
    rol = models.CharField(max_length=20)
    descripcion = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'rol_usuario'

    def _str_(self):
        return self.rol


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
    imagen_perfil = models.TextField(null=True, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'usuario'

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


class Imagen(models.Model):
    url = models.ImageField(upload_to='iconos_perfil/')  

    class Meta:
        db_table = 'imagenes'

    def __str__(self):
        return self.url.url if self.url else ""



class Ejercicio(models.Model):
    nombre = models.CharField(max_length=50)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    animacion = models.ForeignKey(Imagen, on_delete=models.SET_NULL, null=True)
    descripcion = models.TextField(null=True, blank=True)
    nivel_esfuerzo = models.SmallIntegerField()
    sug_semanas = models.SmallIntegerField()
    categoria = models.CharField(max_length=50, null=True)

    class Meta:
        db_table = 'ejercicios'

    def _str_(self):
        return self.nombre


class Rutina(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(null=True, blank=True)
    sug_semanas_em = models.SmallIntegerField()
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)

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
    calorias = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
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