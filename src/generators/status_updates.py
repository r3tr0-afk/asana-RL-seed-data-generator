"""
Status Updates Generator
========================

Generates status_updates table data.

Table Schema:
- gid: TEXT PRIMARY KEY
- workspace_gid: TEXT NOT NULL REFERENCES workspaces(gid)
- author_gid: TEXT
- status_type: TEXT CHECK(status_type IN ('on_track', 'at_risk', 'off_track'))
- text: TEXT NOT NULL
- created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- parent_project_gid: TEXT
- parent_portfolio_gid: TEXT
- parent_goal_gid: TEXT
- CHECK (exactly one parent is non-null)

Methodology:
- Weekly/biweekly status updates for active projects
- Status type matches project current_status
- LLM-generated update text
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
from typing import List, Dict, Any
from datetime import datetime, timedelta

from utils.base import (
    generate_gid, format_timestamp, probability_check
)
from utils.llm_content import generate_status_update
from utils.config import NOW


def generate_status_updates(
    projects: List[Dict[str, Any]],
    portfolios: List[Dict[str, Any]],
    goals: List[Dict[str, Any]],
    users: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Generate status update records.
    
    Status updates are posted on projects, portfolios, and goals.
    """
    status_updates = []
    
    # Users by workspace
    users_by_workspace = {}
    for user in users:
        ws_gid = user["workspace_gid"]
        if ws_gid not in users_by_workspace:
            users_by_workspace[ws_gid] = []
        users_by_workspace[ws_gid].append(user)
    
    # Project status updates (main source)
    for project in projects:
        # Skip archived projects
        if project.get("archived"):
            continue
        
        # ~70% of active projects have status updates
        if not probability_check(0.70):
            continue
        
        workspace_gid = project["workspace_gid"]
        ws_users = users_by_workspace.get(workspace_gid, [])
        
        if not ws_users:
            continue
        
        # Parse project created_at
        try:
            proj_created = datetime.strptime(project["created_at"], "%Y-%m-%d %H:%M:%S")
        except:
            proj_created = NOW - timedelta(days=60)
        
        # Generate 1-4 status updates over project lifetime
        num_updates = random.randint(1, 4)
        days_active = (NOW - proj_created).days
        
        if days_active < 7:
            num_updates = 1
        
        for i in range(num_updates):
            # Space updates ~weekly
            update_offset = timedelta(days=(i + 1) * 7 + random.randint(-2, 2))
            update_time = proj_created + update_offset
            
            if update_time > NOW:
                break
            
            # Author is project owner or random team member
            author = random.choice(ws_users)
            
            # Status type (may differ from current)
            if i == num_updates - 1:
                # Latest update matches current status
                status_type = project.get("current_status", "on_track")
            else:
                # Historical updates
                status_type = random.choices(
                    ["on_track", "at_risk", "off_track"],
                    weights=[0.6, 0.3, 0.1]
                )[0]
            
            text = generate_status_update(
                project["name"],
                status_type,
                author["name"]
            )
            
            update = {
                "gid": generate_gid(),
                "workspace_gid": workspace_gid,
                "author_gid": author["gid"],
                "status_type": status_type,
                "text": text,
                "created_at": format_timestamp(update_time),
                "parent_project_gid": project["gid"],
                "parent_portfolio_gid": None,
                "parent_goal_gid": None,
            }
            status_updates.append(update)
    
    # Portfolio status updates
    for portfolio in portfolios:
        if not probability_check(0.50):
            continue
        
        workspace_gid = portfolio["workspace_gid"]
        ws_users = users_by_workspace.get(workspace_gid, [])
        
        if not ws_users:
            continue
        
        try:
            port_created = datetime.strptime(portfolio["created_at"], "%Y-%m-%d %H:%M:%S")
        except:
            port_created = NOW - timedelta(days=60)
        
        # 1-2 updates per portfolio
        for i in range(random.randint(1, 2)):
            update_time = port_created + timedelta(days=(i + 1) * 14 + random.randint(-3, 3))
            if update_time > NOW:
                break
            
            author = random.choice(ws_users)
            status_type = random.choice(["on_track", "at_risk"])
            
            text = generate_status_update(
                portfolio["name"],
                status_type,
                author["name"]
            )
            
            update = {
                "gid": generate_gid(),
                "workspace_gid": workspace_gid,
                "author_gid": author["gid"],
                "status_type": status_type,
                "text": text,
                "created_at": format_timestamp(update_time),
                "parent_project_gid": None,
                "parent_portfolio_gid": portfolio["gid"],
                "parent_goal_gid": None,
            }
            status_updates.append(update)
    
    # Goal status updates
    for goal in goals:
        if not probability_check(0.40):
            continue
        
        workspace_gid = goal["workspace_gid"]
        ws_users = users_by_workspace.get(workspace_gid, [])
        
        if not ws_users:
            continue
        
        try:
            goal_created = datetime.strptime(goal["created_at"], "%Y-%m-%d %H:%M:%S")
        except:
            goal_created = NOW - timedelta(days=60)
        
        update_time = goal_created + timedelta(days=random.randint(14, 45))
        if update_time > NOW:
            update_time = NOW - timedelta(days=random.randint(1, 7))
        
        author = random.choice(ws_users)
        status_type = "on_track" if not goal.get("is_completed") else "on_track"
        
        text = generate_status_update(
            goal["name"],
            status_type,
            author["name"]
        )
        
        update = {
            "gid": generate_gid(),
            "workspace_gid": workspace_gid,
            "author_gid": author["gid"],
            "status_type": status_type,
            "text": text,
            "created_at": format_timestamp(update_time),
            "parent_project_gid": None,
            "parent_portfolio_gid": None,
            "parent_goal_gid": goal["gid"],
        }
        status_updates.append(update)
    
    return status_updates


if __name__ == "__main__":
    print("Status updates generator ready")
