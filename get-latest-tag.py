from github import Github
import dotenv

dotenv.load()

gitToken = dotenv.get('GITHUB_TOKEN')
repo = dotenv.get('REPO_NAME')
tagFile = dotenv.get('LATEST_TAG_FILE')

print(repo)
print(tagFile)

# or using an access token
myGithub = Github(gitToken)

repo = myGithub.get_repo(repo)
releaseTag = repo.get_latest_release().tag_name

tagFile = open(tagFile, "w")
tagFile.write(releaseTag)
tagFile.close()

print(releaseTag)
