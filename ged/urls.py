from django.conf.urls import include, url
from . import views
from django.conf.urls.static import static
from django.conf import settings

app_name='ged'

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^(?P<pk>\d+)/livro/$', views.home_livro, name='home_livro'),
    url(r'^(?P<pk>\d+)/tipo/$', views.home_tipo, name='home_tipo'),
    url(r'^busca/$', views.home_busca, name='home_busca'),
    url(r'^tipo/new/$', views.tipo_new, name='tipo_new'),
    url(r'^tipo/list/$', views.tipo_list, name='tipo_list'),
    url(r'^tipo/(?P<pk>\d+)/edit/$', views.tipo_edit, name='tipo_edit'),
    url(r'^tipo/(?P<pk>\d+)/del/$', views.tipo_del, name='tipo_del'),    
    url(r'^empresa$', views.empresar, name='empresa'),
    url(r'^empresa_edit$', views.empresa, name='empresa_edit'),
    url(r'^livro/new/$', views.livro_new, name='livro_new'),
    url(r'^livro/list/$', views.livro_list, name='livro_list'),
    url(r'^livro/(?P<pk>\d+)/edit/$', views.livro_edit, name='livro_edit'),
    url(r'^livro/(?P<pk>\d+)/del/$', views.livro_del, name='livro_del'),
    # url(r'^pagina/new/$', views.pagina_new, name='pagina_new'),
    url(r'^pagina/list/$', views.pagina_list, name='pagina_list'),
    url(r'^pagina/(?P<pk>\d+)/edit/$', views.pagina_edit, name='pagina_edit'),
    url(r'^pagina/paginacao/$', views.paginacao, name='paginacao'),
    url(r'^pagina/(?P<pk>\d+)/edite/$', views.pagina_edit_e, name='pagina_edit_e'),
    url(r'^pagina/editp/$', views.pagina_edit_p, name='pagina_edit_p'),
    url(r'^pagina/(?P<livro_pk>\d+)/new/$', views.pagina_new, name='pagina_new_livro'),
    url(r'^pagina/(?P<tipo_pk>\d+)/new_tipo/$', views.pagina_new_tipo, name='pagina_new_tipo'),
    url(r'^pagina/(?P<pk>\d+)/del/$', views.pagina_del, name='pagina_del'),
    url(r'^backup_list/$', views.backup_list, name='backup_list'),
    url(r'^backup/$', views.backup, name='backup'),
    # url(r'^pagina/new/$', views.pagina_newj, name='pagina_new'),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STORAGE_URL, document_root=settings.STORAGE_ROOT)
    urlpatterns += static(settings.RESOURCES_URL, document_root=settings.RESOURCES_ROOT)