import os
import git
from pathlib import Path, WindowsPath
from state import State
from nodes.extractor import ExtractNode
from nodes.reporter import ReporterNode
from nodes.analyzer import AnalyzerNode
from utils.clients import OpenAIClient
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END

CLONE_DIR = Path(__file__).absolute().parent / "clone" / "eeazycrm";
REPORT_DIR = Path(__file__).absolute().parent / "report" / "eeazycrm";

def clone_repository(ssh_repo_url: str, clone_dir: str):
    """Clones a Git repository to the specified directory."""
    try:
        if not os.path.exists(clone_dir):
            os.makedirs(clone_dir)
        git.Repo.clone_from(ssh_repo_url, clone_dir)
        print(f"Repository cloned successfully to {clone_dir}")
    except git.GitCommandError as e:
        print(f"Error cloning repository: {e}")

def get_graph_builder() -> StateGraph:
    extractNode = ExtractNode()
    analyzerNode = AnalyzerNode(OpenAIClient.get_instance())
    reporterNode = ReporterNode(OpenAIClient.get_instance())

    graph_builder = StateGraph(State)
    graph_builder.add_node("extract", extractNode)
    graph_builder.add_node("analyze", analyzerNode)
    graph_builder.add_node("report", reporterNode)

    graph_builder.add_edge(START, "extract")
    graph_builder.add_edge("extract", "analyze")
    graph_builder.add_edge("analyze", "report")
    graph_builder.add_edge("report", END)

    return graph_builder

def create_if_not_exists(path: WindowsPath) -> bool:
    """Ensures that specified folder existst."""
    if not os.path.exists(path):
        os.makedirs(path)

def ensure_extension(filename: str, extension: str) -> str:
    """Ensures the filename has the given extension."""
    extension = extension if extension.startswith('.') else f'.{extension}'
    
    if not filename.lower().endswith(extension.lower()):
        filename += extension
    
    return filename

def run():
    create_if_not_exists(CLONE_DIR) 
    create_if_not_exists(REPORT_DIR)
    
    state_graph = get_graph_builder().compile()

    try:
        #clone_repository(user_input, CLONE_DIR)
        report_name = input("Provide report name:")
        report_name = ensure_extension(report_name, "md")

        state_graph.invoke({
            "codebase_local_path": CLONE_DIR,
            "report_local_path": REPORT_DIR / report_name
        })
    except Exception as e:
        # fallback if input() is not available
        print(f"Error! {e}")

if __name__ == "__main__":
    load_dotenv()
    run()