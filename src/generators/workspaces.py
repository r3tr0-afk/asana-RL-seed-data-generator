"""Generates workspace records."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Dict, Any
from datetime import timedelta

from utils.base import generate_gid, format_timestamp
from scrapers.data_sources import get_random_company_name
from utils.config import HISTORY_START, VOLUMES


def generate_workspaces() -> List[Dict[str, Any]]:
    """Generate workspace records."""
    workspaces = []
    num_workspaces = VOLUMES["workspaces"]
    
    for i in range(num_workspaces):
        company_name = get_random_company_name()
        
        if i > 0:
            domain = f"{company_name.lower().replace(' ', '')}{i}.com"
        else:
            domain = f"{company_name.lower().replace(' ', '')}.com"
        
        workspace = {
            "gid": generate_gid(),
            "name": company_name,
            "domain": domain,
            "is_organization": 1,
            "created_at": format_timestamp(HISTORY_START - timedelta(days=30)),
        }
        
        workspaces.append(workspace)
    
    return workspaces


if __name__ == "__main__":
    workspaces = generate_workspaces()
    for ws in workspaces:
        print(ws)
