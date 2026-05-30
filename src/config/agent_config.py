AGENT_ROLES = {
    "Strategic Council": {
        "Domain Council Chair": {"model": "claude-3-opus-20240229", "description": "SME selection & governance"},
        "Quality Arbiter": {"model": "claude-3-opus-20240229", "description": "Quality standard setting & tiebreaker"},
        "Ethics & Safety Advisor": {"model": "claude-3-opus-20240229", "description": "Bias, PII, compliance review"},
    },
    "Operational Agents": {
        "Orchestrator": {"model": "claude-3-opus-20240229", "description": "Parent agent, tier classification, coordination"},
        "Task Analyst": {"model": "claude-3-5-sonnet-20240620", "description": "Task decomposition & requirements analysis"},
        "Planner": {"model": "claude-3-5-sonnet-20240620", "description": "Execution planning & sequencing"},
        "Clarifier": {"model": "claude-3-5-sonnet-20240620", "description": "Question formulation for missing requirements"},
        "Researcher": {"model": "claude-3-5-sonnet-20240620", "description": "Evidence gathering & web research"},
        "Executor": {"model": "claude-3-5-sonnet-20240620", "description": "Solution generation with Tree of Thoughts"},
        "Code Reviewer": {"model": "claude-3-5-sonnet-20240620", "description": "Security, performance, style review"},
        "Formatter": {"model": "claude-3-5-sonnet-20240620", "description": "Multi-format output generation"},
        "Verifier": {"model": "claude-3-opus-20240229", "description": "Hallucination detection & fact-checking"},
        "Critic": {"model": "claude-3-opus-20240229", "description": "Adversarial attack (5 vectors)"},
        "Reviewer": {"model": "claude-3-opus-20240229", "description": "Final quality gate"},
        "Memory Curator": {"model": "claude-3-5-sonnet-20240620", "description": "Knowledge extraction & persistence"},
    },
    "Dynamic SME Personas": {
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
}
