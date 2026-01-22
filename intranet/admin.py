from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from .models import (
    Perfil,
    Noticia,
    CategoriaDocumento,
    DocumentoComite,
    Estamento,
    Cargo,
    UnidadFiscalia,
    Documento,
    Capacitacion,
    SocialPost,
    SocialLike,
    SocialComentario,
    Cliente, Proyecto,
    Interaccion,
)

# =========================
# ADMIN ESTAMENTO
# =========================
@admin.register(Estamento)
class EstamentoAdmin(admin.ModelAdmin):
    list_display = ("nombre",)

# =========================
# ADMIN CARGO
# =========================
@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    list_display = ("nombre",)
    search_fields = ("nombre",)

# =========================
# ADMIN UNIDAD FISCALIA
# =========================
@admin.register(UnidadFiscalia)
class UnidadFiscaliaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "estado")
    list_filter = ("estado",)
    search_fields = ("nombre",)

# =========================
# ADMIN DOCUMENTOS
# =========================
class DocumentoComiteInline(admin.TabularInline):
    model = DocumentoComite
    extra = 1
    fields = ('titulo', 'archivo')

@admin.register(CategoriaDocumento)
class CategoriaDocumentoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'orden')
    ordering = ('orden',)
    inlines = [DocumentoComiteInline]

@admin.register(DocumentoComite)
class DocumentoComiteAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'categoria', 'fecha_subida')
    list_filter = ('categoria', 'fecha_subida')
    search_fields = ('titulo',)

@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'categoria', 'fecha_subida', 'subido_por')
    list_filter = ('categoria', 'fecha_subida')
    search_fields = ('titulo',)

# =========================
# ADMIN PERFIL
# =========================
@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'fecha_nacimiento',
        'contacto_nombre',
        'contacto_telefono',
        'contacto_relacion'
    )
    search_fields = ('user__username', 'contacto_nombre')
    list_filter = ('fecha_nacimiento',)
    ordering = ('user__username',)

# =========================
# ADMIN NOTICIAS
# =========================
@admin.register(Noticia)
class NoticiaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'categoria', 'fecha')
    search_fields = ('titulo', 'categoria', 'descripcion')
    list_filter = ('categoria', 'fecha')
    ordering = ('-fecha',)

# =========================
# ADMIN CAPACITACIONES
# =========================
@admin.register(Capacitacion)
class CapacitacionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'perfil', 'institucion', 'fecha')
    search_fields = ('nombre', 'perfil__user__username', 'institucion')
    list_filter = ('fecha',)

# =========================
# ADMIN RED SOCIAL
# =========================
@admin.register(SocialPost)
class SocialPostAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'fecha', 'aprobado', 'en_logros')
    list_filter = ('aprobado', 'en_logros', 'fecha')
    search_fields = ('titulo', 'autor__username')

@admin.register(SocialLike)
class SocialLikeAdmin(admin.ModelAdmin):
    list_display = ('post', 'usuario')

@admin.register(SocialComentario)
class SocialComentarioAdmin(admin.ModelAdmin):
    list_display = ('post', 'usuario', 'fecha')

# =========================
# CUSTOM USER ADMIN
# =========================
admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'is_staff',
        'is_active'
    )
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_active')
    ordering = ('username',)

# C:\Users\Fernando\Desktop\proyecto 2026\mi_intranet\intranet\admin.py



@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    # Cambiamos 'estado' por 'activo' en las columnas visibles
    list_display = ('nombre', 'apellido', 'razon_social', 'activo') 
    
    # Cambiamos 'estado' por 'activo' en los filtros laterales
    list_filter = ('tipo', 'activo') 
    
    search_fields = ('nombre', 'apellido', 'razon_social', 'rut')

@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    # Mostramos el cliente y si tiene imagen
    list_display = ('nombre', 'cliente', 'estado', 'url_referencia')
    list_filter = ('estado', 'cliente')
    search_fields = ('nombre', 'cliente__nombre')