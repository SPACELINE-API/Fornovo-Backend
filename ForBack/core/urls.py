from django.contrib import admin
from django.urls import include, path
from django.conf import settings # Importa o settings.py
from django.conf.urls.static import static # Serve para o uso do /media durante o desenvolvimento

urlpatterns = [
    path('admin', admin.site.urls),
    # Rota para a aplicação de cálculos, projetos e usuarios:
    path('calculos/', include('apps.calculos.urls')),
    path('projetos/', include('apps.projetos.urls')),
    path('usuarios/',include('apps.usuarios.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # Configura pasta pra testar os arquivos de media em desenvolvimento