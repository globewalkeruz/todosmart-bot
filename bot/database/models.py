from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class UserModel(BaseModel):
    user_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    language_code: Optional[str] = None
    created_at: Optional[datetime] = None
    last_active: Optional[datetime] = None


class GroupModel(BaseModel):
    group_id: int
    title: str
    chat_type: str
    is_active: bool = True
    created_at: Optional[datetime] = None


class GroupMemberModel(BaseModel):
    id: Optional[str] = None
    group_id: int
    user_id: int
    role: str = "member"
    joined_at: Optional[datetime] = None


class TaskModel(BaseModel):
    task_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    status: str = "pending"
    created_by: Optional[int] = None
    group_id: Optional[int] = None
    due_date: Optional[datetime] = None
    reminder_time: Optional[datetime] = None
    reminder_job_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class TaskAssignmentModel(BaseModel):
    id: Optional[str] = None
    task_id: str
    user_id: int
    assigned_by: Optional[int] = None
    assigned_at: Optional[datetime] = None


class TaskCompletionModel(BaseModel):
    id: Optional[str] = None
    task_id: str
    user_id: int
    completed_at: Optional[datetime] = None
