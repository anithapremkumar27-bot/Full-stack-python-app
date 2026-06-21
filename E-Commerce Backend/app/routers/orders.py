from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.cart import Cart, CartItem
from app.models.product import Product
from app.models.order import Order, OrderItem
from app.models.user import User
from app.schemas.order import OrderResponse, OrderUpdate
from app.utils.security import get_current_user, get_current_admin

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def place_order(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # 1. Retrieve the user's cart
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart or not cart.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your cart is empty. Add products before placing an order."
        )
    
    # 2. Verify stock availability for all items first
    items_to_order = []
    total_price = 0.0
    
    for item in cart.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {item.product_id} no longer exists."
            )
        if product.stock < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product '{product.name}' has insufficient stock. Available: {product.stock}, in cart: {item.quantity}"
            )
        items_to_order.append((product, item.quantity))
        total_price += product.price * item.quantity

    # 3. Create the Order
    new_order = Order(
        user_id=current_user.id,
        status="Pending",
        total_price=total_price
    )
    db.add(new_order)
    db.commit() # Commit to assign ID
    db.refresh(new_order)
    
    # 4. Create OrderItems, deduct stock, and remove CartItems
    for product, quantity in items_to_order:
        # Create order item record
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=product.id,
            quantity=quantity,
            price=product.price
        )
        db.add(order_item)
        
        # Deduct product stock
        product.stock -= quantity
        
    # Clear the user's cart
    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    
    db.commit()
    db.refresh(new_order)
    return new_order

@router.get("/", response_model=List[OrderResponse])
def get_order_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Order).filter(Order.user_id == current_user.id).order_by(Order.created_at.desc()).all()

@router.get("/admin/all", response_model=List[OrderResponse])
def get_all_orders(admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    return db.query(Order).order_by(Order.created_at.desc()).all()

@router.get("/{order_id}", response_model=OrderResponse)
def get_order_details(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    # Allow if the user is the order owner or is an admin
    if order.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view this order details"
        )
    return order

@router.put("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    status_update: OrderUpdate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    order.status = status_update.status
    db.commit()
    db.refresh(order)
    return order
