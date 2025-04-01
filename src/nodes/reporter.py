import networkx as nx
from state import State
from utils.clients import OpenAIClient

class ReporterNode:
    """A node that builds the report by documenting all extracted business requirements"""

    def generate_markdown_report(self, llm_analysis: str) -> str:
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
        
        return self.llm.invoke(full_prompt).content

    @staticmethod
    def write_to_file(filename: str, content: str, mode: str = "w"):
        """Writes content to a file."""
        with open(filename, mode, encoding="utf-8") as file:
            file.write(content)
        
    def __init__(self, llm: OpenAIClient) -> None:
        self.llm = llm
    
    def __call__(self, state: State):
        analysis_result_content = state["llm_analysis_result"].content
        
        markdown_report = self.generate_markdown_report(analysis_result_content)
        self.write_to_file(state["report_local_path"], markdown_report, "w")
    

