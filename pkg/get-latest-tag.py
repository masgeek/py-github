from os import environ
from dotenv import load_dotenv
from github import Github

load_dotenv(verbose=True)

if 'GITHUB_TOKEN' in environ:
    gitToken = (environ.get('GITHUB_TOKEN'))
else:
    gitToken = ""

if 'REPO_NAME' in environ:
    repo = (environ.get('REPO_NAME'))
else:
    repo = "masgeek/akilimo-mobile"

# or using an access token
myGithub = Github(gitToken)

repo = myGithub.get_repo(repo)
releaseTag = repo.get_latest_release().tag_name

tagFile = open("latest_tag.txt", "w")
tagFile.write(releaseTag)
tagFile.close()

print(releaseTag)
