from sqlalchemy import Column, Integer, String, ForeignKey, Date, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    color = Column(String, nullable=False, default="#8B5CF6") # Hex code default (violet)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship to tasks (deleting a category deletes its tasks)
    tasks = relationship("Task", back_populates="category", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, default="To Do", nullable=False)  # "To Do", "In Progress", "Completed"
    priority = Column(String, default="Medium", nullable=False)  # "Low", "Medium", "High"
    due_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)

    # Relationship back to category
    category = relationship("Category", back_populates="tasks")
