"""
Tasks Generator
===============

Generates tasks table data - the core entity of the Asana simulation.

Table Schema:
- gid: TEXT PRIMARY KEY
- workspace_gid: TEXT NOT NULL REFERENCES workspaces(gid)
- assignee_gid: TEXT
- parent_task_gid: TEXT
- name: TEXT NOT NULL
- description: TEXT
- created_at: TIMESTAMP NOT NULL
- start_on: DATE
- due_on: DATE
- completed_at: TIMESTAMP
- completed: BOOLEAN DEFAULT 0
- is_milestone: BOOLEAN DEFAULT 0

Methodology:
============

1. TASK NAMES (LLM + Templates)
   - Engineering: "[Component] - [Action] - [Detail]" (GitHub Issues analysis)
   - Marketing: "[Campaign] - [Deliverable]" pattern
   - Per-archetype templates for consistency

2. DESCRIPTIONS (LLM + Templates)
   - 20% empty, 50% short (1-3 sentences), 30% detailed (bullets)
   - Templates include requirements, acceptance criteria

3. ASSIGNMENT (Heuristics)
   - 15% unassigned (Asana benchmarks)
   - Assigned based on team membership
   - Weight distribution across team members

4. DUE DATES (Synthetic + Heuristics)
   - 25% within 1 week
   - 40% within 1 month
   - 20% 1-3 months out
   - 10% no due date
   - 5% overdue
   - 85% avoid weekends

5. COMPLETION (Synthetic + Heuristics)
   - Sprint: 70-85% completion
   - Kanban: 55-70%
   - Ongoing: 40-55%
   - Older tasks more likely completed

6. SUBTASKS
   - 20% of tasks have subtasks
   - Max 2 levels deep
   - Parent created before children

Temporal Consistency Rules:
===========================
1. parent_task.created_at <= child_task.created_at
2. created_at <= completed_at <= NOW
3. start_on <= due_on (when both present)
4. Milestone: start_on == due_on OR start_on IS NULL

Relational Consistency:
=======================
1. Assignee must be workspace member
2. Parent task must be in same workspace
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

from utils.base import (
    generate_gid, format_timestamp, format_date,
    generate_creation_wave, generate_due_date, generate_start_date,
    calculate_completion_timestamp, weighted_choice_dict,
    probability_check, random_subset
)
from utils.llm_content import generate_task_description
from scrapers.data_sources import get_random_task_name
from utils.config import (
    VOLUMES, HISTORY_START, HISTORY_END, NOW,
    TASK_CONFIG, PROJECT_CONFIG
)


def generate_tasks(
    workspaces: List[Dict[str, Any]],
    projects: List[Dict[str, Any]],
    sections: List[Dict[str, Any]],
    team_memberships: List[Dict[str, Any]],
    users: List[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Generate task records.
    
    Args:
        workspaces: Workspace records
        projects: Project records
        sections: Section records
        team_memberships: Team membership records
        users: User records
    
    Returns:
        Tuple of (tasks, task_project_memberships)
    
    This is the most complex generator as tasks have:
    - Multiple parent/child relationships
    - Complex temporal constraints
    - Project and section associations
    - Completion state logic
    """
    tasks = []
    task_project_memberships = []
    
    num_tasks = VOLUMES["tasks"]
    subtask_ratio = VOLUMES["subtask_ratio"]
    
    # Calculate base tasks vs subtasks
    num_base_tasks = int(num_tasks * (1 - subtask_ratio))
    num_subtasks = num_tasks - num_base_tasks
    
    # Creation times for base tasks
    base_creation_times = generate_creation_wave(
        num_base_tasks,
        HISTORY_START + timedelta(days=14),  # After projects created
        HISTORY_END - timedelta(days=1),
        growth_curve="exponential"  # More tasks created recently
    )
    
    # Build lookups
    user_by_gid = {u["gid"]: u for u in users}
    project_by_gid = {p["gid"]: p for p in projects}
    
    # Sections by project
    sections_by_project = {}
    for section in sections:
        proj_gid = section["project_gid"]
        if proj_gid not in sections_by_project:
            sections_by_project[proj_gid] = []
        sections_by_project[proj_gid].append(section)
    
    # Team members by team
    members_by_team = {}
    for membership in team_memberships:
        team_gid = membership["team_gid"]
        if team_gid not in members_by_team:
            members_by_team[team_gid] = []
        members_by_team[team_gid].append(membership["user_gid"])
    
    # Users by workspace
    users_by_workspace = {}
    for user in users:
        ws_gid = user["workspace_gid"]
        if ws_gid not in users_by_workspace:
            users_by_workspace[ws_gid] = []
        users_by_workspace[ws_gid].append(user["gid"])
    
    # =========================================================================
    # PHASE 1: Generate base tasks (no parent)
    # =========================================================================
    base_tasks = []
    
    for i in range(num_base_tasks):
        # Select project (weighted by recency)
        project = random.choice(projects)
        workspace_gid = project["workspace_gid"]
        archetype = project.get("archetype", "kanban")
        team_gid = project.get("team_gid")
        proj_created = datetime.strptime(project["created_at"], "%Y-%m-%d %H:%M:%S")
        
        created_at = base_creation_times[i]
        
        # Ensure task created after project
        if created_at < proj_created:
            created_at = proj_created + timedelta(hours=random.randint(1, 48))
        
        # Get project sections
        proj_sections = sections_by_project.get(project["gid"], [])
        
        # Assignee selection
        # 15% unassigned per Asana benchmarks
        if probability_check(TASK_CONFIG["unassigned_ratio"]):
            assignee_gid = None
        else:
            # Prefer team members
            team_members = members_by_team.get(team_gid, [])
            if team_members:
                assignee_gid = random.choice(team_members)
            else:
                ws_users = users_by_workspace.get(workspace_gid, [])
                assignee_gid = random.choice(ws_users) if ws_users else None
        
        # Generate task name
        category = "engineering" if archetype in ["sprint", "bugs"] else "general"
        task_name = get_random_task_name(archetype, category)
        
        # Description complexity
        desc_type = weighted_choice_dict(TASK_CONFIG["description_distribution"])
        description = generate_task_description(task_name, archetype, desc_type)
        
        # Due date
        project_due = None
        if project.get("due_date"):
            try:
                project_due = datetime.strptime(project["due_date"], "%Y-%m-%d")
            except:
                pass
        
        due_on = generate_due_date(
            created_at,
            TASK_CONFIG["due_date_distribution"],
            project_due
        )
        
        # Start date (35% have start dates)
        start_on = generate_start_date(due_on, TASK_CONFIG["has_start_date_ratio"])
        
        # Milestone check (5%)
        is_milestone = 1 if probability_check(TASK_CONFIG["milestone_ratio"]) else 0
        if is_milestone and start_on and due_on:
            # Milestones: start_on == due_on
            start_on = due_on
        
        # Completion logic based on project archetype
        completion_range = TASK_CONFIG["completion_rates"].get(archetype, (0.5, 0.7))
        base_completion_rate = random.uniform(*completion_range)
        
        # Older tasks more likely completed
        days_old = (NOW - created_at).days
        age_factor = min(1.5, 1 + (days_old / 180) * 0.5)
        completion_probability = min(0.95, base_completion_rate * age_factor)
        
        completed = 1 if probability_check(completion_probability) else 0
        
        if completed:
            completed_at = calculate_completion_timestamp(created_at)
        else:
            completed_at = None
        
        # Select section (workflow position)
        section_gid = None
        if proj_sections:
            if completed:
                # Completed tasks in last section
                section = proj_sections[-1]
            else:
                # Distribute across active sections
                active_sections = proj_sections[:-1] if len(proj_sections) > 1 else proj_sections
                section = random.choice(active_sections)
            section_gid = section["gid"]
        
        task = {
            "gid": generate_gid(),
            "workspace_gid": workspace_gid,
            "assignee_gid": assignee_gid,
            "parent_task_gid": None,
            "name": task_name,
            "description": description,
            "created_at": format_timestamp(created_at),
            "start_on": format_date(start_on),
            "due_on": format_date(due_on),
            "completed_at": format_timestamp(completed_at) if completed_at else None,
            "completed": completed,
            "is_milestone": is_milestone,
            # Store metadata for subtask generation
            "_project_gid": project["gid"],
            "_section_gid": section_gid,
            "_archetype": archetype,
            "_team_gid": team_gid,
            "_created_dt": created_at,
        }
        base_tasks.append(task)
        
        # Create task-project membership
        task_project_memberships.append({
            "workspace_gid": workspace_gid,
            "task_gid": task["gid"],
            "project_gid": project["gid"],
            "section_gid": section_gid,
        })
    
    tasks.extend(base_tasks)
    
    # =========================================================================
    # PHASE 2: Generate subtasks
    # =========================================================================
    # Select parent tasks for subtasks
    eligible_parents = [t for t in base_tasks if not t.get("is_milestone")]
    
    if eligible_parents and num_subtasks > 0:
        # Distribute subtasks among parents
        subtasks_per_parent = max(1, num_subtasks // min(len(eligible_parents), num_subtasks // 2))
        
        subtask_count = 0
        for parent in random.sample(eligible_parents, min(len(eligible_parents), num_subtasks)):
            if subtask_count >= num_subtasks:
                break
            
            # 1-4 subtasks per parent
            num_children = random.randint(1, min(4, num_subtasks - subtask_count))
            
            parent_created = parent["_created_dt"]
            
            for j in range(num_children):
                if subtask_count >= num_subtasks:
                    break
                
                # Subtask created after parent (temporal consistency)
                child_created = parent_created + timedelta(
                    hours=random.randint(1, 72),
                    minutes=random.randint(0, 59)
                )
                
                if child_created > NOW:
                    child_created = NOW - timedelta(hours=random.randint(1, 24))
                
                # Subtask naming
                subtask_name = get_random_task_name(parent["_archetype"], "general")
                if len(subtask_name) > 60:
                    subtask_name = subtask_name[:57] + "..."
                
                # Subtasks often simpler descriptions
                if probability_check(0.6):
                    description = ""
                else:
                    description = generate_task_description(subtask_name, parent["_archetype"], "short")
                
                # Due date same or before parent
                parent_due = None
                if parent.get("due_on"):
                    try:
                        parent_due = datetime.strptime(parent["due_on"], "%Y-%m-%d")
                        due_on = parent_due - timedelta(days=random.randint(0, 3))
                    except:
                        due_on = None
                else:
                    due_on = None
                
                # Completion follows parent
                if parent["completed"]:
                    completed = 1 if probability_check(0.9) else 0
                else:
                    completed = 1 if probability_check(0.3) else 0
                
                if completed:
                    completed_at = calculate_completion_timestamp(child_created)
                else:
                    completed_at = None
                
                # Same team/assignee pool as parent
                team_members = members_by_team.get(parent["_team_gid"], [])
                if team_members and probability_check(0.85):
                    assignee_gid = random.choice(team_members)
                else:
                    assignee_gid = parent.get("assignee_gid")
                
                subtask = {
                    "gid": generate_gid(),
                    "workspace_gid": parent["workspace_gid"],
                    "assignee_gid": assignee_gid,
                    "parent_task_gid": parent["gid"],
                    "name": subtask_name,
                    "description": description,
                    "created_at": format_timestamp(child_created),
                    "start_on": None,  # Subtasks rarely have start dates
                    "due_on": format_date(due_on),
                    "completed_at": format_timestamp(completed_at) if completed_at else None,
                    "completed": completed,
                    "is_milestone": 0,  # Subtasks are never milestones
                }
                tasks.append(subtask)
                
                # Subtasks inherit project membership from parent
                task_project_memberships.append({
                    "workspace_gid": parent["workspace_gid"],
                    "task_gid": subtask["gid"],
                    "project_gid": parent["_project_gid"],
                    "section_gid": parent["_section_gid"],
                })
                
                subtask_count += 1
    
    # Clean up internal metadata from tasks
    for task in tasks:
        for key in list(task.keys()):
            if key.startswith("_"):
                del task[key]
    
    return tasks, task_project_memberships


if __name__ == "__main__":
    from gen_workspaces import generate_workspaces
    from gen_users import generate_users
    from gen_teams import generate_teams, generate_team_memberships
    from gen_projects import generate_projects, generate_sections
    
    workspaces = generate_workspaces()
    users, _ = generate_users(workspaces)
    teams = generate_teams(workspaces)
    team_memberships = generate_team_memberships(teams, users)
    projects = generate_projects(workspaces, teams, team_memberships, users)
    sections = generate_sections(projects)
    
    tasks, memberships = generate_tasks(
        workspaces, projects, sections, team_memberships, users
    )
    
    base_count = len([t for t in tasks if t["parent_task_gid"] is None])
    subtask_count = len([t for t in tasks if t["parent_task_gid"] is not None])
    completed_count = len([t for t in tasks if t["completed"]])
    
    print(f"Generated {len(tasks)} tasks:")
    print(f"  Base tasks: {base_count}")
    print(f"  Subtasks: {subtask_count}")
    print(f"  Completed: {completed_count} ({100*completed_count/len(tasks):.1f}%)")
    print(f"  Task-Project memberships: {len(memberships)}")
