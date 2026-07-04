import re
import requests

REPO_URL_PATTERN = re.compile(r"github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$")
MAX_COMMIT_PAGES = 100  # safety cap: 100 * 100 = 10k commits


class GitHubAPIError(Exception):
    pass


class GitHubClient:
    def __init__(self, token=None):
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {"Accept": "application/vnd.github+json"}
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    def parse_url(self, url) -> tuple:
        match = REPO_URL_PATTERN.search(url)
        if not match:
            raise GitHubAPIError(f"'{url}' does not look like a GitHub repository URL")
        return match.group(1), match.group(2)

    def _get(self, path, headers=None, params=None):
        response = requests.get(
            f"{self.base_url}{path}",
            headers={**self.headers, **(headers or {})},
            params=params,
        )
        if response.status_code == 404:
            raise GitHubAPIError(f"Not found: {path}")
        if response.status_code == 403:
            reset = response.headers.get("X-RateLimit-Remaining")
            if reset == "0":
                raise GitHubAPIError(
                    "GitHub API rate limit exceeded. Set GITHUB_TOKEN in .env to raise the limit."
                )
            raise GitHubAPIError(f"Access forbidden for {path} (private repo? invalid/missing token?)")
        if not response.ok:
            raise GitHubAPIError(f"GitHub API error {response.status_code} for {path}")
        return response

    def get_repo(self, owner, repo) -> dict:
        return self._get(f"/repos/{owner}/{repo}").json()

    def get_commits(self, owner, repo, author=None) -> list:
        commits = []
        page = 1
        params = {"per_page": 100}
        if author:
            params["author"] = author
        while page <= MAX_COMMIT_PAGES:
            data = self._get(
                f"/repos/{owner}/{repo}/commits",
                params={**params, "page": page},
            ).json()
            if not data:
                break
            commits.extend(data)
            page += 1
        else:
            print(f"Warning: commit history truncated at {MAX_COMMIT_PAGES * 100} commits")
        return commits

    def get_user(self, username) -> dict:
        return self._get(f"/users/{username}").json()

    def get_user_repos(self, username) -> list:
        repos = []
        page = 1
        while True:
            data = self._get(
                f"/users/{username}/repos",
                params={"per_page": 100, "page": page, "type": "owner"},
            ).json()
            if not data:
                break
            repos.extend(data)
            page += 1
        return repos

    def get_tree(self, owner, repo, branch) -> list:
        data = self._get(f"/repos/{owner}/{repo}/git/trees/{branch}", params={"recursive": 1}).json()
        if data.get("truncated"):
            print("Warning: file tree truncated by GitHub (repository too large to list fully)")
        return [entry for entry in data.get("tree", []) if entry.get("type") == "blob"]

    def get_file_content(self, owner, repo, path, branch) -> str:
        response = self._get(
            f"/repos/{owner}/{repo}/contents/{path}",
            headers={"Accept": "application/vnd.github.raw"},
            params={"ref": branch},
        )
        return response.text
