from github import Github
from environs import Env

env = Env()

env.read_env(".env",recurse=False,verbose=True)

gitToken = env('GITHUB_TOKEN')
repo = env('REPO_NAME')
tagFile = env('LATEST_TAG_FILE')

print(tagFile)
# or using an access token
myGithub = Github(gitToken)

repo = myGithub.get_repo(repo)
releaseTag = repo.get_latest_release().tag_name

tagFile = open(tagFile, "w")
tagFile.write(releaseTag)
tagFile.close()

print(releaseTag)
