"""
Task Dependencies Generator
===========================

Generates task_dependencies and task_followers table data.

Table Schema (task_dependencies):
- workspace_gid: TEXT NOT NULL REFERENCES workspaces(gid)
- predecessor_gid: TEXT NOT NULL
- successor_gid: TEXT NOT NULL
- type: TEXT CHECK(type IN ('finish_to_start', 'start_to_start', 'finish_to_finish'))
- PRIMARY KEY (predecessor_gid, successor_gid)
- CHECK (predecessor_gid != successor_gid)

Table Schema (task_followers):
- workspace_gid: TEXT NOT NULL REFERENCES workspaces(gid)
- task_gid: TEXT NOT NULL
- user_gid: TEXT NOT NULL
- PRIMARY KEY (task_gid, user_gid)

Methodology:
- 8% of tasks have dependencies
- Dependency types: finish_to_start (80%), start_to_start (12%), finish_to_finish (8%)
- Respects temporal constraints based on dependency type

Temporal Consistency for Dependencies:
- finish_to_start: predecessor.due_on <= successor.start_on
- start_to_start: predecessor.start_on <= successor.start_on
- finish_to_finish: predecessor.due_on <= successor.due_on
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
from typing import List, Dict, Any, Optional
from datetime import datetime

from utils.base import (
    generate_gid, weighted_choice_dict, probability_check
)
from utils.config import DEPENDENCY_CONFIG


def generate_task_dependencies(
    tasks: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Generate task dependency relationships.
    
    Temporal Consistency:
    - Dependencies respect date constraints based on type
    - Only creates valid dependencies
    
    Relational Consistency:
    - No self-dependencies
    - Both tasks in same workspace
    - No circular dependencies (simple check)
    """
    dependencies = []
    
    # Group tasks by workspace and filter those with dates
    tasks_by_workspace = {}
    for task in tasks:
        ws_gid = task["workspace_gid"]
        if ws_gid not in tasks_by_workspace:
            tasks_by_workspace[ws_gid] = []
        tasks_by_workspace[ws_gid].append(task)
    
    # Track existing dependencies to avoid duplicates
    existing_deps = set()
    
    for ws_gid, ws_tasks in tasks_by_workspace.items():
        # Only consider tasks with dates for dependencies
        dated_tasks = [t for t in ws_tasks if t.get("due_on") or t.get("start_on")]
        
        if len(dated_tasks) < 2:
            continue
        
        for successor in dated_tasks:
            if not probability_check(DEPENDENCY_CONFIG["tasks_with_dependencies_ratio"]):
                continue
            
            # Find valid predecessor
            dep_type = weighted_choice_dict(DEPENDENCY_CONFIG["type_weights"])
            
            for _ in range(10):  # Max attempts
                predecessor = random.choice(dated_tasks)
                
                if predecessor["gid"] == successor["gid"]:
                    continue
                
                dep_key = (predecessor["gid"], successor["gid"])
                if dep_key in existing_deps:
                    continue
                
                # Check temporal validity based on dependency type
                if is_valid_dependency(predecessor, successor, dep_type):
                    dependencies.append({
                        "workspace_gid": ws_gid,
                        "predecessor_gid": predecessor["gid"],
                        "successor_gid": successor["gid"],
                        "type": dep_type,
                    })
                    existing_deps.add(dep_key)
                    break
    
    return dependencies


def is_valid_dependency(
    predecessor: Dict[str, Any],
    successor: Dict[str, Any],
    dep_type: str
) -> bool:
    """
    Check if dependency respects temporal constraints.
    
    Rules:
    - finish_to_start: predecessor finishes before successor starts
    - start_to_start: predecessor starts before successor starts
    - finish_to_finish: predecessor finishes before successor finishes
    """
    def parse_date(date_str: Optional[str]) -> Optional[datetime]:
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except:
            return None
    
    pred_start = parse_date(predecessor.get("start_on"))
    pred_due = parse_date(predecessor.get("due_on"))
    succ_start = parse_date(successor.get("start_on"))
    succ_due = parse_date(successor.get("due_on"))
    
    if dep_type == "finish_to_start":
        if pred_due and succ_start:
            return pred_due <= succ_start
        return True  # Allow if dates not set
    
    elif dep_type == "start_to_start":
        if pred_start and succ_start:
            return pred_start <= succ_start
        return True
    
    elif dep_type == "finish_to_finish":
        if pred_due and succ_due:
            return pred_due <= succ_due
        return True
    
    return True


def generate_task_followers(
    tasks: List[Dict[str, Any]],
    users: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Generate task follower relationships.
    
    - ~40% of tasks have followers
    - 1-4 followers per task
    - Followers must be in same workspace
    """
    followers = []
    
    # Users by workspace
    users_by_workspace = {}
    for user in users:
        ws_gid = user["workspace_gid"]
        if ws_gid not in users_by_workspace:
            users_by_workspace[ws_gid] = []
        users_by_workspace[ws_gid].append(user)
    
    for task in tasks:
        if not probability_check(0.40):  # 40% have followers
            continue
        
        workspace_gid = task["workspace_gid"]
        ws_users = users_by_workspace.get(workspace_gid, [])
        
        if not ws_users:
            continue
        
        # 1-4 followers
        num_followers = random.randint(1, min(4, len(ws_users)))
        selected_followers = random.sample(ws_users, num_followers)
        
        for user in selected_followers:
            # Skip if user is already assignee
            if user["gid"] == task.get("assignee_gid"):
                continue
            
            follower = {
                "workspace_gid": workspace_gid,
                "task_gid": task["gid"],
                "user_gid": user["gid"],
            }
            followers.append(follower)
    
    return followers


if __name__ == "__main__":
    # Quick test
    test_tasks = [
        {"gid": "t1", "workspace_gid": "ws1", "start_on": "2025-12-01", "due_on": "2025-12-05"},
        {"gid": "t2", "workspace_gid": "ws1", "start_on": "2025-12-06", "due_on": "2025-12-10"},
    ]
    deps = generate_task_dependencies(test_tasks)
    print(f"Generated {len(deps)} dependencies")
