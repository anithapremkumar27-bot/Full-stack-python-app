# E-Commerce Backend API

A fully functional, production-ready, and well-structured E-Commerce Backend API built with **Python**, **FastAPI**, **SQLAlchemy**, and **SQLite**.

## Features

- **JWT Authentication & Authorization**: Secure registration, login, and authorization. Supports role-based access control (RBAC) separating **Admin** and **Customer** roles.
- **Category & Product Management**:
  - Categories: Create (Admin-only), Read (Public).
  - Products: Create/Update/Delete (Admin-only), Read (Public) with optional category/search filters.
- **Cart Management**: Add products, adjust quantities with real-time stock verification, and clear/retrieve carts.
- **Order Placement**: Transaction-safe checkout that checks stock, deducts inventory, records items with checkout-time prices, and stores order history.
- **Automatic Database Seeding**: Creates a default SQLite database (`ecommerce.db`) and seeds a default Admin account on startup.

---

## Directory Structure

```text
E-Commerce Backend/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application initialization & routers
│   ├── config.py        # Settings & environment variables
│   ├── database.py      # SQLite connection & get_db dependency
│   ├── models/          # SQLAlchemy database models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── cart.py
│   │   └── order.py
│   ├── schemas/         # Pydantic validation & response schemas
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── cart.py
│   │   └── order.py
│   ├── routers/         # API Endpoint controllers
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── products.py
│   │   ├── cart.py
│   │   └── orders.py
│   └── utils/
│       ├── __init__.py
│       └── security.py  # Hashing, JWT creation, auth dependencies
├── requirements.txt     # Dependencies
├── run.py               # Runner script
└── README.md            # Documentation
```

---

## Getting Started

### 1. Prerequisites
Ensure you have **Python 3.8+** installed.

### 2. Install Dependencies
Navigate into the backend directory and install requirements:
```bash
pip install -r requirements.txt
```

### 3. Start the Server
Run the helper script:
```bash
python run.py
```
The server will start on [http://127.0.0.1:8000](http://127.0.0.1:8000).

---

## Interactive Documentation

FastAPI provides automatic interactive docs. Once the server is running, visit:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### Default Admin Credentials
For managing categories and products immediately, a default admin is seeded:
- **Email**: `admin@ecommerce.com`
- **Password**: `admin123`

---

## API Endpoints List

### Authentication (`/api/auth`)
- `POST /api/auth/register` - Create a customer account.
- `POST /api/auth/login` - Authenticate & obtain a JWT access token (form-data format).
- `GET /api/auth/me` - Retrieve current user profile.

### Products & Categories (`/api/products`)
- `POST /api/products/categories` - Create a category (**Admin Only**).
- `GET /api/products/categories` - List all categories.
- `GET /api/products/categories/{category_id}` - View category details.
- `POST /api/products/` - Add a product (**Admin Only**).
- `GET /api/products/` - View products. Supports query parameters `category_id` and `search` (name).
- `GET /api/products/{product_id}` - View product details.
- `PUT /api/products/{product_id}` - Edit product properties (**Admin Only**).
- `DELETE /api/products/{product_id}` - Delete product (**Admin Only**).

### Shopping Cart (`/api/cart`)
- `GET /api/cart/` - View user's active shopping cart.
- `POST /api/cart/items` - Add item to cart or increment quantity (checks stock).
- `PUT /api/cart/items/{item_id}` - Update item quantity in cart.
- `DELETE /api/cart/items/{item_id}` - Remove item from cart.

### Orders (`/api/orders`)
- `POST /api/orders/` - Place order from cart (clears cart, deducts stock).
- `GET /api/orders/` - Retrieve order history for the logged-in user.
- `GET /api/orders/{order_id}` - Retrieve details of a specific order (Own orders or Admin).
- `GET /api/orders/admin/all` - View all database orders (**Admin Only**).
- `PUT /api/orders/{order_id}/status` - Update an order's status (**Admin Only**).
