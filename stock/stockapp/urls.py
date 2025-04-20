from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_user, name='login'),
    path('register/', views.register, name='register'),
    path('main_menu/', views.main_menu, name='main_menu'),
    path('add_stock/', views.add_stock, name='add_stock'),
    path('user_portfolio/', views.user_portfolio, name='user_portfolio'),
    path('create_portfolio/', views.create_portfolio, name='create_portfolio'),
    path('portfolio_result/', views.portfolio_result, name='portfolio_result'),
    path('optimizer_info/', views.optimizer_info, name='optimizer_info'),
    path('suggest_stocks/', views.suggest_stocks, name='suggest_stocks'),
]