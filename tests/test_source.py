import json
import unittest

from book_learning_program_data.capture import normalize, source_config
from book_learning_program_data.cli import validate

FIXTURES = {
    "mit-ocw-course-library": (
        "<h1>MIT OpenCourseWare</h1>"
        "<p>Free online course materials from thousands of courses.</p>"
    ),
    "google-developers-certification": (
        "<h1>Google Developers Certification</h1>"
        "<p>Take a certification exam with training content.</p>"
    ),
    "google-gear-mentorship": (
        "<h1>Register for expert-led certification cohorts</h1>"
        "<p>technical mentorship in this no-cost program.</p><p>Certification cohorts</p>"
    ),
    "aws-builder-workshops": (
        "<h1>Workshops now available in AWS Builder Center</h1>"
        "<p>Explore the workshops catalog and filter the results.</p>"
    ),
    "uk-skills-bootcamps-providers": (
        json.dumps({
            "base_path": "/government/publications/skills-bootcamps-training-providers",
            "title": "Skills Bootcamps training providers",
            "description": "The Department for Education publishes local training providers.",
            "details": {"body": "A list of local areas that received government funding to run Skills Bootcamps."},
        })
    ),
    "uk-apprenticeships-directory": (
        "<h1>Become an apprentice</h1>"
        "<p>Find an apprenticeship and explore apprenticeships across England.</p>"
    ),
}


class SourceTests(unittest.TestCase):
    def test_each_registered_source_normalizes(self):
        for source_id, raw in FIXTURES.items():
            with self.subTest(source_id=source_id):
                source = source_config(source_id)
                data = normalize(raw.encode("utf-8"), source, "2026-09-08T00:00:00Z")
                item = data["items"][0]
                item["provenance"].update(raw_object_key="landing/test", bronze_manifest_key="control/manifests/test")
                self.assertEqual(item["category"], source["category"])
                self.assertEqual(validate(data)["schema_version"], "learning_program.v1")

    def test_source_drift_is_rejected(self):
        with self.assertRaises(ValueError):
            normalize(b"<h1>unrelated page</h1>", source_config("mit-ocw-course-library"), "2026-09-08T00:00:00Z")


if __name__ == "__main__":
    unittest.main()
