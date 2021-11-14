from django.urls import path

from . import views

urlpatterns = [
	path('', views.index, name='index'),
	path('subscribe/', views.kv_slash, name='kv_slash')
]