from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from . import views


app_name="login"
urlpatterns = [
	url(r'^login/$', views.login, name='login'),
	url(r'^logout/$', views.logout, name='logout'),
	url(r'^signup/$', views.signup, name='signup'),
	url(r'^list/$', views.list, name='list'),
	url(r'^user/(?P<pk>\d+)/edit/$', views.edit, name='edit'),
  url(r'^user/(?P<pk>\d+)/del/$', views.delete, name='delete'),    
]