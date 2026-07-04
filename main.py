import os
import argparse

from dotenv import load_dotenv

import src.metadata as md
import src.table as table
import src.file_analyzer as analyzer
import src.user_trace as user_trace
from src.github_api import GitHubClient, GitHubAPIError

parser = argparse.ArgumentParser(description="Analyze a GitHub repository or trace a user's commit identities")
target = parser.add_mutually_exclusive_group(required=True)
target.add_argument("-u", "--url", help="URL of the GitHub repository, e.g. https://github.com/user/project", type=str)
target.add_argument("--username", help="GitHub username: scan their public repos for commit name/email traces", type=str)
parser.add_argument("-d", "--detailed", help="Enable detailed analysis", action="store_true", default=False)
parser.add_argument(
    "--help-me-fix",
    help="With --username: print git filter-repo commands to scrub exposed emails from each affected repo. "
         "Optionally pass 'ssh' to generate SSH remote URLs instead of HTTPS (default: https)",
    nargs="?", const="https", choices=["https", "ssh"], default=None,
)

color = {
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "magenta": "\033[95m",
    "cyan": "\033[96m",
    "white": "\033[97m",
    "reset": "\033[0m"
}


def main():
    import src.banner

    load_dotenv()
    token = os.environ.get("GITHUB_TOKEN")

    args = parser.parse_args()
    detailed = args.detailed

    client = GitHubClient(token)

    if args.username:
        trace_user(client, args.username, detailed, args.help_me_fix)
        return

    url = args.url

    try:
        metadata = md.Metadata(client, url, detailed=detailed)
    except GitHubAPIError as e:
        print(f"{color['red']}Error: {e}{color['reset']}")
        return

    print(f"Analyzing {color['green']}{metadata.repo_name}{color['reset']}'s repository by {color['green']}@{metadata.author}{color['reset']}")
    print(f"Total commits: {color['green']}{metadata.commit_count}{color['reset']}")

    print(f"First commit: {color['green']}{metadata.first_commit_date}{color['reset']}")
    print(f"Last commit: {color['green']}{metadata.last_commit_date}{color['reset']}")

    commits_counts = []
    for name in set(metadata.names):
        commits_counts.append(str(metadata.names.count(name)))
    table.show_table([metadata.names, metadata.mails, commits_counts], ["Name", "Mail / user ID", "commits number"], "Authors")

    dates, messages = zip(*metadata.all_commits)
    table.show_table([dates, messages], ["Date", "Message"], f"Commits{' (shorten)' if not detailed else ''}")

    if not token:
        print(f"{color['yellow']}No GITHUB_TOKEN in .env - skipping file/secret scan; metadata-only mode{color['reset']}")
        return

    try:
        fa = analyzer.FileAnalyzer(client, metadata.owner, metadata.repo, metadata.branch)
        fa.list_files()
        interesting_files = fa.file_of_interest()
        print(f"Found {color['green']}{len(interesting_files)}{color['reset']} interesting files")
        if len(interesting_files) > 0:
            table.show_table([interesting_files], ["File"], "Interesting files")

        analysis = fa.analyse(interesting_files)
        if analysis:
            keywords, files, line_numbers, lines = zip(*analysis)
            table.show_table([keywords, files, line_numbers, lines], ["Keyword", "File", "Line number", "Line"], "Analysis")
        else:
            print("Analysis found nothing interesting")
    except GitHubAPIError as e:
        print(f"{color['red']}Error during file scan: {e}{color['reset']}")


def trace_user(client, username, detailed, help_me_fix):
    try:
        trace = user_trace.UserTrace(client, username)
    except GitHubAPIError as e:
        print(f"{color['red']}Error: {e}{color['reset']}")
        return

    print(f"Scanning {color['green']}{trace.repo_count}{color['reset']} non-fork public repositories owned by {color['green']}@{username}{color['reset']}")

    if not trace.identities:
        print("No commits authored by this username were found in their own repositories")
        return

    identities = trace.identities
    names, mails, counts, repos = zip(*identities)
    table.show_table([names, mails, counts, repos], ["Name", "Mail", "Commits found", "Repos"], f"Identities used by @{username}", redundancy=True)

    if detailed:
        repos_col, names_col, mails_col, dates_col = zip(*trace.traces)
        table.show_table([repos_col, names_col, mails_col, dates_col], ["Repo", "Name", "Mail", "Date"], "All traces", redundancy=True)

    exposed = trace.exposed_identities
    if not exposed:
        print(f"{color['green']}No exposed (non-anonymized) email addresses found{color['reset']}")
        return

    print(f"\n{color['red']}Exposed (non-anonymized) email addresses found:{color['reset']}")
    e_names, e_mails, e_counts, e_repos = zip(*[(n, e, str(c), ", ".join(sorted(r))) for n, e, c, r in exposed])
    table.show_table([e_names, e_mails, e_counts, e_repos], ["Name", "Mail", "Commits found", "Repos"], "Exposed identities", redundancy=True)

    if not help_me_fix:
        return
    print_fix_commands(client, username, exposed, protocol=help_me_fix)


def print_fix_commands(client, username, exposed, protocol="https"):
    try:
        user_id = client.get_user(username)["id"]
        safe_email = f"{user_id}+{username}@users.noreply.github.com"
    except GitHubAPIError:
        safe_email = f"{username}@users.noreply.github.com"

    def remote_url(repo):
        if protocol == "ssh":
            return f"git@github.com:{username}/{repo}.git"
        return f"https://github.com/{username}/{repo}.git"

    affected_repos = {}
    for _, email, _, repos in exposed:
        for repo in repos:
            affected_repos.setdefault(repo, set()).add(email)

    print(f"\n{color['yellow']}Fix commands ({color['reset']}run these to scrub the exposed addresses from history{color['yellow']}):{color['reset']}")
    print(f"{color['cyan']}# 0. git-filter-repo is a separate tool, not a built-in git command{color['reset']}")
    print("pip install git-filter-repo   # or: brew install git-filter-repo / apt install git-filter-repo\n")

    print(f"{color['cyan']}# 1. Stop leaking your real email going forward{color['reset']}")
    print(f"git config --global user.email \"{safe_email}\"")
    print("# also enable on GitHub: Settings > Emails > \"Block command line pushes that expose my email address\"\n")

    print(f"{color['cyan']}# 2. Rewrite history in each affected repo, then force-push{color['reset']}")
    for repo, emails in affected_repos.items():
        emails_literal = "{" + ", ".join(f'b"{email}"' for email in sorted(emails)) + "}"
        print(f"\n{color['magenta']}# {repo}{color['reset']}")
        print(f"git clone --bare {remote_url(repo)}")
        print(f"cd {repo}.git")
        print(f"git filter-repo --force --email-callback 'return b\"{safe_email}\" if email in {emails_literal} else email'")
        print(f"git push --force --mirror {remote_url(repo)}")
        print("cd ..")

    print(f"\n{color['red']}Note:{color['reset']} rewriting history changes commit SHAs. Existing forks/clones/PRs still")
    print("carry the old (exposed) commits, and services like GH Archive may already have a permanent copy.")


main()
