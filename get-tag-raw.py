import requests
from requests.exceptions import HTTPError
import json
import dotenv

dotenv.load()

gitToken = dotenv.get('GITHUB_TOKEN')
repo = dotenv.get('REPO_NAME')
tagFile = dotenv.get('LATEST_TAG_FILE')

rootUrl = "https://api.github.com"

url = rootUrl + "/repos/" + repo + "/pulls?base=masters&state=open"
payload = ""
headers = {'authorization': 'token ' + gitToken}


def get_pull_request():
    _url = rootUrl + "/repos/" + repo + "/pulls?base=master&state=open"
    _response = requests.get(_url, data=payload, headers=headers)
    _response.raise_for_status()
    return _response.json()


def latest_tag():
    _url = rootUrl + "/repos/" + repo + "/releases/latest"
    _response = requests.get(_url, data=payload, headers=headers)
    _response.raise_for_status()
    return _response.json()


print(url)
try:
    try:
        jsonResponse = get_pull_request()
        tagArr = (jsonResponse[0]['title']).split()
        tag = tagArr[len(tagArr) - 1]
    except (IndexError, KeyError, TypeError) as err:
        print(f'Index error has occurred: {err}')
        jsonResponse = latest_tag()
        tag = jsonResponse['tag_name']

    tagFile = open(tagFile, "w")
    tagFile.write(tag)
    tagFile.close()
    print(f'Tag created: {tag}')
except HTTPError as http_err:
    print(f'HTTP error occurred: {http_err}')
except Exception as err:
    print(f'Other error occurred: {err}')
