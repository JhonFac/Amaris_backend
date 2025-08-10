# API de Gestión de Fondos de Inversión

API REST desarrollada en Django para gestionar fondos de inversión (FPV y FIC) con conexión a DynamoDB.

## Características

- ✅ Gestión de fondos de inversión (FPV y FIC)
- ✅ Gestión de saldos de clientes
- ✅ Suscripciones y cancelaciones a fondos
- ✅ Registro de transacciones
- ✅ Conexión a DynamoDB
- ✅ API REST completa
- ✅ Sin funcionalidades de notificación

## Estructura del Proyecto

```
backen/
├── funds_management/          # Configuración principal de Django
│   ├── __init__.py
│   ├── settings.py           # Configuración del proyecto
│   ├── urls.py              # URLs principales
│   ├── wsgi.py              # Configuración WSGI
│   └── asgi.py              # Configuración ASGI
├── funds/                    # Aplicación principal
│   ├── __init__.py
│   ├── apps.py              # Configuración de la app
│   ├── dynamo_client.py     # Cliente DynamoDB
│   ├── models.py            # Modelos de datos
│   ├── serializers.py       # Serializers para API
│   ├── services.py          # Lógica de negocio
│   ├── views.py             # Vistas de la API
│   └── urls.py              # URLs de la app
├── manage.py                # Script de gestión de Django
├── requirements.txt         # Dependencias del proyecto
├── env_example.txt          # Ejemplo de variables de entorno
└── README.md               # Este archivo
```

## Instalación

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd backen
```

2. **Crear entorno virtual**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
cp env_example.txt .env
# Editar .env con tus credenciales de AWS
```

5. **Ejecutar migraciones**
```bash
python manage.py migrate
```

6. **Inicializar el sistema**
```bash
python manage.py runserver
# Luego hacer POST a http://localhost:8000/api/initialize/
```

## Configuración de AWS DynamoDB

1. Crear una tabla en DynamoDB con:
   - Partition Key: `pk` (String)
   - Sort Key: `sk` (String)
   - Billing Mode: Pay per request

2. Configurar las credenciales en el archivo `.env`:
```env
AWS_ACCESS_KEY_ID=tu-access-key
AWS_SECRET_ACCESS_KEY=tu-secret-key
AWS_REGION=us-east-1
DYNAMODB_TABLE_NAME=nombre-de-tu-tabla
```

## Endpoints de la API

### Health Check
- `GET /api/health/` - Verificar estado de la API

### Fondos
- `GET /api/funds/` - Listar todos los fondos
- `GET /api/funds/{fund_id}/` - Obtener fondo específico

### Clientes
- `GET /api/clients/{client_id}/balance/` - Obtener balance del cliente
- `GET /api/clients/{client_id}/subscriptions/` - Obtener suscripciones del cliente
- `GET /api/clients/{client_id}/transactions/` - Obtener transacciones del cliente

### Suscripciones
- `POST /api/subscribe/` - Suscribir cliente a un fondo
- `POST /api/cancel/` - Cancelar suscripción a un fondo

### Sistema
- `POST /api/initialize/` - Inicializar sistema con fondos por defecto

## Ejemplos de Uso

### 1. Inicializar el sistema
```bash
curl -X POST http://localhost:8000/api/initialize/
```

### 2. Listar fondos disponibles
```bash
curl http://localhost:8000/api/funds/
```

### 3. Suscribir cliente a un fondo
```bash
curl -X POST http://localhost:8000/api/subscribe/ \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "CLIENT001",
    "fund_id": "1",
    "amount": 100000
  }'
```

### 4. Ver balance del cliente
```bash
curl http://localhost:8000/api/clients/CLIENT001/balance/
```

### 5. Cancelar suscripción
```bash
curl -X POST http://localhost:8000/api/cancel/ \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "CLIENT001",
    "fund_id": "1"
  }'
```

## Estructura de Datos en DynamoDB

### Fondos (Funds)
```
pk: FUND#{fund_id}
sk: FUND#{fund_id}
fund_id: string
name: string
type: FPV|FIC
min_amount: decimal
max_amount: decimal
risk_level: BAJO|MEDIO|ALTO
description: string
created_at: string
```

### Balance de Cliente
```
pk: CLIENT#{client_id}
sk: BALANCE
client_id: string
balance: decimal
updated_at: string
```

### Suscripciones
```
pk: CLIENT#{client_id}
sk: SUBSCRIPTION#{fund_id}
client_id: string
fund_id: string
amount: decimal
subscription_date: string
```

### Transacciones
```
pk: TRANSACTION#{transaction_id}
sk: TRANSACTION#{transaction_id}
transaction_id: string
client_id: string
fund_id: string
amount: decimal
transaction_type: subscription|cancellation
status: completed
created_at: string
```

## Reglas de Negocio

1. **Montos mínimos y máximos**: Cada fondo tiene montos mínimos y máximos de inversión
2. **Saldo suficiente**: El cliente debe tener saldo suficiente para suscribirse
3. **Suscripción única**: Un cliente no puede tener múltiples suscripciones al mismo fondo
4. **Cancelación**: Al cancelar, el monto se devuelve al balance del cliente
5. **Transacciones**: Todas las operaciones generan transacciones registradas

## Desarrollo

### Ejecutar el servidor
```bash
python manage.py runserver
```

### Ejecutar tests
```bash
python manage.py test
```

## Tecnologías Utilizadas

- **Django 4.2.7** - Framework web
- **Django REST Framework 3.14.0** - Framework para APIs REST
- **boto3 1.34.0** - SDK de AWS para Python
- **python-decouple 3.8** - Gestión de variables de entorno
- **django-cors-headers 4.3.1** - Manejo de CORS

## Notas Importantes

- La API está diseñada para ser simple y directa, sin funcionalidades de notificación
- Todos los datos se almacenan en DynamoDB usando un patrón de clave compuesta (pk + sk)
- Los clientes se crean automáticamente con un balance inicial de 1,000,000
- El sistema incluye 5 fondos por defecto (3 FPV y 2 FIC)
