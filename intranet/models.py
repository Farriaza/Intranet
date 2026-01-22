from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django.utils.text import slugify






class Estamento(models.Model):
    nombre = models.CharField(max_length=200, unique=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Cargo(models.Model):
    nombre = models.CharField(max_length=200, unique=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class UnidadFiscalia(models.Model):
    nombre = models.CharField(max_length=300, unique=True)
    estado = models.BooleanField(default=True) 

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre
    
def documento_upload_path(instance, filename):
    return f'documentos/unidad_{instance.unidad.id}/{filename}'






class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="perfil")

    imagen = models.ImageField(upload_to="perfiles/", default="perfiles/perfil.png")

    fecha_nacimiento = models.DateField(null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    run = models.CharField(max_length=10,unique=True,null=True,blank=True,verbose_name="RUN" )
    contacto_nombre = models.CharField(max_length=100, null=True, blank=True)
    contacto_telefono = models.CharField(max_length=20, null=True, blank=True)
    contacto_relacion = models.CharField(max_length=50, null=True, blank=True)

    contacto2_nombre = models.CharField(max_length=100, blank=True, null=True)
    contacto2_telefono = models.CharField(max_length=20, blank=True, null=True)
    contacto2_relacion = models.CharField(max_length=50, blank=True, null=True)

    estamento = models.ForeignKey(
        Estamento, on_delete=models.PROTECT, null=True, blank=True
    )
    cargo = models.ForeignKey(
        Cargo, on_delete=models.PROTECT, null=True, blank=True
    )
    unidad_fiscalia = models.ForeignKey(
        UnidadFiscalia, on_delete=models.PROTECT, null=True, blank=True
    )

    def __str__(self):
        return f"Perfil de {self.user.username}"


class Noticia(models.Model):

    CATEGORIAS = [
    ("Empresa", "Empresa"),
    ("Tecnología", "Tecnología"),
    ("Proyectos", "Proyectos"),
    ("Clientes", "Clientes"),
    ("Comunicados", "Comunicados"),
]


    titulo = models.TextField(max_length=60)
    categoria = models.CharField(max_length=100, choices=CATEGORIAS)
    fecha = models.DateField(auto_now_add=True)
    descripcion = models.TextField(max_length=120)
    imagen = models.ImageField(upload_to='noticias/', blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True, max_length=255)

    autor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="noticias"
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.titulo)
            slug_unico = base_slug
            contador = 1
            while Noticia.objects.filter(slug=slug_unico).exists():
                slug_unico = f"{base_slug}-{contador}"
                contador += 1
            self.slug = slug_unico
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titulo

   

class SocialPost(models.Model):
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=300, blank=True)

    imagen = models.ImageField(upload_to="social/img/", blank=True, null=True)
    video = models.FileField(upload_to="social/video/", blank=True, null=True)

    # 🏆 TEXTO DEL LOGRO
    texto_logro = models.TextField(
        blank=True,
        null=True,
        help_text="Descripción breve del logro institucional"
    )

    fecha = models.DateTimeField(auto_now_add=True)
    aprobado = models.BooleanField(default=False)
    en_logros = models.BooleanField(default=False)

    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return f"Post de {self.autor.username}"



class SocialLike(models.Model):
    post = models.ForeignKey(SocialPost, related_name="likes", on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("post", "usuario")


class SocialComentario(models.Model):
    post = models.ForeignKey(SocialPost, related_name="comentarios", on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    texto = models.TextField(max_length=400)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comentario de {self.usuario.username}"



class Documento(models.Model):

    class Categoria(models.TextChoices):
        REGLAMENTOS = "REGLAMENTOS", "Reglamentos, Protocolos e Instructivos"
        PROCESOS = "PROCESOS", "Procesos de Trabajo"
        BIENESTAR = "BIENESTAR", "Bienestar"

    categoria = models.CharField(
        max_length=20,
        choices=Categoria.choices
    )

    titulo = models.CharField(max_length=255)
    archivo = models.FileField(upload_to="documentos/%Y/%m/")
    fecha_subida = models.DateTimeField(auto_now_add=True)

    subido_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )



    def __str__(self) -> str:
        return f"{self.titulo} - {self.get_categoria_display()}"
    
# models.py
class Capacitacion(models.Model):
    perfil = models.ForeignKey(
        Perfil,
        on_delete=models.CASCADE,
        related_name="capacitaciones"
    )
    nombre = models.CharField(max_length=200)
    institucion = models.CharField(max_length=200)
    fecha = models.DateField()
    documento = models.FileField(
        upload_to="capacitaciones/",
        null=True,
        blank=True
    )

    def __str__(self):
        return self.nombre

class CategoriaDocumento(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["orden"]

    def __str__(self) -> str:
        return self.nombre


class DocumentoComite(models.Model):
    categoria = models.ForeignKey(
        CategoriaDocumento,
        on_delete=models.CASCADE,
        related_name="documentos"
    )
    titulo = models.CharField(max_length=200)
    archivo = models.FileField(upload_to="documentos_comite/%Y/%m/")
    fecha_subida = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha_subida"]

    def __str__(self) -> str:
        return f"{self.categoria} - {self.titulo}"
    

class Cliente(models.Model):
    TIPO_CHOICES = [
        ('natural', 'Persona Natural'),
        ('juridica', 'Persona Jurídica'),
    ]

    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='natural')
    nombre = models.CharField(max_length=100, blank=True, null=True)
    apellido = models.CharField(max_length=100, blank=True, null=True)
    razon_social = models.CharField(max_length=200, blank=True, null=True)
    rut = models.CharField(max_length=50, blank=True, null=True)
    
    email = models.EmailField()
    telefono = models.CharField(max_length=50, blank=True, null=True)
    direccion = models.CharField(max_length=200, blank=True, null=True)
    ciudad = models.CharField(max_length=100, blank=True, null=True)
    
    # CAMBIO CRÍTICO: Eliminamos 'estado' y agregamos 'activo'
    activo = models.BooleanField(default=True) 

    def __str__(self):
        if self.tipo == 'natural':
            return f"{self.nombre} {self.apellido}"
        return self.razon_social or "Sin Razón Social"

class Proyecto(models.Model):
    # Definimos las opciones posibles
    ESTADO_CHOICES = [
        ('Disponible', 'Disponible'),
        ('En Progreso', 'En Progreso'),
        ('Finalizado', 'Finalizado'),
        ('Latente', 'Latente'),
    ]
    
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    imagen = models.ImageField(upload_to='proyectos/', null=True, blank=True)
    url_referencia = models.URLField(max_length=300, blank=True, null=True)
    cliente = models.ForeignKey('Cliente', on_delete=models.SET_NULL, null=True, blank=True, related_name='proyectos')
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    # Agregamos choices y blank=True
    estado = models.CharField(
        max_length=50, 
        choices=ESTADO_CHOICES, 
        default="Disponible", 
        blank=True
    )

    def __str__(self):
        return self.nombre

class Interaccion(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='interacciones')
    fecha = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField()
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.cliente} - {self.fecha.strftime('%d/%m/%Y')}"
