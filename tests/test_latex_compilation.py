from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.base import Base
from app.models import Candidate, Resume, ResumeVersion, ResumeVersionStatus
from app.services.latex_compilation import LatexCompilationService
import app.models.entities  # noqa: F401


@pytest.fixture
def database() -> Session:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def _resume(database: Session, status: ResumeVersionStatus) -> ResumeVersion:
    candidate = Candidate(full_name="Candidate")
    resume = Resume(name="General", candidate=candidate)
    version = ResumeVersion(status=status, version_number=1, tex_content="\\documentclass{article}")
    resume.versions = [version]
    database.add(candidate)
    database.commit()
    database.refresh(version)
    return version


def test_compilation_runs_in_temporary_directory_and_reports_pdf(database: Session) -> None:
    version = _resume(database, ResumeVersionStatus.PROPOSED)
    calls: list[tuple[list[str], Path]] = []

    def runner(command: list[str], cwd: Path, **_: object) -> object:
        calls.append((command, cwd))
        (cwd / "resume.pdf").write_bytes(b"pdf")
        return type("Result", (), {"returncode": 0, "stdout": "ok", "stderr": ""})()

    result = LatexCompilationService(runner=runner).compile_version(
        database, version.resume.candidate_id, version.resume_id, version.id
    )

    assert result.status == "SUCCESS"
    assert result.pdf_filename == "resume.pdf"
    assert result.pdf_size_bytes == 3
    assert "-no-shell-escape" in calls[0][0]
    assert calls[0][0][-1] == "resume.tex"
    assert not calls[0][1].exists()


def test_compilation_reports_missing_compiler(database: Session) -> None:
    version = _resume(database, ResumeVersionStatus.APPROVED)

    def missing_compiler(*_: object, **__: object) -> object:
        raise FileNotFoundError

    result = LatexCompilationService(runner=missing_compiler).compile_version(
        database, version.resume.candidate_id, version.resume_id, version.id
    )

    assert result.status == "UNAVAILABLE"
    assert result.pdf_filename is None


def test_rejected_versions_cannot_be_compiled(database: Session) -> None:
    version = _resume(database, ResumeVersionStatus.REJECTED)

    with pytest.raises(ValueError, match="Only proposed or approved"):
        LatexCompilationService().compile_version(
            database, version.resume.candidate_id, version.resume_id, version.id
        )