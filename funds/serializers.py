from rest_framework import serializers
from .models import Fund, ClientBalance, Transaction, ClientFundSubscription, Client

class FundSerializer(serializers.Serializer):
    fund_id = serializers.CharField(max_length=50)
    name = serializers.CharField(max_length=200)
    type = serializers.CharField(max_length=10)  # FPV, FIC
    min_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    max_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    risk_level = serializers.CharField(max_length=20)
    description = serializers.CharField(required=False, allow_blank=True)
    created_at = serializers.CharField(required=False)

class ClientBalanceSerializer(serializers.Serializer):
    client_id = serializers.CharField(max_length=50)
    balance = serializers.DecimalField(max_digits=15, decimal_places=2)
    updated_at = serializers.CharField(required=False)

class TransactionSerializer(serializers.Serializer):
    transaction_id = serializers.CharField(max_length=50)
    client_id = serializers.CharField(max_length=50)
    fund_id = serializers.CharField(max_length=50)
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    transaction_type = serializers.CharField(max_length=20)
    status = serializers.CharField(max_length=20, default='completed')
    created_at = serializers.CharField(required=False)

class ClientFundSubscriptionSerializer(serializers.Serializer):
    client_id = serializers.CharField(max_length=50)
    fund_id = serializers.CharField(max_length=50)
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    subscription_date = serializers.CharField(required=False)

class SubscriptionRequestSerializer(serializers.Serializer):
    client_id = serializers.CharField(max_length=50)
    fund_id = serializers.CharField(max_length=50)

class CancellationRequestSerializer(serializers.Serializer):
    client_id = serializers.CharField(max_length=50)
    fund_id = serializers.CharField(max_length=50)

class SubscriptionResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()
    subscription = ClientFundSubscriptionSerializer(required=False)
    transaction = TransactionSerializer(required=False)

class DepositRequestSerializer(serializers.Serializer):
    client_id = serializers.CharField(max_length=50)
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)

class DepositResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()
    new_balance = serializers.DecimalField(max_digits=15, decimal_places=2, required=False)
    transaction = TransactionSerializer(required=False)

class CancellationResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()
    transaction = TransactionSerializer(required=False)

class ClientSerializer(serializers.Serializer):
    client_id = serializers.CharField(max_length=50)
    nombre = serializers.CharField(max_length=100)
    apellidos = serializers.CharField(max_length=100)
    ciudad = serializers.CharField(max_length=100)
    email = serializers.EmailField(required=False, allow_null=True, allow_blank=True)
    phone = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    created_at = serializers.CharField(required=False)

class ClientCreateSerializer(serializers.Serializer):
    client_id = serializers.CharField(max_length=50)
    nombre = serializers.CharField(max_length=100)
    apellidos = serializers.CharField(max_length=100)
    ciudad = serializers.CharField(max_length=100)
    email = serializers.EmailField(required=False, allow_null=True, allow_blank=True)
    phone = serializers.CharField(required=False, allow_null=True, allow_blank=True)
