from django.contrib import admin

# Register your models here.
from .models import Tipo, Pagina, Documento

admin.site.register(Tipo)
admin.site.register(Pagina)
admin.site.register(Documento)
