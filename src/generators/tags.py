"""
Tags Generator
==============

Generates tags and task_tags table data.

Table Schema (tags):
- gid: TEXT PRIMARY KEY
- workspace_gid: TEXT NOT NULL REFERENCES workspaces(gid)
- name: TEXT NOT NULL
- color: TEXT
- UNIQUE(workspace_gid, name)

Table Schema (task_tags):
- workspace_gid: TEXT NOT NULL
- task_gid: TEXT NOT NULL
- tag_gid: TEXT NOT NULL
- PRIMARY KEY (task_gid, tag_gid)

Methodology:
- Standard productivity tags (P0-P3, Blocked, etc.)
- 30% of tasks have tags
- 1-3 tags per tagged task
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
from typing import List, Dict, Any, Tuple

from utils.base import generate_gid, probability_check, random_subset
from scrapers.data_sources import TAG_TEMPLATES
from utils.config import VOLUMES, TAG_CONFIG


def generate_tags(workspaces: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generate tag definitions.
    
    Tags are workspace-scoped and follow productivity tool patterns.
    """
    tags = []
    
    num_tags = min(VOLUMES["tags"], len(TAG_TEMPLATES))
    selected_tags = TAG_TEMPLATES[:num_tags]
    
    for workspace in workspaces:
        for name, color in selected_tags:
            tag = {
                "gid": generate_gid(),
                "workspace_gid": workspace["gid"],
                "name": name,
                "color": color,
            }
            tags.append(tag)
    
    return tags


def generate_task_tags(
    tasks: List[Dict[str, Any]],
    tags: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Generate task-tag associations.
    
    Relational Consistency:
    - Tags and tasks must be in same workspace
    - Each task-tag pair is unique
    """
    task_tags = []
    
    # Group tags by workspace
    tags_by_workspace = {}
    for tag in tags:
        ws_gid = tag["workspace_gid"]
        if ws_gid not in tags_by_workspace:
            tags_by_workspace[ws_gid] = []
        tags_by_workspace[ws_gid].append(tag)
    
    for task in tasks:
        # 30% of tasks have tags
        if not probability_check(TAG_CONFIG["tasks_with_tags_ratio"]):
            continue
        
        workspace_gid = task["workspace_gid"]
        ws_tags = tags_by_workspace.get(workspace_gid, [])
        
        if not ws_tags:
            continue
        
        # 1-3 tags per task
        num_tags = random.randint(1, min(TAG_CONFIG["max_tags_per_task"], len(ws_tags)))
        selected_tags = random.sample(ws_tags, num_tags)
        
        for tag in selected_tags:
            task_tag = {
                "workspace_gid": workspace_gid,
                "task_gid": task["gid"],
                "tag_gid": tag["gid"],
            }
            task_tags.append(task_tag)
    
    return task_tags


if __name__ == "__main__":
    test_workspaces = [{"gid": "ws1", "name": "Test"}]
    tags = generate_tags(test_workspaces)
    print(f"Generated {len(tags)} tags")
    for t in tags[:5]:
        print(f"  {t['name']} ({t['color']})")
