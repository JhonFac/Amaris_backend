import uuid
from decimal import Decimal
from .models import Fund, ClientBalance, Transaction, ClientFundSubscription, Client
from .notifications import NotificationService
from .dynamo_client import DynamoDBClient

class FundService:
    @staticmethod
    def initialize_default_funds():
        """Inicializar fondos por defecto"""
        default_funds = [
            {
                'fund_id': '1',
                'name': 'FPV_EL CLIENTE_RECAUDADORA',
                'type': 'FPV',
                'min_amount': Decimal('75000'),
                'max_amount': Decimal('10000000'),
                'risk_level': 'BAJO',
                'description': 'Fondo de pensión voluntaria - El Cliente Recaudadora'
            },
            {
                'fund_id': '2',
                'name': 'FPV_EL CLIENTE_ECOPETROL',
                'type': 'FPV',
                'min_amount': Decimal('125000'),
                'max_amount': Decimal('10000000'),
                'risk_level': 'MEDIO',
                'description': 'Fondo de pensión voluntaria - El Cliente Ecopetrol'
            },
            {
                'fund_id': '3',
                'name': 'DEUDAPRIVADA',
                'type': 'FIC',
                'min_amount': Decimal('50000'),
                'max_amount': Decimal('5000000'),
                'risk_level': 'BAJO',
                'description': 'Fondo de inversión colectiva - Deuda Privada'
            },
            {
                'fund_id': '4',
                'name': 'FDO-ACCIONES',
                'type': 'FIC',
                'min_amount': Decimal('250000'),
                'max_amount': Decimal('5000000'),
                'risk_level': 'ALTO',
                'description': 'Fondo de inversión colectiva - Acciones'
            },
            {
                'fund_id': '5',
                'name': 'FPV_EL CLIENTE_DINAMICA',
                'type': 'FPV',
                'min_amount': Decimal('100000'),
                'max_amount': Decimal('10000000'),
                'risk_level': 'MEDIO',
                'description': 'Fondo de pensión voluntaria - El Cliente Dinámica'
            }
        ]
        
        for fund_data in default_funds:
            fund = Fund(**fund_data)
            Fund.save(fund)
        
        return len(default_funds)

class ClientServiceManager:
    @staticmethod
    def create_client(client_id, nombre, apellidos, ciudad, email=None, phone=None):
        """Crear un nuevo cliente con saldo inicial de $500,000"""
        # Verificar que el cliente no existe
        existing_client = Client.get_by_id(client_id)
        if existing_client:
            return {
                'success': False,
                'message': f'El cliente {client_id} ya existe'
            }
        
        # Crear cliente
        client = Client(client_id, nombre, apellidos, ciudad, email=email, phone=phone)
        Client.save(client)
        
        # Crear balance inicial de $500,000
        initial_balance = ClientBalance(client_id, Decimal('500000'))
        ClientBalance.save(initial_balance)
        
        # Crear transacción inicial
        transaction_id = str(uuid.uuid4())
        transaction = Transaction(
            transaction_id=transaction_id,
            client_id=client_id,
            fund_id='INITIAL_BALANCE',
            amount=Decimal('500000'),
            transaction_type='SALDO_INICIAL'
        )
        Transaction.save(transaction)
        
        # Notificar creación
        NotificationService.notify_client(
            client_id,
            subject='Bienvenido: cuenta creada',
            message=(
                f'Hola {nombre}, tu cliente {client_id} fue creado con saldo inicial de 500000.'
            )
        )

        return {
            'success': True,
            'message': f'Cliente {client_id} creado exitosamente con saldo inicial de $500,000',
            'client': client,
            'initial_balance': initial_balance,
            'transaction': transaction
        }
    
    @staticmethod
    def get_client(client_id):
        """Obtener información de un cliente"""
        client = Client.get_by_id(client_id)
        if not client:
            return {
                'success': False,
                'message': f'Cliente {client_id} no encontrado'
            }
        
        return {
            'success': True,
            'client': client
        }
    
    @staticmethod
    def get_all_clients():
        """Obtener todos los clientes"""
        clients = Client.get_all()
        return {
            'success': True,
            'clients': clients,
            'total_clients': len(clients)
        }

class ClientService:
    @staticmethod
    def get_or_create_balance(client_id, initial_balance=Decimal('0')):
        """Obtener o crear balance del cliente (ahora inicia en 0)"""
        balance = ClientBalance.get_by_client_id(client_id)
        if not balance:
            balance = ClientBalance(client_id, initial_balance)
            ClientBalance.save(balance)
        return balance
    
    @staticmethod
    def update_balance(client_id, new_balance):
        """Actualizar balance del cliente"""
        balance = ClientBalance(client_id, new_balance)
        ClientBalance.save(balance)
        return balance
    
    @staticmethod
    def deposit(client_id, amount):
        """Realizar depósito a la cuenta del cliente"""
        # Validar que el cliente existe
        client = Client.get_by_id(client_id)
        if not client:
            return {
                'success': False,
                'message': f'El cliente {client_id} no existe. Debe crear el cliente primero.'
            }
        
        # Validar monto positivo
        if amount <= 0:
            return {
                'success': False,
                'message': 'El monto debe ser mayor a 0'
            }
        
        # Obtener balance actual
        current_balance = ClientService.get_or_create_balance(client_id)
        
        # Calcular nuevo balance
        new_balance_amount = current_balance.balance + amount
        
        # Actualizar balance
        updated_balance = ClientService.update_balance(client_id, new_balance_amount)
        
        # Crear transacción de depósito
        transaction_id = str(uuid.uuid4())
        transaction = Transaction(
            transaction_id=transaction_id,
            client_id=client_id,
            fund_id='DEPOSIT',  # Identificador especial para depósitos
            amount=amount,
            transaction_type='DEPOSITO'
        )
        Transaction.save(transaction)
        
        # Notificar depósito
        NotificationService.notify_client(
            client_id,
            subject='Depósito recibido',
            message=(
                f'Se acreditaron {amount} a tu cuenta. Nuevo saldo: {updated_balance.balance}.'
            )
        )

        return {
            'success': True,
            'message': f'Depósito realizado exitosamente',
            'new_balance': updated_balance.balance,
            'transaction': transaction
        }

