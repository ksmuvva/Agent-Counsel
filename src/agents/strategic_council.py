"""Tier 3-4 strategic council agents: governance, quality, ethics."""
from __future__ import annotations

from core.base_agent import Agent
from config.models import OPUS


def domain_council_chair() -> Agent:
    return Agent(
        name="Domain Council Chair",
        description="SME selection & governance",
        model=OPUS,
        system_prompt=(
            "You are the Domain Council Chair. Given a task, identify the domains "
            "involved and recommend which SME personas should be engaged from this "
            "roster: IAM Architect, Cloud Architect, Security Analyst, Data "
            "Engineer, AI/ML Engineer, Test Engineer, Business Analyst, Technical "
            "Writer, DevOps Engineer, Frontend Developer. End your reply with a line "
            "'SELECTED: <comma-separated persona names>'."
        ),
    )


def quality_arbiter() -> Agent:
    return Agent(
        name="Quality Arbiter",
        description="Quality standard setting & tiebreaker",
        model=OPUS,
        system_prompt=(
            "You are the Quality Arbiter. Set explicit quality standards and act as "
            "the decisive tiebreaker in debates, weighing each argument on its merits."
        ),
    )


def ethics_safety_advisor() -> Agent:
    return Agent(
        name="Ethics & Safety Advisor",
        description="Bias, PII, compliance review",
        model=OPUS,
        system_prompt=(
            "You are the Ethics & Safety Advisor. Review content for bias, PII "
            "exposure, and compliance issues, and clearly flag any concerns."
        ),
    )
