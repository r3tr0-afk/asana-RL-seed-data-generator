"""
Custom Fields Generator
=======================

Generates custom field definitions, options, settings, and values.

Tables:
- custom_field_definitions
- custom_field_options  
- project_custom_field_settings
- portfolio_custom_field_settings
- custom_field_values
- portfolio_custom_field_values

Methodology:
- Standard fields: Priority, Status, Story Points, Sprint, etc.
- Enum fields have predefined options
- Values match field type (enforced by schema)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
from typing import List, Dict, Any, Tuple

from utils.base import generate_gid, probability_check
from utils.config import CUSTOM_FIELD_TEMPLATES


def generate_custom_field_definitions(
    workspaces: List[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Generate custom field definitions and their options.
    
    Returns:
        Tuple of (definitions, options)
    """
    definitions = []
    options = []
    
    for workspace in workspaces:
        ws_gid = workspace["gid"]
        
        for field_template in CUSTOM_FIELD_TEMPLATES:
            field_gid = generate_gid()
            
            # Map type
            field_type = field_template["type"]
            if field_type == "enum":
                resource_subtype = "enum"
            elif field_type == "number":
                resource_subtype = "number"
            else:
                resource_subtype = "text"
            
            definition = {
                "gid": field_gid,
                "workspace_gid": ws_gid,
                "name": field_template["name"],
                "resource_subtype": resource_subtype,
            }
            definitions.append(definition)
            
            # Generate options for enum fields
            if field_type == "enum" and "options" in field_template:
                for option_name, option_color in field_template["options"]:
                    option = {
                        "gid": generate_gid(),
                        "field_gid": field_gid,
                        "workspace_gid": ws_gid,
                        "name": option_name,
                        "color": option_color,
                    }
                    options.append(option)
    
    return definitions, options


