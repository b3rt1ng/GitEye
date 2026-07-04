import re
from collections import Counter

NOREPLY_PATTERN = re.compile(r'^(\d+\+)?[^@]+@users\.noreply\.github\.com$|^noreply@github\.com$', re.IGNORECASE)


class UserTrace:
    def __init__(self, client, username) -> None:
        self.client = client
        self.username = username

        all_repos = client.get_user_repos(username)
        self.repos = [repo for repo in all_repos if not repo.get("fork")]

        self.traces = []
        for repo in self.repos:
            commits = client.get_commits(username, repo["name"], author=username)
            for commit in commits:
                author = commit["commit"]["author"]
                self.traces.append((repo["name"], author["name"], author["email"], author["date"]))

    @property
    def repo_count(self) -> int:
        return len(self.repos)

    @staticmethod
    def is_exposed(email) -> bool:
        return not NOREPLY_PATTERN.match(email)

    def _grouped(self) -> list:
        counts = Counter((name, email) for _, name, email, _ in self.traces)
        repos_by_identity = {}
        for repo, name, email, _ in self.traces:
            repos_by_identity.setdefault((name, email), set()).add(repo)
        return [
            (name, email, count, repos_by_identity[(name, email)])
            for (name, email), count in counts.most_common()
        ]

    @property
    def identities(self) -> list:
        return [(name, email, str(count), ", ".join(sorted(repos))) for name, email, count, repos in self._grouped()]

    @property
    def exposed_identities(self) -> list:
        return [(name, email, count, repos) for name, email, count, repos in self._grouped() if self.is_exposed(email)]
