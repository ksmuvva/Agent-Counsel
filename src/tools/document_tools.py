"""Multi-modal document tools.

Real implementations backed by openpyxl / python-docx / python-pptx. Each
method degrades to a clear, actionable error if the optional dependency is not
installed, rather than silently returning mock data.
"""
from typing import Any, Dict, List


class MissingDependencyError(RuntimeError):
    """Raised when an optional document library is not installed."""


class DocumentTools:
    """Read and write common office document formats."""

    name = "document_tools"

    # ---- Excel ---------------------------------------------------------
    @staticmethod
    def read_excel(path: str) -> Dict[str, List[List[Any]]]:
        try:
            import openpyxl
        except ImportError as exc:  # pragma: no cover
            raise MissingDependencyError(
                "openpyxl is required to read Excel files (pip install openpyxl)."
            ) from exc
        wb = openpyxl.load_workbook(path, data_only=True)
        return {
            sheet.title: [list(row) for row in sheet.iter_rows(values_only=True)]
            for sheet in wb.worksheets
        }

    @staticmethod
    def write_excel(path: str, rows: List[List[Any]], sheet_name: str = "Sheet1") -> str:
        try:
            import openpyxl
        except ImportError as exc:  # pragma: no cover
            raise MissingDependencyError(
                "openpyxl is required to write Excel files (pip install openpyxl)."
            ) from exc
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = sheet_name
        for row in rows:
            ws.append(row)
        wb.save(path)
        return path

    # ---- Word ----------------------------------------------------------
    @staticmethod
    def read_word(path: str) -> str:
        try:
            import docx
        except ImportError as exc:  # pragma: no cover
            raise MissingDependencyError(
                "python-docx is required to read Word files (pip install python-docx)."
            ) from exc
        document = docx.Document(path)
        return "\n".join(p.text for p in document.paragraphs)

    @staticmethod
    def write_word(path: str, content: str) -> str:
        try:
            import docx
        except ImportError as exc:  # pragma: no cover
            raise MissingDependencyError(
                "python-docx is required to write Word files (pip install python-docx)."
            ) from exc
        document = docx.Document()
        for paragraph in content.split("\n"):
            document.add_paragraph(paragraph)
        document.save(path)
        return path

    # ---- PowerPoint ----------------------------------------------------
    @staticmethod
    def read_powerpoint(path: str) -> List[str]:
        try:
            from pptx import Presentation
        except ImportError as exc:  # pragma: no cover
            raise MissingDependencyError(
                "python-pptx is required to read PowerPoint files (pip install python-pptx)."
            ) from exc
        prs = Presentation(path)
        slides: List[str] = []
        for slide in prs.slides:
            texts = [
                shape.text
                for shape in slide.shapes
                if shape.has_text_frame and shape.text
            ]
            slides.append("\n".join(texts))
        return slides

    @staticmethod
    def write_powerpoint(path: str, slides: List[Dict[str, str]]) -> str:
        try:
            from pptx import Presentation
        except ImportError as exc:  # pragma: no cover
            raise MissingDependencyError(
                "python-pptx is required to write PowerPoint files (pip install python-pptx)."
            ) from exc
        prs = Presentation()
        layout = prs.slide_layouts[1]
        for spec in slides:
            slide = prs.slides.add_slide(layout)
            slide.shapes.title.text = spec.get("title", "")
            slide.placeholders[1].text = spec.get("body", "")
        prs.save(path)
        return path


class WebSearchTool:
    """Web research tool.

    Uses the Tavily API when ``TAVILY_API_KEY`` is set; otherwise raises so the
    caller can decide how to proceed instead of returning fabricated results.
    """

    name = "web_search"

    @staticmethod
    def search(query: str, max_results: int = 5) -> List[Dict[str, str]]:
        import os

        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise MissingDependencyError(
                "Web search requires TAVILY_API_KEY (or wire in your own provider)."
            )
        try:
            import requests
        except ImportError as exc:  # pragma: no cover
            raise MissingDependencyError(
                "requests is required for web search (pip install requests)."
            ) from exc
        resp = requests.post(
            "https://api.tavily.com/search",
            json={"api_key": api_key, "query": query, "max_results": max_results},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        return [
            {"title": r.get("title", ""), "url": r.get("url", ""), "content": r.get("content", "")}
            for r in data.get("results", [])
        ]
