from state.code_analysis import CodeAnalysisState
from utils.clients import OpenAIClient
from utils.tools import Helper
from prompts.templates import format_markdown_prompt 

class ReportNode:
    """A node that builds the report by documenting all extracted business requirements."""

    def __init__(self, llm_client: OpenAIClient) -> None:
        self.llm_client = llm_client
    
    def __call__(self, state: CodeAnalysisState) -> None:  
        print(f"Running reporting node...")

        full_prompt = format_markdown_prompt.format(
            collected_insights=state["llm_analysis_result"].content)
        
        Helper.write_to_file(
            state["report_local_file_path"], 
            self.llm_client.invoke(full_prompt).content)
    

