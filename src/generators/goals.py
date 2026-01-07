"""
Goals Generator
===============

Generates goals table data.

Table Schema:
- gid: TEXT PRIMARY KEY
- workspace_gid: TEXT NOT NULL REFERENCES workspaces(gid)
- owner_gid: TEXT
- name: TEXT NOT NULL
- due_on: DATE
- is_completed: BOOLEAN DEFAULT 0
- created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- CHECK (due_on IS NULL OR due_on >= DATE(created_at))

Methodology:
- Goals follow OKR naming patterns
- Quarterly goals (3-month horizon)
- Completion rate ~40% (goals are ambitious)
- Owned by senior users

Temporal Consistency:
- due_on >= created_at (enforced by database)
- Completed goals: older ones more likely completed
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
from typing import List, Dict, Any
from datetime import timedelta

from utils.base import (
    generate_gid, format_timestamp, format_date,
    generate_creation_wave, probability_check
)
from scrapers.data_sources import GOAL_TEMPLATES, METRICS
from utils.config import VOLUMES, HISTORY_START, NOW


def generate_goals(
    workspaces: List[Dict[str, Any]],
    users: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Generate goal records.
    
    Ref: OKR frameworks - quarterly goal setting with 70% achievement target
    
    Returns:
        List of goal dictionaries
    """
    goals = []
    
    num_goals = VOLUMES["goals"]
    
    # Goals created throughout history (quarterly patterns)
    creation_times = generate_creation_wave(
        num_goals,
        HISTORY_START,
        NOW - timedelta(days=30),
        growth_curve="linear"
    )
    
    # Users by workspace
    users_by_workspace = {}
    for user in users:
        ws_gid = user["workspace_gid"]
        if ws_gid not in users_by_workspace:
            users_by_workspace[ws_gid] = []
        users_by_workspace[ws_gid].append(user)
    
    for i in range(num_goals):
        workspace = workspaces[i % len(workspaces)]
        ws_gid = workspace["gid"]
        created_at = creation_times[i]
        
        # Owner selection
        ws_users = users_by_workspace.get(ws_gid, [])
        owner_gid = random.choice(ws_users)["gid"] if ws_users else None
        
        # Generate goal name
        template = random.choice(GOAL_TEMPLATES)
        name = template.format(
            metric=random.choice(METRICS),
            percent=random.randint(10, 50),
            product=random.choice(["Platform", "Dashboard", "API", "Mobile App"]),
            date=f"Q{((NOW.month - 1) // 3) + 1} {NOW.year}",
            number=random.randint(100, 10000),
            initiative=random.choice(["automation", "migration", "redesign"]),
            platform=random.choice(["cloud", "new infrastructure", "microservices"]),
            capability=random.choice(["analytics", "reporting", "integrations"]),
        )
        
        # Due date: end of quarter (3 months from creation)
        due_on = created_at + timedelta(days=random.randint(60, 120))
        if due_on > NOW + timedelta(days=90):
            due_on = NOW + timedelta(days=random.randint(30, 90))
        
        # Completion: older goals more likely completed
        # ~40% overall completion (goals are stretch targets)
        days_since_creation = (NOW - created_at).days
        completion_probability = min(0.6, 0.1 + (days_since_creation / 180) * 0.5)
        is_completed = 1 if probability_check(completion_probability) else 0
        
        goal = {
            "gid": generate_gid(),
            "workspace_gid": ws_gid,
            "owner_gid": owner_gid,
            "name": name,
            "due_on": format_date(due_on),
            "is_completed": is_completed,
            "created_at": format_timestamp(created_at),
        }
        goals.append(goal)
    
    return goals


if __name__ == "__main__":
    from gen_workspaces import generate_workspaces
    from gen_users import generate_users
    
    workspaces = generate_workspaces()
    users, _ = generate_users(workspaces)
    goals = generate_goals(workspaces, users)
    
    print(f"Generated {len(goals)} goals")
    for g in goals[:5]:
        print(f"  [{g['is_completed']}] {g['name']}")
