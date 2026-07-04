import datetime


class Metadata:
    def __init__(self, client, url, detailed=False) -> None:
        self.client = client
        self.owner, self.repo = client.parse_url(url)
        self.detailed = detailed

        self.repo_info = client.get_repo(self.owner, self.repo)
        self.branch = self.repo_info["default_branch"]
        self.commits = client.get_commits(self.owner, self.repo)

    @property
    def repo_name(self) -> str:
        return self.repo_info["name"]

    @property
    def author(self) -> str:
        return self.commits[0]["commit"]["author"]["name"]

    @property
    def names(self) -> list:
        return [commit["commit"]["author"]["name"] for commit in self.commits]

    @property
    def mails(self) -> list:
        return [commit["commit"]["author"]["email"] for commit in self.commits]

    @property
    def commit_count(self) -> int:
        return len(self.commits)

    @property
    def first_commit_date(self) -> str:
        return self._format_date(self.commits[-1]["commit"]["author"]["date"])

    @property
    def last_commit_date(self) -> str:
        return self._format_date(self.commits[0]["commit"]["author"]["date"])

    @property
    def all_commits(self) -> list:
        commits = self.commits
        if not self.detailed:
            commits = commits[:5] + commits[-5:]
        return reversed([
            [self._format_date(commit["commit"]["author"]["date"]), commit["commit"]["message"].replace("\n", "")]
            for commit in commits
        ])

    @staticmethod
    def _format_date(iso_date: str) -> str:
        return datetime.datetime.strptime(iso_date, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M:%S")
