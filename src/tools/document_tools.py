"""Real, in-process tools exposed to the agents via the Claude Agent SDK.

These are genuine `@tool` functions: when an agent decides to call one, the SDK
executes this Python code and feeds the result back into the model's reasoning
loop. The document tools perform real file I/O via openpyxl / python-docx /
python-pptx. ``build_tool_server`` packages them as an in-process MCP server.
"""
from __future__ import annotations

import os
from typing import Any, Dict

from claude_agent_sdk import create_sdk_mcp_server, tool


def _ok(text: str) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": text}]}


def _err(text: str) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": f"ERROR: {text}"}], "is_error": True}


# --------------------------------------------------------------------------- #
# Excel
# --------------------------------------------------------------------------- #
@tool("write_excel", "Write rows of data to a real .xlsx file", {"path": str, "rows_json": str})
async def write_excel(args: Dict[str, Any]) -> Dict[str, Any]:
    import json

    try:
        import openpyxl
    except ImportError:
        return _err("openpyxl is not installed (pip install openpyxl).")
    try:
        rows = json.loads(args["rows_json"])
        wb = openpyxl.Workbook()
        ws = wb.active
        for row in rows:
            ws.append(row if isinstance(row, list) else [row])
        wb.save(args["path"])
        return _ok(f"Wrote {len(rows)} rows to {args['path']}")
    except Exception as exc:  # surface real errors to the model
        return _err(str(exc))


@tool("read_excel", "Read all rows from the first sheet of an .xlsx file", {"path": str})
async def read_excel(args: Dict[str, Any]) -> Dict[str, Any]:
    try:
        import openpyxl
    except ImportError:
        return _err("openpyxl is not installed (pip install openpyxl).")
    try:
        wb = openpyxl.load_workbook(args["path"], data_only=True)
        ws = wb.active
        rows = [list(r) for r in ws.iter_rows(values_only=True)]
        return _ok(str(rows))
    except Exception as exc:
        return _err(str(exc))


# --------------------------------------------------------------------------- #
# Word
# --------------------------------------------------------------------------- #
@tool("write_word", "Write text content to a real .docx file", {"path": str, "content": str})
async def write_word(args: Dict[str, Any]) -> Dict[str, Any]:
    try:
        import docx
    except ImportError:
        return _err("python-docx is not installed (pip install python-docx).")
    try:
        document = docx.Document()
        for paragraph in args["content"].split("\n"):
            document.add_paragraph(paragraph)
        document.save(args["path"])
        return _ok(f"Wrote document to {args['path']}")
    except Exception as exc:
        return _err(str(exc))


@tool("read_word", "Read all paragraph text from a .docx file", {"path": str})
async def read_word(args: Dict[str, Any]) -> Dict[str, Any]:
    try:
        import docx
    except ImportError:
        return _err("python-docx is not installed (pip install python-docx).")
    try:
        document = docx.Document(args["path"])
        return _ok("\n".join(p.text for p in document.paragraphs))
    except Exception as exc:
        return _err(str(exc))


# --------------------------------------------------------------------------- #
# PowerPoint
# --------------------------------------------------------------------------- #
@tool(
    "write_powerpoint",
    "Write slides to a real .pptx file. slides_json is a list of {title, body}.",
    {"path": str, "slides_json": str},
)
async def write_powerpoint(args: Dict[str, Any]) -> Dict[str, Any]:
    import json

    try:
        from pptx import Presentation
    except ImportError:
        return _err("python-pptx is not installed (pip install python-pptx).")
    try:
        slides = json.loads(args["slides_json"])
        prs = Presentation()
        layout = prs.slide_layouts[1]
        for spec in slides:
            slide = prs.slides.add_slide(layout)
            slide.shapes.title.text = spec.get("title", "")
            slide.placeholders[1].text = spec.get("body", "")
        prs.save(args["path"])
        return _ok(f"Wrote {len(slides)} slides to {args['path']}")
    except Exception as exc:
        return _err(str(exc))


# --------------------------------------------------------------------------- #
# Web search (real, via Tavily; errors clearly if unconfigured)
# --------------------------------------------------------------------------- #
@tool("web_search", "Search the web for up-to-date information", {"query": str})
async def web_search(args: Dict[str, Any]) -> Dict[str, Any]:
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return _err("web_search requires TAVILY_API_KEY to be set.")
    try:
        import requests

        resp = requests.post(
            "https://api.tavily.com/search",
            json={"api_key": api_key, "query": args["query"], "max_results": 5},
            timeout=30,
        )
        resp.raise_for_status()
        results = resp.json().get("results", [])
        lines = [f"- {r.get('title')}: {r.get('url')}\n  {r.get('content', '')[:300]}" for r in results]
        return _ok("\n".join(lines) if lines else "No results.")
    except Exception as exc:
        return _err(str(exc))


ALL_TOOLS = [
    write_excel,
    read_excel,
    write_word,
    read_word,
    write_powerpoint,
    web_search,
]

# Fully-qualified tool names as the agents must reference them in allowed_tools.
TOOL_SERVER_NAME = "council_tools"
DOCUMENT_TOOL_NAMES = [
    f"mcp__{TOOL_SERVER_NAME}__write_excel",
    f"mcp__{TOOL_SERVER_NAME}__read_excel",
    f"mcp__{TOOL_SERVER_NAME}__write_word",
    f"mcp__{TOOL_SERVER_NAME}__read_word",
    f"mcp__{TOOL_SERVER_NAME}__write_powerpoint",
]
WEB_SEARCH_TOOL_NAME = f"mcp__{TOOL_SERVER_NAME}__web_search"


def build_tool_server():
    """Create the in-process MCP server exposing all council tools."""
    return create_sdk_mcp_server(name=TOOL_SERVER_NAME, version="1.0.0", tools=ALL_TOOLS)
