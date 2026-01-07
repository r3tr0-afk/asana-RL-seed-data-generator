"""
Stories and Comments Generator
==============================

Generates stories (comments/activity) table data.

Table Schema:
- gid: TEXT PRIMARY KEY
- workspace_gid: TEXT NOT NULL REFERENCES workspaces(gid)
- task_gid: TEXT NOT NULL
- created_by_gid: TEXT
- text: TEXT NOT NULL
- type: TEXT CHECK(type IN ('comment', 'system')) DEFAULT 'comment'
- created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

Methodology:
- 80% comments, 20% system stories
- Average 2.5 comments per task
- Comments created after task creation
- System stories log events (assignment, completion, etc.)
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
from utils.llm_content import generate_comment
from scrapers.data_sources import COMMENT_TEMPLATES, SYSTEM_STORY_TEMPLATES
from utils.config import STORY_CONFIG, NOW


def generate_stories(
    tasks: List[Dict[str, Any]],
    users: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Generate story records for tasks.
    
    Temporal Consistency:
    - story.created_at >= task.created_at
    - story.created_at <= NOW
    """
    stories = []
    
    # Users by workspace
    users_by_workspace = {}
    for user in users:
        ws_gid = user["workspace_gid"]
        if ws_gid not in users_by_workspace:
            users_by_workspace[ws_gid] = []
        users_by_workspace[ws_gid].append(user)
    
    user_by_gid = {u["gid"]: u for u in users}
    
    for task in tasks:
        workspace_gid = task["workspace_gid"]
        task_gid = task["gid"]
        
        # Parse task created_at
        try:
            task_created = datetime.strptime(task["created_at"], "%Y-%m-%d %H:%M:%S")
        except:
            task_created = NOW - timedelta(days=30)
        
        # Number of stories (Poisson-ish distribution around mean)
        avg_stories = STORY_CONFIG["avg_comments_per_task"]
        num_stories = max(0, int(random.gauss(avg_stories, 1.5)))
        num_stories = min(num_stories, 10)  # Cap at 10
        
        ws_users = users_by_workspace.get(workspace_gid, [])
        
        for i in range(num_stories):
            # Story created sometime after task creation
            min_offset = timedelta(hours=i * 4)  # Space out stories
            max_offset = timedelta(days=min(30, (NOW - task_created).days or 1))
            
            story_time = random_timestamp(
                task_created + min_offset,
                min(task_created + max_offset, NOW),
                business_hours_only=False,
                weekday_weighted=True
            )
            
            # Author
            if ws_users:
                author = random.choice(ws_users)
                author_gid = author["gid"]
                author_name = author["name"]
            else:
                author_gid = None
                author_name = "Team Member"
            
            # Type: 80% comment, 20% system
            if probability_check(STORY_CONFIG["comment_ratio"]):
                story_type = "comment"
                text = generate_comment(
                    task["name"],
                    author_name,
                    {"mention": random.choice(ws_users)["name"].split()[0] if ws_users else "team"}
                )
            else:
                story_type = "system"
                # System stories
                template = random.choice(SYSTEM_STORY_TEMPLATES)
                text = template.format(
                    date=(story_time + timedelta(days=7)).strftime("%b %d"),
                    person=random.choice(ws_users)["name"] if ws_users else "someone",
                    project="the project",
                    section="In Progress",
                    priority="P1",
                    tag="blocked",
                )
            
            story = {
                "gid": generate_gid(),
                "workspace_gid": workspace_gid,
                "task_gid": task_gid,
                "created_by_gid": author_gid,
                "text": text,
                "type": story_type,
                "created_at": format_timestamp(story_time),
            }
            stories.append(story)
    
    return stories


if __name__ == "__main__":
    # Quick test
    test_tasks = [
        {"gid": "123", "workspace_gid": "ws1", "name": "Test task", "created_at": "2025-12-01 10:00:00"}
    ]
    test_users = [
        {"gid": "u1", "workspace_gid": "ws1", "name": "John Doe"}
    ]
    stories = generate_stories(test_tasks, test_users)
    print(f"Generated {len(stories)} stories")
