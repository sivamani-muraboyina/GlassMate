import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.models import Candidate, Evidence, Project
from app.services.github import GitHubRepositoryClient, GitHubRepositoryError, RepositorySnapshot
from app.services.project_intelligence import ProjectIntelligenceService


class FakeGitHubClient:
    def __init__(self, snapshot: RepositorySnapshot) -> None:
        self.snapshot = snapshot
        self.fetch_count = 0

    def fetch(self, repository_url: str) -> RepositorySnapshot:
        self.fetch_count += 1
        return RepositorySnapshot(
            name=self.snapshot.name,
            repository_url=repository_url,
            readme=self.snapshot.readme,
            top_level_paths=self.snapshot.top_level_paths,
            technologies=self.snapshot.technologies,
        )


@pytest.fixture
def database() -> Session:
    engine = create_engine("sqlite://")
    import app.models.entities  # noqa: F401

    from app.db.base import Base

    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_project_import_persists_evidence_and_reuses_unchanged_snapshot(database: Session) -> None:
    candidate = Candidate(full_name="Test Candidate")
    database.add(candidate)
    database.commit()
    database.refresh(candidate)
    fake_client = FakeGitHubClient(
        RepositorySnapshot(
            name="glassmate-demo",
            repository_url="",
            readme="# GlassMate Demo\n\nA job assistant.",
            top_level_paths=("backend", "README.md", ".gitignore"),
            technologies=("Python",),
        )
    )
    service = ProjectIntelligenceService(fake_client)

    project, refreshed = service.import_project(
        database, candidate.id, "https://github.com/example/glassmate-demo"
    )
    unchanged_project, refreshed_again = service.import_project(
        database, candidate.id, "https://github.com/example/glassmate-demo"
    )

    assert refreshed is True
    assert refreshed_again is False
    assert project.id == unchanged_project.id
    assert project.purpose == "A job assistant."
    assert project.technologies == ["Python"]
    assert project.candidate_contribution is None
    assert database.query(Evidence).count() == 1
    assert database.query(Project).count() == 1
    assert fake_client.fetch_count == 2


def test_project_import_requires_existing_candidate(database: Session) -> None:
    service = ProjectIntelligenceService(FakeGitHubClient(RepositorySnapshot("demo", "", None, (), ())))

    with pytest.raises(LookupError):
        service.import_project(database, 999, "https://github.com/example/demo")


def test_github_client_rejects_non_github_urls() -> None:
    with pytest.raises(GitHubRepositoryError):
        GitHubRepositoryClient._parse_repository_url("https://example.com/demo")
