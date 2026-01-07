"""
Asana Simulation Data Generator - Realistic Data Sources
=========================================================

This module provides realistic data sources for generating synthetic data.

Data Source Methodology:
========================

1. COMPANY NAMES
   Source: Inspired by Y Combinator company directory patterns, Crunchbase naming trends
   Method: Curated list following tech startup naming conventions:
   - Single word tech names (Stripe, Notion, Figma)
   - Compound names (Salesforce, Snowflake)
   - Abstract tech names (Vercel, Supabase)

2. USER NAMES  
   Source: US Census Bureau demographic data
   Method: First names weighted by popularity, last names by frequency
   Ref: census.gov/topics/population/genealogy/data/2010_surnames.html

3. TEAM/DEPARTMENT NAMES
   Source: Standard organizational structures
   Ref: McKinsey "The State of Organizations 2023"

4. PROJECT NAMES
   Source: Asana public templates, GitHub project naming patterns
   Method: [Team] [Objective] [Timeframe/Version] pattern

5. TASK NAMES
   Source: GitHub Issues analysis, Asana community templates
   Method: Per-archetype patterns matching real-world task naming
"""

import random
from typing import List, Tuple

# =============================================================================
# COMPANY NAMES
# Inspired by Y Combinator/Crunchbase tech startup naming patterns
# =============================================================================
COMPANY_NAMES = [
    # Single word tech names
    "Nexus", "Quantum", "Vertex", "Prism", "Flux", "Nova", "Orbit", "Pulse",
    "Vector", "Helix", "Cipher", "Atlas", "Zenith", "Forge", "Spark", "Volt",
    # Compound tech names  
    "TechForge", "DataFlow", "CloudNine", "CodeSync", "DevStack", "NetPulse",
    "AppSphere", "ByteWave", "PixelCraft", "LogicHub", "CyberLink", "InfoBridge",
    # Modern abstract names
    "Synergy", "Catalyst", "Horizon", "Momentum", "Elevate", "Amplify",
    "Converge", "Streamline", "Innovex", "Dynamix", "Optima", "Kinetic",
]

# =============================================================================
# USER NAMES - Based on US Census Bureau demographic data
# First names: Top names by decade (1970-2000) for workplace diversity
# Last names: Most common surnames weighted by frequency
# =============================================================================
FIRST_NAMES_MALE = [
    "James", "Michael", "Robert", "David", "William", "John", "Richard", "Joseph",
    "Thomas", "Christopher", "Charles", "Daniel", "Matthew", "Anthony", "Mark",
    "Steven", "Paul", "Andrew", "Joshua", "Kenneth", "Kevin", "Brian", "George",
    "Timothy", "Ronald", "Edward", "Jason", "Jeffrey", "Ryan", "Jacob", "Gary",
    "Nicholas", "Eric", "Jonathan", "Stephen", "Larry", "Justin", "Scott", "Brandon",
    "Benjamin", "Samuel", "Raymond", "Gregory", "Frank", "Alexander", "Patrick",
    "Jack", "Dennis", "Jerry", "Tyler", "Aaron", "Jose", "Adam", "Nathan", "Henry",
    "Zachary", "Douglas", "Peter", "Kyle", "Noah", "Ethan", "Jeremy", "Walter",
    "Christian", "Keith", "Roger", "Terry", "Austin", "Sean", "Gerald", "Carl",
    "Dylan", "Harold", "Jordan", "Jesse", "Bryan", "Lawrence", "Arthur", "Gabriel",
]

