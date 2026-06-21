from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.config import settings
from app.database import engine, Base, SessionLocal
from app.models.user import User
from app.models.cart import Cart
from app.utils.security import hash_password
from app.routers import auth, products, cart, orders

# Ensure database tables exist
Base.metadata.create_all(bind=engine)

def seed_admin_user():
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.email == settings.DEFAULT_ADMIN_EMAIL).first()
        if not admin:
            hashed_pwd = hash_password(settings.DEFAULT_ADMIN_PASSWORD)
            admin = User(
                email=settings.DEFAULT_ADMIN_EMAIL,
                full_name=settings.DEFAULT_ADMIN_NAME,
                hashed_password=hashed_pwd,
                is_admin=True
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            
            # Create a cart for the admin
            admin_cart = Cart(user_id=admin.id)
            db.add(admin_cart)
            db.commit()
            print(f"Default admin user seeded: {settings.DEFAULT_ADMIN_EMAIL}")
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run migrations/seed database on startup
    seed_admin_user()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="A comprehensive E-Commerce Backend API featuring JWT role-based authentication, category/product management, cart systems, and checkout ordering.",
    lifespan=lifespan
)

@app.get("/", tags=["Health Check"])
def read_root():
    return {
        "status": "online",
        "message": "Welcome to the E-Commerce Backend API!",
        "docs_url": "/docs"
    }

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(cart.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
