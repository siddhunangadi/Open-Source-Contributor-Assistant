import os
import requests
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}


class GitHubService:

    BASE_URL = "https://api.github.com"

    @staticmethod
    def search_repositories(query: str, per_page: int = 10):
        url = f"{GitHubService.BASE_URL}/search/repositories"

        params = {
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": per_page
        }

        response = requests.get(
            url,
            headers=HEADERS,
            params=params
        )

        response.raise_for_status()

        return response.json()

    @staticmethod
    def get_repository(owner: str, repo: str):
        url = f"{GitHubService.BASE_URL}/repos/{owner}/{repo}"

        response = requests.get(
            url,
            headers=HEADERS
        )

        response.raise_for_status()

        return response.json()

    @staticmethod
    def get_issues(
        owner: str,
        repo: str,
        state: str = "open",
        per_page: int = 20
    ):
        url = f"{GitHubService.BASE_URL}/repos/{owner}/{repo}/issues"

        params = {
            "state": state,
            "per_page": per_page
        }

        response = requests.get(
            url,
            headers=HEADERS,
            params=params
        )

        response.raise_for_status()

        return response.json()

    @staticmethod
    def get_issue(
        owner: str,
        repo: str,
        issue_number: int
    ):
        url = (
            f"{GitHubService.BASE_URL}/repos/"
            f"{owner}/{repo}/issues/{issue_number}"
        )

        response = requests.get(
            url,
            headers=HEADERS
        )

        response.raise_for_status()

        return response.json()

    @staticmethod
    def get_readme(
        owner: str,
        repo: str
    ):
        url = (
            f"{GitHubService.BASE_URL}/repos/"
            f"{owner}/{repo}/readme"
        )

        response = requests.get(
            url,
            headers=HEADERS
        )

        response.raise_for_status()

        return response.json()

    @staticmethod
    def get_file_contents(
        owner: str,
        repo: str,
        path: str
    ):
        url = (
            f"{GitHubService.BASE_URL}/repos/"
            f"{owner}/{repo}/contents/{path}"
        )

        response = requests.get(
            url,
            headers=HEADERS
        )

        response.raise_for_status()

        return response.json()

    @staticmethod
    def get_repository_tree(
        owner: str,
        repo: str,
        branch: str = "main"
    ):
        """
        Fetch the full recursive file tree of a repository branch.
        Falls back to 'master' if 'main' returns 404.
        """
        for ref in (branch, "master", "HEAD"):
            url = (
                f"{GitHubService.BASE_URL}/repos/"
                f"{owner}/{repo}/git/trees/{ref}"
            )
            response = requests.get(
                url,
                headers=HEADERS,
                params={"recursive": "1"}
            )
            if response.status_code == 200:
                data = response.json()
                # Return only blob (file) paths, not trees
                files = [
                    item["path"]
                    for item in data.get("tree", [])
                    if item.get("type") == "blob"
                ]
                return {
                    "ref": ref,
                    "truncated": data.get("truncated", False),
                    "files": files,
                    "total_files": len(files),
                }
        response.raise_for_status()
        return {}

    @staticmethod
    def search_code(
        owner: str,
        repo: str,
        query: str,
        per_page: int = 20,
    ):
        """
        Search for exact identifiers inside a repository using GitHub code search.
        Ideal for finding class/function definitions by name.
        """
        url = f"{GitHubService.BASE_URL}/search/code"
        params = {
            "q": f"{query} repo:{owner}/{repo}",
            "per_page": per_page,
        }
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        items = response.json().get("items", [])
        return [
            {
                "path": item["path"],
                "html_url": item["html_url"],
                "repository": item.get("repository", {}).get("full_name", ""),
            }
            for item in items
        ]