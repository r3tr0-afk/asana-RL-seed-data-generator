"""
Models Module
=============

Data models for the Asana simulation entities.
Currently using dictionaries - could be extended to dataclasses/Pydantic.
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Workspace:
    gid: str
    name: str
    is_organization: bool
    email_domain: Optional[str]
    created_at: datetime


@dataclass
class User:
    gid: str
    workspace_gid: str
    name: str
    email: str
    status: str
    role: str
    created_at: datetime


@dataclass
class Team:
    gid: str
    workspace_gid: str
    name: str
    description: Optional[str]
    created_at: datetime


@dataclass
class Project:
    gid: str
    workspace_gid: str
    team_gid: Optional[str]
    name: str
    description: Optional[str]
    owner_gid: Optional[str]
    default_view: str
    current_status: Optional[str]
    archived: bool
    created_at: datetime
    due_date: Optional[datetime]


@dataclass
class Task:
    gid: str
    workspace_gid: str
    assignee_gid: Optional[str]
    parent_task_gid: Optional[str]
    name: str
    description: Optional[str]
    created_at: datetime
    start_on: Optional[datetime]
    due_on: Optional[datetime]
    completed_at: Optional[datetime]
    completed: bool
    is_milestone: bool
