"""Declarative roster of permanent agents and SME personas."""
from config.models import OPUS, SONNET

AGENT_ROLES = {
    "Strategic Council": {
        "Domain Council Chair": {"model": OPUS, "description": "SME selection & governance"},
        "Quality Arbiter": {"model": OPUS, "description": "Quality standard setting & tiebreaker"},
        "Ethics & Safety Advisor": {"model": OPUS, "description": "Bias, PII, compliance review"},
    },
    "Operational": {
        "Orchestrator": {"model": OPUS, "description": "Parent agent, tier classification, coordination"},
        "Task Analyst": {"model": SONNET, "description": "Task decomposition & requirements analysis"},
        "Planner": {"model": SONNET, "description": "Execution planning & sequencing"},
        "Clarifier": {"model": SONNET, "description": "Question formulation for missing requirements"},
        "Researcher": {"model": SONNET, "description": "Evidence gathering & web research"},
        "Executor": {"model": SONNET, "description": "Solution generation with Tree of Thoughts"},
        "Code Reviewer": {"model": SONNET, "description": "Security, performance, style review"},
        "Formatter": {"model": SONNET, "description": "Multi-format output generation"},
        "Verifier": {"model": OPUS, "description": "Hallucination detection & fact-checking"},
        "Critic": {"model": OPUS, "description": "Adversarial attack (5 vectors)"},
        "Reviewer": {"model": OPUS, "description": "Final quality gate"},
        "Memory Curator": {"model": SONNET, "description": "Knowledge extraction & persistence"},
    },
}

SME_PERSONAS = {
    "IAM Architect": {"domain": "Identity & Access Management", "skills": ["SailPoint", "CyberArk", "RBAC"]},
    "Cloud Architect": {"domain": "Cloud Infrastructure", "skills": ["Azure", "AWS", "GCP"]},
    "Security Analyst": {"domain": "Security & Compliance", "skills": ["Threat modelling", "OWASP"]},
    "Data Engineer": {"domain": "Data Pipelines", "skills": ["ETL", "databases", "SQL"]},
    "AI/ML Engineer": {"domain": "AI/ML Systems", "skills": ["GenAI", "RAG", "agents"]},
    "Test Engineer": {"domain": "Testing Strategies", "skills": ["Test cases", "SIT", "UAT"]},
    "Business Analyst": {"domain": "Requirements & Processes", "skills": ["BPMN", "gap analysis"]},
    "Technical Writer": {"domain": "Documentation", "skills": ["Docs", "tenders", "reports"]},
    "DevOps Engineer": {"domain": "CI/CD & Infrastructure", "skills": ["Docker", "Kubernetes", "Terraform"]},
    "Frontend Developer": {"domain": "UI Development", "skills": ["Streamlit", "React", "dashboards"]},
}
