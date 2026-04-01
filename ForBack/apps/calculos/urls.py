from django.urls import path
from . import views
app_name = 'calculos'
from .views import levantamentoCampo

urlpatterns = [
    path('form-levantamento', levantamentoCampo.as_view()),
    path('form-levantamento/<uuid:projeto_id>', levantamentoCampo.as_view()),
]