from django.urls import path
from . import views

app_name ="website" #For namespacing purpose

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('activate/', views.activate_account, name='activate'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_request, name='logout'),
    path('login/', views.login_request, name='login'),
    path("new-expense/", views.create_expense, name="create-expense"),
    path('your-budget/', views.check_budget, name='check-budget'),
    path('new-budget/', views.create_budget, name='create-budget'),
    path('your-expense/', views.check_expense, name='check-expense'),
    path('settings/', views.settings_view, name='settings'),
    path('password/', views.change_password, name='change_password'),
    path('profile/', views.user_page, name='profile'),
]
