"""Generates likes for tasks and comments (~25% of tasks, ~15% of comments)."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
from typing import List, Dict, Any

from utils.base import generate_gid, probability_check


def generate_likes(
    tasks: List[Dict[str, Any]],
    stories: List[Dict[str, Any]],
    users: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Generate like records (each user can like a task/story only once)."""
    likes = []
    
    users_by_workspace = {}
    for user in users:
        ws_gid = user["workspace_gid"]
        if ws_gid not in users_by_workspace:
            users_by_workspace[ws_gid] = []
        users_by_workspace[ws_gid].append(user)
    
    task_likes = set()
    story_likes = set()
    
    for task in tasks:
        if not probability_check(0.25):
            continue
        
        workspace_gid = task["workspace_gid"]
        ws_users = users_by_workspace.get(workspace_gid, [])
        
        if not ws_users:
            continue
        
        num_likes = random.randint(1, min(5, len(ws_users)))
        likers = random.sample(ws_users, num_likes)
        
        for user in likers:
            key = (user["gid"], task["gid"])
            if key in task_likes:
                continue
            task_likes.add(key)
            
            likes.append({
                "gid": generate_gid(),
                "workspace_gid": workspace_gid,
                "user_gid": user["gid"],
                "task_gid": task["gid"],
                "story_gid": None,
            })
    
    comment_stories = [s for s in stories if s.get("type") == "comment"]
    
    for story in comment_stories:
        if not probability_check(0.15):
            continue
        
        workspace_gid = story["workspace_gid"]
        ws_users = users_by_workspace.get(workspace_gid, [])
        
        if not ws_users:
            continue
        
        num_likes = random.randint(1, min(3, len(ws_users)))
        likers = random.sample(ws_users, num_likes)
        
        for user in likers:
            key = (user["gid"], story["gid"])
            if key in story_likes:
                continue
            story_likes.add(key)
            
            likes.append({
                "gid": generate_gid(),
                "workspace_gid": workspace_gid,
                "user_gid": user["gid"],
                "task_gid": None,
                "story_gid": story["gid"],
            })
    
    return likes


if __name__ == "__main__":
    test_tasks = [{"gid": "t1", "workspace_gid": "ws1"}]
    test_stories = [{"gid": "s1", "workspace_gid": "ws1", "type": "comment"}]
    test_users = [{"gid": "u1", "workspace_gid": "ws1"}]
    likes = generate_likes(test_tasks, test_stories, test_users)
    print(f"Generated {len(likes)} likes")
