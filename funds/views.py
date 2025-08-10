from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    FundSerializer, ClientBalanceSerializer, TransactionSerializer,
    ClientFundSubscriptionSerializer, SubscriptionRequestSerializer,
    CancellationRequestSerializer, SubscriptionResponseSerializer,
    CancellationResponseSerializer, DepositRequestSerializer,
    ClientSerializer, ClientCreateSerializer
)
from .models import Fund, ClientBalance, Transaction, ClientFundSubscription, Client
from .services import FundService, ClientService, SubscriptionService, ClientServiceManager
from .dynamo_client import DynamoDBClient

@api_view(['GET'])
def health_check(request):
    """Health check endpoint"""
    return Response({
        'status': 'healthy',
        'message': 'API funcionando correctamente'
    })

@api_view(['GET'])
def list_funds(request):
    """Listar todos los fondos disponibles"""
    try:
        funds = Fund.get_all()
        serializer = FundSerializer(funds, many=True)
        return Response({
            'success': True,
            'funds': serializer.data
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al obtener fondos: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_fund(request, fund_id):
    """Obtener un fondo específico"""
    try:
        fund = Fund.get_by_id(fund_id)
        if fund:
            serializer = FundSerializer(fund)
            return Response({
                'success': True,
                'fund': serializer.data
            })
        else:
            return Response({
                'success': False,
                'message': f'Fondo {fund_id} no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al obtener fondo: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_client_balance(request, client_id):
    """Obtener balance de un cliente junto con sus fondos suscritos"""
    try:
        # Obtener balance del cliente
        balance = ClientService.get_or_create_balance(client_id)
        balance_serializer = ClientBalanceSerializer(balance)
        
        # Obtener suscripciones del cliente
        subscriptions = ClientFundSubscription.get_by_client_id(client_id)
        subscriptions_data = []
        
        for subscription in subscriptions:
            # Obtener información detallada del fondo
            fund = Fund.get_by_id(subscription.fund_id)
            subscription_info = {
                'fund_id': subscription.fund_id,
                'fund_name': fund.name if fund else 'Fondo no encontrado',
                'fund_type': fund.type if fund else '',
                'subscribed_amount': subscription.amount,
                'subscription_date': subscription.subscription_date
            }
            subscriptions_data.append(subscription_info)
        
        return Response({
            'success': True,
            'balance': balance_serializer.data,
            'subscribed_funds': subscriptions_data,
            'total_subscribed_funds': len(subscriptions_data)
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al obtener balance: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def subscribe_to_fund(request):
    """Suscribir cliente a un fondo"""
    try:
        serializer = SubscriptionRequestSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            result = SubscriptionService.subscribe_to_fund(
                data['client_id'],
                data['fund_id']
            )
            
            if result['success']:
                response_serializer = SubscriptionResponseSerializer(result)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'success': False,
                'message': 'Datos inválidos',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al procesar suscripción: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def cancel_subscription(request):
    """Cancelar suscripción a un fondo"""
    try:
        serializer = CancellationRequestSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            result = SubscriptionService.cancel_subscription(
                data['client_id'],
                data['fund_id']
            )
            
            if result['success']:
                response_serializer = CancellationResponseSerializer(result)
                return Response(response_serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'success': False,
                'message': 'Datos inválidos',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al procesar cancelación: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_client_subscriptions(request, client_id):
    """Obtener suscripciones de un cliente"""
    try:
        subscriptions = ClientFundSubscription.get_by_client_id(client_id)
        serializer = ClientFundSubscriptionSerializer(subscriptions, many=True)
        return Response({
            'success': True,
            'subscriptions': serializer.data
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al obtener suscripciones: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_client_transactions(request, client_id):
    """Obtener transacciones de un cliente"""
    try:
        transactions = Transaction.get_by_client_id(client_id)
        serializer = TransactionSerializer(transactions, many=True)
        return Response({
            'success': True,
            'transactions': serializer.data
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al obtener transacciones: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def initialize_system(request):
    """Inicializar el sistema con fondos por defecto"""
    try:
        # Crear tabla si no existe
        client = DynamoDBClient()
        client.create_table_if_not_exists()
        
        # Inicializar fondos por defecto
        funds_count = FundService.initialize_default_funds()
        
        return Response({
            'success': True,
            'message': f'Sistema inicializado correctamente. {funds_count} fondos creados.'
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al inicializar sistema: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def deposit(request):
    """Realizar depósito a la cuenta del cliente"""
    try:
        serializer = DepositRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Datos inválidos',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        client_id = serializer.validated_data['client_id']
        amount = serializer.validated_data['amount']
        
        result = ClientService.deposit(client_id, amount)
        
        if result['success']:
            response_data = {
                'success': True,
                'message': result['message'],
                'new_balance': result['new_balance']
            }
            
            # Agregar datos de transacción si existe
            if 'transaction' in result:
                transaction_serializer = TransactionSerializer(result['transaction'])
                response_data['transaction'] = transaction_serializer.data
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': False,
                'message': result['message']
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al realizar depósito: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def create_client(request):
    """Crear un nuevo cliente con saldo inicial de $500,000"""
    try:
        serializer = ClientCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Datos inválidos',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        result = ClientServiceManager.create_client(
            data['client_id'],
            data['nombre'],
            data['apellidos'],
            data['ciudad'],
            data.get('email'),
            data.get('phone')
        )
        
        if result['success']:
            client_serializer = ClientSerializer(result['client'])
            balance_serializer = ClientBalanceSerializer(result['initial_balance'])
            transaction_serializer = TransactionSerializer(result['transaction'])
            
            return Response({
                'success': True,
                'message': result['message'],
                'client': client_serializer.data,
                'initial_balance': balance_serializer.data,
                'initial_transaction': transaction_serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': False,
                'message': result['message']
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al crear cliente: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_client(request, client_id):
    """Obtener información de un cliente específico"""
    try:
        result = ClientServiceManager.get_client(client_id)
        
        if result['success']:
            client_serializer = ClientSerializer(result['client'])
            return Response({
                'success': True,
                'client': client_serializer.data
            })
        else:
            return Response({
                'success': False,
                'message': result['message']
            }, status=status.HTTP_404_NOT_FOUND)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al obtener cliente: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def list_clients(request):
    """Listar todos los clientes"""
    try:
        result = ClientServiceManager.get_all_clients()
        
        if result['success']:
            clients_serializer = ClientSerializer(result['clients'], many=True)
            return Response({
                'success': True,
                'clients': clients_serializer.data,
                'total_clients': result['total_clients']
            })
        else:
            return Response({
                'success': False,
                'message': 'Error al obtener clientes'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al listar clientes: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
