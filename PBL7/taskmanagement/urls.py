from django.urls import path
from . import views

urlpatterns = [
    path('task-management/', views.index, name='index'),
]