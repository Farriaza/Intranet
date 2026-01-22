from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required,  user_passes_test
from django.utils import timezone
from datetime import timedelta, date
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Cliente, Proyecto, Interaccion
from .forms import ClienteForm, ProyectoForm, InteraccionForm
from .models import Perfil, Noticia, Estamento, Cargo, UnidadFiscalia
from .forms import NoticiaForm, UserUpdateForm, PerfilUpdateForm, PerfilUsuarioForm
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.db.models import Q

import time
from .models import SocialPost, SocialLike, SocialComentario
from .forms import SocialPostForm
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import UnidadFiscalia, Documento
from .forms import DocumentoForm
import re
from .models import Capacitacion
from datetime import datetime
from .models import CategoriaDocumento
from .forms import DocumentoComiteForm
# LOGIN
User = get_user_model()

@login_required
def guardar_capacitacion(request):
    if request.method != "POST":
        return redirect("perfil")


    # Garantiza que el perfil exista
    perfil, _ = Perfil.objects.get_or_create(user=request.user)

    nombre = request.POST.get("nombre", "").strip()
    institucion = request.POST.get("institucion", "").strip()
    fecha = request.POST.get("fecha")
    documento = request.FILES.get("documento")

    if not nombre or not institucion or not fecha:
        messages.error(request, "Todos los campos son obligatorios.")
        return redirect("perfil")


    Capacitacion.objects.create(
        perfil=perfil,
        nombre=nombre,
        institucion=institucion,
        fecha=fecha,
        documento=documento
    )

    messages.success(request, "Capacitación agregada correctamente.")
    return redirect("perfil")


@login_required
def actualizar_perfil(request):
    if request.method == "POST":
        user = request.user
        perfil = user.perfil

        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.email = request.POST.get("email")
        user.save()

        perfil.telefono = request.POST.get("telefono")
        perfil.run = request.POST.get("run")
        perfil.fecha_nacimiento = request.POST.get("fecha_nacimiento")
        perfil.estamento_id = request.POST.get("estamento")
        perfil.cargo_id = request.POST.get("cargo")
        perfil.unidad_fiscalia_id = request.POST.get("unidad_fiscalia")

        if request.FILES.get("imagen"):
            perfil.imagen = request.FILES["imagen"]

        perfil.contacto_nombre = request.POST.get("contacto_nombre")
        perfil.contacto_relacion = request.POST.get("contacto_relacion")
        perfil.contacto_telefono = request.POST.get("contacto_telefono")

        perfil.contacto2_nombre = request.POST.get("contacto2_nombre")
        perfil.contacto2_relacion = request.POST.get("contacto2_relacion")
        perfil.contacto2_telefono = request.POST.get("contacto2_telefono")

        perfil.save()

        
        messages.success(request, "Perfil actualizado correctamente")

    return redirect("perfil")  
 
@login_required
def guardar_capacitaciones(request):
    if request.method == "POST":
        Capacitacion.objects.create(
            usuario=request.user,
            nombre=request.POST.get("nombre"),
            institucion=request.POST.get("institucion"),
            fecha=request.POST.get("fecha"),
            documento=request.FILES.get("documento")
        )

        messages.success(request, "Capacitación registrada correctamente")

    return redirect("perfil")



@login_required
def perfil_usuario(request):
    perfil = request.user.perfil

    capacitaciones = perfil.capacitaciones.all()

    return render(request, "intranet/perfil.html", {
        "ESTAMENTOS": Estamento.objects.all(),
        "CARGOS": Cargo.objects.all(),
        "UNIDADES": UnidadFiscalia.objects.all(),
        "capacitaciones": capacitaciones,  
    })



def es_admin(user):
    # Ajusta la condición según tu proyecto
    return user.is_staff or user.is_superuser
def es_super(user):
    return user.is_authenticated and user.is_superuser

def es_prensa(user):
    return user.is_authenticated and (
        user.is_superuser or user.is_staff
    )


