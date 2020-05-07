from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('signup/', views.signup, name="signup"),
    path('login/', views.login, name="login"),
    path('logout/', auth_views.LogoutView.as_view(), name="logout"),
    path('create_group/', views.create_group, name="create_group"),
    path('submit_url/<int:pk>/', views.submit_url, name="submit_url"),
    path('api/', views.submit_url_api, name="submit_url_api"),
    path('view/<int:pk>/', views.view_group, name="view_group"),
    path('view/<int:pk>/adduser/', views.add_user_to_group, name="add_user_to_group"),
    path('view/<int:pk>/<int:reference>/', views.view_references, name="view_reference"),
    path('view/<int:pk>/<int:reference>/edit/', views.edit_references, name="edit_references"),
    path('view/<int:pk>/<int:reference>/upload/', views.uploadPDFToReference, name="upload_to_reference"),
    path('add/<int:pk>/', views.add, name="add"),
    path('add/<int:pk>/<int:template>/', views.add_template, name="add_template"),
    path('upload/<int:pk>/', views.uploadReference, name="upload"),
    path('upload_bib/<int:group>/', views.upload_bib, name="upload_bib"),
    path('delete/<int:reference>/', views.delete_reference, name="delete_reference"),
    path('export/<int:pk>/export.bib', views.export, name="export"),
    path('search/', views.search, name="search"),
    path('key/', views.view_API_key, name="key"),
    path('view_404', views.view_404, name="view_404"),
    path('', views.index, name="home")
]
