from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('signup/', views.signup, name="signup"),
    path('login/', views.login, name="login"),
    path('logout/', auth_views.LogoutView.as_view(), name="logout"),
    path('create_group/', views.create_group, name="create_group"),
    path('view/<int:pk>/', views.view_group, name="view_group"),
    path('add/<int:pk>/', views.add, name="add"),
    path('', views.index, name="home")
]
