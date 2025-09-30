from django.db import models

class RolUsuario(models.Model):
    rol = models.CharField(max_length=20)
    descripcion = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.rol


class Usuario(models.Model):
    nombre = models.CharField(max_length=50)
    ap_Pat = models.CharField(max_length=50)
    ap_Mat = models.CharField(max_length=50)
    correo = models.EmailField(max_length=254, unique=True)
    semana_embarazo = models.SmallIntegerField(null=True, blank=True)
    rol = models.ForeignKey(RolUsuario, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.nombre} {self.ap_Pat} {self.ap_Mat}"


class Rangos(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    rbpm_inferior = models.SmallIntegerField()
    rbpm_superior = models.SmallIntegerField()
    rox_inferior = models.DecimalField(max_digits=5, decimal_places=2)
    rox_superior = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"Rangos de {self.usuario}"


class TipoLectura(models.Model):
    tipo = models.CharField(max_length=50)
    descripcion = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.tipo


class Lectura(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    lectura_bpm = models.SmallIntegerField()
    lectura_ox = models.DecimalField(max_digits=5, decimal_places=2)
    tipo = models.ForeignKey(TipoLectura, on_delete=models.SET_NULL, null=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    def __str__(self):
        return f"Lectura {self.id_lectura} de {self.usuario}"


class TipoAlerta(models.Model):
    tipo = models.CharField(max_length=50)
    descripcion = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.tipo


class Alerta(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    descripcion = models.TextField()
    fecha_alerta = models.DateTimeField(auto_now_add=True)
    tipo = models.ForeignKey(TipoAlerta, on_delete=models.SET_NULL, null=True)
    lectura = models.ForeignKey(Lectura, on_delete=models.CASCADE)

    def __str__(self):
        return f"Alerta {self.id_alerta} - {self.tipo}"


class Animacion(models.Model):
    nombre_ejercicio = models.CharField(max_length=50)
    url_anima = models.TextField()
    descripcion = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.ejercicio


class Ejercicio(models.Model):
    nombre = models.CharField(max_length=50)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    animacion = models.ForeignKey(Animacion, on_delete=models.SET_NULL, null=True)
    descripcion = models.TextField(null=True, blank=True)
    nivel_esfuerzo = models.SmallIntegerField()
    sug_semanas = models.SmallIntegerField()

    def __str__(self):
        return self.nombre


class Rutina(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(null=True, blank=True)
    sug_semanas_em = models.SmallIntegerField()

    def __str__(self):
        return self.nombre


class CrearRutina(models.Model):
    series = models.SmallIntegerField()
    repeticiones = models.SmallIntegerField()
    tiempo_seg = models.SmallIntegerField()
    ejercicio = models.ForeignKey(Ejercicio, on_delete=models.CASCADE)
    rutina = models.ForeignKey(Rutina, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.rutina} - {self.ejercicio}"


class Resena(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    ejercicio = models.ForeignKey(Ejercicio, on_delete=models.CASCADE)
    descripcion = models.TextField()

    def __str__(self):
        return f"Reseña {self.id_resena} - {self.usuario}"


class Retroalimentacion(models.Model):
    rutina = models.ForeignKey(Rutina, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    comentario = models.TextField()

    def __str__(self):
        return f"Feedback de {self.usuario} - {self.rutina}"


class ContactoEmerg(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=50)
    ap_Pat = models.CharField(max_length=50)
    ap_Mat = models.CharField(max_length=50)
    correo = models.EmailField(max_length=254)

    def __str__(self):
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

    def __str__(self):
        return f"Historial {self.rutina} de {self.usuario}"


class TipoTema(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.nombre


class ContenidoEducativo(models.Model):
    titulo = models.CharField(max_length=50)
    texto = models.TextField()
    tema = models.ForeignKey(TipoTema, on_delete=models.CASCADE)
    urls_img = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.titulo
