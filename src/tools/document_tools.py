from typing import Any, Dict

class DocumentTools:
    """Tools for interacting with Excel, Word, and PowerPoint files."""
    
    @staticmethod
    def read_excel(file_path: str) -> Dict[str, Any]:
        print(f"Reading Excel file: {file_path}")
        return {"data": "Mock Excel data"}

    @staticmethod
    def write_excel(file_path: str, data: Dict[str, Any]):
        print(f"Writing Excel file: {file_path}")

    @staticmethod
    def read_word(file_path: str) -> str:
        print(f"Reading Word file: {file_path}")
        return "Mock Word content"

    @staticmethod
    def write_word(file_path: str, content: str):
        print(f"Writing Word file: {file_path}")

    @staticmethod
    def read_ppt(file_path: str) -> Dict[str, Any]:
        print(f"Reading PowerPoint file: {file_path}")
        return {"slides": "Mock PPT slides"}

    @staticmethod
    def write_ppt(file_path: str, data: Dict[str, Any]):
        print(f"Writing PowerPoint file: {file_path}")

class WebSearchTool:
    """Tool for web search."""
    
    @staticmethod
    def search(query: str) -> str:
        print(f"Searching the web for: {query}")
        return f"Mock search results for: {query}"
