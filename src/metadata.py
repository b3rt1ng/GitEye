import git
import datetime

class Metadata:
    def __init__(self, git_path, detailed=False) -> None:
        """Initialize the metadata object"""
        self.path = git_path
        self.repo = git.Repo(git_path)
        self.detailed = detailed # If false, the commits will only show the 5 first and the 5 last commits

    @property
    def repo_name(self) -> str:
        """Return the name of the repository"""
        return self.repo.remotes.origin.url.split("/")[-1].replace(".git","")
    
    @property
    def author(self) -> str:
        """Return the name of the author"""
        return self.repo.head.commit.author.name
    
    @property
    def names(self) -> list:
        """Return the names of the commit authors"""
        return [commit.author.name for commit in self.repo.iter_commits()]
    
    @property
    def mails(self) -> list:
        """Return the emails of the commit authors"""
        return [commit.author.email for commit in self.repo.iter_commits()]
    
    @property
    def commit_count(self) -> int:
        """Return the number of commits"""
        return len(list(self.repo.iter_commits()))
    
    @property
    def first_commit_date(self) -> str:
        """Return the date of the first commit"""
        return datetime.datetime.fromtimestamp(list(self.repo.iter_commits())[-1].committed_date).strftime("%Y-%m-%d %H:%M:%S")

    @property
    def last_commit_date(self) -> str:
        """Return the date of the last commit"""
        return datetime.datetime.fromtimestamp(self.repo.head.commit.committed_date).strftime("%Y-%m-%d %H:%M:%S")
    
    @property
    def all_commits(self) -> list:
        """return a list like this: [[date, message], ...]"""
        commits = list(self.repo.iter_commits())
        if not self.detailed:
            commits = commits[:5] + commits[-5:]
        return reversed([[datetime.datetime.fromtimestamp(commit.committed_date).strftime("%Y-%m-%d %H:%M:%S"), commit.message.replace("\n","")] for commit in commits])
