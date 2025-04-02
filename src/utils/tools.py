import os
import re
import git
import shutil
from pathlib import Path
from datetime import datetime

class Helper:

    @staticmethod
    def create_if_not_exists(path: Path) -> None:
        """Ensures that specified folder exists."""

        if not os.path.exists(path):
            os.makedirs(path)

    @staticmethod
    def ensure_extension(file_name: str, extension: str) -> str:
        """Ensures the file_name has the given extension."""

        extension = extension if extension.startswith('.') else f'.{extension}'
        
        if not file_name.lower().endswith(extension.lower()):
            file_name += extension
        
        return file_name

    @staticmethod
    def validate_ssh_link(ssh_link: str) -> str:
        """Ensures the ssh_link has the valid format."""

        ssh_pattern = r"^[\w\-\.]+@[\w\-\.]+:[\w\-\/]+(\.git)?$"
        if not re.match(ssh_pattern, ssh_link):
            raise ValueError(f"Invalid SSH link format: {ssh_link}")
        else:
            return ssh_link;

    @staticmethod
    def ssh_clone_repository(ssh_repo_url: str, clone_dir: Path) -> None:
        """Clones a Git repository to the specified directory."""
        try:
            if not os.path.exists(clone_dir):
                os.makedirs(clone_dir)

            if bool(os.listdir(clone_dir)):
                return
            
            git.Repo.clone_from(ssh_repo_url, clone_dir)
            print(f"Repository cloned successfully to {clone_dir}")
        except git.GitCommandError as e:
            print(f"Error cloning repository: {e}")

    @staticmethod
    def write_to_file(file_path: Path, content: str, backup_if_exists: bool = True) -> None:
        """Writes content to a file."""

        if not file_path:
            raise ValueError("Filename cannot be empty")
    
        if not content:
            raise ValueError("Content cannot be empty")

        file_dir = os.path.dirname(file_path)

        if not os.path.exists(file_dir):
                os.makedirs(file_dir)

        if backup_if_exists:
            if os.path.exists(file_path):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_filename = f"{str(file_path).rsplit('.', 1)[0]}_{timestamp}.md"
                shutil.copy2(file_path, backup_filename)

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)