def generate_project_custom_field_settings(
    projects: List[Dict[str, Any]],
    field_definitions: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Generate project custom field settings.
    
    ~60% of projects have custom fields attached.
    """
    settings = []
    
    # Fields by workspace
    fields_by_workspace = {}
    for field in field_definitions:
        ws_gid = field["workspace_gid"]
        if ws_gid not in fields_by_workspace:
            fields_by_workspace[ws_gid] = []
        fields_by_workspace[ws_gid].append(field)
    
    for project in projects:
        if not probability_check(0.60):
            continue
        
        ws_gid = project["workspace_gid"]
        ws_fields = fields_by_workspace.get(ws_gid, [])
        
        if not ws_fields:
            continue
        
        # Attach 2-5 fields to project
        num_fields = random.randint(2, min(5, len(ws_fields)))
        selected_fields = random.sample(ws_fields, num_fields)
        
        for i, field in enumerate(selected_fields):
            setting = {
                "workspace_gid": ws_gid,
                "project_gid": project["gid"],
                "custom_field_gid": field["gid"],
                "is_important": 1 if i == 0 else 0,  # First field is important
            }
            settings.append(setting)
    
    return settings


def generate_portfolio_custom_field_settings(
    portfolios: List[Dict[str, Any]],
    field_definitions: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Generate portfolio custom field settings.
    """
    settings = []
    
    fields_by_workspace = {}
    for field in field_definitions:
        ws_gid = field["workspace_gid"]
        if ws_gid not in fields_by_workspace:
            fields_by_workspace[ws_gid] = []
        fields_by_workspace[ws_gid].append(field)
    
    for portfolio in portfolios:
        if not probability_check(0.40):
            continue
        
        ws_gid = portfolio["workspace_gid"]
        ws_fields = fields_by_workspace.get(ws_gid, [])
        
        if not ws_fields:
            continue
        
        num_fields = random.randint(1, min(3, len(ws_fields)))
        selected_fields = random.sample(ws_fields, num_fields)
        
        for field in selected_fields:
            setting = {
                "workspace_gid": ws_gid,
                "portfolio_gid": portfolio["gid"],
                "custom_field_gid": field["gid"],
            }
            settings.append(setting)
    
    return settings


def generate_custom_field_values(
    tasks: List[Dict[str, Any]],
    project_field_settings: List[Dict[str, Any]],
    task_project_memberships: List[Dict[str, Any]],
    field_definitions: List[Dict[str, Any]],
    field_options: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Generate custom field values for tasks.
    
    Relational Consistency:
    - Values only for fields attached to task's project
    - Value type matches field definition type
    """
    values = []
    
    # Build lookups
    field_by_gid = {f["gid"]: f for f in field_definitions}
    
    options_by_field = {}
    for opt in field_options:
        if opt["field_gid"] not in options_by_field:
            options_by_field[opt["field_gid"]] = []
        options_by_field[opt["field_gid"]].append(opt)
    
    # Fields per project
    fields_per_project = {}
    for setting in project_field_settings:
        proj_gid = setting["project_gid"]
        if proj_gid not in fields_per_project:
            fields_per_project[proj_gid] = []
        fields_per_project[proj_gid].append(setting["custom_field_gid"])
    
    # Task to project mapping
    task_to_project = {}
    for membership in task_project_memberships:
        task_to_project[membership["task_gid"]] = membership["project_gid"]
    
    for task in tasks:
        project_gid = task_to_project.get(task["gid"])
        if not project_gid:
            continue
        
        project_fields = fields_per_project.get(project_gid, [])
        if not project_fields:
            continue
        
        # Generate values for some fields
        for field_gid in project_fields:
            if not probability_check(0.70):  # 70% fill rate
                continue
            
            field = field_by_gid.get(field_gid)
            if not field:
                continue
            
            value = {
                "workspace_gid": task["workspace_gid"],
                "task_gid": task["gid"],
                "field_gid": field_gid,
                "text_value": None,
                "number_value": None,
                "enum_option_gid": None,
            }
            
            # Set value based on field type
            if field["resource_subtype"] == "text":
                value["text_value"] = random.choice([
                    "See documentation",
                    "Needs review",
                    "In progress",
                    "Waiting for input",
                    "",
                ])
            elif field["resource_subtype"] == "number":
                if "Points" in field["name"]:
                    value["number_value"] = random.choice([1, 2, 3, 5, 8, 13])
                elif "Hours" in field["name"]:
                    value["number_value"] = round(random.uniform(0.5, 40), 1)
                else:
                    value["number_value"] = random.randint(1, 100)
            elif field["resource_subtype"] == "enum":
                field_opts = options_by_field.get(field_gid, [])
                if field_opts:
                    value["enum_option_gid"] = random.choice(field_opts)["gid"]
            
            values.append(value)
    
    return values


def generate_portfolio_custom_field_values(
    portfolios: List[Dict[str, Any]],
    portfolio_field_settings: List[Dict[str, Any]],
    field_definitions: List[Dict[str, Any]],
    field_options: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Generate custom field values for portfolios.
    """
    values = []
    
    field_by_gid = {f["gid"]: f for f in field_definitions}
    
    options_by_field = {}
    for opt in field_options:
        if opt["field_gid"] not in options_by_field:
            options_by_field[opt["field_gid"]] = []
        options_by_field[opt["field_gid"]].append(opt)
    
    fields_per_portfolio = {}
    for setting in portfolio_field_settings:
        port_gid = setting["portfolio_gid"]
        if port_gid not in fields_per_portfolio:
            fields_per_portfolio[port_gid] = []
        fields_per_portfolio[port_gid].append(setting["custom_field_gid"])
    
    for portfolio in portfolios:
        portfolio_fields = fields_per_portfolio.get(portfolio["gid"], [])
        
        for field_gid in portfolio_fields:
            if not probability_check(0.60):
                continue
            
            field = field_by_gid.get(field_gid)
            if not field:
                continue
            
            value = {
                "workspace_gid": portfolio["workspace_gid"],
                "portfolio_gid": portfolio["gid"],
                "field_gid": field_gid,
                "text_value": None,
                "number_value": None,
                "enum_option_gid": None,
            }
            
            if field["resource_subtype"] == "text":
                value["text_value"] = "Portfolio notes"
            elif field["resource_subtype"] == "number":
                value["number_value"] = random.randint(1, 100)
            elif field["resource_subtype"] == "enum":
                field_opts = options_by_field.get(field_gid, [])
                if field_opts:
                    value["enum_option_gid"] = random.choice(field_opts)["gid"]
            
            values.append(value)
    
    return values


if __name__ == "__main__":
    test_workspaces = [{"gid": "ws1"}]
    defs, opts = generate_custom_field_definitions(test_workspaces)
    print(f"Generated {len(defs)} field definitions and {len(opts)} options")
