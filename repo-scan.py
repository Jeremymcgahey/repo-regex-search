import re
import sys
import os
import requests
import json
import cli.app
from dotenv import load_dotenv


def fetch_repo(page, username, access_token, verbose):
    url = f"https://api.github.com/search/repositories?q=user:{username}&per_page=100&page={page}"

    #  grabs a list of all the items in repository
    request = requests.get(url, auth=(username, access_token))
    if not request.ok:
        if verbose:
            print("Bad Response: ", request.status_code, " received")
        return
    text = request.content
    print(text)
    git = json.loads(text)
    print(type(git["items"]))
    return git["items"]


@cli.app.CommandLineApp
def repo_scan(app):
    verbose = app.params.verbose
    path = app.params.path
    search = app.params.search

    load_dotenv()
    access_token = os.getenv("ACCESS_TOKEN")
    username = os.getenv("GIT_USERNAME")
    page = 1

    repos = fetch_repo(page, username, access_token, verbose)

    bad_repos = []
    good_repos = []

    #  using the repository names we grab the data from each and check the dockerfile
    for repo in repos:
        repo_name = repo["name"]
        if verbose:
            print("Repository name:", repo_name)
        url = f"https://raw.githubusercontent.com/{username}/{repo_name}/master/{path}"
        request = requests.get(url, auth=(username, access_token))
        if not request.ok:
            if verbose:
                print(f"File not found in: {url}")
            continue

        pattern = re.compile(search)
        match = pattern.search(request.text)
        if match is None:
            if verbose:
                print("Bad repository")
            bad_repos.append(url)

        else:
            if verbose:
                print("Good repository")
            good_repos.append(url)

    #  output repos as json
    if app.params.good_case:
        sys.stdout.write(json.dumps(good_repos))
    else:
        sys.stdout.write(json.dumps(bad_repos))


repo_scan.add_param("-v", "--verbose", help="enables print statements", default=False, action="store_true")
repo_scan.add_param("-p", "--path", help="sets the repo path", default=".docker/build/Dockerfile", type=str)
repo_scan.add_param("-s", "--search", help="regex raw string to search", default=r"FROM composer\:[0-9\.]+", type=str)
repo_scan.add_param("-gc", "--good_case", help="enables good cases", default=False, action="store_true")

if __name__ == "__main__":
    repo_scan.run()
