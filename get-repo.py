import os
from github import Github

gitToken = (os.environ['GITHUB_TOKEN'])

# or using an access token
myGithub = Github(gitToken)

repo = myGithub.get_repo("masgeek/akilimo-mobile")
releaseTag = repo.get_latest_release().tag_name

print(releaseTag)

tagFile = open("latest_tag.txt", "w")
tagFile.write(releaseTag)
tagFile.close()