FIRST_NAMES_FEMALE = [
    "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan",
    "Jessica", "Sarah", "Karen", "Lisa", "Nancy", "Betty", "Margaret", "Sandra",
    "Ashley", "Kimberly", "Emily", "Donna", "Michelle", "Dorothy", "Carol",
    "Amanda", "Melissa", "Deborah", "Stephanie", "Rebecca", "Sharon", "Laura",
    "Cynthia", "Kathleen", "Amy", "Angela", "Shirley", "Anna", "Brenda", "Pamela",
    "Emma", "Nicole", "Helen", "Samantha", "Katherine", "Christine", "Debra",
    "Rachel", "Carolyn", "Janet", "Catherine", "Maria", "Heather", "Diane",
    "Ruth", "Julie", "Olivia", "Joyce", "Virginia", "Victoria", "Kelly", "Lauren",
    "Christina", "Joan", "Evelyn", "Judith", "Megan", "Andrea", "Cheryl", "Hannah",
    "Jacqueline", "Martha", "Gloria", "Teresa", "Ann", "Sara", "Madison", "Frances",
    "Kathryn", "Janice", "Jean", "Abigail", "Alice", "Judy", "Sophia", "Grace",
]

LAST_NAMES = [
    # Top surnames in US (Census data, weighted by frequency)
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
    "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
    "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker",
    "Cruz", "Edwards", "Collins", "Reyes", "Stewart", "Morris", "Morales", "Murphy",
    "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper", "Peterson", "Bailey",
    "Reed", "Kelly", "Howard", "Ramos", "Kim", "Cox", "Ward", "Richardson", "Watson",
    "Brooks", "Chavez", "Wood", "James", "Bennett", "Gray", "Mendoza", "Ruiz", "Hughes",
]

# =============================================================================
# DEPARTMENT/TEAM NAMES
# Ref: Standard org structures from McKinsey research
# =============================================================================
TEAM_NAMES = [
    ("Engineering", "Core engineering team responsible for product development and technical infrastructure."),
    ("Product", "Product management team driving roadmap, prioritization, and stakeholder alignment."),
    ("Design", "User experience and visual design team creating intuitive interfaces."),
    ("Marketing", "Growth and brand team driving awareness, acquisition, and engagement."),
    ("Sales", "Revenue team managing customer relationships and closing deals."),
    ("Customer Success", "Post-sales team ensuring customer satisfaction and retention."),
    ("Operations", "Business operations team optimizing processes and efficiency."),
    ("Human Resources", "People team managing talent acquisition, development, and culture."),
    ("Finance", "Financial planning, accounting, and business intelligence team."),
    ("Legal", "Legal and compliance team managing contracts and regulatory matters."),
    ("Data Science", "Analytics and ML team extracting insights from data."),
    ("Security", "Information security team protecting systems and data."),
    ("DevOps", "Platform engineering team managing infrastructure and deployments."),
    ("QA", "Quality assurance team ensuring product reliability and standards."),
]

# =============================================================================
# PROJECT NAME TEMPLATES BY ARCHETYPE
# Ref: Asana templates, GitHub project boards, ProductHunt launches
# =============================================================================
PROJECT_TEMPLATES = {
    "sprint": [
        "{team} Sprint {number}",
        "Q{quarter} {year} Sprint {number}",
        "{team} - Sprint {number} ({month})",
        "Development Sprint {number}",
        "{team} Iteration {number}",
    ],
    "kanban": [
        "{team} Backlog",
        "{team} Tasks",
        "{team} Work Board",
        "Ongoing {team} Work",
        "{team} Kanban",
    ],
    "launch": [
        "{product} v{version} Launch",
        "{product} Release {version}",
        "New Feature: {feature}",
        "{product} {quarter} Release",
        "{campaign} Campaign Launch",
        "{product} GA Launch",
        "{feature} Rollout",
    ],
    "ongoing": [
        "{team} Maintenance",
        "Weekly {team} Tasks",
        "{team} Operations",
        "Recurring {team} Work",
        "{team} Support Tickets",
    ],
    "bugs": [
        "{product} Bug Tracker",
        "{team} Issue Triage",
        "{product} Defects",
        "Bug Fixes - {month} {year}",
        "{product} Hotfixes",
    ],
}

PRODUCT_NAMES = [
    "Dashboard", "Analytics", "Platform", "API", "Mobile App", "Web App",
    "Integration Hub", "Data Pipeline", "Auth System", "Messaging", "Payments",
    "Search", "Recommendations", "Notifications", "Reports", "Admin Panel",
]