@login_required
@user_passes_test(es_admin)
def panel_usuarios(request):
    # Procesamiento de Creación de Usuario (POST)
    if request.method == "POST":
        try:
            with transaction.atomic():
                # 1. Crear el usuario de Django
                nuevo_user = User.objects.create_user(
                    username=request.POST.get("username"),
                    first_name=request.POST.get("first_name"),
                    last_name=request.POST.get("last_name"),
                    email=request.POST.get("email"),
                    password=request.POST.get("password")
                )

                # 2. Actualizar el Perfil (usamos get porque el modelo puede tener señales)
                perfil, _ = Perfil.objects.get_or_create(user=nuevo_user)
                perfil.run = request.POST.get("run")
                perfil.telefono = request.POST.get("telefono")
                perfil.unidad_fiscalia_id = request.POST.get("unidad_fiscalia")
                perfil.cargo_id = request.POST.get("cargo")
                perfil.estamento_id = request.POST.get("estamento")
                perfil.save()
                
            return redirect('panel_usuarios')
        except Exception:
            # Aquí podrías agregar un mensaje de error con messages.error
            pass

    # Lógica de búsqueda y visualización existente
    q = request.GET.get("q", "").strip()
    usuarios = User.objects.select_related("perfil__unidad_fiscalia", "perfil__cargo").order_by("username")

    if q:
        usuarios = usuarios.filter(
            Q(username__icontains=q) | Q(first_name__icontains=q) |
            Q(last_name__icontains=q) | Q(email__icontains=q)
        )

    # Asegurar que todos tengan perfil (se recomienda mover esto a una señal post_save)
    for u in usuarios:
        Perfil.objects.get_or_create(user=u)

    # Datos adicionales para el Modal
    unidades = UnidadFiscalia.objects.all()
    cargos = Cargo.objects.all()
    estamentos = Estamento.objects.all()

    return render(request, "panel_usuarios.html", {
        "usuarios": usuarios,
        "busqueda": q,
        "unidades": unidades,
        "cargos": cargos,
        "estamentos": estamentos,
    })

