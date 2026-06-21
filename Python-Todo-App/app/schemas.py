from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime, date

# --- CATEGORY SCHEMAS ---
class CategoryBase(BaseModel):
    name: str
    color: str = "#8B5CF6" # Default color code (violet)

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- TASK SCHEMAS ---
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[str] = "To Do"  # "To Do", "In Progress", "Completed"
    priority: Optional[str] = "Medium"  # "Low", "Medium", "High"
    due_date: Optional[date] = None
    category_id: int

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[date] = None
    category_id: Optional[int] = None

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    due_date: Optional[date] = None
    category_id: int
    created_at: datetime
    category: Optional[CategoryResponse] = None

    model_config = ConfigDict(from_attributes=True)


# Category with detailed tasks list (optional reference helper)
class CategoryDetailResponse(CategoryResponse):
    tasks: List[TaskResponse] = []

    model_config = ConfigDict(from_attributes=True)