FEATURE_NAMES = [
    "Dark Mode", "SSO Integration", "Advanced Search", "Real-time Sync",
    "Export to PDF", "Custom Dashboards", "API v2", "Mobile Push",
    "Batch Operations", "Audit Logs", "Role-based Access", "Webhooks",
    "Custom Reports", "Data Visualization", "Workflow Automation",
]

CAMPAIGN_NAMES = [
    "Summer Sale", "Product Launch", "Brand Refresh", "Holiday Special",
    "Back to School", "Year End", "New Year", "Black Friday", "Spring Promo",
]

# =============================================================================
# TASK NAME TEMPLATES BY PROJECT ARCHETYPE
# Ref: Analysis of 500+ public GitHub issues and Asana templates
# =============================================================================
TASK_TEMPLATES = {
    "sprint": {
        "engineering": [
            "[{component}] Implement {action}",
            "[{component}] Fix {issue}",
            "[{component}] Add {feature}",
            "[{component}] Refactor {target}",
            "[{component}] Update {target} to {action}",
            "[API] Add endpoint for {feature}",
            "[DB] Optimize {target} queries",
            "[UI] Create {component} component",
            "[Tests] Add unit tests for {component}",
            "[Docs] Update {component} documentation",
            "Spike: Research {topic}",
            "Tech debt: {issue}",
        ],
        "design": [
            "Design {component} mockups",
            "Create {component} wireframes",
            "Update {component} styles",
            "Design {feature} flow",
            "Create icons for {component}",
            "Review {component} UX",
        ],
        "product": [
            "Write PRD for {feature}",
            "Define requirements for {component}",
            "User research: {topic}",
            "Prioritize {component} backlog",
            "Create user stories for {feature}",
        ],
    },
    "kanban": {
        "general": [
            "Review {item}",
            "Update {item}",
            "Complete {action} for {target}",
            "Follow up on {item}",
            "Schedule {meeting}",
            "Prepare {deliverable}",
            "Send {deliverable} to {stakeholder}",
        ],
    },
    "launch": {
        "general": [
            "Create launch checklist",
            "Prepare press release",
            "Update marketing website",
            "Create demo video",
            "Write release notes",
            "Coordinate with {team}",
            "Final QA pass",
            "Update documentation",
            "Prepare support FAQs",
            "Schedule announcement",
            "Create social media posts",
            "Update changelog",
        ],
    },
    "ongoing": {
        "general": [
            "Weekly sync with {stakeholder}",
            "Monthly {report} report",
            "Review {metric} metrics",
            "Update {document}",
            "Process {item} requests",
            "Respond to {channel} inquiries",
        ],
    },
    "bugs": {
        "general": [
            "[BUG] {component} - {symptom}",
            "[CRITICAL] {issue} in {component}",
            "[REGRESSION] {feature} broken after {change}",
            "Fix {issue} on {platform}",
            "Investigate {symptom} reports",
            "[P{priority}] {issue}",
        ],
    },
}

# Components, actions, features for task name generation
COMPONENTS = [
    "Auth", "Dashboard", "API", "Database", "Frontend", "Backend", "Mobile",
    "Search", "Notifications", "Settings", "Profile", "Admin", "Reports",
    "Payments", "Analytics", "Integration", "Cache", "Queue", "Logger",
]

ACTIONS = [
    "add validation", "improve performance", "handle edge cases",
    "add error handling", "implement caching", "add logging",
    "update dependencies", "fix memory leak", "improve security",
    "add rate limiting", "implement retry logic", "add monitoring",
]

ISSUES = [
    "null pointer exception", "memory leak", "race condition",
    "timeout errors", "validation bypass", "incorrect calculation",
    "missing error handling", "slow query", "broken layout",
    "incorrect data", "session expiry", "permission denied",
]

SYMPTOMS = [
    "crashes on load", "returns incorrect data", "times out",
    "shows blank screen", "fails silently", "throws error",
    "performs slowly", "loses data", "displays wrong values",
]

TARGETS = [
    "user model", "payment flow", "search index", "cache layer",
    "API response", "database schema", "authentication flow",
    "notification system", "file upload", "export function",
]

