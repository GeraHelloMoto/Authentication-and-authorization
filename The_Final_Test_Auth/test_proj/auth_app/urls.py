from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view()),
    path('login/', views.LoginView.as_view()),
    path('profile/', views.ProfileView.as_view()),
    path('products/', views.ProductsView.as_view()),
    path('users/', views.UsersView.as_view()),
    path('test/', views.auth_test_page),
    path('profile/update/', views.UpdateProfileView.as_view()),
    path('profile/delete/', views.DeleteAccountView.as_view()),
]