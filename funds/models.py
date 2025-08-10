from datetime import datetime
from .dynamo_client import DynamoDBClient

class Fund:
    def __init__(self, fund_id, name, type, min_amount, max_amount, risk_level, description=None, created_at=None):
        self.fund_id = fund_id
        self.name = name
        self.type = type  # FPV, FIC
        self.min_amount = min_amount
        self.max_amount = max_amount
        self.risk_level = risk_level
        self.description = description
        self.created_at = created_at or datetime.utcnow().isoformat()
    
    def to_dynamo_item(self):
        return {
            'pk': f'FUND#{self.fund_id}',
            'sk': f'FUND#{self.fund_id}',
            'fund_id': self.fund_id,
            'name': self.name,
            'type': self.type,
            'min_amount': self.min_amount,
            'max_amount': self.max_amount,
            'risk_level': self.risk_level,
            'description': self.description,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dynamo_item(cls, item):
        return cls(
            fund_id=item['fund_id'],
            name=item['name'],
            type=item['type'],
            min_amount=item['min_amount'],
            max_amount=item['max_amount'],
            risk_level=item['risk_level'],
            description=item.get('description'),
            created_at=item.get('created_at')
        )
    
    @staticmethod
    def save(fund):
        client = DynamoDBClient()
        return client.put_item(fund.to_dynamo_item())
    
    @staticmethod
    def get_by_id(fund_id):
        client = DynamoDBClient()
        item = client.get_item(f'FUND#{fund_id}', f'FUND#{fund_id}')
        if item:
            return Fund.from_dynamo_item(item)
        return None
    
    @staticmethod
    def get_all():
        client = DynamoDBClient()
        items = client.scan()
        funds = []
        for item in items:
            if item['pk'].startswith('FUND#'):
                funds.append(Fund.from_dynamo_item(item))
        return funds

class ClientBalance:
    def __init__(self, client_id, balance, updated_at=None):
        self.client_id = client_id
        self.balance = balance
        self.updated_at = updated_at or datetime.utcnow().isoformat()
    
    def to_dynamo_item(self):
        return {
            'pk': f'CLIENT#{self.client_id}',
            'sk': 'BALANCE',
            'client_id': self.client_id,
            'balance': self.balance,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dynamo_item(cls, item):
        return cls(
            client_id=item['client_id'],
            balance=item['balance'],
            updated_at=item.get('updated_at')
        )
    
    @staticmethod
    def save(balance):
        client = DynamoDBClient()
        return client.put_item(balance.to_dynamo_item())
    
    @staticmethod
    def get_by_client_id(client_id):
        client = DynamoDBClient()
        item = client.get_item(f'CLIENT#{client_id}', 'BALANCE')
        if item:
            return ClientBalance.from_dynamo_item(item)
        return None

class Transaction:
    def __init__(self, transaction_id, client_id, fund_id, amount, transaction_type, status='completed', created_at=None):
        self.transaction_id = transaction_id
        self.client_id = client_id
        self.fund_id = fund_id
        self.amount = amount
        self.transaction_type = transaction_type  # subscription, cancellation
        self.status = status
        self.created_at = created_at or datetime.utcnow().isoformat()
    
    def to_dynamo_item(self):
        """Store transactions partitioned by client for efficient per-client queries.
        pk: CLIENT#{client_id}
        sk: TRANSACTION#{transaction_id}
        """
        return {
            'pk': f'CLIENT#{self.client_id}',
            'sk': f'TRANSACTION#{self.transaction_id}',
            'transaction_id': self.transaction_id,
            'client_id': self.client_id,
            'fund_id': self.fund_id,
            'amount': self.amount,
            'transaction_type': self.transaction_type,
            'status': self.status,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dynamo_item(cls, item):
        return cls(
            transaction_id=item['transaction_id'],
            client_id=item['client_id'],
            fund_id=item['fund_id'],
            amount=item['amount'],
            transaction_type=item['transaction_type'],
            status=item.get('status', 'completed'),
            created_at=item.get('created_at')
        )
    
    @staticmethod
    def save(transaction):
        client = DynamoDBClient()
        return client.put_item(transaction.to_dynamo_item())
    
    @staticmethod
    def get_by_client_id(client_id):
        client = DynamoDBClient()
        items = client.query(f'CLIENT#{client_id}', 'TRANSACTION#')
        transactions = []
        for item in items:
            if item['sk'].startswith('TRANSACTION#'):
                transactions.append(Transaction.from_dynamo_item(item))
        return transactions

class ClientFundSubscription:
    def __init__(self, client_id, fund_id, amount, subscription_date=None):
        self.client_id = client_id
        self.fund_id = fund_id
        self.amount = amount
        self.subscription_date = subscription_date or datetime.utcnow().isoformat()
    
    def to_dynamo_item(self):
        return {
            'pk': f'CLIENT#{self.client_id}',
            'sk': f'SUBSCRIPTION#{self.fund_id}',
            'client_id': self.client_id,
            'fund_id': self.fund_id,
            'amount': self.amount,
            'subscription_date': self.subscription_date
        }
    
    @classmethod
    def from_dynamo_item(cls, item):
        return cls(
            client_id=item['client_id'],
            fund_id=item['fund_id'],
            amount=item['amount'],
            subscription_date=item['subscription_date']
        )
    
    @staticmethod
    def save(subscription):
        client = DynamoDBClient()
        return client.put_item(subscription.to_dynamo_item())
    
    @staticmethod
    def get_by_client_id(client_id):
        client = DynamoDBClient()
        items = client.query(f'CLIENT#{client_id}', 'SUBSCRIPTION#')
        subscriptions = []
        for item in items:
            if item['sk'].startswith('SUBSCRIPTION#'):
                subscriptions.append(ClientFundSubscription.from_dynamo_item(item))
        return subscriptions
    
    @staticmethod
    def get_by_client_and_fund(client_id, fund_id):
        client = DynamoDBClient()
        item = client.get_item(f'CLIENT#{client_id}', f'SUBSCRIPTION#{fund_id}')
        if item:
            return ClientFundSubscription.from_dynamo_item(item)
        return None
    
    @staticmethod
    def delete(client_id, fund_id):
        client = DynamoDBClient()
        return client.delete_item(f'CLIENT#{client_id}', f'SUBSCRIPTION#{fund_id}')

class Client:
    def __init__(self, client_id, nombre, apellidos, ciudad, email=None, phone=None, created_at=None):
        self.client_id = client_id
        self.nombre = nombre
        self.apellidos = apellidos
        self.ciudad = ciudad
        self.email = email
        self.phone = phone
        self.created_at = created_at or datetime.utcnow().isoformat()
    
    def to_dynamo_item(self):
        return {
            'pk': f'CLIENT#{self.client_id}',
            'sk': f'CLIENT#{self.client_id}',
            'client_id': self.client_id,
            'nombre': self.nombre,
            'apellidos': self.apellidos,
            'ciudad': self.ciudad,
            'email': self.email,
            'phone': self.phone,
            'created_at': self.created_at
        }
    
    @staticmethod
    def from_dynamo_item(item):
        return Client(
            client_id=item['client_id'],
            nombre=item['nombre'],
            apellidos=item['apellidos'],
            ciudad=item['ciudad'],
            email=item.get('email'),
            phone=item.get('phone'),
            created_at=item.get('created_at')
        )
    
    @staticmethod
    def save(client):
        """Guardar cliente en DynamoDB"""
        dynamo_client = DynamoDBClient()
        dynamo_client.put_item(client.to_dynamo_item())
    
    @staticmethod
    def get_by_id(client_id):
        """Obtener cliente por ID"""
        client = DynamoDBClient()
        item = client.get_item(f'CLIENT#{client_id}', f'CLIENT#{client_id}')
        if item:
            return Client.from_dynamo_item(item)
        return None
    
    @staticmethod
    def get_all():
        """Obtener todos los clientes"""
        client = DynamoDBClient()
        items = client.scan()
        clients = []
        for item in items:
            if item['pk'].startswith('CLIENT#') and item['sk'].startswith('CLIENT#'):
                clients.append(Client.from_dynamo_item(item))
        return clients
    
    @staticmethod
    def delete(client_id):
        """Eliminar cliente"""
        client = DynamoDBClient()
        return client.delete_item(f'CLIENT#{client_id}', f'CLIENT#{client_id}')
