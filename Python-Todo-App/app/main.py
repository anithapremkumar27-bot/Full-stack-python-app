from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os

from app import crud, models, schemas
from app.database import engine, get_db

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Premium To-Do App API",
    description="Backend API for the glassmorphic dark-mode To-Do Dashboard",
    version="1.0.0"
)

# Run default category pre-population on startup
@app.on_event("startup")
def startup_populate():
    db = next(get_db())
    try:
        crud.prepopulate_categories(db)
    finally:
        db.close()

# --- API ROUTES ---

# Category Endpoints
@app.get("/api/categories", response_model=List[schemas.CategoryResponse])
def read_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_categories(db, skip=skip, limit=limit)

@app.post("/api/categories", response_model=schemas.CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    db_category = crud.get_category_by_name(db, name=category.name)
    if db_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A category with this name already exists."
        )
    return crud.create_category(db=db, category=category)

@app.delete("/api/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    success = crud.delete_category(db, category_id=category_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found."
        )
    return None


# Task Endpoints
@app.get("/api/tasks", response_model=List[schemas.TaskResponse])
def read_tasks(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return crud.get_tasks(
        db, 
        skip=skip, 
        limit=limit, 
        status=status, 
        priority=priority, 
        category_id=category_id, 
        search=search
    )

@app.post("/api/tasks", response_model=schemas.TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    db_cat = crud.get_category(db, category_id=task.category_id)
    if not db_cat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found."
        )
    return crud.create_task(db=db, task=task)

@app.put("/api/tasks/{task_id}", response_model=schemas.TaskResponse)
def update_task(task_id: int, task_update: schemas.TaskUpdate, db: Session = Depends(get_db)):
    # If category_id is updated, check if it exists
    if task_update.category_id is not None:
        db_cat = crud.get_category(db, category_id=task_update.category_id)
        if not db_cat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found."
            )
    
    db_task = crud.update_task(db, task_id=task_id, task_update=task_update)
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found."
        )
    return db_task

@app.delete("/api/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    success = crud.delete_task(db, task_id=task_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found."
        )
    return None


# --- STATIC FILES & SPA SERVING ---

# Ensure directories exist
os.makedirs("app/static/css", exist_ok=True)
os.makedirs("app/static/js", exist_ok=True)

# Mount the static directory for CSS, JS, images, etc.
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Catch-all root serving index.html
@app.get("/")
def read_index():
    index_path = os.path.join("app", "static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "To-Do Backend API Running. Please create index.html in app/static/"}
