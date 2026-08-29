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