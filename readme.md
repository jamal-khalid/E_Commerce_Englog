# E_Commerce Enlog Backend - README

## Overview

This is a Django REST Framework backend for an e-commerce platform with integrated real-time WebSocket notifications using Django Channels and Signals. It supports user management, product catalog, shopping cart, and order processing with live order status updates via WebSocket.

## Requirements

### Python 3.10+

### Redis server for Channels layer (default localhost:6379)

### PostgreSQL or configured database backend

### SSL certificates for secure WebSocket

### Uvicorn for ASGI server

## Setup
### Clone repository and create virtual environment:

git clone -b dev_release <repository_url>
cd E_Commerce_Englog
python -m venv env
source env/bin/activate
pip install -r requirements.txt

### Run Migrations and Migrate:
python manage.py makemigrations
python manage.py migrate 

### Run Uvicorn server: With SSL (recommended):

uvicorn e_commerce.asgi:application --host 0.0.0.0 --port 8018 --ssl-keyfile /path/to/key.pem --ssl-certfile /path/to/cert.pem --log-level debug

#### Register a new user Endpoint:
#### POST /api/register/ 
#### Payload:
{
  "email": "user@example.com",
  "username": "user123",
  "name": "John Doe",
  "password": "your_password",
  "password2": "your_password",
  "address": "123 Street",
  "phone": "1234567890"
}

#### Obtain JWT tokens (login)
#### POST /api/login/
### Payload:

{
  "email": "user@example.com",
  "password": "your_password"
}

#### to Refresh the Access token If Expire:  Post Request - /api/token/refresh/
#### Payload:

{
  "refresh": "<your_refresh_token>"
}
##### then use the new access token 

#### Response:
#### You get an access and refresh token.

#### Access protected endpoints with token
#### Include this header in your requests:

Authorization: Bearer <access_token>

#### With each subsequent request include this token into Headers

#### Test user profile
#### GET /api/profile/

Returns your user details.

#### To update the user details 
#### PATCH /api/profile/
{
  "name": "Khalid Jamal",
  "phone": "+919876543210"
}

### Manage categories (admin only)

####  List categories: GET /api/categories/
####  Create category: POST /api/categories/

{
  "name": "Electronics",
  "description": "All kinds of electronic devices and gadgets"
}

#### Update category: PATCH on /api/categories/{categories_id}/

{
  "name": "Electronics 2"
}

#### Delete category: DELETE on /api/categories/{categories_id}/

### Manage Products (admin only)

#### Create Products: /api/products/

{
  "name": "Smartphone XYZ",
  "description": "Latest model with advanced features",
  "price": "299.99",
  "stock": 100,
  "category_id": 1
}

#### List products: GET /api/products/

#### Update products: PATCH  on /api/products/{products_id}/

{
  "name": "Smartphone XYZ 2 "
}

#### Delete products: Delete  on /api/products/{products_id}/

##### Supports filters, e.g.
##### GET /api/products/?category=1&price_min=10&price_max=100&stock=1



### Cart endpoints (authenticated user)

#### List cart items: GET /api/cart/

#### Add Items to Cart
#### POST /api/cart/

{
  "product_id": 1,
  "quantity": 2
}

#### Update cart item quantity: PATCH on /api/cart/{id}/

#### Remove from cart: DELETE /api/cart/{id}/

#### Place order by creating order from cart:

#### POST /api/orders/ with no body needed.

#### Retrieve single order details : GET /api/orders/{order_id}/

#### Get order list: GET /api/orders/ 

#### View order history: GET /api/orders/history/

### Admin updates order status
#### POST /api/orders/{order_id}/update_status/

#### Payload:

{
  "status": "SHIPPED"
}

#### This triggers real-time notification if WebSocket client connected.


### Test real-time notifications

#### Connect your websocket client (e.g Websocket King)
#### Use JWT to authenticate over WebSocket.

wss://<server_id>:<port>/ws/notifications/?token=<access_token>


### Note: Use Access Token into Header in each api after login