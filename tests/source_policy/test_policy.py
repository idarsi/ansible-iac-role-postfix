"""Focused policy checks; uses unittest and YAML fixtures, no test framework dependency."""

from pathlib import Path
import sys
import unittest

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from check_source_policy import check_artifacts, parse_workflow  # noqa: E402


FIXTURES = Path(__file__).with_name("fixtures")


class WorkflowPolicyTests(unittest.TestCase):
    def test_repository_workflow_passes(self) -> None:
        root = Path(__file__).resolve().parents[2]
        text = (root / ".github/workflows/tests.yml").read_text(encoding="utf-8")
        parse_workflow(text)

    def test_job_permission_override_is_checked(self) -> None:
        text = (FIXTURES / "job-write-permission.yml").read_text(encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "job 'build'.*contents: read"):
            parse_workflow(text)

    def test_sensitive_trigger_is_rejected(self) -> None:
        text = (FIXTURES / "sensitive-trigger.yml").read_text(encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "sensitive trigger"):
            parse_workflow(text)

    def test_sensitive_trigger_in_event_list_is_rejected(self) -> None:
        text = (FIXTURES / "sensitive-trigger-list.yml").read_text(encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "sensitive trigger"):
            parse_workflow(text)

    def test_top_level_permissions_required_and_exact(self) -> None:
        text = (FIXTURES / "broad-permissions.yml").read_text(encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "workflow permissions"):
            parse_workflow(text)

    def test_duplicate_yaml_keys_are_rejected(self) -> None:
        text = (FIXTURES / "duplicate-permissions.yml").read_text(encoding="utf-8")
        with self.assertRaisesRegex(yaml.YAMLError, "duplicate key"):
            parse_workflow(text)

    def test_document_and_license_artifact_content(self) -> None:
        self.assertEqual(check_artifacts(), [])


if __name__ == "__main__":
    unittest.main()
