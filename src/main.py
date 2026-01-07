"""
Asana Simulation Data Generator

Generates synthetic data for an Asana simulation database.
Usage: python src/main.py
Output: output/asana_simulation.sqlite
"""

import os
import sys
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.config import SEED, VOLUMES
from generators.workspaces import generate_workspaces
from generators.users import generate_users
from generators.teams import generate_teams, generate_team_memberships
from generators.portfolios import generate_portfolios
from generators.goals import generate_goals
from generators.projects import (
    generate_projects, generate_project_templates,
    generate_sections, generate_project_briefs
)
from generators.tasks import generate_tasks
from generators.stories import generate_stories
from generators.tags import generate_tags, generate_task_tags
from generators.dependencies import generate_task_dependencies, generate_task_followers
from generators.custom_fields import (
    generate_custom_field_definitions,
    generate_project_custom_field_settings,
    generate_portfolio_custom_field_settings,
    generate_custom_field_values,
    generate_portfolio_custom_field_values,
)
from generators.attachments import generate_attachments
from generators.likes import generate_likes
from generators.status_updates import generate_status_updates
from generators.portfolio_items import generate_portfolio_items
from generators.provenance import create_provenance_records, STRATEGY_DESCRIPTIONS


def create_database(db_path: str, schema_path: str) -> sqlite3.Connection:
    """Create a new SQLite database from schema.sql."""
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = OFF")  # Disable during bulk insert for performance
    
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    
    conn.executescript(schema_sql)
    return conn


def insert_records(conn: sqlite3.Connection, table_name: str, records: list):
    """Insert records into a table, silently skipping duplicates."""
    if not records:
        return
    
    columns = records[0].keys()
    placeholders = ', '.join(['?' for _ in columns])
    column_names = ', '.join(columns)
    sql = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"
    
    for record in records:
        values = [record[col] for col in columns]
        try:
            conn.execute(sql, values)
        except sqlite3.IntegrityError:
            pass  # Skip duplicates
        except Exception as e:
            print(f"  Warning: Failed to insert into {table_name}: {e}")
    
    conn.commit()


