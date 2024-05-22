from git import Repo
import os
import shutil

def download(git_url):
    """Download the repository from the given URL and return the path to the repository"""
    current_path = os.getcwd()
    temp_path = os.path.join(current_path, "temp")
    if os.path.exists(temp_path):
        print("Removing old repository...          \r", end="")
        shutil.rmtree(temp_path)
    print("Downloading repository...           \r", end="")
    Repo.clone_from(git_url, temp_path)
    return temp_path