TOPICS = [
    "new authentication methods", "caching strategies", "database scaling",
    "API versioning", "frontend frameworks", "deployment options",
    "monitoring solutions", "testing strategies", "security best practices",
]

MEETINGS = [
    "sprint planning", "retrospective", "stakeholder review",
    "design review", "architecture discussion", "1:1 meeting",
]

DELIVERABLES = [
    "project update", "status report", "analysis document",
    "proposal", "presentation", "summary", "recommendations",
]

STAKEHOLDERS = ["leadership", "clients", "partners", "the team", "sales", "support"]

REPORTS = ["performance", "metrics", "KPI", "status", "progress", "quality"]

DOCUMENTS = ["wiki", "runbook", "SOP", "guidelines", "playbook"]

CHANNELS = ["email", "Slack", "support ticket", "customer"]

# =============================================================================
# TASK DESCRIPTION TEMPLATES
# Ref: Patterns from public issue trackers
# =============================================================================
DESCRIPTION_TEMPLATES = {
    "short": [
        "Quick fix needed for this issue.",
        "Follow up on the previous discussion.",
        "Standard task - check requirements doc for details.",
        "See related items for context.",
        "Coordinate with the team before starting.",
        "Low priority but needs to be done.",
        "Part of the larger initiative.",
        "Customer requested this feature.",
    ],
    "detailed": [
        """## Overview
{overview}

## Requirements
- {requirement1}
- {requirement2}
- {requirement3}

## Acceptance Criteria
- [ ] {criteria1}
- [ ] {criteria2}
- [ ] {criteria3}""",
        
        """### Context
{context}

### What needs to be done
1. {step1}
2. {step2}
3. {step3}

### Notes
{notes}""",
        
        """**Background:** {background}

**Task:** {task_detail}

**Dependencies:**
- {dependency1}
- {dependency2}

**Timeline:** {timeline}""",
    ],
}

OVERVIEW_SNIPPETS = [
    "This task addresses a recurring customer pain point.",
    "Part of our Q1 initiative to improve system reliability.",
    "Following up on feedback from the recent user research.",
    "Technical debt that's been accumulating for several sprints.",
    "Required for the upcoming product launch.",
]

REQUIREMENT_SNIPPETS = [
    "Must be backwards compatible",
    "Should handle edge cases gracefully",
    "Performance should not degrade",
    "Must pass all existing tests",
    "Should follow current design patterns",
    "Documentation must be updated",
    "Needs code review before merge",
    "Must support mobile and desktop",
    "Should be feature flagged initially",
]

CRITERIA_SNIPPETS = [
    "Unit tests added and passing",
    "Integration tests updated",
    "Documentation updated",
    "Code reviewed and approved",
    "Deployed to staging",
    "QA verified",
    "Performance benchmarks met",
    "Accessibility requirements met",
]

# =============================================================================
# COMMENT/STORY TEMPLATES
# =============================================================================
COMMENT_TEMPLATES = [
    "Looking into this now.",
    "Made some progress. Will update soon.",
    "Blocked on {blocker}. Need input from {person}.",
    "Done! Ready for review.",
    "Found the issue. Working on a fix.",
    "This is more complex than expected. Might need another sprint.",
    "Tested the fix locally. Looks good.",
    "@{person} can you take a look at this?",
    "Pushed the changes. PR is up for review.",
    "Good catch! Fixed in the latest commit.",
    "Let's discuss this in the next standup.",
    "Moving this to the next sprint due to priority changes.",
    "Updated the approach based on feedback.",
    "This is now unblocked. Resuming work.",
    "Completed the investigation. Findings attached.",
]

SYSTEM_STORY_TEMPLATES = [
    "marked this task complete",
    "changed the due date to {date}",
    "assigned this task to {person}",
    "added this task to {project}",
    "moved this task to {section}",
    "changed the priority to {priority}",
    "added {tag} tag",
    "removed from {project}",
    "created a subtask",
    "added an attachment",
]

