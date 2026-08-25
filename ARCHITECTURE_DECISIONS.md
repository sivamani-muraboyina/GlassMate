# GlassMate Architecture Decisions

1. Project Name
   GlassMate

2. Frontend/API
   React → FastAPI → Services/Orchestrator

3. Orchestrator
   Deterministic Python workflow

4. Agent Execution
   Synchronous for interactive workflows,
   background for discovery/monitoring

5. Calendar
   Integration/service, not an agent

6. MCP
   Selective agent-facing/external tool interface

7. Database
   PostgreSQL with candidate, evidence, jobs,
   matching, resumes, applications and agent runs

8. Claims/Evidence
   Explicit Claim → Evidence relationship

9. Unknown Handling
   NULL ≠ UNKNOWN ≠ NOT_SUPPORTED

10. Matching
    Simple deterministic score used for workflow routing

11. Job Sources
    Source adapter architecture; platform-compliant access

12. OAuth
    Minimal OAuth for required integrations

13. Application Modes
    PREPARE / APPROVAL_REQUIRED / AUTO_APPLY

14. Company Information
    VERIFIED / INFERRED / UNKNOWN

15. Critic
    Independent validation, max 3 revisions

16. Candidate Contribution
    GitHub does not automatically prove authorship

17. LaTeX
    Sandboxed deterministic compilation

18. External Actions
    Authorization + idempotency

19. Deduplication
    Job fingerprint + GitHub content hash

20. Phase Order
    Interfaces first, integrations later

21. Git
    Phase-based commits

22. README
    Update after architecture is finalized

last plot
Resolve the five documentation inconsistencies you identified using
the following decisions.

Do NOT implement application code.

Do NOT change the architecture.

Do NOT create new agents or services.

1. PROJECT NAME

GlassMate is the canonical project name.

Any old JOBPILOT references should be treated as outdated.

2. APPLICATION MODES

The canonical application modes are:

PREPARE
APPROVAL_REQUIRED
AUTO_APPLY

PREPARE:
GlassMate prepares the application but the user performs the final
application manually.

APPROVAL_REQUIRED:
GlassMate prepares the application, runs the Critic, then requires
explicit user approval before performing the external action.

AUTO_APPLY:
The user has explicitly enabled automatic application and the target
application mechanism supports compliant automation.

The old AUTO / SUGGEST / MANUAL terminology is obsolete.

3. PHASE ORDER

There is no requirement to move the database or feature phases later.

"Interfaces first, integrations later" means that agent/tool/service
interfaces should be designed cleanly before implementing external
integrations.

Keep the practical development order in DEVELOPMENT.md.

Do not introduce unnecessary infrastructure.

4. README

Change the Architecture status from:

"Coming soon"

to something indicating that the architecture is defined in:

ARCHITECTURE_DECISIONS.md

5. MATCH SCORE

Use a simple deterministic score.

Requirement states:

SUPPORTED = 1.0
PARTIALLY_SUPPORTED = 0.5
NOT_SUPPORTED = 0
UNKNOWN = excluded from the denominator

Requirement weights:

REQUIRED = 2
PREFERRED = 1

The score is used for workflow routing and job selection.

It is NOT a probability of getting hired.

Do not introduce ML ranking or a complicated scoring model.

After making these documentation-only changes:

1. Show me the files changed.
2. Show me the final relevant sections.
3. Do not implement any application code.
4. Do not start Phase 0.