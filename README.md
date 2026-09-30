# book-learning-program-data

Find learning access and credentials by prerequisites and workload.

Status: **local source pilot**, version 0.1.0. Six manually invoked official
public pages now run through the shared bounded capture and lake replay lane.
There is no scheduler, hosted API, consumer integration or application action.
The CLI still provides a machine-readable JSON contract and searches synthetic
examples; capture never falls back from live data to fixtures.

## Users and boundary

For people and small teams discovering learning programs.
Training admissions and learning offers; funding records link to scholarship instead of duplicating it.

Subcategories: course, certification, bootcamp, mentorship, workshop, apprenticeship-training.

Domain-specific terms: `learning_format`, `prerequisites`, `credential`, `hours_required`.
Each record represents one program/offer intake window. A repeat intake receives
a distinct source record ID. Cross-domain packages use `related_records` rather
than copying the same award into several products.

## Run locally

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
book-learning-program-data contract
book-learning-program-data demo --open-only
book-learning-program-data demo --query "course"
book-learning-program-data validate src/book_learning_program_data/demo.json
python -m unittest discover -s tests -v
python -m pip install -e ".[dev]"  # pytest + pinned ruff
ruff check . && python -m pytest -q
```

CI (`.github/workflows/ci.yml`) runs `ruff check`, the offline test suite and a
CLI smoke test on Python 3.10 and 3.13. `tests/test_registry.py` keeps
`sources.json`, the packaged `source*.json` configs and the contract in sync.

With dependencies already available, use `PYTHONPATH=src python3 -m book_learning_program_data`.
`demo` uses the fixed synthetic clock 2026-09-07T00:00:00Z unless `--as-of` is
provided. `--open-only` excludes closed, unknown-deadline, expired, stale (72h
default), and future-checked records. This is an availability filter; it does
not assert personal eligibility, selection probability, or a guaranteed payout.

Contract: `src/book_learning_program_data/schema.json` (`learning_program.v1`).
Unknown amounts, currencies, eligibility and deadlines remain unknown. Cash,
credit, discount, in-kind benefits and access are different value kinds. Never
sum them as cash income. Queries and validation are read-only and do not persist
provided files. The `live` label requires captured lineage, but validation alone
does not verify that referenced lake objects exist or prove source truth.

## Data ownership and source policy

Owner: bookchaowalit. Public program metadata only; no applications, personal
screening answers, financial credentials, cookies, or private transcripts.
See `sources.json` and the source policy files under `src/`: MIT OpenCourseWare,
Google Developers Certification, Google GEAR, AWS Builder Center workshops,
GOV.UK Skills Bootcamps and Apprenticeships.gov.uk are enabled for public
metadata only. Exact source
permission and retention remain reviewed per source.
No spending, account creation or messaging.

Implemented flow: approved source pull → immutable landing bytes
and checksum → Bronze Parquet and manifest through the shared lake runtime →
versioned read-only contract → consumer pull. Each product owns its source
adapters and lake prefix. Producers never write into another app's database,
CRM, tasks, application tracker, or notification system.

## Remaining implementation gates

1. Keep the six reviewed source adapters fresh and add parser fixtures when a
   provider changes its public contract; the `bootcamp` source remains a
   directory, not an admission or placement guarantee.
2. Expand field extraction and live quality monitoring without inferring
   credential, completion or employment outcomes.
3. Package the local shared capture runtime for independent deployment.
4. Add retention/access controls and runtime monitoring.
5. Connect a read-only consumer. Personal eligibility, ranking, deadlines and
   application workflow belong to consumers with separate private storage.

## Official source pilots

Sources: [MIT OpenCourseWare](https://ocw.mit.edu/),
[Google Developers Certification](https://developers.google.com/certification),
[Google GEAR](https://developers.google.com/program/gear/getcertified),
[AWS Builder Center workshops](https://aws.amazon.com/about-aws/whats-new/2025/11/workshops-available-aws-builder-center/),
the [GOV.UK Skills Bootcamps directory](https://www.gov.uk/government/publications/skills-bootcamps-training-providers),
and [Apprenticeships.gov.uk](https://www.apprenticeships.gov.uk/apprentices). The exact source
configurations live beside the adapter. The pages are read for bounded public
metadata only; no account, exam, application or employment claim is created.

Run from this repository with the existing data-lake Python environment:

```bash
export SOLO_EMPIRE_ROOT=/home/bookchaowalit/book/solo-empire
PYTHONPATH=src "$SOLO_EMPIRE_ROOT/infra/.venv-datalake/bin/python" -m book_learning_program_data.capture acquire --lake "$PWD/data/lake" --state-dir "$PWD/data/control"
PYTHONPATH=src "$SOLO_EMPIRE_ROOT/infra/.venv-datalake/bin/python" -m book_learning_program_data.capture records --lake "$PWD/data/lake" --state-dir "$PWD/data/control"
PYTHONPATH=src "$SOLO_EMPIRE_ROOT/infra/.venv-datalake/bin/python" -m book_learning_program_data.capture acquire --source-id google-developers-certification --lake "$PWD/data/lake" --state-dir "$PWD/data/control"
```

The adapter requires source-specific visible markers and emits unknown
deadlines when the page does not publish an application window. A course
directory is not treated as an open admission call, and a certification or
apprenticeship page does not guarantee a credential, job or paid placement.

No runtime port is reserved. The former `opportunity.v1` is archival; `job.v1` remains a separate job-data contract.
Breaking contract changes require a new version and a consumer migration.
There is no production deployment to roll back; discard demo output or restore
the previous contract version locally. Source permission, live availability,
lake replay and real eligibility are **unverified**, not passing gates.
