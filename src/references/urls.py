from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('signup/', views.signup, name="signup"),
    path('login/', views.login, name="login"),
    path('logout/', auth_views.LogoutView.as_view(), name="logout"),
    path('create_group/', views.create_group, name="create_group"),
    path('submit_url/<int:pk>/', views.submit_url, name="submit_url"),
    path('view/<int:pk>/', views.view_group, name="view_group"),
    path('view/<int:pk>/<int:reference>/', views.view_references, name="view_reference"),
    path('add/<int:pk>/', views.add, name="add"),
    path('add/<int:pk>/<str:template>/', views.add_template, name="add_template"),
    path('upload/<int:pk>/', views.uploadReference, name="upload"),
    path('view_404', views.view_404, name="view_404"),
    path('', views.index, name="home")
]
