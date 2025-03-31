import os
import git
from pathlib import Path
from state import State
from nodes.extractor import ExtractNode
from nodes.reporter import ReporterNode
from nodes.analyzer import AnalyzerNode
from utils.clients import OpenAIClient
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END

CLONE_DIR = Path(__file__).absolute().parent / "clone";

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
    reporterNode = ReporterNode()

    graph_builder = StateGraph(State)
    graph_builder.add_node("extract", extractNode)
    graph_builder.add_node("analyze", analyzerNode)
    graph_builder.add_node("report", reporterNode)

    graph_builder.add_edge(START, "extract")
    graph_builder.add_edge("extract", "analyze")
    graph_builder.add_edge("analyze", "report")
    graph_builder.add_edge("report", END)

    return graph_builder

def run(): 
    graph_builder = get_graph_builder()
    while True:
        try:
            user_input = input("Provide SSH link for repository: ")
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break

            clone_repository(user_input, CLONE_DIR)
            graph = graph_builder.compile()
            graph.invoke({"message": "initial_state"})
        except:
            # fallback if input() is not available
            print("Error!")
            break

if __name__ == "__main__":
    load_dotenv()
    run()