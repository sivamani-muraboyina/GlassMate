from dataclasses import dataclass
import base64
import hashlib
import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


class GitHubRepositoryError(Exception):
    pass


@dataclass(frozen=True)
class RepositorySnapshot:
    name: str
    repository_url: str
    readme: str | None
    top_level_paths: tuple[str, ...]
    technologies: tuple[str, ...]

    @property
    def content_hash(self) -> str:
        payload = json.dumps(
            {
                "readme": self.readme,
                "top_level_paths": self.top_level_paths,
                "technologies": self.technologies,
            },
            sort_keys=True,
        ).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()


class GitHubRepositoryClient:
    def __init__(self, token: str | None = None) -> None:
        self.token = token

    def fetch(self, repository_url: str) -> RepositorySnapshot:
        owner, repository = self._parse_repository_url(repository_url)
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "GlassMate"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        metadata = self._get_json(f"https://api.github.com/repos/{owner}/{repository}", headers)
        contents = self._get_json(f"https://api.github.com/repos/{owner}/{repository}/contents", headers)
        readme_payload = self._get_json(
            f"https://api.github.com/repos/{owner}/{repository}/readme", headers, allow_not_found=True
        )
        readme = self._decode_readme(readme_payload)
        paths = tuple(item["name"] for item in contents if isinstance(item, dict) and "name" in item)
        languages = self._get_json(
            f"https://api.github.com/repos/{owner}/{repository}/languages", headers, allow_not_found=True
        )
        technologies = tuple(languages.keys()) if isinstance(languages, dict) else ()
        return RepositorySnapshot(
            name=metadata.get("name", repository),
            repository_url=repository_url,
            readme=readme,
            top_level_paths=paths,
            technologies=technologies,
        )

    @staticmethod
    def _parse_repository_url(repository_url: str) -> tuple[str, str]:
        parsed = urlparse(repository_url)
        if parsed.netloc.lower() != "github.com":
            raise GitHubRepositoryError("repository_url must point to github.com")
        parts = [part for part in parsed.path.split("/") if part]
        if len(parts) < 2:
            raise GitHubRepositoryError("repository_url must include an owner and repository")
        return parts[0], parts[1].removesuffix(".git")

    @staticmethod
    def _decode_readme(payload: object) -> str | None:
        if not isinstance(payload, dict) or payload.get("encoding") != "base64":
            return None
        content = payload.get("content")
        if not isinstance(content, str):
            return None
        return base64.b64decode(content).decode("utf-8", errors="replace")

    @staticmethod
    def _get_json(url: str, headers: dict[str, str], allow_not_found: bool = False) -> object:
        try:
            with urlopen(Request(url, headers=headers), timeout=15) as response:
                return json.load(response)
        except HTTPError as error:
            if allow_not_found and error.code == 404:
                return None
            raise GitHubRepositoryError(f"GitHub request failed with status {error.code}") from error
        except (URLError, TimeoutError, json.JSONDecodeError) as error:
            raise GitHubRepositoryError("GitHub request could not be completed") from error
