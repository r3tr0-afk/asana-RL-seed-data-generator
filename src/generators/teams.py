"""
Teams Generator
===============

Generates teams and team_memberships table data.

Table Schema (teams):
- gid: TEXT PRIMARY KEY
- workspace_gid: TEXT NOT NULL REFERENCES workspaces(gid)
- name: TEXT NOT NULL
- description: TEXT
- created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- UNIQUE(workspace_gid, name)

Table Schema (team_memberships):
- team_gid: TEXT NOT NULL
- user_gid: TEXT NOT NULL
- workspace_gid: TEXT NOT NULL
- role: TEXT CHECK(role IN ('admin', 'member', 'commenter')) DEFAULT 'member'
- is_guest: BOOLEAN DEFAULT 0
- PRIMARY KEY (team_gid, user_gid)

Methodology:
- Team names from standard organizational structures (McKinsey research)
- Each user belongs to 1-3 teams (cross-functional team patterns)
- Admin ratio: 15% per team
- Team creation early in company history
- Relational Consistency: Users can only join teams in their workspace
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
from typing import List, Dict, Any, Tuple
from datetime import timedelta

from utils.base import (
    generate_gid, format_timestamp, weighted_choice,
    generate_creation_wave, probability_check
)
from scrapers.data_sources import TEAM_NAMES
from utils.config import (
    VOLUMES, HISTORY_START, HISTORY_END, TEAM_MEMBERSHIP_DISTRIBUTION
)


def generate_teams(workspaces: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generate team records.
    
    Args:
        workspaces: List of workspace records
    
    Returns:
        List of team dictionaries
    
    Methodology:
    - Standard department names from organizational research
    - Teams created in first month of company history
    """
    teams = []
    
    num_teams = min(VOLUMES["teams"], len(TEAM_NAMES))
    
    # Select team names (prioritize essential departments)
    selected_teams = TEAM_NAMES[:num_teams]
    
    # Teams created early in history
    team_start = HISTORY_START - timedelta(days=25)
    team_end = HISTORY_START
    creation_times = generate_creation_wave(
        num_teams, team_start, team_end, growth_curve="linear"
    )
    
    for i, (name, description) in enumerate(selected_teams):
        workspace = workspaces[i % len(workspaces)]
        
        team = {
            "gid": generate_gid(),
            "workspace_gid": workspace["gid"],
            "name": name,
            "description": description,
            "created_at": format_timestamp(creation_times[i]),
        }
        teams.append(team)
    
    return teams


def generate_team_memberships(
    teams: List[Dict[str, Any]],
    users: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Generate team membership records.
    
    Args:
        teams: List of team records
        users: List of user records
    
    Returns:
        List of team_membership dictionaries
    
    Methodology:
    - Each user belongs to 1-3 teams (cross-functional patterns)
    - Ref: Modern orgs emphasize cross-functional collaboration
    - Admin ratio: 15% per team
    - Larger teams: Engineering, Product (more members)
    - Smaller teams: Legal, Finance (fewer members)
    
    Relational Consistency:
    - Users can only join teams in their workspace
    - Team membership must reference valid team and user
    """
    memberships = []
    
    min_teams = TEAM_MEMBERSHIP_DISTRIBUTION["min_teams_per_user"]
    max_teams = TEAM_MEMBERSHIP_DISTRIBUTION["max_teams_per_user"]
    admin_ratio = TEAM_MEMBERSHIP_DISTRIBUTION["admin_ratio"]
    guest_ratio = TEAM_MEMBERSHIP_DISTRIBUTION["guest_ratio"]
    
    # Group users by workspace
    users_by_workspace = {}
    for user in users:
        ws_gid = user["workspace_gid"]
        if ws_gid not in users_by_workspace:
            users_by_workspace[ws_gid] = []
        users_by_workspace[ws_gid].append(user)
    
    # Group teams by workspace
    teams_by_workspace = {}
    for team in teams:
        ws_gid = team["workspace_gid"]
        if ws_gid not in teams_by_workspace:
            teams_by_workspace[ws_gid] = []
        teams_by_workspace[ws_gid].append(team)
    
    # Assign users to teams within their workspace
    for ws_gid, ws_users in users_by_workspace.items():
        ws_teams = teams_by_workspace.get(ws_gid, [])
        if not ws_teams:
            continue
        
        # Track team sizes for balancing
        team_members = {team["gid"]: [] for team in ws_teams}
        
        for user in ws_users:
            # Determine number of teams for this user
            num_teams_to_join = random.randint(min_teams, min(max_teams, len(ws_teams)))
            
            # Weight team selection - prefer less populated teams
            team_weights = []
            for team in ws_teams:
                # Larger weight for teams with fewer members
                current_size = len(team_members[team["gid"]])
                weight = 1.0 / (current_size + 1)
                
                # Boost engineering team (typically larger)
                if "Engineering" in team["name"]:
                    weight *= 2.5
                elif "Product" in team["name"]:
                    weight *= 1.8
                elif "Legal" in team["name"] or "Finance" in team["name"]:
                    weight *= 0.5
                
                team_weights.append(weight)
            
            # Select teams for this user
            selected_teams = []
            available_teams = list(zip(ws_teams, team_weights))
            
            for _ in range(num_teams_to_join):
                if not available_teams:
                    break
                
                teams_list, weights_list = zip(*available_teams)
                selected = weighted_choice(list(teams_list), list(weights_list))
                selected_teams.append(selected)
                
                # Remove selected team from available
                available_teams = [
                    (t, w) for t, w in available_teams if t["gid"] != selected["gid"]
                ]
            
            # Create memberships
            for team in selected_teams:
                # Determine role
                if probability_check(admin_ratio):
                    role = "admin"
                elif probability_check(0.05):  # 5% commenters
                    role = "commenter"
                else:
                    role = "member"
                
                membership = {
                    "team_gid": team["gid"],
                    "user_gid": user["gid"],
                    "workspace_gid": ws_gid,
                    "role": role,
                    "is_guest": 1 if probability_check(guest_ratio) else 0,
                }
                memberships.append(membership)
                team_members[team["gid"]].append(user["gid"])
    
    return memberships


if __name__ == "__main__":
    # Test generation
    from gen_workspaces import generate_workspaces
    from gen_users import generate_users
    
    workspaces = generate_workspaces()
    users, _ = generate_users(workspaces)
    teams = generate_teams(workspaces)
    memberships = generate_team_memberships(teams, users)
    
    print(f"Generated {len(teams)} teams and {len(memberships)} memberships")
    for team in teams:
        print(team["name"])
