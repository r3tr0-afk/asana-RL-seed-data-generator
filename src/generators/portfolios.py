"""
Portfolios Generator
====================

Generates portfolios table data.

Table Schema:
- gid: TEXT PRIMARY KEY
- workspace_gid: TEXT NOT NULL REFERENCES workspaces(gid)
- owner_gid: TEXT
- name: TEXT NOT NULL
- color: TEXT
- created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

Methodology:
- Portfolio names follow OKR/strategic initiative patterns
- Owned by senior users (first 30% in creation order)
- Created early in history (strategic tools set up first)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
from typing import List, Dict, Any
from datetime import timedelta

from utils.base import generate_gid, format_timestamp, generate_creation_wave
from scrapers.data_sources import PORTFOLIO_TEMPLATES
from utils.config import VOLUMES, HISTORY_START, ASANA_COLORS, NOW


def generate_portfolios(
    workspaces: List[Dict[str, Any]],
    users: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Generate portfolio records.
    
    Args:
        workspaces: List of workspace records
        users: List of user records (for owner assignment)
    
    Returns:
        List of portfolio dictionaries
    
    Methodology:
    - Strategic portfolios for quarterly/yearly planning
    - Owners are typically senior users
    - Created at beginning of planning periods
    """
    portfolios = []
    
    num_portfolios = VOLUMES["portfolios"]
    
    # Portfolios created early in history
    creation_times = generate_creation_wave(
        num_portfolios,
        HISTORY_START - timedelta(days=20),
        HISTORY_START + timedelta(days=30),
        growth_curve="linear"
    )
    
    # Get users per workspace for owner assignment
    users_by_workspace = {}
    for user in users:
        ws_gid = user["workspace_gid"]
        if ws_gid not in users_by_workspace:
            users_by_workspace[ws_gid] = []
        users_by_workspace[ws_gid].append(user)
    
    for i in range(num_portfolios):
        workspace = workspaces[i % len(workspaces)]
        ws_gid = workspace["gid"]
        
        # Select owner (prefer earlier users - more senior)
        ws_users = users_by_workspace.get(ws_gid, [])
        if ws_users:
            senior_pool = ws_users[:max(1, len(ws_users) // 3)]  # Top 1/3
            owner = random.choice(senior_pool)
            owner_gid = owner["gid"]
        else:
            owner_gid = None
        
        # Generate portfolio name
        template = random.choice(PORTFOLIO_TEMPLATES)
        name = template.format(
            quarter=((NOW.month - 1) // 3) + 1,
            year=NOW.year,
            team=random.choice(["Engineering", "Product", "Company"])
        )
        
        portfolio = {
            "gid": generate_gid(),
            "workspace_gid": ws_gid,
            "owner_gid": owner_gid,
            "name": name,
            "color": random.choice(ASANA_COLORS),
            "created_at": format_timestamp(creation_times[i]),
        }
        portfolios.append(portfolio)
    
    return portfolios


if __name__ == "__main__":
    from gen_workspaces import generate_workspaces
    from gen_users import generate_users
    
    workspaces = generate_workspaces()
    users, _ = generate_users(workspaces)
    portfolios = generate_portfolios(workspaces, users)
    
    print(f"Generated {len(portfolios)} portfolios")
    for p in portfolios:
        print(f"  {p['name']}")
