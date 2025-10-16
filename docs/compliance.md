# HIPAA Compliance and PHI Handling for healthcare-ml-system

This document defines mandatory policies, technical controls, and operational workflows to ensure HIPAA compliance for systems processing Protected Health Information (PHI). It also explains the rationale behind each requirement and maps it to code, CI/CD, and testing practices so compliance is continuously verifiable.

## Scope
- Applies to all code in this repository, its build artifacts, and operational environments where PHI may flow (training, inference, ETL, analytics, and logs).
- Covers developers, reviewers, CI/CD, and runtime operators.

## Key HIPAA Rules Addressed
- Privacy Rule: Limits uses/disclosures of PHI, requires minimum necessary access.
- Security Rule: Safeguards for confidentiality, integrity, and availability (administrative, physical, technical).
- Breach Notification Rule: Incident response and notification obligations.

Rationale: Mapping rules to concrete controls reduces ambiguity and ensures testability. Encoding these mappings in code and CI makes drift detectable early.

## Definitions
- PHI: Any individually identifiable health information in any form, including identifiers combined with health data. Examples: name, address, email, phone, MRN, account numbers, full dates, biometric identifiers, images with faces, and any combinations that can identify a person.
- De-identified data: Data processed under HIPAA Safe Harbor (18 identifiers removed) or expert determination; still treated as sensitive unless explicitly marked and verified.

Rationale: Clear definitions prevent accidental misclassification that leads to improper handling in code paths and logs.

## PHI Handling Workflow
1) Data Classification at Ingress
   - All incoming datasets must be labeled one of: PHI, Limited Dataset, De-identified, or Non-PHI in a dataset.yaml manifest stored alongside data and referenced in code.
   - Code must check classification before processing and select appropriate pipelines.
   - CI policy-as-code validates manifests and blocks merges if missing.
   Rationale: Early classification gates prevent PHI entering non-compliant paths.

2) Access Control (Least Privilege)
   - Enforce role-based access control (RBAC) via cloud IAM; separate roles for developer, reviewer, operator, and automated jobs.
   - Secrets and keys managed by a vault; no static credentials in code.
   - Data access tokens are short-lived; workload identity preferred.
   Rationale: Minimizes blast radius and audit scope; provable via IaC checks.

3) Encryption
   - In transit: TLS 1.2+ for all services; HSTS enabled; certificate pinning where applicable.
   - At rest: Storage encrypted with AES-256 using customer-managed keys (CMKs); key rotation at least annually; backups encrypted.
   - In memory: Avoid writing sensitive buffers to disk; zero sensitive memory where feasible.
   Rationale: Protects data confidentiality across surfaces; verifiable via config scans and integration tests.

4) Data Minimization and Pseudonymization
   - Use explicit field allow-lists; drop disallowed fields at boundaries.
   - Pseudonymize identifiers with salted HMACs for linkage without direct identity exposure; salts managed in vault.
   - Training/inference pipelines operate on pseudonymized IDs; re-identification only in controlled services.
   Rationale: Reduces PHI propagation; unit tests enforce field filtering.

5) Logging and Observability
   - No raw PHI in logs. Use structured logs with redaction middleware default-on.
   - Redaction rules: mask emails, phones, SSNs, MRNs, free text using regex and schema-aware filters.
   - Segregate security/audit logs from app logs; restrict access and retention.
   Rationale: Logs are high-risk exfil paths; automated redaction tests catch regressions.

6) Data Retention and Deletion
   - Dataset manifests specify retention windows; lifecycle policies auto-expire; backups respect the same policies.
   - Right-to-delete processes: deletion job keyed by pseudonymous ID; tombstones recorded in audit log.
   Rationale: Limits long-term exposure; deletion is provable through audit records.

7) Vendor and Transmission Controls
   - Business Associate Agreements (BAAs) required for all vendors handling PHI.
   - Data leaving the system is blocked unless destination is allow-listed and BAA-verified.
   Rationale: Ensures downstream HIPAA obligations are satisfied; enforced via egress policies and tests.