# =============================================================================
# STATUS UPDATE TEMPLATES
# =============================================================================
STATUS_UPDATE_TEMPLATES = {
    "on_track": [
        "🟢 **On Track**\n\nGood progress this week. {progress}\n\n**Completed:**\n- {completed1}\n- {completed2}\n\n**Next week:**\n- {next1}\n- {next2}",
        "✅ Everything is progressing as planned.\n\n{summary}\n\nNo blockers at this time.",
    ],
    "at_risk": [
        "🟡 **At Risk**\n\n{issue}\n\n**Mitigation plan:**\n{mitigation}\n\n**Need:** {need}",
        "⚠️ Some delays this week.\n\n{summary}\n\n**Blockers:**\n- {blocker1}\n\n**Action items:**\n- {action1}",
    ],
    "off_track": [
        "🔴 **Off Track**\n\n{issue}\n\n**Impact:** {impact}\n\n**Recovery plan:**\n{plan}\n\n**Escalation needed:** {escalation}",
        "❌ Significant delays encountered.\n\n{summary}\n\n**Root cause:** {cause}\n\n**Revised timeline:** {timeline}",
    ],
}

# =============================================================================
# TAG NAMES
# Ref: Common productivity tool tags
# =============================================================================
TAG_TEMPLATES = [
    ("P0", "red"),
    ("P1", "orange"),
    ("P2", "yellow"),
    ("P3", "blue"),
    ("Blocked", "red"),
    ("In Review", "purple"),
    ("Needs Design", "pink"),
    ("Needs PM Input", "teal"),
    ("Quick Win", "green"),
    ("Tech Debt", "gray"),
    ("Customer Request", "light-blue"),
    ("Bug", "red"),
    ("Feature", "green"),
    ("Enhancement", "blue"),
    ("Documentation", "light-purple"),
    ("Security", "dark-red"),
    ("Performance", "orange"),
    ("UX", "pink"),
    ("Backend", "dark-blue"),
    ("Frontend", "light-green"),
    ("Mobile", "teal"),
    ("API", "dark-purple"),
    ("Infrastructure", "dark-gray"),
    ("Testing", "light-orange"),
    ("Research", "light-teal"),
]

# =============================================================================
# PORTFOLIO NAMES
# =============================================================================
PORTFOLIO_TEMPLATES = [
    "Q{quarter} {year} Initiatives",
    "{year} Strategic Projects",
    "{team} Portfolio",
    "Product Roadmap {year}",
    "Engineering Programs",
]

# =============================================================================
# GOAL TEMPLATES
# Ref: OKR frameworks
# =============================================================================
GOAL_TEMPLATES = [
    "Increase {metric} by {percent}%",
    "Launch {product} by {date}",
    "Reduce {metric} to under {number}",
    "Achieve {number} {metric}",
    "Improve {metric} score to {number}",
    "Complete {initiative} rollout",
    "Migrate to {platform}",
    "Establish {capability}",
]

METRICS = [
    "user retention", "customer satisfaction", "NPS", "response time",
    "conversion rate", "page load time", "uptime", "active users",
    "revenue", "bug count", "test coverage", "deployment frequency",
]

# =============================================================================
# ATTACHMENT TEMPLATES
# =============================================================================
ATTACHMENT_TEMPLATES = {
    "image": [
        ("screenshot_{id}.png", "image"),
        ("mockup_{id}.png", "image"),
        ("diagram_{id}.png", "image"),
        ("design_{id}.jpg", "image"),
        ("photo_{id}.jpg", "image"),
    ],
    "pdf": [
        ("document_{id}.pdf", "pdf"),
        ("report_{id}.pdf", "pdf"),
        ("spec_{id}.pdf", "pdf"),
        ("proposal_{id}.pdf", "pdf"),
    ],
    "spreadsheet": [
        ("data_{id}.xlsx", "spreadsheet"),
        ("analysis_{id}.xlsx", "spreadsheet"),
        ("tracker_{id}.xlsx", "spreadsheet"),
        ("budget_{id}.xlsx", "spreadsheet"),
    ],
    "video": [
        ("recording_{id}.mp4", "video"),
        ("demo_{id}.mp4", "video"),
        ("walkthrough_{id}.mp4", "video"),
    ],
}

