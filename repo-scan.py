import sys
import os
import requests
import json
import cli.app
from dotenv import load_dotenv


@cli.app.CommandLineApp
def repo_scan(app):
    verbose = repo_scan.params.verbose
    path = repo_scan.params.path

    load_dotenv()
    access_token = os.getenv("ACCESS_TOKEN")
    username = os.getenv("USER")

    url = f"https://api.github.com/search/repositories?q=user:{username}"

    #  grabs a list of all the items in repository
    request = requests.get(url, auth=(username, access_token))
    if not request.ok:
        if verbose:
            print("Bad Response: Exiting.")
        return
    text = request.content
    git = json.loads(text)
    repos = git["items"]
    bad_repos = []

    #  using the repository names we grab the data from each and check the dockerfile
    for repo in repos:
        repo_name = repo["name"]
        if verbose:
            print("Repository name:", repo_name)
        url = f"https://raw.githubusercontent.com/{username}/{repo_name}/main/{path}"
        request = requests.get(url, auth=(username, access_token))
        if not request.ok:
            if verbose:
                print(f"File not found in: {url}")
            continue
        text = request.text
        index = text.find("FROM composer") + 13  # end of FROM composer string + 1

        if text[index:index + 7] == ":latest":
            if verbose:
                print("Version :latest")
            bad_repos.append(url)

        elif text[index:index + 1] == ":":
            if verbose:
                print("Good repository")

        else:
            if verbose:
                print("Bad repository")
            bad_repos.append(url)

    #  output for bad_repos as json
    sys.stdout.write(json.dumps(bad_repos))


repo_scan.add_param("-v", "--verbose", help="enables print statements", default=False, action="store_true")
repo_scan.add_param("-p", "--path", help="sets the repo path", default=".docker/build/Dockerfile", type=str)

if __name__ == "__main__":
    repo_scan.run()
