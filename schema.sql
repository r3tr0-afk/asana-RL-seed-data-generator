PRAGMA foreign_keys = ON;

CREATE TABLE workspaces (
    gid TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    domain TEXT NOT NULL UNIQUE, 
    is_organization BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE users (    
    gid TEXT PRIMARY KEY,
    workspace_gid TEXT NOT NULL REFERENCES workspaces(gid),
    email TEXT NOT NULL UNIQUE, 
    name TEXT NOT NULL,
    photo_url TEXT,
    status TEXT CHECK(status IN ('active', 'away', 'dnd', 'deactivated')) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE (gid, workspace_gid) 
);

CREATE TABLE workspace_memberships (
    workspace_gid TEXT NOT NULL REFERENCES workspaces(gid),
    user_gid TEXT NOT NULL REFERENCES users(gid),
    is_guest BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (workspace_gid, user_gid)
);





CREATE TABLE teams (
    gid TEXT PRIMARY KEY,
    workspace_gid TEXT NOT NULL REFERENCES workspaces(gid),
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(workspace_gid, name), 
    UNIQUE(gid, workspace_gid) 
);

CREATE TABLE team_memberships (
    team_gid TEXT NOT NULL,
    user_gid TEXT NOT NULL,
    workspace_gid TEXT NOT NULL, 
    role TEXT CHECK(role IN ('admin', 'member', 'commenter')) DEFAULT 'member',
    is_guest BOOLEAN DEFAULT 0,
    
    PRIMARY KEY (team_gid, user_gid),
    
    FOREIGN KEY (team_gid, workspace_gid) REFERENCES teams(gid, workspace_gid) ON DELETE CASCADE,
    FOREIGN KEY (user_gid, workspace_gid) REFERENCES users(gid, workspace_gid) ON DELETE CASCADE
);

CREATE TABLE portfolios (
    gid TEXT PRIMARY KEY,
    workspace_gid TEXT NOT NULL REFERENCES workspaces(gid),
    owner_gid TEXT,
    name TEXT NOT NULL,
    color TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(gid, workspace_gid), 
    FOREIGN KEY (owner_gid, workspace_gid) REFERENCES users(gid, workspace_gid) ON DELETE SET NULL
);

CREATE TABLE portfolio_items (
    portfolio_gid TEXT NOT NULL,
    workspace_gid TEXT NOT NULL, 
    
    linked_project_gid TEXT,
    linked_portfolio_gid TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    
    CHECK (
        (linked_project_gid IS NOT NULL AND linked_portfolio_gid IS NULL) OR 
        (linked_project_gid IS NULL AND linked_portfolio_gid IS NOT NULL)
    ),
    
    CHECK (portfolio_gid != linked_portfolio_gid),

    FOREIGN KEY (portfolio_gid, workspace_gid) REFERENCES portfolios(gid, workspace_gid) ON DELETE CASCADE,
    FOREIGN KEY (linked_project_gid, workspace_gid) REFERENCES projects(gid, workspace_gid) ON DELETE CASCADE,
    FOREIGN KEY (linked_portfolio_gid, workspace_gid) REFERENCES portfolios(gid, workspace_gid) ON DELETE CASCADE,
    
    PRIMARY KEY (portfolio_gid, linked_project_gid, linked_portfolio_gid)
);

CREATE TABLE goals (
    gid TEXT PRIMARY KEY,
    workspace_gid TEXT NOT NULL REFERENCES workspaces(gid),
    owner_gid TEXT,
    name TEXT NOT NULL,
    due_on DATE,
    is_completed BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(gid, workspace_gid),
    
    CHECK (due_on IS NULL OR due_on >= DATE(created_at)),
    FOREIGN KEY (owner_gid, workspace_gid) REFERENCES users(gid, workspace_gid) ON DELETE SET NULL
);





CREATE TABLE projects (
    gid TEXT PRIMARY KEY,
    workspace_gid TEXT NOT NULL REFERENCES workspaces(gid),
    team_gid TEXT, 
    owner_gid TEXT,
    
    name TEXT NOT NULL,
    archetype TEXT, 
    layout TEXT DEFAULT 'list', 
    current_status TEXT CHECK(current_status IN ('on_track', 'at_risk', 'off_track')) DEFAULT 'on_track',
    due_date DATE,
    archived BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE (gid, workspace_gid), 
    
    CHECK (due_date IS NULL OR due_date >= DATE(created_at)),
    FOREIGN KEY (team_gid, workspace_gid) REFERENCES teams(gid, workspace_gid),
    FOREIGN KEY (owner_gid, workspace_gid) REFERENCES users(gid, workspace_gid) ON DELETE SET NULL
);

CREATE TABLE project_templates (
    gid TEXT PRIMARY KEY,
    team_gid TEXT NOT NULL REFERENCES teams(gid),
    name TEXT NOT NULL,
    structure_json TEXT, 
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE project_briefs (
    gid TEXT PRIMARY KEY,
    workspace_gid TEXT NOT NULL, 
    project_gid TEXT NOT NULL,
    html_text TEXT NOT NULL,
    title TEXT DEFAULT 'Overview',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(gid, workspace_gid),
    UNIQUE(project_gid),
    
    FOREIGN KEY (project_gid, workspace_gid) REFERENCES projects(gid, workspace_gid) ON DELETE CASCADE
);

CREATE TABLE status_updates (
    gid TEXT PRIMARY KEY,
    workspace_gid TEXT NOT NULL REFERENCES workspaces(gid), 
    author_gid TEXT,
    status_type TEXT CHECK(status_type IN ('on_track', 'at_risk', 'off_track')),
    text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    parent_project_gid TEXT,
    parent_portfolio_gid TEXT,
    parent_goal_gid TEXT,
    
    CHECK (
        (parent_project_gid IS NOT NULL AND parent_portfolio_gid IS NULL AND parent_goal_gid IS NULL) OR
        (parent_project_gid IS NULL AND parent_portfolio_gid IS NOT NULL AND parent_goal_gid IS NULL) OR
        (parent_project_gid IS NULL AND parent_portfolio_gid IS NULL AND parent_goal_gid IS NOT NULL)
    ),
    
    FOREIGN KEY (parent_project_gid, workspace_gid) REFERENCES projects(gid, workspace_gid) ON DELETE CASCADE,
    FOREIGN KEY (parent_portfolio_gid, workspace_gid) REFERENCES portfolios(gid, workspace_gid) ON DELETE CASCADE,
    FOREIGN KEY (parent_goal_gid, workspace_gid) REFERENCES goals(gid, workspace_gid) ON DELETE CASCADE,
    
    FOREIGN KEY (author_gid, workspace_gid) REFERENCES users(gid, workspace_gid) ON DELETE SET NULL
);

CREATE TABLE sections (
    gid TEXT PRIMARY KEY,
    workspace_gid TEXT NOT NULL, 
    project_gid TEXT NOT NULL,
    name TEXT NOT NULL,
    order_index INTEGER NOT NULL,
    
    UNIQUE (gid, project_gid), 
    UNIQUE (gid, workspace_gid), 
    
    FOREIGN KEY (project_gid, workspace_gid) REFERENCES projects(gid, workspace_gid) ON DELETE CASCADE
);





CREATE TABLE tasks (
    gid TEXT PRIMARY KEY,
    workspace_gid TEXT NOT NULL REFERENCES workspaces(gid),
    assignee_gid TEXT, 
    parent_task_gid TEXT,
    
    name TEXT NOT NULL,
    description TEXT, 
    created_at TIMESTAMP NOT NULL,
    start_on DATE,
    due_on DATE,
    completed_at TIMESTAMP,
    completed BOOLEAN DEFAULT 0,
    is_milestone BOOLEAN DEFAULT 0,
    
    UNIQUE(gid, workspace_gid), 

    FOREIGN KEY (assignee_gid, workspace_gid) REFERENCES users(gid, workspace_gid) ON DELETE SET NULL,
    
    
    FOREIGN KEY (parent_task_gid, workspace_gid) REFERENCES tasks(gid, workspace_gid) ON DELETE CASCADE,

    CHECK (completed_at IS NULL OR completed_at >= created_at),
    CHECK ((completed = 1 AND completed_at IS NOT NULL) OR (completed = 0 AND completed_at IS NULL)),
    CHECK (parent_task_gid != gid),
    CHECK (start_on IS NULL OR due_on IS NULL OR start_on <= due_on),
    CHECK (is_milestone = 0 OR (start_on IS NULL OR start_on = due_on))
);


CREATE TRIGGER validate_task_hierarchy_recursion
BEFORE UPDATE OF parent_task_gid ON tasks
FOR EACH ROW
WHEN NEW.parent_task_gid IS NOT NULL
BEGIN
    WITH RECURSIVE ancestry(id) AS (
        SELECT NEW.parent_task_gid
        UNION ALL
        SELECT t.parent_task_gid
        FROM tasks t
        JOIN ancestry a ON t.gid = a.id
        WHERE t.parent_task_gid IS NOT NULL
    )
    SELECT RAISE(ABORT, 'Graph Cycle Detected: Task cannot be its own ancestor.')
    FROM ancestry
    WHERE id = NEW.gid;
END;

CREATE TRIGGER validate_task_parent_time_insert
BEFORE INSERT ON tasks
FOR EACH ROW
WHEN NEW.parent_task_gid IS NOT NULL
BEGIN
    SELECT RAISE(ABORT, 'Time Paradox: Child task cannot be created before Parent task.')
    FROM tasks AS parent
    WHERE parent.gid = NEW.parent_task_gid
    AND parent.created_at > NEW.created_at;
END;

CREATE TRIGGER validate_task_parent_time_update
BEFORE UPDATE OF parent_task_gid, created_at ON tasks
FOR EACH ROW
WHEN NEW.parent_task_gid IS NOT NULL
BEGIN
    SELECT RAISE(ABORT, 'Time Paradox: Child task cannot be older than Parent task.')
    FROM tasks AS parent
    WHERE parent.gid = NEW.parent_task_gid
    AND parent.created_at > NEW.created_at;
END;

CREATE TABLE task_project_memberships (
    workspace_gid TEXT NOT NULL, 
    task_gid TEXT NOT NULL,
    project_gid TEXT NOT NULL,
    section_gid TEXT, 
    
    PRIMARY KEY (task_gid, project_gid),
    
    FOREIGN KEY (task_gid, workspace_gid) REFERENCES tasks(gid, workspace_gid) ON DELETE CASCADE,
    FOREIGN KEY (project_gid, workspace_gid) REFERENCES projects(gid, workspace_gid) ON DELETE CASCADE,
    FOREIGN KEY (section_gid, project_gid) REFERENCES sections(gid, project_gid)
);

CREATE TABLE task_dependencies (
    workspace_gid TEXT NOT NULL REFERENCES workspaces(gid), 
    predecessor_gid TEXT NOT NULL,
    successor_gid TEXT NOT NULL,
    type TEXT CHECK(type IN ('finish_to_start', 'start_to_start', 'finish_to_finish')) DEFAULT 'finish_to_start',
    
    PRIMARY KEY (predecessor_gid, successor_gid),
    
    FOREIGN KEY (predecessor_gid, workspace_gid) REFERENCES tasks(gid, workspace_gid) ON DELETE CASCADE,
    FOREIGN KEY (successor_gid, workspace_gid) REFERENCES tasks(gid, workspace_gid) ON DELETE CASCADE,
    CHECK (predecessor_gid != successor_gid)
);




CREATE TRIGGER validate_dependency_logic_insert
BEFORE INSERT ON task_dependencies
BEGIN
    SELECT RAISE(ABORT, 'Time Paradox: Dependency logic violated.')
    FROM tasks AS pred, tasks AS succ
    WHERE pred.gid = NEW.predecessor_gid 
    AND succ.gid = NEW.successor_gid
    AND (
        (NEW.type = 'finish_to_start' AND pred.due_on > succ.start_on AND pred.due_on IS NOT NULL AND succ.start_on IS NOT NULL) OR
        (NEW.type = 'start_to_start' AND pred.start_on > succ.start_on AND pred.start_on IS NOT NULL AND succ.start_on IS NOT NULL) OR
        (NEW.type = 'finish_to_finish' AND pred.due_on > succ.due_on AND pred.due_on IS NOT NULL AND succ.due_on IS NOT NULL)
    );
END;

CREATE TRIGGER validate_dependency_logic_update_tasks
BEFORE UPDATE OF start_on, due_on ON tasks
BEGIN
    
    SELECT RAISE(ABORT, 'Time Paradox: Moving this task violates a dependency (as Predecessor).')
    FROM task_dependencies AS dep
    JOIN tasks AS succ ON dep.successor_gid = succ.gid
    WHERE dep.predecessor_gid = NEW.gid
    AND (
        (dep.type = 'finish_to_start' AND NEW.due_on > succ.start_on AND NEW.due_on IS NOT NULL AND succ.start_on IS NOT NULL) OR
        (dep.type = 'start_to_start' AND NEW.start_on > succ.start_on AND NEW.start_on IS NOT NULL AND succ.start_on IS NOT NULL) OR
        (dep.type = 'finish_to_finish' AND NEW.due_on > succ.due_on AND NEW.due_on IS NOT NULL AND succ.due_on IS NOT NULL)
    );

    
    SELECT RAISE(ABORT, 'Time Paradox: Moving this task violates a dependency (as Successor).')
    FROM task_dependencies AS dep
    JOIN tasks AS pred ON dep.predecessor_gid = pred.gid
    WHERE dep.successor_gid = NEW.gid
    AND (
        (dep.type = 'finish_to_start' AND pred.due_on > NEW.start_on AND pred.due_on IS NOT NULL AND NEW.start_on IS NOT NULL) OR
        (dep.type = 'start_to_start' AND pred.start_on > NEW.start_on AND pred.start_on IS NOT NULL AND NEW.start_on IS NOT NULL) OR
        (dep.type = 'finish_to_finish' AND pred.due_on > NEW.due_on AND pred.due_on IS NOT NULL AND NEW.due_on IS NOT NULL)
    );
END;

CREATE TABLE task_followers (
    workspace_gid TEXT NOT NULL REFERENCES workspaces(gid), 
    task_gid TEXT NOT NULL,
    user_gid TEXT NOT NULL,
    
    PRIMARY KEY (task_gid, user_gid),
    
    FOREIGN KEY (task_gid, workspace_gid) REFERENCES tasks(gid, workspace_gid) ON DELETE CASCADE,
    FOREIGN KEY (user_gid, workspace_gid) REFERENCES users(gid, workspace_gid) ON DELETE CASCADE
);





CREATE TABLE stories (
    gid TEXT PRIMARY KEY,
    workspace_gid TEXT NOT NULL REFERENCES workspaces(gid), 
    task_gid TEXT NOT NULL,
    created_by_gid TEXT,
    text TEXT NOT NULL,
    type TEXT CHECK(type IN ('comment', 'system')) DEFAULT 'comment',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(gid, workspace_gid),
    
    FOREIGN KEY (task_gid, workspace_gid) REFERENCES tasks(gid, workspace_gid) ON DELETE CASCADE,
    FOREIGN KEY (created_by_gid, workspace_gid) REFERENCES users(gid, workspace_gid)
);

CREATE TABLE attachments (
    gid TEXT PRIMARY KEY,
    workspace_gid TEXT NOT NULL REFERENCES workspaces(gid), 
    
    parent_task_gid TEXT,
    parent_brief_gid TEXT,
    
    name TEXT NOT NULL,
    resource_url TEXT, 
    resource_type TEXT CHECK(resource_type IN ('image', 'video', 'pdf', 'spreadsheet')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_gid TEXT,
    
    CHECK (
        (parent_task_gid IS NOT NULL AND parent_brief_gid IS NULL) OR
        (parent_task_gid IS NULL AND parent_brief_gid IS NOT NULL)
    ),
    
    FOREIGN KEY (parent_task_gid, workspace_gid) REFERENCES tasks(gid, workspace_gid) ON DELETE CASCADE,
    FOREIGN KEY (parent_brief_gid, workspace_gid) REFERENCES project_briefs(gid, workspace_gid) ON DELETE CASCADE,
    FOREIGN KEY (created_by_gid, workspace_gid) REFERENCES users(gid, workspace_gid)
);

CREATE TABLE tags (
    gid TEXT PRIMARY KEY,
    workspace_gid TEXT NOT NULL REFERENCES workspaces(gid),
    name TEXT NOT NULL,
    color TEXT,
    UNIQUE(workspace_gid, name),
    UNIQUE(gid, workspace_gid)
);

CREATE TABLE task_tags (
    workspace_gid TEXT NOT NULL, 
    task_gid TEXT NOT NULL,
    tag_gid TEXT NOT NULL,
    
    PRIMARY KEY (task_gid, tag_gid),
    
    FOREIGN KEY (task_gid, workspace_gid) REFERENCES tasks(gid, workspace_gid) ON DELETE CASCADE,
    FOREIGN KEY (tag_gid, workspace_gid) REFERENCES tags(gid, workspace_gid) ON DELETE CASCADE
);

CREATE TABLE likes (
    gid TEXT PRIMARY KEY,
    workspace_gid TEXT NOT NULL REFERENCES workspaces(gid),
    user_gid TEXT NOT NULL,
    
    task_gid TEXT,
    story_gid TEXT,
    
    CHECK (
        (task_gid IS NOT NULL AND story_gid IS NULL) OR 
        (task_gid IS NULL AND story_gid IS NOT NULL)
    ),
    
    UNIQUE(user_gid, task_gid),
    UNIQUE(user_gid, story_gid),
    
    FOREIGN KEY (user_gid, workspace_gid) REFERENCES users(gid, workspace_gid) ON DELETE CASCADE,
    FOREIGN KEY (task_gid, workspace_gid) REFERENCES tasks(gid, workspace_gid) ON DELETE CASCADE,
    FOREIGN KEY (story_gid, workspace_gid) REFERENCES stories(gid, workspace_gid) ON DELETE CASCADE
);





CREATE TABLE custom_field_definitions (
    gid TEXT PRIMARY KEY,
    workspace_gid TEXT NOT NULL REFERENCES workspaces(gid),
    name TEXT NOT NULL,
    resource_subtype TEXT CHECK(resource_subtype IN ('text', 'enum', 'number', 'multi_enum')),
    
    UNIQUE(workspace_gid, name),
    UNIQUE(gid, workspace_gid) 
);

CREATE TABLE custom_field_options (
    gid TEXT PRIMARY KEY,
    field_gid TEXT NOT NULL,
    workspace_gid TEXT NOT NULL,
    name TEXT NOT NULL,
    color TEXT,
    
    
    UNIQUE(field_gid, gid), 
    
    FOREIGN KEY (field_gid, workspace_gid) REFERENCES custom_field_definitions(gid, workspace_gid) ON DELETE CASCADE
);

CREATE TABLE project_custom_field_settings (
    workspace_gid TEXT NOT NULL, 
    project_gid TEXT NOT NULL,
    custom_field_gid TEXT NOT NULL,
    is_important BOOLEAN DEFAULT 0, 
    
    PRIMARY KEY (project_gid, custom_field_gid),
    
    FOREIGN KEY (project_gid, workspace_gid) REFERENCES projects(gid, workspace_gid) ON DELETE CASCADE,
    FOREIGN KEY (custom_field_gid, workspace_gid) REFERENCES custom_field_definitions(gid, workspace_gid) ON DELETE CASCADE
);

CREATE TABLE portfolio_custom_field_settings (
    workspace_gid TEXT NOT NULL, 
    portfolio_gid TEXT NOT NULL,
    custom_field_gid TEXT NOT NULL,
    
    PRIMARY KEY (portfolio_gid, custom_field_gid),
    
    FOREIGN KEY (portfolio_gid, workspace_gid) REFERENCES portfolios(gid, workspace_gid) ON DELETE CASCADE,
    FOREIGN KEY (custom_field_gid, workspace_gid) REFERENCES custom_field_definitions(gid, workspace_gid) ON DELETE CASCADE
);

CREATE TABLE custom_field_values (
    workspace_gid TEXT NOT NULL, 
    task_gid TEXT NOT NULL,
    field_gid TEXT NOT NULL,
    text_value TEXT,
    number_value REAL,
    enum_option_gid TEXT, 
    
    PRIMARY KEY (task_gid, field_gid),
    
    FOREIGN KEY (task_gid, workspace_gid) REFERENCES tasks(gid, workspace_gid) ON DELETE CASCADE,
    FOREIGN KEY (field_gid, workspace_gid) REFERENCES custom_field_definitions(gid, workspace_gid) ON DELETE CASCADE,
    
    
    FOREIGN KEY (field_gid, enum_option_gid) REFERENCES custom_field_options(field_gid, gid),
    
    CHECK (
        (CASE WHEN text_value IS NOT NULL THEN 1 ELSE 0 END) +
        (CASE WHEN number_value IS NOT NULL THEN 1 ELSE 0 END) +
        (CASE WHEN enum_option_gid IS NOT NULL THEN 1 ELSE 0 END) <= 1
    )
);

CREATE TRIGGER validate_custom_field_type_integrity
BEFORE INSERT ON custom_field_values
BEGIN
    SELECT RAISE(ABORT, 'Type Mismatch: Value does not match Field Definition type.')
    FROM custom_field_definitions AS def
    WHERE def.gid = NEW.field_gid
    AND (
        (def.resource_subtype = 'text' AND NEW.text_value IS NULL) OR
        (def.resource_subtype = 'number' AND NEW.number_value IS NULL) OR
        (def.resource_subtype = 'enum' AND NEW.enum_option_gid IS NULL)
    );
END;

CREATE TABLE portfolio_custom_field_values (
    workspace_gid TEXT NOT NULL, 
    portfolio_gid TEXT NOT NULL,
    field_gid TEXT NOT NULL,
    text_value TEXT,
    number_value REAL,
    enum_option_gid TEXT, 
    
    PRIMARY KEY (portfolio_gid, field_gid),
    
    FOREIGN KEY (portfolio_gid, workspace_gid) REFERENCES portfolios(gid, workspace_gid) ON DELETE CASCADE,
    FOREIGN KEY (field_gid, workspace_gid) REFERENCES custom_field_definitions(gid, workspace_gid) ON DELETE CASCADE,
    
    
    FOREIGN KEY (field_gid, enum_option_gid) REFERENCES custom_field_options(field_gid, gid)
);

CREATE TABLE _meta_provenance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    source_strategy TEXT NOT NULL, 
    row_count INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE INDEX idx_tasks_assignee_completed ON tasks(assignee_gid, completed);
CREATE INDEX idx_tasks_created_at ON tasks(created_at);
CREATE INDEX idx_task_proj_mem_lookup ON task_project_memberships(project_gid, section_gid);
CREATE INDEX idx_deps_lookup ON task_dependencies(predecessor_gid);
CREATE INDEX idx_stories_task ON stories(task_gid);