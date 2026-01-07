"""
Users Generator
===============

Generates users and workspace_memberships table data.

Table Schema (users):
- gid: TEXT PRIMARY KEY
- workspace_gid: TEXT NOT NULL REFERENCES workspaces(gid)
- email: TEXT NOT NULL UNIQUE
- name: TEXT NOT NULL
- photo_url: TEXT
- status: TEXT CHECK(status IN ('active', 'away', 'dnd', 'deactivated')) DEFAULT 'active'
- created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

Table Schema (workspace_memberships):
- workspace_gid: TEXT NOT NULL REFERENCES workspaces(gid)
- user_gid: TEXT NOT NULL REFERENCES users(gid)
- is_guest: BOOLEAN DEFAULT 0
- created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- PRIMARY KEY (workspace_gid, user_gid)

Methodology:
- Names from US Census Bureau demographic data
- Email format: firstname.lastname@domain
- Status distribution: 90% active, 5% away, 3% dnd, 2% deactivated
- Photo URLs using placeholder service pattern
- Creation timestamps distributed over 6-month history
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Dict, Any, Tuple
from datetime import datetime

from utils.base import (
    generate_gid, format_timestamp, weighted_choice_dict,
    generate_creation_wave
)
from scrapers.data_sources import get_random_full_name
from utils.config import (
    VOLUMES, HISTORY_START, HISTORY_END, USER_STATUS_WEIGHTS,
    TEAM_MEMBERSHIP_DISTRIBUTION
)


def generate_users(workspaces: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Generate user records and workspace memberships.
    
    Args:
        workspaces: List of workspace records (need gid and domain)
    
    Returns:
        Tuple of (users list, workspace_memberships list)
    
    Methodology:
    - Census-based name distribution for realistic demographics
    - 90% active, gradual decreasing for other statuses
    - Linear growth curve for creation timestamps
    - Guest ratio: 5%
    """
    users = []
    memberships = []
    
    num_users = VOLUMES["users"]
    
    # Generate creation timestamps with growth curve
    creation_times = generate_creation_wave(
        num_users, HISTORY_START, HISTORY_END, growth_curve="s_curve"
    )
    
    # Track used emails to ensure uniqueness
    used_emails = set()
    
    for i in range(num_users):
        workspace = workspaces[i % len(workspaces)]
        workspace_gid = workspace["gid"]
        domain = workspace["domain"]
        
        # Generate unique name and email
        max_attempts = 10
        for _ in range(max_attempts):
            first_name, last_name = get_random_full_name()
            full_name = f"{first_name} {last_name}"
            email = f"{first_name.lower()}.{last_name.lower()}@{domain}"
            
            if email not in used_emails:
                used_emails.add(email)
                break
            else:
                # Add number suffix for uniqueness
                suffix = len([e for e in used_emails if e.startswith(f"{first_name.lower()}.{last_name.lower()}")])
                email = f"{first_name.lower()}.{last_name.lower()}{suffix + 1}@{domain}"
                if email not in used_emails:
                    used_emails.add(email)
                    break
        
        # Determine status based on distribution
        # Ref: Average organization has ~5% away at any time
        status = weighted_choice_dict(USER_STATUS_WEIGHTS)
        
        user_gid = generate_gid()
        
        user = {
            "gid": user_gid,
            "workspace_gid": workspace_gid,
            "email": email,
            "name": full_name,
            "photo_url": f"https://ui-avatars.com/api/?name={first_name}+{last_name}&size=128",
            "status": status,
            "created_at": format_timestamp(creation_times[i]),
        }
        users.append(user)
        
        # Create workspace membership
        is_guest = 1 if i < int(num_users * TEAM_MEMBERSHIP_DISTRIBUTION["guest_ratio"]) else 0
        
        membership = {
            "workspace_gid": workspace_gid,
            "user_gid": user_gid,
            "is_guest": is_guest,
            "created_at": format_timestamp(creation_times[i]),
        }
        memberships.append(membership)
    
    return users, memberships


if __name__ == "__main__":
    # Test generation
    from gen_workspaces import generate_workspaces
    
    workspaces = generate_workspaces()
    users, memberships = generate_users(workspaces)
    
    print(f"Generated {len(users)} users and {len(memberships)} memberships")
    for user in users[:5]:
        print(user)
