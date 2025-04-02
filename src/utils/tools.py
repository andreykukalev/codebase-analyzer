import os
import re
import git
import shutil
from pathlib import Path
from datetime import datetime


class Helper:
    """Utility class providing helper methods for file and repository operations."""

    @staticmethod
    def create_if_not_exists(path: Path) -> None:
        """Ensure that the specified folder exists."""
        if not os.path.exists(path):
            os.makedirs(path)

    @staticmethod
    def ensure_extension(file_name: str, extension: str) -> str:
        """Ensure the file_name has the given extension."""
        extension = extension if extension.startswith('.') else f'.{extension}'
        if not file_name.lower().endswith(extension.lower()):
            file_name += extension
        return file_name

    @staticmethod
    def validate_ssh_link(ssh_link: str) -> str:
        """Validate the SSH link format."""
        ssh_pattern = r"^[\w\-\.]+@[\w\-\.]+:[\w\-\/]+(\.git)?$"
        if not re.match(ssh_pattern, ssh_link):
            raise ValueError(f"Invalid SSH link format: {ssh_link}")
        return ssh_link

    @staticmethod
    def ssh_clone_repository(ssh_repo_url: str, clone_dir: Path) -> None:
        """
        Clone a Git repository to the specified directory.

        Args:
            ssh_repo_url (str): The SSH URL of the repository.
            clone_dir (Path): The directory where the repository will be cloned.
        """
        try:
            if not os.path.exists(clone_dir):
                os.makedirs(clone_dir)

            if os.listdir(clone_dir):  # Skip cloning if the directory is not empty
                return

            git.Repo.clone_from(ssh_repo_url, clone_dir)
            print(f"Repository cloned successfully to {clone_dir}")
        except git.GitCommandError as e:
            print(f"Error cloning repository: {e}")

    @staticmethod
    def write_to_file(file_path: Path, content: str, backup_if_exists: bool = True) -> None:
        """
        Write content to a file, optionally creating a backup if the file exists.

        Args:
            file_path (Path): The path to the file.
            content (str): The content to write.
            backup_if_exists (bool): Whether to create a backup if the file exists.
        """
        if not file_path:
            raise ValueError("Filename cannot be empty")

        if not content:
            raise ValueError("Content cannot be empty")

        file_dir = os.path.dirname(file_path)
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)

        if backup_if_exists and os.path.exists(file_path):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{str(file_path).rsplit('.', 1)[0]}_{timestamp}.md"
            shutil.copy2(file_path, backup_filename)

        with open(file_path, "w", encoding="utf-8") as output_file:
            output_file.write(content)