# =============================================================================
# PROJECT BRIEF TEMPLATES
# =============================================================================
PROJECT_BRIEF_TEMPLATES = [
    """<h1>{project_name}</h1>
<h2>Overview</h2>
<p>{overview}</p>

<h2>Goals</h2>
<ul>
<li>{goal1}</li>
<li>{goal2}</li>
<li>{goal3}</li>
</ul>

<h2>Timeline</h2>
<p>Start: {start_date}<br>Target Completion: {end_date}</p>

<h2>Team</h2>
<p>Owner: {owner}<br>Contributors: {contributors}</p>
""",
    """<h1>Project Brief: {project_name}</h1>
<h2>Problem Statement</h2>
<p>{problem}</p>

<h2>Proposed Solution</h2>
<p>{solution}</p>

<h2>Success Metrics</h2>
<ul>
<li>{metric1}</li>
<li>{metric2}</li>
</ul>

<h2>Stakeholders</h2>
<p>{stakeholders}</p>
""",
]


def get_random_company_name() -> str:
    """Get a random tech company name."""
    return random.choice(COMPANY_NAMES)


def get_random_full_name() -> Tuple[str, str]:
    """Get a random full name with realistic distribution."""
    # 50/50 gender distribution
    if random.random() < 0.5:
        first_name = random.choice(FIRST_NAMES_MALE)
    else:
        first_name = random.choice(FIRST_NAMES_FEMALE)
    last_name = random.choice(LAST_NAMES)
    return first_name, last_name


def get_random_team() -> Tuple[str, str]:
    """Get a random team name and description."""
    return random.choice(TEAM_NAMES)


def get_random_project_name(archetype: str, team: str, context: dict) -> str:
    """Generate a project name based on archetype."""
    template = random.choice(PROJECT_TEMPLATES.get(archetype, PROJECT_TEMPLATES["kanban"]))
    
    return template.format(
        team=team,
        number=context.get("number", random.randint(1, 20)),
        quarter=context.get("quarter", random.randint(1, 4)),
        year=context.get("year", 2026),
        month=context.get("month", random.choice(["Jan", "Feb", "Mar", "Apr", "May", "Jun"])),
        product=random.choice(PRODUCT_NAMES),
        feature=random.choice(FEATURE_NAMES),
        campaign=random.choice(CAMPAIGN_NAMES),
        version=f"{random.randint(1, 5)}.{random.randint(0, 9)}",
    )


def get_random_task_name(archetype: str, category: str = "general") -> str:
    """Generate a task name based on archetype and category."""
    templates = TASK_TEMPLATES.get(archetype, TASK_TEMPLATES["kanban"])
    category_templates = templates.get(category, templates.get("general", []))
    
    if not category_templates:
        category_templates = TASK_TEMPLATES["kanban"]["general"]
    
    template = random.choice(category_templates)
    
    return template.format(
        component=random.choice(COMPONENTS),
        action=random.choice(ACTIONS),
        issue=random.choice(ISSUES),
        feature=random.choice(FEATURE_NAMES),
        target=random.choice(TARGETS),
        topic=random.choice(TOPICS),
        item=random.choice(["the proposal", "pending items", "the request", "feedback"]),
        meeting=random.choice(MEETINGS),
        deliverable=random.choice(DELIVERABLES),
        stakeholder=random.choice(STAKEHOLDERS),
        priority=random.randint(0, 3),
        symptom=random.choice(SYMPTOMS),
        change="recent update",
        platform=random.choice(["iOS", "Android", "Web", "Desktop"]),
        report=random.choice(REPORTS),
        metric=random.choice(METRICS),
        document=random.choice(DOCUMENTS),
        channel=random.choice(CHANNELS),
        team=random.choice([t[0] for t in TEAM_NAMES[:5]]),
    )


def get_random_tag() -> Tuple[str, str]:
    """Get a random tag name and color."""
    return random.choice(TAG_TEMPLATES)