## Audit Logging Practices
- Audit Scope: access events (who, what resource, action, reason), data flows, config changes, model deployments, permission changes, key usage.
- Required Fields: timestamp (UTC, ISO 8601), actor (service or user), subject (resource ID), action, request_id, auth_context, outcome, hash of payload or record key (not PHI), source_ip, user_agent.
- Immutability: append-only logs shipped to WORM/SIEM with write-once retention and integrity verification (hash chaining or cloud-provided immutability).
- Separation of Duties: only compliance officers can read full audit logs; engineering sees metrics/alerts.
- Retention: minimum 6 years for HIPAA-relevant audit records.

Rationale: Forensics and compliance reviews require complete, tamper-evident histories; integrity is testable via periodic verification jobs.

## Compliance Verification Steps (Code and CI/CD)
- Policy-as-code: Use tools like OPA/Conftest to enforce:
  - No plaintext secrets; image scans pass; base images hardened.
  - All services declare data classification and logging redaction enabled.
  - Network egress only to allow-listed endpoints; TLS required.
  - Infrastructure resources (buckets, DBs) must have encryption and access policies.
- Unit Tests:
  - Redaction functions remove PHI tokens from representative payloads.
  - Field allow-lists drop disallowed identifiers.
  - Pseudonymization is deterministic with rotation support; collisions tested.
- Integration Tests:
  - End-to-end flow validates that PHI never appears in logs, metrics, or traces.
  - TLS enforced; reject plaintext connections.
  - Deletion requests propagate to storage and audits are written.
- Static Analysis:
  - Secrets scanners (e.g., trufflehog, gitleaks) gated in CI.
  - Custom linters forbid printing or logging sensitive fields and using insecure crypto.
- IaC Validation:
  - Terraform/Cloud templates checked for encryption, RBAC, key rotation, logging sinks, retention, and WORM.
- Change Management:
  - PR templates require data classification, threat model updates, and security review for PHI-touching changes.

Rationale: Automated gates create a measurable control plane; failure conditions block merges and deployments.

## Incident Response and Breach Handling
- Detection: alert on anomalous access patterns, failed redaction tests, or forbidden egress.
- Containment: revoke credentials/keys, isolate workloads, suspend nonessential data flows.
- Eradication/Recovery: patch vulnerabilities, rotate keys, validate data integrity, restore from clean backups.
- Notification: follow HIPAA timelines; coordinate with privacy officer and legal.
- Postmortem: root-cause analysis, control improvements, additional tests to prevent regression.

Rationale: A predefined, tested process reduces response time and regulatory risk; exercises scheduled at least annually.

## Developer Responsibilities
- Never commit sample PHI; use synthetic datasets.
- Run pre-commit hooks for secret scan and PHI-token detection.
- Use environment-specific configs; never reuse production credentials.
- Report incidents immediately via the security channel.

Rationale: Human factors are a common root cause; guardrails plus training reduce errors and make reviews objective.

## How These Controls Fit Into Code and Testing
- Code: modules expose Redactor, Classifier, Pseudonymizer interfaces; adapters wired via dependency injection so tests can stub.
- Tests: fixtures include PHI-like tokens and ensure redaction; golden files confirm no identifiers leak.
- CI: pipelines enforce policy gates, run scanners, and publish compliance reports as artifacts.
- CD: deployment requires passing compliance badge; runtime config validated on startup.

Rationale: Embedding compliance into developer workflows ensures continuous enforcement, not just documentation.

## Appendix: Safe Harbor Identifiers to Remove
1) Names
2) Geographic subdivisions smaller than a state (street, city, ZIP except first 3 digits in limited cases)
3) All elements of dates (except year) directly related to an individual
4) Phone/fax numbers
5) Email addresses
6) SSNs
7) MRNs and account numbers
8) Certificate/license numbers
9) Vehicle identifiers
10) Device identifiers and serial numbers
11) URLs
12) IP addresses
13) Biometric identifiers
14) Full face photos and comparable images
15) Any other unique identifying number, characteristic, or code

Rationale: Removing these prevents re-identification via direct identifiers; tests verify filters across these categories.
