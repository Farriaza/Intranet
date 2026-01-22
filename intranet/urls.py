from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import noticias_listado, noticia_detalle
from .views import comite_paritario 
urlpatterns = [

   
    path('', views.index, name='index'),
    path('inicio/', views.inicio, name='inicio'),
    path('perfil/actualizar/', views.actualizar_perfil, name='actualizar_perfil'),
    path("perfil/", views.perfil_usuario, name="perfil"),
    path("perfil/capacitacion/guardar/", views.guardar_capacitacion, name="guardar_capacitacion"),
    path("register/", views.register_usuario, name="register"),
    path("login_usuario/", views.login_usuario, name="login_usuario"),
    path("logout/", views.logout_view, name="logout"),
    path("sistema/", views.sistemas_view, name="sistema"),
    #path('campanas/', views.campanas, name='campanas'),
    path('personal/', views.organigrama_empresa, name='personal'),

    path('informacion/', views.informacion, name='informacion'),
    path('instituciones/', views.instituciones, name='instituciones'),
    path('multimedia/', views.multimedia, name='multimedia'),
    path( 'password_reset/',auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'),name='password_reset'),
    path('password_reset_done/',auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path( 'reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/',auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    path("prensa/", views.prensa_panel, name="prensa_panel"),
    path("prensa/agregar/", views.agregar_noticia, name="agregar_noticia"),
    path("prensa/editar/<int:id>/", views.editar_noticia, name="editar_noticia"),
    path("prensa/eliminar/<int:id>/", views.eliminar_noticia, name="eliminar_noticia"),
    path("noticias/", noticias_listado, name="noticias_listado"),
    path("noticias/<slug:slug>/", noticia_detalle, name="noticia_detalle"), 
    path("usuarios/panel/", views.panel_usuarios, name="panel_usuarios"),
    path("usuarios/<int:user_id>/editar/", views.editar_usuario, name="editar_usuario"),   
    path("social/", views.social_instagram, name="social_instagram"),
    path("social/", views.social_instagram, name="social_home"),
    path("social/like/<int:post_id>/", views.social_like_toggle, name="social_like"),    
    path("social/comentar/<int:post_id>/", views.social_comentar, name="social_comentar"),
    path("social/subir/", views.social_subir, name="social_subir"),
    path("social/feed/", views.social_instagram, name="social_feed"),
    path("social/moderar/", views.social_moderar, name="social_moderar"),
    path("social/moderar/aprobar/<int:post_id>/", views.social_aprobar, name="social_aprobar"),
    path("social/moderar/rechazar/<int:post_id>/", views.social_rechazar, name="social_rechazar"),
    path("eliminar/<int:post_id>/", views.social_eliminar, name="social_eliminar"),
    path('comite-paritario/', comite_paritario, name='comite_paritario'),
    path("documentos/", views.documentos, name="documentos"),
    path("documentos/eliminar/<int:doc_id>/",views.eliminar_documento, name="eliminar_documento" ),
    path("comite-paritario/", views.comite_paritario, name="comite_paritario"), 
path('proyecto/nuevo/', views.agregar_proyecto, name='gestion_catalogo'), 
    path('proyecto/editar/<int:pk>/', views.agregar_proyecto, name='editar_proyecto'),
    path('proyecto/eliminar/<int:pk>/', views.eliminar_proyecto, name='eliminar_proyecto'),
    path('cliente/', views.panel_clientes, name='cliente'),
    path('agregar/', views.agregar_cliente, name='agregar_cliente'),
    path('editar/<int:cliente_id>/', views.editar_cliente, name='editar_cliente'),
    path('cliente/eliminar/<int:cliente_id>/', views.eliminar_cliente, name='eliminar_cliente'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
