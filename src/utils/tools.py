import os
import git
from pathlib import Path

class GitHelper:

    @staticmethod
    def ssh_clone_repository(ssh_repo_url: str, clone_dir: Path):
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