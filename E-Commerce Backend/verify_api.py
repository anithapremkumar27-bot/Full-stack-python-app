import urllib.request
import urllib.parse
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def make_request(path, method="GET", headers=None, data=None):
    if headers is None:
        headers = {}
    url = f"{BASE_URL}{path}"
    
    req_data = None
    if data is not None:
        if headers.get("Content-Type") == "application/x-www-form-urlencoded":
            req_data = urllib.parse.urlencode(data).encode("utf-8")
        else:
            headers["Content-Type"] = "application/json"
            req_data = json.dumps(data).encode("utf-8")
            
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            res_data = response.read().decode("utf-8")
            return response.status, json.loads(res_data) if res_data else {}
    except urllib.error.HTTPError as e:
        err_data = e.read().decode("utf-8")
        try:
            parsed_err = json.loads(err_data)
        except Exception:
            parsed_err = err_data
        return e.code, parsed_err
    except urllib.error.URLError as e:
        print(f"Connection Error: {e.reason}")
        return 0, str(e.reason)

def main():
    print("=" * 60)
    print("Starting API Verification for E-Commerce Backend")
    print("=" * 60)
    
    # 1. Health check
    print("\n[1] Testing Health Check...")
    status, res = make_request("/")
    if status == 200:
        print("[OK] Health Check PASSED:", res.get("message"))
    else:
        print("[FAIL] Health Check FAILED. Is the server running? Status:", status)
        return

    # 2. Admin Login
    print("\n[2] Logging in as seeded Admin...")
    admin_login_data = {
        "username": "admin@ecommerce.com",
        "password": "admin123"
    }
    status, res = make_request(
        "/api/auth/login", 
        method="POST", 
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=admin_login_data
    )
    if status == 200:
        admin_token = res.get("access_token")
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        print("[OK] Admin Login PASSED. Token acquired.")
    else:
        print("[FAIL] Admin Login FAILED. Status:", status, res)
        return

    # 3. Create Category
    print("\n[3] Creating new product category...")
    category_name = f"Electronics-{int(time.time())}"
    category_data = {
        "name": category_name,
        "description": "Electronic gadgets and devices"
    }
    status, res = make_request("/api/products/categories", method="POST", headers=admin_headers, data=category_data)
    category_id = None
    if status == 201:
        category_id = res.get("id")
        print(f"[OK] Category creation PASSED. Category ID: {category_id}, Name: {category_name}")
    else:
        print("[FAIL] Category creation FAILED. Status:", status, res)
        return

    # 4. Create Product
    print("\n[4] Creating product inside the category...")
    product_data = {
        "name": "Smart Phone X",
        "description": "High-end smartphone with OLED screen",
        "price": 999.99,
        "stock": 50,
        "category_id": category_id
    }
    status, res = make_request("/api/products/", method="POST", headers=admin_headers, data=product_data)
    product_id = None
    if status == 201:
        product_id = res.get("id")
        print(f"[OK] Product creation PASSED. Product ID: {product_id}, Name: {res.get('name')}")
    else:
        print("[FAIL] Product creation FAILED. Status:", status, res)
        return

    # 5. Register Customer
    print("\n[5] Registering a new Customer...")
    customer_email = f"customer-{int(time.time())}@test.com"
    customer_data = {
        "email": customer_email,
        "full_name": "Alice Customer",
        "password": "customerpass123"
    }
    status, res = make_request("/api/auth/register", method="POST", data=customer_data)
    if status == 201:
        print(f"[OK] Customer registration PASSED. Registered: {res.get('email')}")
    else:
        print("[FAIL] Customer registration FAILED. Status:", status, res)
        return

    # 6. Customer Login
    print("\n[6] Logging in as the new Customer...")
    customer_login_data = {
        "username": customer_email,
        "password": "customerpass123"
    }
    status, res = make_request(
        "/api/auth/login", 
        method="POST", 
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=customer_login_data
    )
    if status == 200:
        customer_token = res.get("access_token")
        customer_headers = {"Authorization": f"Bearer {customer_token}"}
        print("[OK] Customer Login PASSED. Token acquired.")
    else:
        print("[FAIL] Customer Login FAILED. Status:", status, res)
        return

    # 7. Customer views products
    print("\n[7] Querying available products...")
    status, res = make_request("/api/products/", headers=customer_headers)
    if status == 200 and len(res) > 0:
        print(f"[OK] Query products PASSED. Found {len(res)} products.")
    else:
        print("[FAIL] Query products FAILED. Status:", status, res)
        return

    # 8. Add Product to Cart
    print("\n[8] Adding product to Shopping Cart...")
    cart_item_data = {
        "product_id": product_id,
        "quantity": 2
    }
    status, res = make_request("/api/cart/items", method="POST", headers=customer_headers, data=cart_item_data)
    cart_item_id = None
    if status == 201:
        cart_item_id = res.get("id")
        print(f"[OK] Add to cart PASSED. Item ID: {cart_item_id}, Quantity: {res.get('quantity')}")
    else:
        print("[FAIL] Add to cart FAILED. Status:", status, res)
        return

    # 9. View Cart
    print("\n[9] Fetching shopping cart details...")
    status, res = make_request("/api/cart/", headers=customer_headers)
    if status == 200:
        items = res.get("items", [])
        print(f"[OK] View cart PASSED. Cart ID: {res.get('id')}, Items inside: {len(items)}")
    else:
        print("[FAIL] View cart FAILED. Status:", status, res)
        return

    # 10. Place Order
    print("\n[10] Placing checkout Order...")
    status, res = make_request("/api/orders/", method="POST", headers=customer_headers)
    order_id = None
    if status == 201:
        order_id = res.get("id")
        print(f"[OK] Place order PASSED. Order ID: {order_id}, Total: ${res.get('total_price')}, Status: {res.get('status')}")
    else:
        print("[FAIL] Place order FAILED. Status:", status, res)
        return

    # 11. View Customer Order History
    print("\n[11] Retrieving customer order history...")
    status, res = make_request("/api/orders/", headers=customer_headers)
    if status == 200:
        print(f"[OK] Order history PASSED. Orders count: {len(res)}")
    else:
        print("[FAIL] Order history FAILED. Status:", status, res)
        return

    # 12. Admin reads all orders
    print("\n[12] Admin retrieving all orders in system...")
    status, res = make_request("/api/orders/admin/all", headers=admin_headers)
    if status == 200:
        print(f"[OK] Admin read all orders PASSED. Total orders in DB: {len(res)}")
    else:
        print("[FAIL] Admin read all orders FAILED. Status:", status, res)
        return

    # 13. Admin updates order status
    print("\n[13] Admin updating order status to 'Processing'...")
    status_update = {"status": "Processing"}
    status, res = make_request(f"/api/orders/{order_id}/status", method="PUT", headers=admin_headers, data=status_update)
    if status == 200:
        print(f"[OK] Order status update PASSED. New Status: {res.get('status')}")
    else:
        print("[FAIL] Order status update FAILED. Status:", status, res)
        return

    print("\n" + "=" * 60)
    print("ALL API ENDPOINT FLOWS VERIFIED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    main()
