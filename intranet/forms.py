from django import forms
from django.contrib.auth.models import User
from .models import Documento
import os
from django.core.exceptions import ValidationError
from .models import (
    Perfil,
    Noticia,
    SocialPost,
    DocumentoComite,
    Estamento,
    Cargo,
    UnidadFiscalia,
)

from django import forms
from .models import Cliente, Proyecto, Interaccion

# ACTUALIZAR USUARIO (perfil propio - SOLO User)


class UserUpdateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]

        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }

        error_messages = {
            "first_name": {"required": "Debe ingresar su nombre."},
            "last_name": {"required": "Debe ingresar su apellido."},
            "email": {
                "required": "Debe ingresar su correo institucional.",
                "invalid": "Ingrese un correo electrónico válido.",
            },
        }



# ACTUALIZAR PERFIL (perfil propio - SOLO Perfil)


class PerfilUpdateForm(forms.ModelForm):

    fecha_nacimiento = forms.DateField(
        required=False,
        widget=forms.DateInput(
            format="%Y-%m-%d",
            attrs={"type": "date", "class": "form-control"},
        ),
        input_formats=["%Y-%m-%d"],
    )

    class Meta:
        model = Perfil
        fields = [
            "imagen",
            "fecha_nacimiento",
            "telefono",
            "run",

            "estamento",
            "cargo",
            "unidad_fiscalia",

            "contacto_nombre",
            "contacto_telefono",
            "contacto_relacion",

            "contacto2_nombre",
            "contacto2_telefono",
            "contacto2_relacion",
        ]

        widgets = {
            "telefono": forms.TextInput(attrs={"class": "form-control"}),

            "estamento": forms.Select(attrs={"class": "form-select"}),
            "cargo": forms.Select(attrs={"class": "form-select"}),
            "unidad_fiscalia": forms.Select(attrs={"class": "form-select"}),

            "contacto_nombre": forms.TextInput(attrs={"class": "form-control"}),
            "contacto_telefono": forms.TextInput(attrs={"class": "form-control"}),
            "contacto_relacion": forms.TextInput(attrs={"class": "form-control"}),

            "contacto2_nombre": forms.TextInput(attrs={"class": "form-control"}),
            "contacto2_telefono": forms.TextInput(attrs={"class": "form-control"}),
            "contacto2_relacion": forms.TextInput(attrs={"class": "form-control"}),
        }

    def clean(self):
        cleaned = super().clean()

        c2_nombre = cleaned.get("contacto2_nombre")
        c2_tel = cleaned.get("contacto2_telefono")
        c2_rel = cleaned.get("contacto2_relacion")

        if any([c2_nombre, c2_tel, c2_rel]) and not all([c2_nombre, c2_tel, c2_rel]):
            raise forms.ValidationError(
                "Si ingresa un segundo contacto de emergencia, debe completar todos sus campos."
            )

        return cleaned



# FORM UNIFICADO (ADMIN edita User + Perfil)


