"""
Portfolio Items Generator
=========================

Generates portfolio_items table data.

Table Schema:
- portfolio_gid: TEXT NOT NULL
- workspace_gid: TEXT NOT NULL
- linked_project_gid: TEXT
- linked_portfolio_gid: TEXT
- created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- CHECK (exactly one of linked_project_gid, linked_portfolio_gid is non-null)
- CHECK (portfolio_gid != linked_portfolio_gid)

Methodology:
- Portfolios contain projects (primary)
- Some portfolios may link to other portfolios
- Items from same workspace only
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
from typing import List, Dict, Any
from datetime import datetime, timedelta

from utils.base import format_timestamp, probability_check
from utils.config import NOW


def generate_portfolio_items(
    portfolios: List[Dict[str, Any]],
    projects: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Generate portfolio item records.
    
    Relational Consistency:
    - Projects and portfolios must be in same workspace
    - No self-linking portfolios
    - Each project can be in multiple portfolios
    """
    items = []
    
    # Group by workspace
    portfolios_by_workspace = {}
    for portfolio in portfolios:
        ws_gid = portfolio["workspace_gid"]
        if ws_gid not in portfolios_by_workspace:
            portfolios_by_workspace[ws_gid] = []
        portfolios_by_workspace[ws_gid].append(portfolio)
    
    projects_by_workspace = {}
    for project in projects:
        ws_gid = project["workspace_gid"]
        if ws_gid not in projects_by_workspace:
            projects_by_workspace[ws_gid] = []
        projects_by_workspace[ws_gid].append(project)
    
    for portfolio in portfolios:
        workspace_gid = portfolio["workspace_gid"]
        
        try:
            port_created = datetime.strptime(portfolio["created_at"], "%Y-%m-%d %H:%M:%S")
        except:
            port_created = NOW - timedelta(days=60)
        
        ws_projects = projects_by_workspace.get(workspace_gid, [])
        ws_portfolios = portfolios_by_workspace.get(workspace_gid, [])
        
        # Add 3-8 projects to each portfolio
        if ws_projects:
            num_projects = random.randint(3, min(8, len(ws_projects)))
            selected_projects = random.sample(ws_projects, num_projects)
            
            for project in selected_projects:
                item = {
                    "portfolio_gid": portfolio["gid"],
                    "workspace_gid": workspace_gid,
                    "linked_project_gid": project["gid"],
                    "linked_portfolio_gid": None,
                    "created_at": format_timestamp(port_created + timedelta(days=random.randint(1, 7))),
                }
                items.append(item)
        
        # Occasionally link to another portfolio (10% chance)
        if probability_check(0.10):
            other_portfolios = [p for p in ws_portfolios if p["gid"] != portfolio["gid"]]
            if other_portfolios:
                linked_portfolio = random.choice(other_portfolios)
                item = {
                    "portfolio_gid": portfolio["gid"],
                    "workspace_gid": workspace_gid,
                    "linked_project_gid": None,
                    "linked_portfolio_gid": linked_portfolio["gid"],
                    "created_at": format_timestamp(port_created + timedelta(days=random.randint(1, 14))),
                }
                items.append(item)
    
    return items


if __name__ == "__main__":
    print("Portfolio items generator ready")
