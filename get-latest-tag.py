from github import Github
from os import getenv, path
from dotenv import load_dotenv

load_dotenv()

gitToken = getenv('GITHUB_TOKEN')
repo = getenv('REPO_NAME')
tagFile = getenv('LATEST_TAG_FILE')

print(repo)
print(tagFile)

# or using an access token
myGithub = Github(gitToken)

repo = myGithub.get_repo(repo)
releaseTag = repo.get_latest_release().tag_name
pr = repo.create_git_blob

print(pr)

tagFile = open(tagFile, "w")
tagFile.write(releaseTag)
tagFile.close()

print(releaseTag)
