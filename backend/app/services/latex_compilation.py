from collections.abc import Callable
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Resume, ResumeVersion, ResumeVersionStatus
from app.schemas.latex import LatexCompilationResponse


Runner = Callable[..., subprocess.CompletedProcess[str]]


class LatexCompilationService:
    def __init__(
        self,
        compiler: str = "pdflatex",
        timeout_seconds: int = 30,
        runner: Runner = subprocess.run,
    ) -> None:
        self.compiler = compiler
        self.timeout_seconds = timeout_seconds
        self.runner = runner

    def compile_version(
        self, session: Session, candidate_id: int, resume_id: int, version_id: int
    ) -> LatexCompilationResponse:
        version = session.scalar(
            select(ResumeVersion)
            .join(Resume)
            .where(
                Resume.id == resume_id,
                Resume.candidate_id == candidate_id,
                ResumeVersion.id == version_id,
            )
        )
        if version is None:
            raise LookupError(f"Resume version {version_id} was not found")
        if version.status not in {ResumeVersionStatus.PROPOSED, ResumeVersionStatus.APPROVED}:
            raise ValueError("Only proposed or approved resume versions can be compiled")

        with TemporaryDirectory(prefix="glassmate-latex-") as temporary_directory:
            work_dir = Path(temporary_directory)
            tex_path = work_dir / "resume.tex"
            pdf_path = work_dir / "resume.pdf"
            tex_path.write_text(version.tex_content, encoding="utf-8")
            command = self._command(tex_path, work_dir)
            try:
                result = self.runner(
                    command,
                    cwd=work_dir,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout_seconds,
                    check=False,
                )
            except FileNotFoundError:
                return LatexCompilationResponse(
                    version_id=version.id,
                    status="UNAVAILABLE",
                    pdf_filename=None,
                    pdf_size_bytes=None,
                    log="",
                    error=f"LaTeX compiler '{self.compiler}' was not found",
                )
            except subprocess.TimeoutExpired as error:
                return LatexCompilationResponse(
                    version_id=version.id,
                    status="FAILED",
                    pdf_filename=None,
                    pdf_size_bytes=None,
                    log=self._output(error.stdout, error.stderr),
                    error=f"LaTeX compilation exceeded {self.timeout_seconds} seconds",
                )

            log = self._output(result.stdout, result.stderr)
            if result.returncode != 0:
                return LatexCompilationResponse(
                    version_id=version.id,
                    status="FAILED",
                    pdf_filename=None,
                    pdf_size_bytes=None,
                    log=log,
                    error="LaTeX compilation failed",
                )
            if not pdf_path.is_file():
                return LatexCompilationResponse(
                    version_id=version.id,
                    status="FAILED",
                    pdf_filename=None,
                    pdf_size_bytes=None,
                    log=log,
                    error="LaTeX compiler exited successfully but produced no PDF",
                )
            return LatexCompilationResponse(
                version_id=version.id,
                status="SUCCESS",
                pdf_filename="resume.pdf",
                pdf_size_bytes=pdf_path.stat().st_size,
                log=log,
                error=None,
            )

    def _command(self, tex_path: Path, work_dir: Path) -> list[str]:
        return [
            self.compiler,
            "-no-shell-escape",
            "-interaction=nonstopmode",
            "-halt-on-error",
            "-file-line-error",
            "-output-directory",
            str(work_dir),
            tex_path.name,
        ]

    @staticmethod
    def _output(stdout: str | bytes | None, stderr: str | bytes | None) -> str:
        values = []
        for value in (stdout, stderr):
            if value:
                values.append(value.decode(errors="replace") if isinstance(value, bytes) else value)
        return "\n".join(values)[-12000:]