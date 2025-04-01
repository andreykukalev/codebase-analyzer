import os
import shutil
from pathlib import Path
from datetime import datetime
from state.code_analysis import CodeAnalysisState
from utils.clients import OpenAIClient

class ReportNode:
    """A node that builds the report by documenting all extracted business requirements"""

    def _generate_markdown_report(self, llm_analysis: str) -> str:
        """Generates a Markdown report from LLM analysis and method graph."""
        prompt = """
        You are an expert technical writer. Given the following business requirements and method invocation graph, generate a structured Markdown report.
        
        Business Requirements:
        {business_requirements}
        
        The report should include:
        - A high-level summary of the business logic
        - A breakdown of functionalities and their corresponding methods
        - A list of method invocation paths
        - Links to the corresponding code files (if available)
        """
    
        full_prompt = prompt.format(business_requirements=llm_analysis)
        
        return self.llm_client.invoke(full_prompt).content

    @staticmethod
    def _write_to_file(file_path: Path, content: str, mode: str = "w"):
        """Writes content to a file."""

        if not file_path:
            raise ValueError("Filename cannot be empty")
    
        if not content:
            raise ValueError("Content cannot be empty")

        file_dir = os.path.dirname(file_path)

        if not os.path.exists(file_dir):
                os.makedirs(file_dir)

        if os.path.exists(file_path):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{str(file_path).rsplit('.', 1)[0]}_{timestamp}.md"
            shutil.copy2(file_path, backup_filename)

        with open(file_path, mode, encoding="utf-8") as file:
            file.write(content)
        
    def __init__(self, llm_client: OpenAIClient) -> None:
        self.llm_client = llm_client
    
    def __call__(self, state: CodeAnalysisState):
        analysis_result_content = state["llm_analysis_result"].content
        
        markdown_report = self._generate_markdown_report(analysis_result_content)
        self._write_to_file(state["report_local_path"], markdown_report)
    

