"""
Attachments Generator
=====================

Generates attachments table data.

Table Schema:
- gid: TEXT PRIMARY KEY
- workspace_gid: TEXT NOT NULL REFERENCES workspaces(gid)
- parent_task_gid: TEXT
- parent_brief_gid: TEXT
- name: TEXT NOT NULL
- resource_url: TEXT
- resource_type: TEXT CHECK(resource_type IN ('image', 'video', 'pdf', 'spreadsheet'))
- created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- created_by_gid: TEXT

Methodology:
- 15% of tasks have attachments
- Resource types: image (40%), pdf (30%), spreadsheet (20%), video (10%)
- Realistic file naming patterns
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
from typing import List, Dict, Any
from datetime import datetime, timedelta

from utils.base import (
    generate_gid, format_timestamp, random_timestamp, probability_check
)
from scrapers.data_sources import ATTACHMENT_TEMPLATES
from utils.config import VOLUMES, NOW


def generate_attachments(
    tasks: List[Dict[str, Any]],
    project_briefs: List[Dict[str, Any]],
    users: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Generate attachment records.
    
    Attachments can be on tasks or project briefs.
    """
    attachments = []
    
    # Users by workspace
    users_by_workspace = {}
    for user in users:
        ws_gid = user["workspace_gid"]
        if ws_gid not in users_by_workspace:
            users_by_workspace[ws_gid] = []
        users_by_workspace[ws_gid].append(user)
    
    attachment_id = 1
    
    # Task attachments
    for task in tasks:
        if not probability_check(VOLUMES["attachments_ratio"]):
            continue
        
        workspace_gid = task["workspace_gid"]
        
        # Parse task created_at
        try:
            task_created = datetime.strptime(task["created_at"], "%Y-%m-%d %H:%M:%S")
        except:
            task_created = NOW - timedelta(days=30)
        
        # 1-3 attachments per task with attachments
        num_attachments = random.randint(1, 3)
        
        ws_users = users_by_workspace.get(workspace_gid, [])
        
        for _ in range(num_attachments):
            # Resource type distribution
            type_weights = {"image": 0.40, "pdf": 0.30, "spreadsheet": 0.20, "video": 0.10}
            resource_type = random.choices(
                list(type_weights.keys()),
                weights=list(type_weights.values())
            )[0]
            
            # Get template for this type
            templates = ATTACHMENT_TEMPLATES.get(resource_type, ATTACHMENT_TEMPLATES["image"])
            template = random.choice(templates)
            filename = template[0].format(id=attachment_id)
            
            attachment_time = random_timestamp(
                task_created,
                min(task_created + timedelta(days=14), NOW),
                weekday_weighted=True
            )
            
            creator = random.choice(ws_users) if ws_users else None
            
            attachment = {
                "gid": generate_gid(),
                "workspace_gid": workspace_gid,
                "parent_task_gid": task["gid"],
                "parent_brief_gid": None,
                "name": filename,
                "resource_url": f"https://storage.example.com/files/{filename}",
                "resource_type": resource_type,
                "created_at": format_timestamp(attachment_time),
                "created_by_gid": creator["gid"] if creator else None,
            }
            attachments.append(attachment)
            attachment_id += 1
    
    # Brief attachments
    for brief in project_briefs:
        if not probability_check(0.30):  # 30% of briefs have attachments
            continue
        
        workspace_gid = brief["workspace_gid"]
        
        try:
            brief_created = datetime.strptime(brief["created_at"], "%Y-%m-%d %H:%M:%S")
        except:
            brief_created = NOW - timedelta(days=30)
        
        ws_users = users_by_workspace.get(workspace_gid, [])
        
        # 1-2 per brief
        for _ in range(random.randint(1, 2)):
            resource_type = random.choice(["image", "pdf"])
            templates = ATTACHMENT_TEMPLATES.get(resource_type, ATTACHMENT_TEMPLATES["image"])
            template = random.choice(templates)
            filename = template[0].format(id=attachment_id)
            
            creator = random.choice(ws_users) if ws_users else None
            
            attachment = {
                "gid": generate_gid(),
                "workspace_gid": workspace_gid,
                "parent_task_gid": None,
                "parent_brief_gid": brief["gid"],
                "name": filename,
                "resource_url": f"https://storage.example.com/files/{filename}",
                "resource_type": resource_type,
                "created_at": format_timestamp(brief_created),
                "created_by_gid": creator["gid"] if creator else None,
            }
            attachments.append(attachment)
            attachment_id += 1
    
    return attachments


if __name__ == "__main__":
    test_tasks = [
        {"gid": "t1", "workspace_gid": "ws1", "created_at": "2025-12-01 10:00:00"}
    ]
    test_users = [{"gid": "u1", "workspace_gid": "ws1", "name": "Test"}]
    attachments = generate_attachments(test_tasks, [], test_users)
    print(f"Generated {len(attachments)} attachments")
