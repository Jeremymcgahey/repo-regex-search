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
    git = json.loads(text)
    return git["items"], git["total_count"]


@cli.app.CommandLineApp
def repo_scan(app):
    verbose = app.params.verbose
    path = app.params.path
    search = app.params.search
    branch = app.params.branch

    def debug(*args):
        if verbose:
            print(args)

    load_dotenv()
    access_token = os.getenv("GIT_ACCESS_TOKEN")
    username = os.getenv("GIT_USERNAME")

    page = 1
    bad_repos = []
    good_repos = []

    repos = fetch_repo(page, username, access_token, verbose)
    remaining = repos[1] // 100 + 1
    debug(f"Total items: {repos[1]}")

    while 0 < remaining:
        debug(f"Pages remaining: {remaining}")

        repos = fetch_repo(page, username, access_token, verbose)[0]
        #  using the repo names we grab the data from each and check against regex
        for repo in repos:
            repo_name = repo["name"]
            debug("Repository name:", repo_name)

            url = f"https://raw.githubusercontent.com/{username}/{repo_name}/{branch}/{path}"
            request = requests.get(url, auth=(username, access_token))
            if not request.ok:
                debug(f"File not found in: {url}")
                continue

            pattern = re.compile(search)
            match = pattern.search(request.text)
            if match is None:
                debug("Bad repository")
                bad_repos.append(url)

            else:
                debug("Good repository")
                good_repos.append(url)

        remaining -= 1
        page += 1

    #  output repos as json
    if app.params.good_case:
        sys.stdout.write(json.dumps(good_repos))
    else:
        sys.stdout.write(json.dumps(bad_repos))


#  defining all of the cli parameters
repo_scan.add_param("-v", "--verbose", help="enables print statements", default=False, action="store_true")
repo_scan.add_param("-gc", "--good_case", help="show matched repos", default=False, action="store_true")
repo_scan.add_param("-p", "--path", help="sets the file path to scan", default=".docker/build/Dockerfile", type=str)
repo_scan.add_param("-s", "--search", help="regex string to match", default=r"FROM composer\:[0-9\.]+", type=str)
repo_scan.add_param("-b", "--branch", help="set the repository branch", default="master", type=str)

if __name__ == "__main__":
    repo_scan.run()
