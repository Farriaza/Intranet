from django import template
import os

register = template.Library()

@register.filter
def extension(value):
    """Devuelve la extensión del archivo en minúsculas sin el punto"""
    if not value:
        return ''
    name, ext = os.path.splitext(str(value))
    return ext[1:].lower()  # elimina el punto

@register.filter
def icono_documento(value):
    """Devuelve la clase del icono según la extensión"""
    ext = extension(value)
    if ext == "pdf":
        return "bi bi-file-earmark-pdf text-danger"
    elif ext in ["doc", "docx"]:
        return "bi bi-file-earmark-word text-primary"
    elif ext in ["xls", "xlsx"]:
        return "bi bi-file-earmark-excel text-success"
    elif ext in ["ppt", "pptx"]:
        return "bi bi-file-earmark-powerpoint text-warning"
    else:
        return "bi bi-file-earmark-text"
