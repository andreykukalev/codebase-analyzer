import os
import re
from dotenv import load_dotenv
from nodes.analyzing import AnalyzeNode
from nodes.extracting import ExtractNode
from nodes.reporting import ReportNode
from pathlib import Path
from state.code_analysis import CodeAnalysisState
from utils.clients import OpenAIClient
from utils.tools import GitHelper

from langgraph.graph import StateGraph, START, END

load_dotenv()

CLONE_DIR = Path(os.getenv("CLONE_DIR_PATH"));
REPORT_DIR = Path(os.getenv("REPORT_DIR_PATH"));

def get_graph_builder() -> StateGraph:
    extractNode = ExtractNode()
    analyzerNode = AnalyzeNode(OpenAIClient.get_instance())
    reporterNode = ReportNode(OpenAIClient.get_instance())

    graph_builder = StateGraph(CodeAnalysisState)
    graph_builder.add_node("extract", extractNode)
    graph_builder.add_node("analyze", analyzerNode)
    graph_builder.add_node("report", reporterNode)

    graph_builder.add_edge(START, "extract")
    graph_builder.add_edge("extract", "analyze")
    graph_builder.add_edge("analyze", "report")
    graph_builder.add_edge("report", END)

    return graph_builder

def create_if_not_exists(path: Path) -> bool:
    """Ensures that specified folder existst."""

    if not os.path.exists(path):
        os.makedirs(path)

def ensure_extension(filename: str, extension: str) -> str:
    """Ensures the filename has the given extension."""
    extension = extension if extension.startswith('.') else f'.{extension}'
    
    if not filename.lower().endswith(extension.lower()):
        filename += extension
    
    return filename

def validate_ssh_link(ssh_link: str):
    ssh_pattern = r"^[\w\-\.]+@[\w\-\.]+:[\w\-\/]+(\.git)?$"
    if not re.match(ssh_pattern, ssh_link):
        raise ValueError(f"Invalid SSH link format: {ssh_link}")
    else:
        return ssh_link;


def run():
    create_if_not_exists(CLONE_DIR) 
    create_if_not_exists(REPORT_DIR)
    
    state_graph = get_graph_builder().compile()

    try:
        ssh_link = validate_ssh_link(input("Provide ssh link to remote repository:"))

        repo_name = ssh_link.split(":")[-1].split("/")[-1]
        report_name = ensure_extension(input("Provide report name:"), "md")

        GitHelper.ssh_clone_repository(ssh_link, CLONE_DIR / repo_name)

        state_graph.invoke({
            "codebase_local_path": CLONE_DIR / repo_name,
            "report_local_path": REPORT_DIR / repo_name / report_name
        })
    except Exception as e:
        # fallback if input() is not available
        print(f"Error! {e}")

if __name__ == "__main__":  
    run()