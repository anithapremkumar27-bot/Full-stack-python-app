from sqlalchemy.orm import Session
from app import models, schemas

# --- CATEGORY CRUD ---

def get_categories(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Category).offset(skip).limit(limit).all()

def get_category(db: Session, category_id: int):
    return db.query(models.Category).filter(models.Category.id == category_id).first()

def get_category_by_name(db: Session, name: str):
    return db.query(models.Category).filter(models.Category.name == name).first()

def create_category(db: Session, category: schemas.CategoryCreate):
    db_category = models.Category(name=category.name, color=category.color)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def delete_category(db: Session, category_id: int):
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if db_category:
        db.delete(db_category)
        db.commit()
        return True
    return False

def prepopulate_categories(db: Session):
    # Check if any categories exist
    if db.query(models.Category).count() == 0:
        default_categories = [
            {"name": "Work", "color": "#3B82F6"},       # Blue
            {"name": "Personal", "color": "#10B981"},   # Emerald
            {"name": "Health", "color": "#EF4444"},     # Rose
            {"name": "Shopping", "color": "#F59E0B"}    # Amber
        ]
        for cat in default_categories:
            db_cat = models.Category(name=cat["name"], color=cat["color"])
            db.add(db_cat)
        db.commit()


# --- TASK CRUD ---

def get_tasks(db: Session, skip: int = 0, limit: int = 100, status: str = None, priority: str = None, category_id: int = None, search: str = None):
    query = db.query(models.Task)
    if status:
        query = query.filter(models.Task.status == status)
    if priority:
        query = query.filter(models.Task.priority == priority)
    if category_id:
        query = query.filter(models.Task.category_id == category_id)
    if search:
        query = query.filter(models.Task.title.ilike(f"%{search}%") | models.Task.description.ilike(f"%{search}%"))
    
    # Order by due date (nulls last is good, but simple order is fine)
    return query.order_by(models.Task.due_date.asc(), models.Task.created_at.desc()).offset(skip).limit(limit).all()

def get_task(db: Session, task_id: int):
    return db.query(models.Task).filter(models.Task.id == task_id).first()

def create_task(db: Session, task: schemas.TaskCreate):
    db_task = models.Task(
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        due_date=task.due_date,
        category_id=task.category_id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task(db: Session, task_id: int, task_update: schemas.TaskUpdate):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not db_task:
        return None
    
    update_data = task_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_task, key, value)
        
    db.commit()
    db.refresh(db_task)
    return db_task

def delete_task(db: Session, task_id: int):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task:
        db.delete(db_task)
        db.commit()
        return True
    return False
