"""The real agent execution engine, built on the Claude Agent SDK.

Each agent invocation is a genuine ReAct loop: the SDK drives the model, which
may call the in-process tools we expose, observe their results, and iterate
until it produces a final answer. There is no simulation or mock path — running
an agent requires a working Claude Agent SDK environment (an authenticated
`claude` CLI or `ANTHROPIC_API_KEY`).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    McpSdkServerConfig,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    query,
)


@dataclass
class AgentResult:
    """The real outcome of an agent run."""

    text: str
    cost_usd: float
    num_turns: int
    duration_ms: int
    tools_used: List[str] = field(default_factory=list)
    is_error: bool = False
    model: Optional[str] = None
    usage: Dict[str, Any] = field(default_factory=dict)


async def invoke_agent(
    *,
    system_prompt: str,
    prompt: str,
    model: str,
    mcp_servers: Optional[Dict[str, McpSdkServerConfig]] = None,
    allowed_tools: Optional[List[str]] = None,
    max_turns: int = 8,
) -> AgentResult:
    """Run a single agent to completion and return its real result.

    The model autonomously decides whether and how to call the supplied tools;
    we surface which tools were actually invoked, the real USD cost, and the
    number of reasoning turns reported by the SDK.
    """
    granted = allowed_tools or []
    # Sandbox each council agent to ONLY its own tools:
    #  - ``tools`` removes the host CLI's built-ins (Bash, Write, Skill, ...) so
    #    the agent can't wander off-task into the surrounding project.
    #  - ``allowed_tools`` pre-approves those tools so they run without a
    #    permission prompt (we avoid bypassPermissions: the CLI refuses it under
    #    root, and pre-approval is the safer mechanism).
    #  - ``setting_sources=[]`` ignores any host user/project/local settings.
    options = ClaudeAgentOptions(
        system_prompt=system_prompt,
        model=model,
        mcp_servers=mcp_servers or {},
        tools=granted,
        allowed_tools=granted,
        setting_sources=[],
        max_turns=max_turns,
    )

    text_parts: List[str] = []
    tools_used: List[str] = []
    result_msg: Optional[ResultMessage] = None

    # If the model exhausts its turn budget the SDK raises mid-stream; we still
    # want whatever text/tool activity accumulated rather than failing the whole
    # pipeline, so we capture it and mark the result as an error.
    stream_error: Optional[str] = None
    try:
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        text_parts.append(block.text)
                    elif isinstance(block, ToolUseBlock):
                        tools_used.append(block.name)
            elif isinstance(message, ResultMessage):
                result_msg = message
    except Exception as exc:  # noqa: BLE001 - surfaced via AgentResult.is_error
        stream_error = str(exc)

    if result_msg is not None:
        final_text = result_msg.result or "\n".join(text_parts).strip()
        return AgentResult(
            text=final_text,
            cost_usd=result_msg.total_cost_usd or 0.0,
            num_turns=result_msg.num_turns,
            duration_ms=result_msg.duration_ms,
            tools_used=tools_used,
            is_error=result_msg.is_error,
            model=model,
            usage=result_msg.usage or {},
        )

    # No ResultMessage (e.g. the stream raised). Degrade gracefully if we have
    # partial text; otherwise re-raise so genuine failures are not hidden.
    partial = "\n".join(text_parts).strip()
    if partial:
        return AgentResult(
            text=partial,
            cost_usd=0.0,
            num_turns=0,
            duration_ms=0,
            tools_used=tools_used,
            is_error=True,
            model=model,
        )
    raise RuntimeError(stream_error or "Agent run produced no ResultMessage from the SDK.")