class PerfilUsuarioForm(forms.ModelForm):

    # -------- CAMPOS DE USER --------
    first_name = forms.CharField(
        label="Nombre",
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        error_messages={"required": "Debe ingresar el nombre del usuario."},
    )

    last_name = forms.CharField(
        label="Apellido",
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        error_messages={"required": "Debe ingresar el apellido del usuario."},
    )

    email = forms.EmailField(
        label="Correo electrónico",
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-control"}),
        error_messages={
            "required": "Debe ingresar un correo electrónico.",
            "invalid": "Ingrese un correo electrónico válido.",
        },
    )

    is_active = forms.BooleanField(
        label="Usuario activo",
        required=False,
    )

    # FIX DEFINITIVO
    fecha_nacimiento = forms.DateField(
        required=False,
        widget=forms.DateInput(
            format="%Y-%m-%d",
            attrs={"type": "date", "class": "form-control"},
        ),
        input_formats=["%Y-%m-%d"],
    )

    class Meta:
        model = Perfil
        fields = [
            "imagen",
            "fecha_nacimiento",
            "telefono",
            "run",

            "estamento",
            "cargo",
            "unidad_fiscalia",

            "contacto_nombre",
            "contacto_telefono",
            "contacto_relacion",

            "contacto2_nombre",
            "contacto2_telefono",
            "contacto2_relacion",
        ]

        widgets = {
            "telefono": forms.TextInput(attrs={"class": "form-control"}),

            "estamento": forms.Select(attrs={"class": "form-select"}),
            "cargo": forms.Select(attrs={"class": "form-select"}),
            "unidad_fiscalia": forms.Select(attrs={"class": "form-select"}),

            "contacto_nombre": forms.TextInput(attrs={"class": "form-control"}),
            "contacto_telefono": forms.TextInput(attrs={"class": "form-control"}),
            "contacto_relacion": forms.TextInput(attrs={"class": "form-control"}),

            "contacto2_nombre": forms.TextInput(attrs={"class": "form-control"}),
            "contacto2_telefono": forms.TextInput(attrs={"class": "form-control"}),
            "contacto2_relacion": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and getattr(self.instance, "user", None):
            user = self.instance.user
            self.fields["first_name"].initial = user.first_name
            self.fields["last_name"].initial = user.last_name
            self.fields["email"].initial = user.email
            self.fields["is_active"].initial = user.is_active

    def clean(self):
        cleaned = super().clean()

        c2_nombre = cleaned.get("contacto2_nombre")
        c2_tel = cleaned.get("contacto2_telefono")
        c2_rel = cleaned.get("contacto2_relacion")

        if any([c2_nombre, c2_tel, c2_rel]) and not all([c2_nombre, c2_tel, c2_rel]):
            raise forms.ValidationError(
                "Si ingresa un segundo contacto de emergencia, debe completar todos sus campos."
            )

        return cleaned

    def save(self, commit=True):
        perfil = super().save(commit=False)
        user = perfil.user

        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        user.is_active = self.cleaned_data.get("is_active", True)

        if commit:
            user.save()
            perfil.save()

        return perfil



# NOTICIAS


class NoticiaForm(forms.ModelForm):

    class Meta:
        model = Noticia
        fields = ["titulo", "categoria", "descripcion", "imagen", "link"]

        widgets = {
            "titulo": forms.TextInput(attrs={"class": "form-control"}),
            "categoria": forms.Select(attrs={"class": "form-select"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control"}),
            "link": forms.URLInput(attrs={"class": "form-control"}),
        }



# SOCIAL POST


class SocialPostForm(forms.ModelForm):

    class Meta:
        model = SocialPost
        fields = ["titulo", "imagen", "video"]

class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ["categoria", "titulo", "archivo"]

    def clean_archivo(self):
        archivo = self.cleaned_data.get('archivo')
        if archivo:
            ext = os.path.splitext(archivo.name)[1].lower()
            valid_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']
            if ext not in valid_extensions:
                raise ValidationError(
                    f"Tipo de archivo no permitido. Solo se permiten: {', '.join(valid_extensions)}"
                )
        return archivo

class DocumentoComiteForm(forms.ModelForm):
    class Meta:
        model = DocumentoComite
        fields = ['categoria', 'titulo', 'archivo']

        widgets = {
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título del documento'
            }),
            'archivo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


# C:\Users\Fernando\Desktop\proyecto 2026\mi_intranet\intranet\forms.py

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [
            'tipo', 'nombre', 'apellido', 'razon_social', 'rut', 
            'email', 'telefono', 'direccion', 'ciudad', 'activo' # <-- CAMBIO AQUÍ
        ]

class ProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = ['cliente', 'nombre', 'descripcion', 'fecha_inicio', 'fecha_fin', 'estado']

class InteraccionForm(forms.ModelForm):
    class Meta:
        model = Interaccion
        fields = ['cliente', 'descripcion', 'usuario']

# intranet/forms.py
class ProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = ['cliente', 'nombre', 'descripcion', 'imagen', 'url_referencia', 'fecha_inicio', 'fecha_fin', 'estado']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'url_referencia': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'fecha_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-select'}), # Ahora leerá los CHOICES del modelo
        }