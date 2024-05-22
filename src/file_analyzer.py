import os
import json
import re

class FileAnalyzer:
    def __init__(self, directory):
        self.directory = directory
        self.files_list = []
        with open('interest.json') as f:
            config = json.load(f)
        self.keywords = config['keywords']
        self.files_extentions = config['files_extentions']



    def list_files(self) -> list:
        for root, dirs, files in os.walk(self.directory):
            if '.git' in dirs:
                dirs.remove('.git')  # Ignorer le sous-répertoire .git
            if '.github' in dirs:
                dirs.remove('.github')
            for file in files:
                self.files_list.append(os.path.join(root, file))
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
                with open(file) as f:
                    lines = f.readlines()
                    for line_num, line in enumerate(lines, start=1):
                        for keyword in self.keywords:
                            pattern = re.compile(keyword, re.IGNORECASE)
                            if re.search(pattern, line):
                                report.append((keyword, file, str(line_num), line.replace('\n', '')))    
                                break
        return report
