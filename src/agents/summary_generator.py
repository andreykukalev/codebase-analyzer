import os
from nodes.analyzing import AnalyzeNode
from nodes.extracting import ExtractNode
from nodes.reporting import ReportNode
from pathlib import Path
from state.code_analysis import CodeAnalysisState
from utils.clients import OpenAIClient
from utils.tools import Helper
from datetime import datetime

from langgraph.graph import StateGraph, START, END

class SummaryGeneratorAgent:
    """An agent, which builds and runs DAG flow for analysing python codebase and producing business requirements overview."""

    def __init__(self) -> None:
        self.CLONE_DIR = Path(os.getenv("CLONE_DIR_PATH"));
        self.REPORT_DIR = Path(os.getenv("REPORT_DIR_PATH"));
        self.TRACES_DIR = Path(os.getenv("TRACES_DIR_PATH"));

    @staticmethod
    def _get_graph_builder() -> StateGraph:
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

    def run(self) -> None:
        Helper.create_if_not_exists(self.CLONE_DIR) 
        Helper.create_if_not_exists(self.REPORT_DIR)
        Helper.create_if_not_exists(self.TRACES_DIR)
        
        state_graph = self._get_graph_builder().compile()

        try:
            ssh_link = Helper.validate_ssh_link(input("Provide ssh link to remote repository:"))

            repo_name = ssh_link.split(":")[-1].split("/")[-1]
            report_name = Helper.ensure_extension(input("Provide report name:"), "md")
            codebase_local_dir_path = self.CLONE_DIR / repo_name

            Helper.ssh_clone_repository(ssh_link, codebase_local_dir_path)

            state_graph.invoke({
                "traces_local_dir_path": self.TRACES_DIR / f"{repo_name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}",
                "codebase_local_dir_path": codebase_local_dir_path,
                "report_local_file_path": self.REPORT_DIR / repo_name / report_name
            })
        except Exception as e:
            # fallback if input() is not available
            print(f"Error! {e}")
