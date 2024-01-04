from django.urls import path
from django.conf.urls import handler404

from . import views
handler404 = handler404

urlpatterns = [
    path("", views.index, name="index"),
    path('wiki/<str:title>/', views.wiki_page, name='wiki-page'),
    path('create/', views.create, name='create'),
    path('random/', views.random, name='random'),
    path('edit/<str:title>/', views.edit, name='edit'),
    path('search/', views.search, name='search'),
]
