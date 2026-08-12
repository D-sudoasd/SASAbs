# Author confirmation form

Complete every field truthfully, then use the answers to replace all four
`[Author input required before submission: ...]` markers in `paper/paper.md`.
Do not infer a declaration from repository metadata alone.

## Authorship and correspondence

- Final author list in order:
- Corresponding author:
- Corresponding email:
- Affiliation(s), including city and country:
- ORCID for each author:
- Confirmation that every listed author agrees to authorship and accountability:

## Research use

- Research question or experiment:
- Software version or commit used:
- Input data type and instrument/workflow:
- Commands or interface used:
- Outputs used in the research:
- How `saxsabs` affected the analysis:
- Public paper, preprint, data, workflow, or editor-visible evidence:
- Independent/external users or integrations, if any:

## AI usage disclosure

For each tool, give product, model, recoverable version/date, locations used,
and scope of assistance. If an earlier exact version cannot be recovered, state
that fact explicitly and retain supporting account/log evidence where possible.

| Product | Model/version/date | Code/docs/paper locations | Nature and scope |
| --- | --- | --- | --- |
| GitHub Copilot | | | |
| Anthropic Claude | | | |
| OpenAI Codex | | | |
| Other | | | |

Confirm verbatim if true:

> All human authors reviewed, edited, and validated every AI-assisted output
> included in the submitted software, documentation, figures, and manuscript.
> The human authors made the core scientific, architectural, and design
> decisions and accept full responsibility for the submission.

- Confirmation: yes / no

## Funding, acknowledgements, sponsor role, and competing interests

- Funding organization(s), grant number(s), or “No external funding”:
- Sponsor role in study design, software development, analysis, interpretation,
  manuscript preparation, and submission decision:
- People/facilities to acknowledge:
- Competing interests, or explicit “The authors declare no competing interests”:

## CRediT contributions

Assign applicable roles to every author: Conceptualization, Data curation,
Formal analysis, Funding acquisition, Investigation, Methodology, Project
administration, Resources, Software, Supervision, Validation, Visualization,
Writing - original draft, and Writing - review & editing.

| Author | Confirmed CRediT roles |
| --- | --- |
| | |

## Final checks

- Actual submission date (`D Month YYYY`):
- `paper.md` date updated to the actual submission date:
- Strict readiness command returns PASS:
- Confirmation JSON copied from `docs/submission-confirmations.example.json`,
  completed from evidence, and passed with `--manual-confirmations`:
- Public CI URL for the submitted revision:
- Commit SHA submitted to JOSS:
- Confirmation date (`YYYY-MM-DD`, matching the paper submission date):
- Research-evidence reference retained for editorial verification:
- Confirmed commit is the current clean `joss-submission` HEAD:

The software tag, GitHub Release, and exact-version archive DOI are created
after successful JOSS review and recorded in the review issue before acceptance.
