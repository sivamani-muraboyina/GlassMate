from sqlalchemy.orm import Session

from app.models import Candidate, Evidence, EvidenceStatus, Project, ProjectEvidence
from app.services.github import GitHubRepositoryClient, RepositorySnapshot


class ProjectIntelligenceService:
    def __init__(self, client: GitHubRepositoryClient | None = None) -> None:
        self.client = client or GitHubRepositoryClient()

    def import_project(self, session: Session, candidate_id: int, repository_url: str) -> tuple[Project, bool]:
        if session.get(Candidate, candidate_id) is None:
            raise LookupError(f"Candidate {candidate_id} was not found")
        snapshot = self.client.fetch(repository_url)
        existing = (
            session.query(Project)
            .filter(Project.candidate_id == candidate_id, Project.repository_url == repository_url)
            .one_or_none()
        )
        if existing is not None and existing.content_hash == snapshot.content_hash:
            return existing, False

        project = existing or Project(candidate_id=candidate_id, repository_url=repository_url)
        project.name = snapshot.name
        project.purpose = self._purpose_from_readme(snapshot.readme)
        project.technologies = list(snapshot.technologies)
        project.architecture_summary = self._architecture_from_paths(snapshot.top_level_paths)
        project.candidate_contribution = None
        project.content_hash = snapshot.content_hash
        if existing is None:
            session.add(project)
            session.flush()

        evidence = Evidence(
            source_type="github_repository",
            source_uri=repository_url,
            content=self._evidence_content(snapshot),
            status=EvidenceStatus.VERIFIED,
        )
        session.add(evidence)
        session.flush()
        session.add(ProjectEvidence(project_id=project.id, evidence_id=evidence.id))
        session.commit()
        session.refresh(project)
        return project, True

    @staticmethod
    def _purpose_from_readme(readme: str | None) -> str | None:
        if not readme:
            return None
        paragraphs = [part.strip() for part in readme.split("\n\n") if part.strip()]
        for paragraph in paragraphs:
            if not paragraph.startswith("#"):
                return " ".join(paragraph.split())[:500]
        return None

    @staticmethod
    def _architecture_from_paths(paths: tuple[str, ...]) -> str | None:
        if not paths:
            return None
        visible_paths = [path for path in paths if not path.startswith(".")]
        if not visible_paths:
            return None
        return "Top-level repository entries: " + ", ".join(sorted(visible_paths))

    @staticmethod
    def _evidence_content(snapshot: RepositorySnapshot) -> str:
        return (
            f"Repository: {snapshot.name}\n"
            f"Technologies: {', '.join(snapshot.technologies) or 'UNKNOWN'}\n"
            f"Top-level entries: {', '.join(snapshot.top_level_paths) or 'UNKNOWN'}\n"
            f"README:\n{snapshot.readme or 'UNKNOWN'}"
        )
