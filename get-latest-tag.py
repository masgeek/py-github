from os import environ
from github import Github
from environs import Env

env = Env()

if 'GITHUB_TOKEN' in environ:
    gitToken = (environ.get('GITHUB_TOKEN'))
else:
    gitToken = ""

if 'REPO_NAME' in environ:
    repo = (environ.get('REPO_NAME'))
else:
    repo = "masgeek/akilimo-mobile"

if 'LATEST_TAG_FILE' in environ:
    tagFile = (environ.get('LATEST_TAG_FILE'))
else:
    tagFile = "latest_tag.txt"

print(tagFile)
# or using an access token
myGithub = Github(gitToken)

repo = myGithub.get_repo(repo)
releaseTag = repo.get_latest_release().tag_name

tagFile = open(tagFile, "w")
tagFile.write(releaseTag)
tagFile.close()

print(releaseTag)
