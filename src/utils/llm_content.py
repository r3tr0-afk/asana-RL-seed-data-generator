"""
LLM Content Generator - Using Local Ollama Models
==================================================

This module provides LLM-powered content generation for:
- Task descriptions
- Comments/stories
- Project briefs
- Status updates

Uses Ollama for local inference with lightweight models.

Prompt Engineering Methodology:
- Parameterized prompts with context injection
- Few-shot examples for consistent formatting
- Temperature control for variety
"""

import os
import random
from typing import Optional, Dict, Any, List

from utils.config import ENABLE_LLM, OLLAMA_MODEL, OLLAMA_HOST
from scrapers.data_sources import (
    DESCRIPTION_TEMPLATES,
    OVERVIEW_SNIPPETS,
    REQUIREMENT_SNIPPETS,
    CRITERIA_SNIPPETS,
    COMMENT_TEMPLATES,
    STATUS_UPDATE_TEMPLATES,
    PROJECT_BRIEF_TEMPLATES,
)

# Try to import ollama, but make it optional
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False


class LLMContentGenerator:
    """
    Generate realistic content using local LLM or fallback templates.
    
    Methodology:
    - Primary: Use Ollama with lightweight models (llama3.2:1b, phi3:mini)
    - Fallback: Template-based generation when LLM unavailable
    - Ensures variety through parameterized prompts and temperature
    """
    
    def __init__(self):
        self.enabled = ENABLE_LLM and OLLAMA_AVAILABLE
        self.model = OLLAMA_MODEL
        
        if self.enabled:
            try:
                # Test connection
                ollama.list()
                print(f"[OK] LLM enabled using {self.model}")
            except Exception as e:
                print(f"[!] LLM not available: {e}")
                self.enabled = False
    
    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 200
    ) -> Optional[str]:
        """
        Generate content using LLM.
        
        Args:
            prompt: The generation prompt
            temperature: Creativity (0.0-1.0)
            max_tokens: Maximum response length
        
        Returns:
            Generated text or None
        """
        if not self.enabled:
            return None
        
        try:
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                options={
                    "temperature": temperature,
                    "num_predict": max_tokens,
                }
            )
            return response.get("response", "").strip()
        except Exception as e:
            print(f"LLM generation failed: {e}")
            return None
    
    # =========================================================================
    # TASK DESCRIPTION GENERATION
    # =========================================================================
    
    def generate_task_description(
        self,
        task_name: str,
        project_type: str,
        complexity: str = "short"
    ) -> str:
        """
        Generate a task description.
        
        Prompt Template (for LLM):
        ```
        You are writing a task description for a project management tool.
        
        Task: {task_name}
        Project Type: {project_type}
        Complexity: {complexity}
        
        Write a brief, professional task description. Be specific and actionable.
        {complexity_instruction}
        ```
        
        Variety Strategy:
        - Temperature 0.7-0.9 for text variety
        - Complexity parameter changes structure
        - Project type influences terminology
        """
        
        complexity_instructions = {
            "empty": "Return empty string.",
            "short": "Keep it to 1-2 sentences. No formatting.",
            "detailed": "Include sections: Overview, Requirements (bullet points), Acceptance Criteria (checkboxes)."
        }
        
        # Try LLM first
        if self.enabled and complexity != "empty":
            prompt = f"""You are writing a task description for a project management tool like Asana.

Task: {task_name}
Project Type: {project_type}
Complexity: {complexity}

Write a professional task description. {complexity_instructions.get(complexity, '')}
Do not include the task name in your response. Just the description."""

            result = self.generate(
                prompt,
                temperature=0.8 if complexity == "detailed" else 0.7,
                max_tokens=300 if complexity == "detailed" else 100
            )
            
            if result:
                return result
        
        # Fallback: Template-based generation
        return self._generate_description_fallback(task_name, project_type, complexity)
    
    def _generate_description_fallback(
        self,
        task_name: str,
        project_type: str,
        complexity: str
    ) -> str:
        """Template-based fallback for task descriptions."""
        
        if complexity == "empty":
            return ""
        
        if complexity == "short":
            return random.choice(DESCRIPTION_TEMPLATES["short"])
        
        # Detailed description
        template = random.choice(DESCRIPTION_TEMPLATES["detailed"])
        
        return template.format(
            overview=random.choice(OVERVIEW_SNIPPETS),
            requirement1=random.choice(REQUIREMENT_SNIPPETS),
            requirement2=random.choice(REQUIREMENT_SNIPPETS),
            requirement3=random.choice(REQUIREMENT_SNIPPETS),
            criteria1=random.choice(CRITERIA_SNIPPETS),
            criteria2=random.choice(CRITERIA_SNIPPETS),
            criteria3=random.choice(CRITERIA_SNIPPETS),
            context=random.choice(OVERVIEW_SNIPPETS),
            step1="Review requirements and dependencies",
            step2="Implement the changes",
            step3="Test and document",
            notes="Please reach out if you have any questions.",
            background=random.choice(OVERVIEW_SNIPPETS),
            task_detail="Complete the implementation as specified.",
            dependency1="Dependent on API changes",
            dependency2="Needs design review",
            timeline="Target completion within this sprint",
        )
    
    # =========================================================================
    # COMMENT GENERATION
    # =========================================================================
    
    def generate_comment(
        self,
        task_name: str,
        author_name: str,
        context: Dict[str, Any] = None
    ) -> str:
        """
        Generate a realistic task comment.
        
        Prompt Template (for LLM):
        ```
        You are {author_name} leaving a comment on a task in a project management tool.
        
        Task: {task_name}
        
        Write a brief, natural-sounding work comment. Examples:
        - Progress updates
        - Questions
        - Status changes
        - Blockers
        
        Keep it to 1-2 sentences. Be casual but professional.
        ```
        """
        context = context or {}
        
        if self.enabled:
            prompt = f"""You are {author_name} leaving a comment on a task in Asana.

Task: {task_name}

Write a brief, natural work comment (1-2 sentences). Could be a progress update, question, or status note. Be casual but professional. No greetings or signatures."""

            result = self.generate(prompt, temperature=0.8, max_tokens=80)
            if result:
                return result
        
        # Fallback
        comment = random.choice(COMMENT_TEMPLATES)
        return comment.format(
            blocker="pending review",
            person=context.get("mention", "team"),
            project="the project",
            section="In Progress",
            priority="P1",
            tag="blocked",
            date="next week",
        )
    
    # =========================================================================
    # STATUS UPDATE GENERATION
    # =========================================================================
    
    def generate_status_update(
        self,
        project_name: str,
        status_type: str,
        author_name: str
    ) -> str:
        """
        Generate a project status update.
        
        Prompt Template (for LLM):
        ```
        You are {author_name} writing a {status_type} status update for project: {project_name}
        
        Write a status update with:
        - Brief summary
        - Key accomplishments (if on_track)
        - Issues/blockers (if at_risk or off_track)
        - Next steps
        
        Use markdown formatting. Keep it concise.
        ```
        """
        
        if self.enabled:
            prompt = f"""You are {author_name} writing a project status update in Asana.

Project: {project_name}
Status: {status_type.replace('_', ' ').title()}

Write a brief status update (3-5 sentences) with:
- Current state summary
- Key accomplishments or issues
- Next steps

Use markdown formatting with emojis for status indicators."""

            result = self.generate(prompt, temperature=0.7, max_tokens=250)
            if result:
                return result
        
        # Fallback
        templates = STATUS_UPDATE_TEMPLATES.get(status_type, STATUS_UPDATE_TEMPLATES["on_track"])
        template = random.choice(templates)
        
        return template.format(
            progress="Made good progress on core features.",
            completed1="Finished API integration",
            completed2="Updated documentation",
            next1="Begin testing phase",
            next2="Stakeholder review",
            summary="The project is progressing well with no major blockers.",
            issue="Some scope creep has impacted the timeline.",
            mitigation="Prioritizing critical path items.",
            need="Additional resources for testing.",
            blocker1="Waiting on design assets",
            action1="Follow up with design team",
            impact="May delay launch by 1 week.",
            plan="Focusing on critical features first.",
            escalation="Need executive decision on scope.",
            cause="Unexpected technical complexity.",
            timeline="Revised ETA: end of next week",
        )
    
    # =========================================================================
    # PROJECT BRIEF GENERATION
    # =========================================================================
    
    def generate_project_brief(
        self,
        project_name: str,
        team_name: str,
        owner_name: str,
        created_at: str
    ) -> str:
        """
        Generate an HTML project brief.
        
        Uses templates with dynamic content insertion.
        """
        
        template = random.choice(PROJECT_BRIEF_TEMPLATES)
        
        return template.format(
            project_name=project_name,
            overview=f"This project aims to deliver key improvements for the {team_name} team.",
            goal1="Improve efficiency by 20%",
            goal2="Reduce manual work",
            goal3="Enhance user experience",
            start_date=created_at,
            end_date="TBD",
            owner=owner_name,
            contributors=f"{team_name} team members",
            problem=f"Current processes need optimization for better {team_name.lower()} outcomes.",
            solution=f"Implementing new workflows and tools to streamline {team_name.lower()} operations.",
            metric1="Time to completion reduced by 30%",
            metric2="Team satisfaction score above 8/10",
            stakeholders=f"{owner_name}, {team_name} leads",
        )


# Global instance
_llm_generator = None


def get_llm_generator() -> LLMContentGenerator:
    """Get or create the singleton LLM generator instance."""
    global _llm_generator
    if _llm_generator is None:
        _llm_generator = LLMContentGenerator()
    return _llm_generator


def generate_task_description(
    task_name: str,
    project_type: str,
    complexity: str = "short"
) -> str:
    """Convenience function for task description generation."""
    return get_llm_generator().generate_task_description(task_name, project_type, complexity)


def generate_comment(
    task_name: str,
    author_name: str,
    context: Dict[str, Any] = None
) -> str:
    """Convenience function for comment generation."""
    return get_llm_generator().generate_comment(task_name, author_name, context)


def generate_status_update(
    project_name: str,
    status_type: str,
    author_name: str
) -> str:
    """Convenience function for status update generation."""
    return get_llm_generator().generate_status_update(project_name, status_type, author_name)


def generate_project_brief(
    project_name: str,
    team_name: str,
    owner_name: str,
    created_at: str
) -> str:
    """Convenience function for project brief generation."""
    return get_llm_generator().generate_project_brief(project_name, team_name, owner_name, created_at)
