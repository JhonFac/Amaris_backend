import boto3
from django.conf import settings
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)

class DynamoDBClient:
    def __init__(self):
        self.dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.table_name = settings.DYNAMODB_TABLE_NAME
        self.table = self.dynamodb.Table(self.table_name)
    
    def create_table_if_not_exists(self):
        """Crear tabla si no existe"""
        try:
            self.dynamodb.create_table(
                TableName=self.table_name,
                KeySchema=[
                    {
                        'AttributeName': 'pk',
                        'KeyType': 'HASH'  # Partition key
                    },
                    {
                        'AttributeName': 'sk',
                        'KeyType': 'RANGE'  # Sort key
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'pk',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'sk',
                        'AttributeType': 'S'
                    }
                ],
                BillingMode='PAY_PER_REQUEST'
            )
            logger.info(f"Tabla {self.table_name} creada exitosamente")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceInUseException':
                logger.info(f"Tabla {self.table_name} ya existe")
            else:
                raise e
    
    def put_item(self, item):
        """Insertar o actualizar un item"""
        try:
            response = self.table.put_item(Item=item)
            return response
        except ClientError as e:
            logger.error(f"Error al insertar item: {e}")
            raise e
    
    def get_item(self, pk, sk):
        """Obtener un item específico"""
        try:
            response = self.table.get_item(
                Key={
                    'pk': pk,
                    'sk': sk
                }
            )
            return response.get('Item')
        except ClientError as e:
            logger.error(f"Error al obtener item: {e}")
            raise e
    
    def query(self, pk, sk_prefix=None):
        """Consultar items por partition key"""
        try:
            if sk_prefix:
                response = self.table.query(
                    KeyConditionExpression='pk = :pk AND begins_with(sk, :sk_prefix)',
                    ExpressionAttributeValues={
                        ':pk': pk,
                        ':sk_prefix': sk_prefix
                    }
                )
            else:
                response = self.table.query(
                    KeyConditionExpression='pk = :pk',
                    ExpressionAttributeValues={
                        ':pk': pk
                    }
                )
            return response.get('Items', [])
        except ClientError as e:
            logger.error(f"Error al consultar items: {e}")
            raise e
    
    def scan(self):
        """Escanear toda la tabla"""
        try:
            response = self.table.scan()
            return response.get('Items', [])
        except ClientError as e:
            logger.error(f"Error al escanear tabla: {e}")
            raise e
    
    def update_item(self, pk, sk, update_expression, expression_values):
        """Actualizar un item"""
        try:
            response = self.table.update_item(
                Key={
                    'pk': pk,
                    'sk': sk
                },
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values,
                ReturnValues="ALL_NEW"
            )
            return response.get('Attributes')
        except ClientError as e:
            logger.error(f"Error al actualizar item: {e}")
            raise e
    
    def delete_item(self, pk, sk):
        """Eliminar un item"""
        try:
            response = self.table.delete_item(
                Key={
                    'pk': pk,
                    'sk': sk
                }
            )
            return response
        except ClientError as e:
            logger.error(f"Error al eliminar item: {e}")
            raise e
