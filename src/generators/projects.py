"""
Projects Generator
==================

Generates projects, project_templates, project_briefs, and sections table data.

Table Schema (projects):
- gid: TEXT PRIMARY KEY
- workspace_gid: TEXT NOT NULL REFERENCES workspaces(gid)
- team_gid: TEXT
- owner_gid: TEXT
- name: TEXT NOT NULL
- archetype: TEXT
- layout: TEXT DEFAULT 'list'
- current_status: TEXT CHECK(current_status IN ('on_track', 'at_risk', 'off_track'))
- due_date: DATE
- archived: BOOLEAN DEFAULT 0
- created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

Methodology:
- Project archetypes: sprint (35%), kanban (25%), launch (20%), ongoing (15%), bugs (5%)
- Status distribution: on_track (65%), at_risk (25%), off_track (10%)
- 12% of older projects archived
- Sections created per archetype template

Relational Consistency:
- Projects belong to teams within same workspace
- Sections belong to their parent project
- Owners must be team members
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
from typing import List, Dict, Any, Tuple
from datetime import timedelta

from utils.base import (
    generate_gid, format_timestamp, format_date,
    generate_creation_wave, weighted_choice_dict, probability_check
)
from utils.llm_content import generate_project_brief
from scrapers.data_sources import get_random_project_name, PROJECT_BRIEF_TEMPLATES
from utils.config import (
    VOLUMES, HISTORY_START, HISTORY_END, NOW,
    PROJECT_CONFIG, SECTION_TEMPLATES
)


def generate_projects(
    workspaces: List[Dict[str, Any]],
    teams: List[Dict[str, Any]],
    team_memberships: List[Dict[str, Any]],
    users: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Generate project records.
    
    Methodology:
    - Projects distributed across teams
    - Archetype determines workflow style
    - Status reflects project health
    - Older projects more likely archived
    """
    projects = []
    
    num_projects = VOLUMES["projects"]
    
    # Creation times distributed over history
    creation_times = generate_creation_wave(
        num_projects,
        HISTORY_START + timedelta(days=7),  # After teams created
        HISTORY_END - timedelta(days=7),
        growth_curve="s_curve"
    )
    
    # Build team -> members mapping
    team_members = {}
    for membership in team_memberships:
        team_gid = membership["team_gid"]
        if team_gid not in team_members:
            team_members[team_gid] = []
        team_members[team_gid].append(membership["user_gid"])
    
    # Group teams by workspace
    teams_by_workspace = {}
    for team in teams:
        ws_gid = team["workspace_gid"]
        if ws_gid not in teams_by_workspace:
            teams_by_workspace[ws_gid] = []
        teams_by_workspace[ws_gid].append(team)
    
    sprint_counter = 1
    
    for i in range(num_projects):
        workspace = workspaces[i % len(workspaces)]
        ws_gid = workspace["gid"]
        created_at = creation_times[i]
        
        # Select team
        ws_teams = teams_by_workspace.get(ws_gid, [])
        if not ws_teams:
            continue
        team = random.choice(ws_teams)
        
        # Select owner from team members
        members = team_members.get(team["gid"], [])
        owner_gid = random.choice(members) if members else None
        
        # Determine archetype
        archetype = weighted_choice_dict(PROJECT_CONFIG["archetype_weights"])
        
        # Generate name based on archetype
        context = {
            "number": sprint_counter if archetype == "sprint" else random.randint(1, 10),
            "quarter": ((NOW.month - 1) // 3) + 1,
            "year": NOW.year,
            "month": created_at.strftime("%b"),
        }
        if archetype == "sprint":
            sprint_counter += 1
        
        name = get_random_project_name(archetype, team["name"], context)
        
        # Layout based on archetype
        if archetype in ["sprint", "kanban", "bugs"]:
            layout = "board"
        elif archetype == "launch":
            layout = "timeline"
        else:
            layout = weighted_choice_dict(PROJECT_CONFIG["layout_weights"])
        
        # Status
        current_status = weighted_choice_dict(PROJECT_CONFIG["status_weights"])
        
        # Due date
        if probability_check(PROJECT_CONFIG["has_due_date_ratio"]):
            # Due date 2-12 weeks from creation
            due_date = created_at + timedelta(days=random.randint(14, 84))
            if due_date > NOW + timedelta(days=90):
                due_date = NOW + timedelta(days=random.randint(7, 60))
        else:
            due_date = None
        
        # Archived: older projects more likely
        days_old = (NOW - created_at).days
        archive_probability = PROJECT_CONFIG["archived_ratio"] * (days_old / 180)
        archived = 1 if probability_check(archive_probability) else 0
        
        project = {
            "gid": generate_gid(),
            "workspace_gid": ws_gid,
            "team_gid": team["gid"],
            "owner_gid": owner_gid,
            "name": name,
            "archetype": archetype,
            "layout": layout,
            "current_status": current_status,
            "due_date": format_date(due_date) if due_date else None,
            "archived": archived,
            "created_at": format_timestamp(created_at),
        }
        projects.append(project)
    
    return projects


def generate_project_templates(teams: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generate project template records.
    """
    templates = []
    
    num_templates = VOLUMES["project_templates"]
    
    template_names = [
        "Sprint Template",
        "Bug Tracking Template",
        "Product Launch Template",
        "Marketing Campaign Template",
        "Onboarding Template",
        "Weekly Standup Template",
        "Quarterly Planning Template",
        "Customer Feedback Template",
    ]
    
    for i in range(min(num_templates, len(template_names))):
        team = teams[i % len(teams)]
        
        # Structure JSON based on template type
        structure = {
            "sections": SECTION_TEMPLATES.get(
                "sprint" if "Sprint" in template_names[i] else "kanban",
                SECTION_TEMPLATES["kanban"]
            ),
            "default_fields": ["Priority", "Status"],
        }
        
        template = {
            "gid": generate_gid(),
            "team_gid": team["gid"],
            "name": template_names[i],
            "structure_json": str(structure),
            "created_at": format_timestamp(HISTORY_START + timedelta(days=i * 5)),
        }
        templates.append(template)
    
    return templates


def generate_sections(projects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generate section records for each project.
    
    Relational Consistency:
    - Each section belongs to exactly one project
    - Section names come from archetype templates
    - Order index maintains section ordering
    """
    sections = []
    
    for project in projects:
        archetype = project.get("archetype", "kanban")
        section_names = SECTION_TEMPLATES.get(archetype, SECTION_TEMPLATES["kanban"])
        
        for order_idx, section_name in enumerate(section_names):
            section = {
                "gid": generate_gid(),
                "workspace_gid": project["workspace_gid"],
                "project_gid": project["gid"],
                "name": section_name,
                "order_index": order_idx,
            }
            sections.append(section)
    
    return sections


def generate_project_briefs(
    projects: List[Dict[str, Any]],
    teams: List[Dict[str, Any]],
    users: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Generate project brief records.
    
    ~60% of projects have briefs
    """
    briefs = []
    
    # Build lookup dicts
    team_by_gid = {t["gid"]: t for t in teams}
    user_by_gid = {u["gid"]: u for u in users}
    
    for project in projects:
        # 60% have briefs
        if not probability_check(0.6):
            continue
        
        team = team_by_gid.get(project["team_gid"], {})
        owner = user_by_gid.get(project["owner_gid"], {})
        
        html_content = generate_project_brief(
            project_name=project["name"],
            team_name=team.get("name", "Team"),
            owner_name=owner.get("name", "Project Owner"),
            created_at=project["created_at"][:10],
        )
        
        brief = {
            "gid": generate_gid(),
            "workspace_gid": project["workspace_gid"],
            "project_gid": project["gid"],
            "html_text": html_content,
            "title": "Overview",
            "created_at": project["created_at"],
        }
        briefs.append(brief)
    
    return briefs


if __name__ == "__main__":
    from gen_workspaces import generate_workspaces
    from gen_users import generate_users
    from gen_teams import generate_teams, generate_team_memberships
    
    workspaces = generate_workspaces()
    users, _ = generate_users(workspaces)
    teams = generate_teams(workspaces)
    team_memberships = generate_team_memberships(teams, users)
    projects = generate_projects(workspaces, teams, team_memberships, users)
    sections = generate_sections(projects)
    
    print(f"Generated {len(projects)} projects and {len(sections)} sections")
    for p in projects[:5]:
        print(f"  [{p['archetype']}] {p['name']}")
