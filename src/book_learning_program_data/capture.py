"""Capture reviewed public learning-program pages through the shared lake runtime."""
import argparse
import json
import os
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

from .cli import resource, validate


class Text(HTMLParser):
    """Extract visible text while ignoring executable page content."""

    def __init__(self):
        super().__init__()
        self.parts = []
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "noscript", "svg"}:
            self.hidden += 1

    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript", "svg"}:
            self.hidden = max(0, self.hidden - 1)

    def handle_data(self, value):
        if not self.hidden:
            self.parts.append(value)


REQUIRED_MARKERS = {
    "mit-ocw-course-library": ("opencourseware", "free online course materials", "courses"),
    "google-developers-certification": ("google developers certification", "certification exam", "training content"),
    "google-gear-mentorship": ("technical mentorship", "no-cost program", "certification cohorts"),
    "aws-builder-workshops": ("workshops now available in aws builder center", "workshops catalog", "filter"),
    "uk-skills-bootcamps-providers": ("skills bootcamps", "training providers", "government funding"),
    "uk-apprenticeships-directory": ("become an apprentice", "find an apprenticeship", "apprenticeships"),
}


def normalize(raw, source, checked_at):
    """Turn one official page into a conservative learning-program record."""
    markers = REQUIRED_MARKERS.get(source["id"])
    if not markers:
        raise ValueError("unknown learning-program source")
    if source.get("access") == "govuk-api":
        body = json.loads(raw)
        if not isinstance(body, dict):
            raise ValueError("GOV.UK source document drift")
        if body.get("base_path") != source["source_url"].removeprefix("https://www.gov.uk"):
            raise ValueError("GOV.UK source path drift")
        if body.get("title") != source["title"] or not isinstance(body.get("details"), dict):
            raise ValueError("GOV.UK source document drift")
        parser = Text()
        parser.feed(" ".join(
            str(value)
            for value in (body.get("title", ""), body.get("description", ""), body["details"].get("body", ""))
        ))
        text = " ".join(" ".join(parser.parts).split())
    else:
        parser = Text()
        parser.feed(raw.decode("utf-8"))
        text = " ".join(" ".join(parser.parts).split())
    folded = text.casefold()
    if not all(marker.casefold() in folded for marker in markers):
        raise ValueError("learning-program source drift or challenge page")

    terms = {
        "learning_format": source["learning_format"],
        "prerequisites": source["prerequisites"],
        "credential": source["credential"],
        "hours_required": None,
    }
    item = {
        "id": source["id"],
        "title": source["title"],
        "category": source["category"],
        "source_url": source["source_url"],
        "provider": source["provider"],
        "status": "unknown",
        "deadline": {"kind": "unknown", "at": None},
        "eligible_countries": source.get("eligible_countries", ["GLOBAL"]),
        "eligibility_text": source["eligibility_text"],
        "value": {
            "kind": source.get("value_kind", "access"),
            "amount": None,
            "currency": None,
            "guaranteed": False,
        },
        "cost": {
            "fee_amount": None,
            "currency": None,
            "auto_renewal": None,
            "notes": source["cost_notes"],
        },
        "terms": terms,
        "related_records": [],
        "provenance": {
            "evidence_kind": "captured",
            "source_id": source["id"],
            "source_record_id": source["id"],
            "checked_at": checked_at,
            "raw_object_key": None,
            "bronze_manifest_key": None,
        },
    }
    return {
        "schema_version": source["schema_version"],
        "source": source["product"],
        "retrieved_at": checked_at,
        "data_status": "live",
        "items": [item],
    }


def source_config(source_id=None):
    if source_id is None:
        return resource("source.json")
    if not re.fullmatch(r"[a-z0-9-]+", source_id):
        raise ValueError("invalid source id")
    base = resource("source.json")
    if base["id"] == source_id:
        return base
    try:
        return resource("source-" + source_id + ".json")
    except FileNotFoundError:
        raise ValueError("unknown source id") from None


def main(argv=None):
    selector = argparse.ArgumentParser(add_help=False)
    selector.add_argument("--source-id")
    selected, remaining = selector.parse_known_args(argv)
    root = os.environ.get("SOLO_EMPIRE_ROOT")
    if not root:
        print("Set SOLO_EMPIRE_ROOT to the local shared capture/lake runtime.", file=sys.stderr)
        return 2
    runtime = Path(root).resolve() / "infra/scripts"
    if not (runtime / "discovery/capture_runtime.py").is_file():
        print("Shared discovery runtime is unavailable.", file=sys.stderr)
        return 2
    sys.path.insert(0, str(runtime))
    from discovery.capture_runtime import VERSION, run

    if VERSION != 1:
        raise RuntimeError("unsupported shared capture runtime")
    return run(source_config(selected.source_id), normalize, validate, remaining)


if __name__ == "__main__":
    raise SystemExit(main())
