"""
Configuration constants for data generation.
Based on Asana 'Anatomy of Work' Index, McKinsey reports, and industry benchmarks.
"""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Random seed for reproducibility
SEED = int(os.getenv("SEED", "42"))

# LLM Configuration
ENABLE_LLM = os.getenv("ENABLE_LLM", "true").lower() == "true"
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# Temporal configuration
NOW = datetime(2026, 1, 6, 22, 0, 0)
HISTORY_START = NOW - timedelta(days=180)  # 6 months of history
HISTORY_END = NOW
BUSINESS_HOURS_START = 9
BUSINESS_HOURS_END = 18

# Volume configuration (enterprise scale: 5,000-10,000 employees)
VOLUMES = {
    "workspaces": 1,
    "users": 5000,
    "teams": 120,
    "portfolios": 50,
    "goals": 200,
    "projects": 600,
    "project_templates": 25,
    "sections_per_project": (3, 7),
    "tasks": 50000,
    "subtask_ratio": 0.20,
    "stories_per_task": (0, 8),
    "attachments_ratio": 0.15,
    "tags": 150,
    "custom_fields": 15,
}

# Distribution parameters
USER_STATUS_WEIGHTS = {
    "active": 0.90,
    "away": 0.05,
    "dnd": 0.03,
    "deactivated": 0.02,
}

TEAM_MEMBERSHIP_DISTRIBUTION = {
    "min_teams_per_user": 1,
    "max_teams_per_user": 3,
    "admin_ratio": 0.15,
    "guest_ratio": 0.05,
}

PROJECT_CONFIG = {
    "archetype_weights": {
        "sprint": 0.35,
        "kanban": 0.25,
        "launch": 0.20,
        "ongoing": 0.15,
        "bugs": 0.05,
    },
    "layout_weights": {
        "list": 0.50,
        "board": 0.35,
        "timeline": 0.15,
    },
    "status_weights": {
        "on_track": 0.65,
        "at_risk": 0.25,
        "off_track": 0.10,
    },
    "archived_ratio": 0.12,
    "has_due_date_ratio": 0.75,
}

TASK_CONFIG = {
    "unassigned_ratio": 0.15,  # 15% unassigned per Asana benchmarks
    "due_date_distribution": {
        "within_week": 0.25,
        "within_month": 0.40,
        "one_to_three_months": 0.20,
        "no_due_date": 0.10,
        "overdue": 0.05,
    },
    "has_start_date_ratio": 0.35,
    "completion_rates": {
        "sprint": (0.70, 0.85),
        "kanban": (0.55, 0.70),
        "launch": (0.60, 0.75),
        "ongoing": (0.40, 0.55),
        "bugs": (0.65, 0.80),
    },
    "milestone_ratio": 0.05,
    "description_distribution": {
        "empty": 0.20,
        "short": 0.50,
        "detailed": 0.30,
    },
    "weekend_due_date_ratio": 0.12,
}

# Log-normal distribution for task completion times
COMPLETION_TIME_CONFIG = {
    "log_normal_mean": 1.5,  # Median ~4.5 days
    "log_normal_sigma": 0.8,
    "min_days": 0.1,
    "max_days": 30,
}

# Higher weights = more tasks created on that day
DAY_OF_WEEK_WEIGHTS = {
    0: 1.2,  # Monday
    1: 1.3,  # Tuesday
    2: 1.2,  # Wednesday
    3: 1.0,  # Thursday
    4: 0.8,  # Friday
    5: 0.3,  # Saturday
    6: 0.2,  # Sunday
}

STORY_CONFIG = {
    "comment_ratio": 0.80,
    "avg_comments_per_task": 2.5,
}

TAG_CONFIG = {
    "tasks_with_tags_ratio": 0.30,
    "max_tags_per_task": 3,
}

DEPENDENCY_CONFIG = {
    "tasks_with_dependencies_ratio": 0.08,
    "type_weights": {
        "finish_to_start": 0.80,
        "start_to_start": 0.12,
        "finish_to_finish": 0.08,
    },
}

# Section templates by project archetype
SECTION_TEMPLATES = {
    "sprint": ["Backlog", "To Do", "In Progress", "In Review", "Done"],
    "kanban": ["New", "Ready", "In Progress", "Blocked", "Done", "Archived"],
    "launch": ["Planning", "Design", "Development", "Testing", "Launch Prep", "Launched"],
    "ongoing": ["Not Started", "Active", "On Hold", "Completed"],
    "bugs": ["New", "Triaged", "In Progress", "Fixed", "Verified", "Closed"],
}

CUSTOM_FIELD_TEMPLATES = [
    {
        "name": "Priority",
        "type": "enum",
        "options": [
            ("P0 - Critical", "red"),
            ("P1 - High", "orange"),
            ("P2 - Medium", "yellow"),
            ("P3 - Low", "blue"),
        ],
    },
    {"name": "Story Points", "type": "number"},
    {
        "name": "Sprint",
        "type": "enum",
        "options": [
            ("Sprint 1", "blue"),
            ("Sprint 2", "green"),
            ("Sprint 3", "purple"),
            ("Sprint 4", "teal"),
        ],
    },
    {
        "name": "Status",
        "type": "enum",
        "options": [
            ("Not Started", "gray"),
            ("In Progress", "blue"),
            ("Blocked", "red"),
            ("Complete", "green"),
        ],
    },
    {"name": "Estimated Hours", "type": "number"},
    {"name": "Actual Hours", "type": "number"},
    {"name": "Notes", "type": "text"},
    {
        "name": "Review Status",
        "type": "enum",
        "options": [
            ("Pending Review", "yellow"),
            ("Approved", "green"),
            ("Needs Revision", "red"),
        ],
    },
]

ASANA_COLORS = [
    "dark-pink", "dark-green", "dark-blue", "dark-red", "dark-teal",
    "dark-brown", "dark-orange", "dark-purple", "dark-warm-gray",
    "light-pink", "light-green", "light-blue", "light-red", "light-teal",
    "light-brown", "light-orange", "light-purple", "light-warm-gray",
]
