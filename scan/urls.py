from django.conf.urls import include, url
from . import views
from django.conf.urls.static import static
from django.conf import settings

app_name='scan'

urlpatterns = [
    url(r'^$', views.home, name='home'),
]