def run_validation(conn: sqlite3.Connection) -> dict:
    """Count rows in each table for validation."""
    results = {}
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """)
    tables = [row[0] for row in cursor.fetchall()]
    
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        results[table] = cursor.fetchone()[0]
    
    return results


def print_summary(counts: dict, duration: float):
    print("\n" + "=" * 60)
    print("GENERATION COMPLETE")
    print("=" * 60)
    print(f"\nDuration: {duration:.2f} seconds")
    print(f"\nRow counts by table:")
    print("-" * 40)
    
    total = 0
    for table, count in sorted(counts.items()):
        if count > 0:
            print(f"  {table:35} {count:>6}")
            total += count
    
    print("-" * 40)
    print(f"  {'TOTAL':35} {total:>6}")


def main():
    start_time = datetime.now()
    batch_id = str(uuid.uuid4())[:8]
    
    print("=" * 60)
    print("ASANA SIMULATION DATA GENERATOR")
    print("=" * 60)
    print(f"\nBatch ID: {batch_id}")
    print(f"Seed: {SEED}")
    print(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    base_dir = Path(__file__).parent.parent
    schema_path = base_dir / "schema.sql"
    output_dir = base_dir / "output"
    db_path = output_dir / "asana_simulation.sqlite"
    
    output_dir.mkdir(exist_ok=True)
    
    print(f"\nOutput: {db_path}")
    print("\n" + "-" * 60)
    
    print("\n1. Creating database from schema.sql...")
    conn = create_database(str(db_path), str(schema_path))
    
    data_counts = {}
    
    # Phase 1: Core Entities
    print("\n2. Generating core entities...")
    
    print("   - Workspaces")
    workspaces = generate_workspaces()
    insert_records(conn, "workspaces", workspaces)
    data_counts["workspaces"] = {"count": len(workspaces), "strategy": STRATEGY_DESCRIPTIONS["workspaces"]}
    
    print("   - Users")
    users, workspace_memberships = generate_users(workspaces)
    insert_records(conn, "users", users)
    insert_records(conn, "workspace_memberships", workspace_memberships)
    data_counts["users"] = {"count": len(users), "strategy": STRATEGY_DESCRIPTIONS["users"]}
    data_counts["workspace_memberships"] = {"count": len(workspace_memberships), "strategy": STRATEGY_DESCRIPTIONS["workspace_memberships"]}
    
    print("   - Teams")
    teams = generate_teams(workspaces)
    insert_records(conn, "teams", teams)
    data_counts["teams"] = {"count": len(teams), "strategy": STRATEGY_DESCRIPTIONS["teams"]}
    
    print("   - Team memberships")
    team_memberships = generate_team_memberships(teams, users)
    insert_records(conn, "team_memberships", team_memberships)
    data_counts["team_memberships"] = {"count": len(team_memberships), "strategy": STRATEGY_DESCRIPTIONS["team_memberships"]}
    
    # Phase 2: Strategic Entities
    print("\n3. Generating strategic entities...")
    
    print("   - Portfolios")
    portfolios = generate_portfolios(workspaces, users)
    insert_records(conn, "portfolios", portfolios)
    data_counts["portfolios"] = {"count": len(portfolios), "strategy": STRATEGY_DESCRIPTIONS["portfolios"]}
    
    print("   - Goals")
    goals = generate_goals(workspaces, users)
    insert_records(conn, "goals", goals)
    data_counts["goals"] = {"count": len(goals), "strategy": STRATEGY_DESCRIPTIONS["goals"]}
    
    # Phase 3: Project Entities
    print("\n4. Generating project entities...")
    
    print("   - Projects")
    projects = generate_projects(workspaces, teams, team_memberships, users)
    insert_records(conn, "projects", projects)
    data_counts["projects"] = {"count": len(projects), "strategy": STRATEGY_DESCRIPTIONS["projects"]}
    
    print("   - Project templates")
    project_templates = generate_project_templates(teams)
    insert_records(conn, "project_templates", project_templates)
    data_counts["project_templates"] = {"count": len(project_templates), "strategy": STRATEGY_DESCRIPTIONS["project_templates"]}
    
    print("   - Sections")
    sections = generate_sections(projects)
    insert_records(conn, "sections", sections)
    data_counts["sections"] = {"count": len(sections), "strategy": STRATEGY_DESCRIPTIONS["sections"]}
    
    print("   - Project briefs")
    project_briefs = generate_project_briefs(projects, teams, users)
    insert_records(conn, "project_briefs", project_briefs)
    data_counts["project_briefs"] = {"count": len(project_briefs), "strategy": STRATEGY_DESCRIPTIONS["project_briefs"]}
    
    # Phase 4: Task Entities
    print("\n5. Generating tasks...")
    
    print("   - Tasks and task-project memberships")
    tasks, task_project_memberships = generate_tasks(
        workspaces, projects, sections, team_memberships, users
    )
    insert_records(conn, "tasks", tasks)
    insert_records(conn, "task_project_memberships", task_project_memberships)
    data_counts["tasks"] = {"count": len(tasks), "strategy": STRATEGY_DESCRIPTIONS["tasks"]}
    data_counts["task_project_memberships"] = {"count": len(task_project_memberships), "strategy": STRATEGY_DESCRIPTIONS["task_project_memberships"]}
    
    # Phase 5: Task-Related Content
    print("\n6. Generating task-related content...")
    
    print("   - Stories (comments)")
    stories = generate_stories(tasks, users)
    insert_records(conn, "stories", stories)
    data_counts["stories"] = {"count": len(stories), "strategy": STRATEGY_DESCRIPTIONS["stories"]}
    
    print("   - Attachments")
    attachments = generate_attachments(tasks, project_briefs, users)
    insert_records(conn, "attachments", attachments)
    data_counts["attachments"] = {"count": len(attachments), "strategy": STRATEGY_DESCRIPTIONS["attachments"]}
    
    print("   - Tags")
    tags = generate_tags(workspaces)
    insert_records(conn, "tags", tags)
    data_counts["tags"] = {"count": len(tags), "strategy": STRATEGY_DESCRIPTIONS["tags"]}
    
    print("   - Task tags")
    task_tags = generate_task_tags(tasks, tags)
    insert_records(conn, "task_tags", task_tags)
    data_counts["task_tags"] = {"count": len(task_tags), "strategy": STRATEGY_DESCRIPTIONS["task_tags"]}
    
    # Phase 6: Relationships
    print("\n7. Generating relationships...")
    
    print("   - Task dependencies")
    task_dependencies = generate_task_dependencies(tasks)
    insert_records(conn, "task_dependencies", task_dependencies)
    data_counts["task_dependencies"] = {"count": len(task_dependencies), "strategy": STRATEGY_DESCRIPTIONS["task_dependencies"]}
    
    print("   - Task followers")
    task_followers = generate_task_followers(tasks, users)
    insert_records(conn, "task_followers", task_followers)
    data_counts["task_followers"] = {"count": len(task_followers), "strategy": STRATEGY_DESCRIPTIONS["task_followers"]}
    
    print("   - Likes")
    likes = generate_likes(tasks, stories, users)
    print(f"     Generated {len(likes)} likes")
    insert_records(conn, "likes", likes)
    data_counts["likes"] = {"count": len(likes), "strategy": STRATEGY_DESCRIPTIONS["likes"]}
    
    # Phase 7: Custom Fields
    print("\n8. Generating custom fields...")
    
    print("   - Custom field definitions and options")
    field_definitions, field_options = generate_custom_field_definitions(workspaces)
    insert_records(conn, "custom_field_definitions", field_definitions)
    insert_records(conn, "custom_field_options", field_options)
    data_counts["custom_field_definitions"] = {"count": len(field_definitions), "strategy": STRATEGY_DESCRIPTIONS["custom_field_definitions"]}
    data_counts["custom_field_options"] = {"count": len(field_options), "strategy": STRATEGY_DESCRIPTIONS["custom_field_options"]}
    
    print("   - Project custom field settings")
    project_field_settings = generate_project_custom_field_settings(projects, field_definitions)
    insert_records(conn, "project_custom_field_settings", project_field_settings)
    data_counts["project_custom_field_settings"] = {"count": len(project_field_settings), "strategy": STRATEGY_DESCRIPTIONS["project_custom_field_settings"]}
    
    print("   - Portfolio custom field settings")
    portfolio_field_settings = generate_portfolio_custom_field_settings(portfolios, field_definitions)
    insert_records(conn, "portfolio_custom_field_settings", portfolio_field_settings)
    data_counts["portfolio_custom_field_settings"] = {"count": len(portfolio_field_settings), "strategy": STRATEGY_DESCRIPTIONS["portfolio_custom_field_settings"]}
    
    print("   - Custom field values")
    field_values = generate_custom_field_values(
        tasks, project_field_settings, task_project_memberships,
        field_definitions, field_options
    )
    insert_records(conn, "custom_field_values", field_values)
    data_counts["custom_field_values"] = {"count": len(field_values), "strategy": STRATEGY_DESCRIPTIONS["custom_field_values"]}
    
    print("   - Portfolio custom field values")
    portfolio_field_values = generate_portfolio_custom_field_values(
        portfolios, portfolio_field_settings, field_definitions, field_options
    )
    insert_records(conn, "portfolio_custom_field_values", portfolio_field_values)
    data_counts["portfolio_custom_field_values"] = {"count": len(portfolio_field_values), "strategy": STRATEGY_DESCRIPTIONS["portfolio_custom_field_values"]}
    
    # Phase 8: Status Updates and Portfolio Items
    print("\n9. Generating status updates...")
    
    print("   - Status updates")
    status_updates = generate_status_updates(projects, portfolios, goals, users)
    insert_records(conn, "status_updates", status_updates)
    data_counts["status_updates"] = {"count": len(status_updates), "strategy": STRATEGY_DESCRIPTIONS["status_updates"]}
    
    print("   - Portfolio items")
    portfolio_items = generate_portfolio_items(portfolios, projects)
    insert_records(conn, "portfolio_items", portfolio_items)
    data_counts["portfolio_items"] = {"count": len(portfolio_items), "strategy": STRATEGY_DESCRIPTIONS["portfolio_items"]}
    
    # Phase 9: Provenance Records
    print("\n10. Recording provenance...")
    provenance_records = create_provenance_records(data_counts, batch_id)
    insert_records(conn, "_meta_provenance", provenance_records)
    
    # Finalize
    print("\n11. Finalizing database...")
    conn.execute("PRAGMA foreign_keys = ON")
    final_counts = run_validation(conn)
    conn.close()
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    print_summary(final_counts, duration)
    
    print(f"\n[OK] Database saved to: {db_path}")
    print("\nGeneration complete!")
    
    return str(db_path)


if __name__ == "__main__":
    main()
