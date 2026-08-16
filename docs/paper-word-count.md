# JOSS paper word-count method

The paper body is counted with Pandoc rather than by counting Markdown tokens:

```powershell
pandoc paper/paper.md --from=markdown --to=plain --resource-path=paper \
  --output=paper-body.txt
```

For the submission-length check, remove the `References` section and the
bracketed author-input markers from `paper-body.txt`, then count tokens matching
`[A-Za-z0-9][A-Za-z0-9'./+^-]*`.

The count must be regenerated after author-controlled content is added. The
current count is recorded by `scripts/check_submission_readiness.py` rather
than hard-coded here.