@login_required
@user_passes_test(es_admin)
def editar_usuario(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    perfil, _ = Perfil.objects.get_or_create(user=user)

    if request.method == "POST":
        form = PerfilUsuarioForm(
            request.POST,
            request.FILES,
            instance=perfil
        )

        new1 = request.POST.get("new_password1")
        new2 = request.POST.get("new_password2")

        if form.is_valid():
            form.save()

            # Cambio de contraseña (solo admin)
            if new1 or new2:
                if new1 == new2:
                    user.set_password(new1)
                    user.save()
                    messages.success(request, "Contraseña actualizada correctamente.")
                else:
                    messages.error(request, "Las contraseñas no coinciden.")
                    return redirect("editar_usuario", user_id=user.id)

            messages.success(request, "Usuario actualizado correctamente.")
            return redirect("panel_usuarios")

        messages.error(request, "Hay errores en el formulario.")

    else:
        form = PerfilUsuarioForm(instance=perfil)

    return render(request, "editar_usuario.html", {
        "form": form,
        "usuario_obj": user,
    })



# INDEX

def index(request):
    return render(request, "index.html")




def inicio(request):

   
    # FILTRO DE CATEGORÍA
   
    categoria = request.GET.get("categoria", "todos")

    noticias_list = Noticia.objects.all().order_by("-fecha")

    if categoria != "todos":
        noticias_list = noticias_list.filter(categoria__iexact=categoria)

    noticias_categoria_completa = (
        Noticia.objects.filter(categoria__iexact=categoria).order_by("-fecha")
        if categoria != "todos"
        else Noticia.objects.all().order_by("-fecha")
    )

   
    # PAGINACIÓN
   
    paginator = Paginator(noticias_list, 2)
    page_number = request.GET.get("pagina")
    noticias = paginator.get_page(page_number)

   
    # CUMPLEAÑOS
   
    hoy = date.today()

    cumple_hoy = Perfil.objects.filter(
        fecha_nacimiento__month=hoy.month,
        fecha_nacimiento__day=hoy.day
    )

    cumples_mes = Perfil.objects.filter(
        fecha_nacimiento__month=hoy.month
    ).order_by("fecha_nacimiento__day")

    todos_cumples = Perfil.objects.exclude(
        fecha_nacimiento__isnull=True
    ).order_by("fecha_nacimiento__month", "fecha_nacimiento__day")

   
    # LOGROS (LO QUE FALTABA)
   
    logros = SocialPost.objects.filter(
        aprobado=True,
        en_logros=True,
        imagen__isnull=False
    ).exclude(imagen="").order_by("-fecha")[:5]

   
    # RECURSOS RÁPIDOS
   
    modulos_rapidos = [
        {"id": 1, "nombre": "COMITE PARITARIO", "url": "http://172.17.215.13/intranet/web/remote.php?accion=comite_paritario", "imagen": "if1.jpg"},
        {"id": 2, "nombre": "MALS", "url": "http://fnintranet/unidades/mals/mals2020_.html", "imagen": "if2.jpg"},
        {"id": 3, "nombre": "BUENAS PRACTICAS", "url": "http://172.17.215.13/intranet/web/remote.php?accion=buenas_practicas", "imagen": "if3.jpg"},
        {"id": 4, "nombre": "CONSULTAS JURIDICAS", "url": "https://reportes.cl", "imagen": "if4.jpg"},
        {"id": 5, "nombre": "REGLAMENTO DE RESPONSABILIDAD", "url": "https://documentos.cl", "imagen": "if5.jpg"},
        {"id": 6, "nombre": "PLAN DE CONTINGENCIA SIAU", "url": "http://172.17.215.13/intranet/web/remote.php?accion=plan_contigencia", "imagen": "if6.jpg"},
        {"id": 7, "nombre": "BIENESTAR", "url": "http://172.18.1.193/rrhh/index.php?option=com_content&view=section&id=20&Itemid=529", "imagen": "if8.png"},
        {"id": 8, "nombre": "PLAN DE EVACUACIÓN", "url": "http://172.17.215.13/intranet/web/remote.php?accion=plan_evacuacion", "imagen": "if7.png"},
    ]

 
    return render(request, "inicio.html", {

        # Noticias
        "noticias": noticias,
        "categoria": categoria,
        "noticias_categoria_completa": noticias_categoria_completa,

        # Cumpleaños
        "cumple_hoy": cumple_hoy,
        "cumples_mes": cumples_mes,
        "todos_cumples": todos_cumples,

        # Logros (AHORA SÍ)
        "logros": logros,

        # Módulos rápidos
        "modulos_rapidos": modulos_rapidos,

        # Catálogos
        "ESTAMENTOS": Estamento.objects.all(),
        "CARGOS": Cargo.objects.all(),
        "UNIDADES": UnidadFiscalia.objects.all(),
    })




# CREAR PERFIL AUTOMÁTICO

@receiver(post_save, sender=User)
def crear_perfil(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.get_or_create(user=instance)



# REGISTRO

def register_usuario(request):
    if request.method == "POST":

        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        area = request.POST.get("area")
        telefono = request.POST.get("telefono")

        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            messages.error(request, "Las contraseñas no coinciden.")
            return redirect("/")

        if len(password1) < 8:
            messages.error(request, "La contraseña debe tener mínimo 8 caracteres.")
            return redirect("/")

        if User.objects.filter(username=username).exists():
            messages.error(request, "El usuario ya existe.")
            return redirect("/")

        if User.objects.filter(email=email).exists():
            messages.error(request, "El correo ya está registrado.")
            return redirect("/")

        # Crear usuario y perfil
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password1
        )

        Perfil.objects.create(
            user=user,
            area=area,
            telefono=telefono
        )

        messages.success(request, "¡Registro exitoso! Ya puedes iniciar sesión.")
        return redirect("/")

    return redirect("/")



login_attempts = {}  # mantener en RAM

MAX_INTENTOS = 3
BLOQUEO_MINUTOS = 2




def login_usuario(request):

    if request.method != "POST":
        return redirect("/")

    username = request.POST.get("username", "").strip()
    password = request.POST.get("password", "").strip()
    remember = request.POST.get("remember_me")

    # ==============================
    # 1. VALIDAR BLOQUEO
    # ==============================

    user_data = login_attempts.get(username, {
        "intentos": 0,
        "bloqueado": False,
    })

    if user_data.get("bloqueado"):
        if timezone.now() < user_data["desbloqueo"]:
            minutos = int(
                (user_data["desbloqueo"] - timezone.now()).total_seconds() // 60
            )
            messages.error(
                request,
                f"Cuenta bloqueada. Intenta nuevamente en {minutos} minuto(s)."
            )
            return redirect("/")
        else:
            user_data = {"intentos": 0, "bloqueado": False}
            login_attempts[username] = user_data

    # ==============================
    # 2. AUTENTICACIÓN DJANGO
    # ==============================

    user = authenticate(request, username=username, password=password)

    if user is not None:
        login_attempts.pop(username, None)
        login(request, user)

        request.session.set_expiry(
            0 if not remember else 60 * 60 * 24 * 7
        )

        return redirect("inicio")

    # ==============================
    # 3. INTENTOS FALLIDOS
    # ==============================

    user_data["intentos"] += 1

    if user_data["intentos"] >= MAX_INTENTOS:
        user_data["bloqueado"] = True
        user_data["desbloqueo"] = timezone.now() + timedelta(
            minutes=BLOQUEO_MINUTOS
        )
        messages.error(
            request,
            f"Cuenta bloqueada por {BLOQUEO_MINUTOS} minutos."
        )
    else:
        restantes = MAX_INTENTOS - user_data["intentos"]
        messages.error(
            request,
            f"Credenciales incorrectas. Intentos restantes: {restantes}"
        )

    login_attempts[username] = user_data
    return redirect("/")



# LOGOUT

def logout_view(request):
    logout(request)
    return redirect("index")









# SIMPLES RENDERS

def sistema(request): return render(request, "sistema.html")
def cliente(request): return render(request, "cliente.html")
def campanas(request): return render(request, "campanas.html")
def unidades(request): return render(request, "unidades.html")

def informacion(request): return render(request, "informacion.html")
def multimedia(request): return render(request, "multimedia.html")



# INSTITUCIONES

def instituciones(request):
    return render(request, "instituciones.html", {
        "comisarias": Comisaria.objects.all(),
        "fiscalias": Fiscalia.objects.all(),
        "juzgados": Juzgado.objects.all(),
    })



# PRENSA

@login_required
@user_passes_test(es_super)
def prensa_panel(request):
    noticias = Noticia.objects.all().order_by("-fecha")
    return render(request, "prensa/panel.html", {"noticias": noticias})



@login_required
def agregar_noticia(request):
    if request.method == "POST":
        form = NoticiaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("prensa_panel")
    else:
        form = NoticiaForm()

    return render(request, "prensa/agregar.html", {"form": form})


@login_required
def editar_noticia(request, id):
    noticia = Noticia.objects.get(id=id)
    form = NoticiaForm(request.POST or None, request.FILES or None, instance=noticia)

    if form.is_valid():
        form.save()
        return redirect("prensa_panel")

    return render(request, "prensa/editar.html", {"form": form})


@login_required
def eliminar_noticia(request, id):
    Noticia.objects.get(id=id).delete()
    return redirect("prensa_panel")


def noticia_detalle(request, slug):
    noticia = get_object_or_404(Noticia, slug=slug)

    return render(request, "noticias/detalle.html", {
        "noticia": noticia
    })


def noticias_listado(request):
    categoria = request.GET.get("categoria")
    query = request.GET.get("q", "").strip()

    noticias = Noticia.objects.all().order_by("-fecha")

    if categoria:
        noticias = noticias.filter(categoria=categoria)

    if query:
        # Búsqueda por texto
        texto_filtro = Q(titulo__icontains=query) | Q(descripcion__icontains=query)

        # Buscar números en la query
        numeros = [int(n) for n in re.findall(r'\d+', query)]

        fecha_filtro = Q()
        for n in numeros:       
            if 1 <= n <= 31:
                fecha_filtro |= Q(fecha__day=n)
            if 1 <= n <= 12:
                fecha_filtro |= Q(fecha__month=n)
            if n > 31:
                fecha_filtro |= Q(fecha__year=n)

        # Combinar filtros de texto y fecha
        if fecha_filtro:
            noticias = noticias.filter(texto_filtro | fecha_filtro)
        else:
            noticias = noticias.filter(texto_filtro)

    categorias = Noticia.CATEGORIAS

    return render(request, "noticias/listado.html", {
        "noticias": noticias,
        "categorias": categorias,
        "categoria_activa": categoria,
        "query": query,
    })


# SISTEMAS VIEW (REGIONALES - NACIONALES)

def sistemas_view(request):

    regionales = [
    ]

    nacionales = [
       
    ]

    paneles = [
    ]

    municipalidades = [
    
      ]

    return render(request, "sistema.html", {
        "regionales": regionales,
        "nacionales": nacionales,
        "paneles": paneles,
        "municipalidades": municipalidades,
    })




@login_required
def social_instagram(request):
    posts = SocialPost.objects.filter(aprobado=True).order_by("-fecha")
    historias = posts[:10]

    liked_ids = set(
        SocialLike.objects.filter(usuario=request.user, post__in=posts)
        .values_list("post_id", flat=True)
    )

    form = SocialPostForm()

    return render(request, "social/instagram.html", {
        "posts": posts,
        "historias": historias,
        "liked_ids": liked_ids,
        "form": form,
    })


@login_required
def social_subir(request):

    if request.method == "POST":
        titulo = request.POST.get("titulo", "").strip()
        texto_logro = request.POST.get("texto_logro", "").strip() or None
        archivo = request.FILES.get("archivo")
        en_logros = request.POST.get("en_logros") == "on"

        if not archivo:
            messages.error(request, "Debe subir una imagen o video.")
            return redirect("social_subir")

        es_imagen = archivo.content_type.startswith("image")
        es_video = archivo.content_type.startswith("video")

        if not (es_imagen or es_video):
            messages.error(request, "Formato no permitido.")
            return redirect("social_subir")

        post = SocialPost.objects.create(
            autor=request.user,
            titulo=titulo,
            texto_logro=texto_logro,  
            aprobado=False,
            en_logros=en_logros
        )

        if es_imagen:
            post.imagen = archivo
        else:
            post.video = archivo

        post.save()

        messages.success(request, "Su publicación fue enviada para revisión.")
        return redirect("social_instagram")

    return render(request, "social/subir.html")





@login_required
def social_like_toggle(request, post_id):
    post = get_object_or_404(SocialPost, pk=post_id, aprobado=True)
    like, created = SocialLike.objects.get_or_create(post=post, usuario=request.user)

    if not created:
        like.delete()
        liked = False
    else:
        liked = True

    return JsonResponse({
        "liked": liked,
        "total_likes": post.total_likes()
    })


@login_required
def social_comentar(request, post_id):
    if request.method == "POST":
        texto = request.POST.get("texto")
        if texto:
            SocialComentario.objects.create(post_id=post_id, usuario=request.user, texto=texto)
    return redirect("social_home")



@staff_member_required
def social_moderar(request):
    pendientes = SocialPost.objects.filter(aprobado=False).order_by("-fecha")
    return render(request, "social/moderacion.html", {"pendientes": pendientes})


@staff_member_required
def social_aprobar(request, post_id):
    post = get_object_or_404(SocialPost, pk=post_id)
    post.aprobado = True
    post.save()
    return redirect("social_moderar")


@staff_member_required
def social_rechazar(request, post_id):
    post = get_object_or_404(SocialPost, pk=post_id)
    post.delete()
    return redirect("social_moderar")



def tiempo_relativo(fecha):
    diferencia = now() - fecha

    if diferencia < timedelta(minutes=1):
        return "Hace unos segundos"
    elif diferencia < timedelta(hours=1):
        minutos = int(diferencia.seconds / 60)
        return f"Hace {minutos} minuto{'s' if minutos != 1 else ''}"
    elif diferencia < timedelta(days=1):
        horas = int(diferencia.seconds / 3600)
        return f"Hace {horas} hora{'s' if horas != 1 else ''}"
    elif diferencia < timedelta(days=2):
        return "Ayer"
    elif diferencia < timedelta(days=7):
        dias = diferencia.days
        return f"Hace {dias} día{'s' if dias != 1 else ''}"
    elif diferencia < timedelta(days=30):
        semanas = int(diferencia.days / 7)
        return f"Hace {semanas} semana{'s' if semanas != 1 else ''}"
    elif diferencia < timedelta(days=365):
        meses = int(diferencia.days / 30)
        return f"Hace {meses} mes{'es' if meses != 1 else ''}"
    else:
        años = int(diferencia.days / 365)
        return f"Hace {años} año{'s' if años != 1 else ''}"


def obtener_comentarios(request, post_id):
    post = get_object_or_404(SocialPost, id=post_id)

    comentarios = post.comentarios.order_by("fecha")

    data = [
        {
            "usuario": c.usuario.username,
            "texto": c.texto,
            "fecha": tiempo_relativo(c.fecha),
        }
        for c in comentarios
    ]

    return JsonResponse(data, safe=False)


@csrf_exempt
def social_reaction(request, post_id):
    post = get_object_or_404(SocialPost, id=post_id)

    like, created = SocialLike.objects.get_or_create(
        post=post,
        usuario=request.user
    )

    if not created:
        like.delete()
        liked = False
    else:
        liked = True

    total = post.likes.count()

    return JsonResponse({
        "liked": liked,
        "total_likes": total
    })


@login_required
def social_eliminar(request, post_id):
    post = get_object_or_404(SocialPost, id=post_id)

    # Permisos: autor o administrador
    if request.user != post.autor and not request.user.is_staff:
        return HttpResponseForbidden(
            "No tienes permiso para eliminar esta publicación."
        )

    post.delete()
    messages.success(request, "La publicación fue eliminada correctamente.")
    return redirect("social_home") 


@login_required
def documentos(request):

    # 🔍 Buscador
    query = request.GET.get("q", "").strip()

    documentos = Documento.objects.all().order_by("categoria", "titulo")

    if query:
        documentos = documentos.filter(
            Q(titulo__icontains=query)
        )

    documentos_por_categoria = {
        Documento.Categoria.REGLAMENTOS: documentos.filter(
            categoria=Documento.Categoria.REGLAMENTOS
        ),
        Documento.Categoria.PROCESOS: documentos.filter(
            categoria=Documento.Categoria.PROCESOS
        ),
        Documento.Categoria.BIENESTAR: documentos.filter(
            categoria=Documento.Categoria.BIENESTAR
        ),
    }

    # ⬆️ Subida de documentos
    if request.method == "POST" and request.user.is_staff:
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.subido_por = request.user         
            doc.save()
            return redirect("documentos")
    else:
        form = DocumentoForm()

    return render(request, "documentos/documentos.html", {
        "documentos_por_categoria": documentos_por_categoria,
        "form": form,
        "query": query,  # ← para mantener el texto en el buscador
    })

@user_passes_test(lambda u: u.is_staff)
def eliminar_documento(request, doc_id):
    documento = get_object_or_404(Documento, id=doc_id)
    documento.delete()
    return redirect("documentos")


@login_required
def comite_paritario(request):

    if request.method == 'POST':
        form = DocumentoComiteForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('comite_paritario')
    else:
        form = DocumentoComiteForm()

    categorias = (
        CategoriaDocumento.objects
        .prefetch_related('documentos')
        .order_by('orden')
    )

    return render(request, 'comite_paritario.html', {
        'categorias': categorias,
        'form': form
    })





@login_required
def organigrama_empresa(request):
    # Traemos todos los perfiles
    todos = Perfil.objects.select_related("user", "cargo").all()

    # CAMBIO CLAVE: Buscamos por el nombre real de tu base de datos
    # Si el cargo se llama "UNIDAD FISCALIA", ponlo aquí:
    ceo = todos.filter(cargo__nombre__icontains="UNIDAD FISCALIA").first()
    
    # Si no encuentra nada con "UNIDAD FISCALIA", intentamos con "CEO" como backup
    if not ceo:
        ceo = todos.filter(cargo__nombre__icontains="CEO").first()

    # El equipo es todo el resto, excluyendo al que encontramos arriba
    equipo = todos.exclude(id=ceo.id if ceo else None).order_by("user__last_name")

    return render(request, "intranet/personal.html", {
        "ceo": ceo,
        "equipo": equipo,
    })




def documentos_comite(request):
    categorias = CategoriaDocumento.objects.prefetch_related("documentos")
    return render(request, "documentos_comite.html", {
        "categorias": categorias
    })


def panel_clientes(request):
    # Traemos todos los clientes ordenados por nombre
    clientes = Cliente.objects.all().order_by('nombre')
    
    cliente_id = request.GET.get('cliente')
    cliente_seleccionado = None
    proyectos = []
    interacciones = []

    if cliente_id:
        # Usamos filter().first() para evitar errores si el ID no existe
        cliente_seleccionado = Cliente.objects.filter(pk=cliente_id).first()
        
        if cliente_seleccionado:
            # Forzamos recarga de DB para asegurar el estado más reciente de 'activo'
            cliente_seleccionado.refresh_from_db()
            proyectos = cliente_seleccionado.proyectos.all()
            interacciones = cliente_seleccionado.interacciones.all()

    context = {
        'clientes': clientes,
        'cliente_seleccionado': cliente_seleccionado,
        'proyectos': proyectos,
        'interacciones': interacciones,
        'form': ClienteForm(),
    }
    return render(request, 'cliente.html', context)

def eliminar_cliente(request, cliente_id):
    """
    Esta función no borra, cambia el estado de ACTIVO a INACTIVO y viceversa.
    """
    cliente = get_object_or_404(Cliente, pk=cliente_id)
    
    # Verificamos que el atributo exista para evitar el AttributeError
    if hasattr(cliente, 'activo'):
        cliente.activo = not cliente.activo
        cliente.save()
    else:
        # Log de error para el arquitecto en la consola
        print(f"DEBUG: El modelo Cliente no tiene el atributo 'activo'. Revisa las migraciones.")
        
    return redirect(f'/cliente/?cliente={cliente_id}')

def agregar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            # Validaciones lógicas según el tipo de persona
            tipo = form.cleaned_data.get('tipo')
            if tipo == 'natural' and (not form.cleaned_data.get('nombre') or not form.cleaned_data.get('apellido')):
                form.add_error(None, "Nombre y Apellido son requeridos para Persona Natural")
            elif tipo == 'juridica' and (not form.cleaned_data.get('razon_social') or not form.cleaned_data.get('rut')):
                form.add_error(None, "Razón Social y RUT son requeridos para Persona Jurídica")

            if not form.errors:
                form.save()
                return redirect('cliente')
    else:
        form = ClienteForm()

    return render(request, 'clientes/form_cliente.html', {'form': form, 'cliente': None})

def editar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, pk=cliente_id)
    
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            # Redirigimos al panel con el cliente aún seleccionado para ver los cambios
            return redirect(f'/cliente/?cliente={cliente_id}') 
    else:
        form = ClienteForm(instance=cliente)
    
    return render(request, 'clientes/editar_cliente.html', {
        'form': form,
        'cliente': cliente,
        'titulo': f"Editar Cliente: {cliente.nombre}"
    })

