import json
import re


class FileAnalyzer:
    def __init__(self, client, owner, repo, branch):
        self.client = client
        self.owner = owner
        self.repo = repo
        self.branch = branch
        self.files_list = []
        with open('interest.json') as f:
            config = json.load(f)
        self.keywords = config['keywords']
        self.files_extentions = config['files_extentions']

    def list_files(self) -> list:
        self.files_list = [entry["path"] for entry in self.client.get_tree(self.owner, self.repo, self.branch)]
        return self.files_list

    def file_of_interest(self) -> list:
        files_of_interest = []
        for file in self.files_list:
            if file.endswith(tuple(self.files_extentions)):
                files_of_interest.append(file)
        return files_of_interest

    def analyse(self, files_list) -> list:
        "search for keywords in files"
        report = []
        for file in files_list:
            if file.endswith(tuple(self.files_extentions)):
                content = self.client.get_file_content(self.owner, self.repo, file, self.branch)
                lines = content.splitlines()
                for line_num, line in enumerate(lines, start=1):
                    for keyword in self.keywords:
                        pattern = re.compile(keyword, re.IGNORECASE)
                        if re.search(pattern, line):
                            report.append((keyword, file, str(line_num), line.replace('\n', '')))
                            break
        return report
