import os
import requests
import json
from dotenv import load_dotenv


def main():
    load_dotenv()
    access_token = os.getenv("ACCESS_TOKEN")
    username = "Jeremymcgahey"
    #  this is require for access to private files
    url = f"https://api.github.com/search/repositories?q=user:{username}"
    #  path will be .docker/build/Dockerfile
    path = "Dockerfile"

    #  grabs a list of all the items in repository
    request = requests.get(url, auth=(username, access_token))
    if not request.ok:
        print("Bad Response: Exiting.")
        return
    text = request.content
    git = json.loads(text)
    print(git)
    repos = git["items"]
    bad_repos = []

    #  using the repository names we grab the data from each and check the dockerfile
    for repo in repos:
        repo_name = repo["name"]
        print("Repository name:", repo_name)
        url = f"https://raw.githubusercontent.com/{username}/{repo_name}/main/{path}"
        request = requests.get(url, auth=(username, access_token))
        if not request.ok:
            print(f"File not found in: {url}")
            break
        text = request.text
        index = text.find("FROM composer") + 13  # end of FROM composer string + 1

        if text[index:index + 7] == ":latest":
            print("Version :latest")
            bad_repos.append(url)

        elif text[index:index + 1] == ":":
            print("Good repository")

        else:
            print("Bad repository")
            bad_repos.append(url)

    #  output for bad_repos as json
    print(json.dumps(bad_repos))


main()
