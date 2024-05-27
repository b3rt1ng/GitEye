import src.metadata as md
import src.table as table
import src.file_analyzer as analyzer
import argparse, re

parser = argparse.ArgumentParser(description="Analyze a git repository")
parser.add_argument("-p", "--path", help="Path to the git repository", type=str, required=True)
parser.add_argument("-d", "--detailed", help="Enable detailed analysis", action="store_true", default=False)

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

# Define regex patterns
web_link_pattern = re.compile(r'^(https?://[^\s]+)$')
# directory_link_pattern = re.compile(r'(?:\/(?:[\w.-]+\/)*[\w.-]+)')


def main():
    import src.banner

    git_path = parser.parse_args().path
    detailed = parser.parse_args().detailed

    if web_link_pattern.match(git_path):
        import src.downloader as downloader
        path = downloader.download(git_path)
        print(f"{color['yellow']}Repository downloaded successfully{color['reset']}")
        metadata = md.Metadata(path, detailed=detailed)

    else:
        metadata = md.Metadata(git_path, detailed=detailed)



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

    fa = analyzer.FileAnalyzer(metadata.path)
    fa.list_files()
    try: 
        interesting_files = fa.file_of_interest()
        print(f"Found {color['green']}{len(interesting_files)}{color['reset']} interesting files")
        if len(interesting_files) > 0:
            table.show_table([interesting_files], ["File"], "Interesting files")
    except:
        print("No interesting files found")

    try:
        keywords, files, line_numbers, lines = zip(*fa.analyse(interesting_files))
        table.show_table([keywords, files, line_numbers, lines], ["Keyword", "File", "Line number", "Line"], "Analysis")
    except:
        print("Analysis found nothing interesting")
    

main()
