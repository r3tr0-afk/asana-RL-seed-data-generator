"""
Meta Provenance Generator
=========================

Generates _meta_provenance table for tracking data generation batches.

Table Schema:
- id: INTEGER PRIMARY KEY AUTOINCREMENT
- batch_id: TEXT NOT NULL
- entity_type: TEXT NOT NULL
- source_strategy: TEXT NOT NULL
- row_count: INTEGER
- timestamp: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Dict, Any
from datetime import datetime
import uuid


def generate_provenance_record(
    entity_type: str,
    source_strategy: str,
    row_count: int,
    batch_id: str = None
) -> Dict[str, Any]:
    """
    Create a provenance record for a data generation batch.
    
    Args:
        entity_type: Table name
        source_strategy: Method used (e.g., "synthetic", "LLM", "template")
        row_count: Number of rows generated
        batch_id: Batch identifier (auto-generated if not provided)
    
    Returns:
        Provenance record dictionary
    """
    if batch_id is None:
        batch_id = str(uuid.uuid4())[:8]
    
    return {
        "batch_id": batch_id,
        "entity_type": entity_type,
        "source_strategy": source_strategy,
        "row_count": row_count,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def create_provenance_records(
    data_counts: Dict[str, Dict[str, Any]],
    batch_id: str = None
) -> List[Dict[str, Any]]:
    """
    Create provenance records for all generated data.
    
    Args:
        data_counts: Dict of {table_name: {"count": n, "strategy": "..."}}
        batch_id: Shared batch ID for this generation run
    
    Returns:
        List of provenance records
    """
    if batch_id is None:
        batch_id = str(uuid.uuid4())[:8]
    
    records = []
    for table_name, info in data_counts.items():
        records.append(generate_provenance_record(
            entity_type=table_name,
            source_strategy=info.get("strategy", "synthetic"),
            row_count=info.get("count", 0),
            batch_id=batch_id,
        ))
    
    return records


# Strategy descriptions for documentation
STRATEGY_DESCRIPTIONS = {
    "workspaces": "Y Combinator-inspired company names, synthetic timestamps",
    "users": "US Census Bureau name distribution, Faker, weighted status",
    "workspace_memberships": "Derived from user-workspace relationships",
    "teams": "McKinsey organizational structure patterns",
    "team_memberships": "Cross-functional distribution (1-3 teams/user)",
    "portfolios": "OKR naming patterns, senior user ownership",
    "goals": "OKR framework templates, age-based completion",
    "projects": "Archetype-based templates (sprint/kanban/launch)",
    "project_templates": "Standard workflow templates",
    "project_briefs": "LLM + HTML templates",
    "sections": "Archetype-specific section templates",
    "tasks": "GitHub Issues patterns, LLM descriptions, log-normal completion",
    "task_project_memberships": "Derived from task-project associations",
    "task_dependencies": "Temporal constraint validation",
    "task_followers": "Random workspace member selection",
    "stories": "LLM comments (80%) + system events (20%)",
    "attachments": "Realistic file type distribution",
    "tags": "Productivity tool patterns (P0-P3, status)",
    "task_tags": "Random tag assignment (30% of tasks)",
    "likes": "Random user engagement",
    "custom_field_definitions": "Standard Asana field types",
    "custom_field_options": "Enum options for fields",
    "project_custom_field_settings": "Field-project associations",
    "portfolio_custom_field_settings": "Field-portfolio associations",
    "custom_field_values": "Type-safe value generation",
    "portfolio_custom_field_values": "Type-safe portfolio values",
    "status_updates": "LLM status summaries",
    "portfolio_items": "Project grouping relationships",
}
