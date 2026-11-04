# Data and scripts for "Memory for Agentic AI" (survey)

Supporting data for the survey *Memory for Agentic AI: A Survey of Mechanisms, Control, Evaluation,
and Evidence in LLM-Based Agents* (H. Mohasel Arjomandi, preprint, November 2026).
Survey cutoff: October 31, 2026.

This repository contains the literature harvest, the screening samples, the full-text extraction
sheets behind the results audit, and the scripts that recompute the bibliometric numbers.

## Contents

| Path | What it is | Used in the paper |
|---|---|---|
| `data/harvest/harvest_config.json` | arXiv queries, date window, title rule | §II-A |
| `data/harvest/harvest.json`, `screening.csv` | All 1,779 unique harvested records (title, date, abstract, matched queries, memory-title flag) | §II, Fig. 1–2 |
| `data/harvest/harvest_summary.json` | Per-query and screening counts | Fig. 1 |
| `data/samples/dropped_sample.csv` | Random 100 of the 828 records removed by the title filter (seed 20261103), with in-scope labels | §II-E (false-negative estimate) |
| `data/samples/corpus_precision_sample.csv` | Random 50 of the 840 corpus records (seed 20261104), with relevance labels | §II-A (precision check) |
| `data/audit/audit_fulltext.tsv` | Full-text extraction for the 16 audited systems: metric, comparators, backbone, full-context baseline, variance, and whether each item appears in the abstract | Table VI |
| `data/audit/locomo_crosspaper.tsv` | Overall LoCoMo scores for the same systems as reported in different papers, with the source table | Table VII, Fig. 4 |
| `data/audit/control_locus_coding.tsv` | Locus coding (H/M/L/A) of the 38 example systems with arXiv IDs | §VI |
| `data/checks/arxiv_id_check.tsv` | Title and first-author check of every arXiv reference | §II-C |
| `data/checks/bibliometrics_output.txt` | Output of `bibliometrics.py` | Table II, §VI |
| `scripts/harvest.py` | Reproducible arXiv harvest (`python3 scripts/harvest.py data/harvest/harvest_config.json <out_dir>`) | §II-A |
| `scripts/bibliometrics.py` | Recomputes the corpus counts, Table II (Wilson intervals, Fisher tests, Holm correction) and the control-locus indicators; can redraw the samples | §II, §VI, Appendix A |
| `scripts/verify_arxiv_ids.py` | Checks arXiv IDs in a BibTeX file against arxiv.org | §II-C |

## Reproduce the numbers

```bash
pip install scipy
python3 scripts/bibliometrics.py data/harvest/harvest.json
```

A fresh harvest with `harvest.py` will differ slightly from `harvest.json`, because arXiv
metadata changes over time. Use the archived file to reproduce the paper's numbers exactly.

## Coding notes and limitations

- Each sheet was coded by a single coder with help from an AI assistant. No second coder was
  available. Each row of the audit sheets names the table or section of the source paper it was
  taken from, so the coding can be checked.
- The audit records what each paper reports. No experiment was re-run.
- In `dropped_sample.csv`, `ai_prescreen` holds the labels used in the paper; the columns
  `in_scope_coder1` and `in_scope_coder2` are left empty for independent re-coding.
- The keyword rules are listed in Appendix A of the paper and at the top of `bibliometrics.py`.
  They have not been validated against human labels.

## Licence

Data (`data/`): CC BY 4.0. Scripts (`scripts/`): MIT. arXiv titles and abstracts are reproduced
from the arXiv API metadata (CC0 1.0).
