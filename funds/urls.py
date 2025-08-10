from django.urls import path
from . import views

urlpatterns = [
    # Health check
    path('health/', views.health_check, name='health_check'),
    
    # Fondos
    path('funds/', views.list_funds, name='list_funds'),
    path('funds/<str:fund_id>/', views.get_fund, name='get_fund'),
    
    # Clientes
    path('clients/', views.list_clients, name='list_clients'),
    path('clients/create/', views.create_client, name='create_client'),
    path('clients/<str:client_id>/', views.get_client, name='get_client'),
    path('clients/<str:client_id>/balance/', views.get_client_balance, name='get_client_balance'),
    path('clients/<str:client_id>/subscriptions/', views.get_client_subscriptions, name='get_client_subscriptions'),
    path('clients/<str:client_id>/transactions/', views.get_client_transactions, name='get_client_transactions'),
    path('deposit/', views.deposit, name='deposit'),
    
    # Suscripciones
    path('subscribe/', views.subscribe_to_fund, name='subscribe_to_fund'),
    path('cancel/', views.cancel_subscription, name='cancel_subscription'),
    
    # Sistema
    path('initialize/', views.initialize_system, name='initialize_system'),
]