class SubscriptionService:
    @staticmethod
    def subscribe_to_fund(client_id, fund_id):
        """Suscribir cliente a un fondo (usa automáticamente el monto mínimo)"""
        # Validar que el cliente existe
        client = Client.get_by_id(client_id)
        if not client:
            return {
                'success': False,
                'message': f'El cliente {client_id} no existe. Debe crear el cliente primero.'
            }
        
        # Validar que el fondo existe
        fund = Fund.get_by_id(fund_id)
        if not fund:
            return {
                'success': False,
                'message': f'Fondo {fund_id} no encontrado'
            }
        
        # El monto será automáticamente el mínimo requerido del fondo
        amount = fund.min_amount
        
        # Obtener balance del cliente
        client_balance = ClientService.get_or_create_balance(client_id)
        
        # Validar que no tenga suscripción previa al mismo fondo
        existing_subscription = ClientFundSubscription.get_by_client_and_fund(client_id, fund_id)
        if existing_subscription:
            return {
                'success': False,
                'message': f'Ya tienes una suscripción activa al fondo "{fund.name}"',
                'fund_info': {
                    'fund_id': fund.fund_id,
                    'name': fund.name,
                    'type': fund.type,
                    'min_amount': fund.min_amount,
                    'max_amount': fund.max_amount,
                    'risk_level': fund.risk_level,
                    'description': fund.description
                },
                'existing_subscription': {
                    'amount': existing_subscription.amount,
                    'subscription_date': existing_subscription.subscription_date
                }
            }
        
        # Validar saldo suficiente para el monto mínimo
        if client_balance.balance < amount:
            return {
                'success': False,
                'message': f'No tiene saldo disponible para vincularse al fondo "{fund.name}"',
                'required_amount': amount,
                'current_balance': client_balance.balance,
                'missing_amount': amount - client_balance.balance,
                'fund_info': {
                    'fund_id': fund.fund_id,
                    'name': fund.name,
                    'type': fund.type,
                    'min_amount': fund.min_amount,
                    'max_amount': fund.max_amount,
                    'risk_level': fund.risk_level,
                    'description': fund.description
                }
            }
        
        # Crear suscripción
        subscription = ClientFundSubscription(client_id, fund_id, amount)
        ClientFundSubscription.save(subscription)
        
        # Actualizar balance del cliente
        new_balance = client_balance.balance - amount
        ClientService.update_balance(client_id, new_balance)
        
        # Registrar transacción
        transaction_id = str(uuid.uuid4())
        transaction = Transaction(transaction_id, client_id, fund_id, amount, 'subscription')
        Transaction.save(transaction)
        
        # Notificar suscripción
        NotificationService.notify_client(
            client_id,
            subject='Suscripción realizada',
            message=(
                f'Te suscribiste al fondo {fund.name} (ID {fund.fund_id}) por {amount}. '
                f'Saldo disponible: {new_balance}.'
            )
        )

        return {
            'success': True,
            'message': f'Suscripción exitosa al fondo {fund.name}',
            'subscription': subscription,
            'transaction': transaction
        }
    
    @staticmethod
    def cancel_subscription(client_id, fund_id):
        """Cancelar suscripción a un fondo"""
        # Validar que el fondo existe
        fund = Fund.get_by_id(fund_id)
        if not fund:
            return {
                'success': False,
                'message': f'Fondo {fund_id} no encontrado'
            }
        
        # Obtener suscripción existente
        subscription = ClientFundSubscription.get_by_client_and_fund(client_id, fund_id)
        if not subscription:
            return {
                'success': False,
                'message': f'No tienes una suscripción activa al fondo {fund_id}'
            }
        
        # Eliminar suscripción
        ClientFundSubscription.delete(client_id, fund_id)
        
        # Devolver monto al balance del cliente
        client_balance = ClientService.get_or_create_balance(client_id)
        new_balance = client_balance.balance + subscription.amount
        ClientService.update_balance(client_id, new_balance)
        
        # Registrar transacción
        transaction_id = str(uuid.uuid4())
        transaction = Transaction(transaction_id, client_id, fund_id, subscription.amount, 'cancellation')
        Transaction.save(transaction)
        
        # Notificar cancelación
        NotificationService.notify_client(
            client_id,
            subject='Suscripción cancelada',
            message=(
                f'Cancelaste el fondo {fund.name} (ID {fund.fund_id}). '
                f'Se devolvieron {subscription.amount}. Nuevo saldo: {new_balance}.'
            )
        )

        return {
            'success': True,
            'message': f'Cancelación exitosa del fondo {fund.name}',
            'transaction': transaction
        }
