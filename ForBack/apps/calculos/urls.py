from django.urls import path
from . import views
app_name = 'calculos'
from .views import levantamentoCampo, GerarMemorialExcel

urlpatterns = [
    path('form-levantamento', levantamentoCampo.as_view()),
    path('form-levantamento/<uuid:projeto_id>', levantamentoCampo.as_view()),
    path('gerar-memorial-mesclado', GerarMemorialExcel.as_view(), name='gerar_memorial_mesclado')
]