def eliminar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, pk=cliente_id)
    
    # FORMA SEGURA: Negación booleana explícita
    cliente.activo = not cliente.activo 
    
    cliente.save()
    
    # Forzamos la redirección para limpiar el estado de la request
    return redirect(f'/cliente/?cliente={cliente_id}')

# intranet/views.py
def agregar_proyecto(request):
    if request.method == 'POST':
        form = ProyectoForm(request.POST)
        if form.is_valid():
            proyecto = form.save()
            # Redirigimos al detalle del cliente al que le asignamos el proyecto
            return redirect(f'/cliente/?cliente={proyecto.cliente.id}')
    else:
        # Si pasas un ID de cliente por la URL, lo pre-seleccionamos
        cliente_id = request.GET.get('cliente_id')
        form = ProyectoForm(initial={'cliente': cliente_id}) if cliente_id else ProyectoForm()
    
    return render(request, 'proyecto_form.html', {'form': form})

def agregar_proyecto(request, pk=None):
    proyecto = get_object_or_404(Proyecto, pk=pk) if pk else None
    
    if request.method == 'POST':
        form = ProyectoForm(request.POST, request.FILES, instance=proyecto)
        if form.is_valid():
            form.save()
            # Redirigimos al nombre definido en urls.py
            return redirect('gestion_catalogo')
    else:
        form = ProyectoForm(instance=proyecto)
    
    proyectos_todos = Proyecto.objects.all().order_by('-id')
    return render(request, 'proyecto_form.html', {
        'form': form,
        'proyectos_todos': proyectos_todos,
    })
    
def gestion_catalogo(request, pk=None):
    proyecto = get_object_or_404(Proyecto, pk=pk) if pk else None
    
    if request.method == 'POST':
        form = ProyectoForm(request.POST, request.FILES, instance=proyecto)
        if form.is_valid():
            form.save()
            messages.success(request, "Proyecto guardado correctamente.")
            return redirect('gestion_catalogo')
    else:
        form = ProyectoForm(instance=proyecto)
    
    proyectos_todos = Proyecto.objects.all().order_by('-id')
    return render(request, 'proyecto_form.html', {
        'form': form,
        'proyectos_todos': proyectos_todos,
        'editando': pk is not None
    })

def eliminar_proyecto(request, pk):
    proyecto = get_object_or_404(Proyecto, pk=pk)
    proyecto.delete()
    messages.warning(request, "Proyecto eliminado.")
    return redirect('gestion_catalogo')