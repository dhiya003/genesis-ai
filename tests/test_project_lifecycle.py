"""Tests for Genesis v1 project and workflow lifecycle stories."""

from __future__ import annotations

from io import StringIO
import json
from unittest.mock import patch
import tempfile
import unittest

from apps.cli.main import main as cli_main
from apps.founder import FounderBusinessRuntime
from apps.project import ProjectLifecycleRuntime
from apps.storage import JsonStore
from apps.workflow import WorkflowEngine


def _seed_ready_project(store: JsonStore) -> tuple[dict[str, object], dict[str, object]]:
    founder = FounderBusinessRuntime(store)
    business = founder.create_business(
        {"name": "Toy Co", "country": "India", "currency": "INR", "primaryMarket": "Parents"},
        founder_id="founder-1",
    )["business"]
    founder.upsert_founder_profile({"name": "Dhiya", "currency": "INR", "riskAppetite": "MEDIUM"}, founder_id="founder-1")
    founder.set_business_vision(str(business["id"]), "Build India's best educational toy company.", founder_id="founder-1")
    founder.add_business_goal(str(business["id"]), {"type": "Revenue", "targetValue": 1000000, "unit": "INR/month", "targetDate": "2027-01-01", "priority": "HIGH"}, founder_id="founder-1")
    founder.add_business_constraint(str(business["id"]), {"type": "Budget", "description": "Stay under INR 250000 for pilot."}, founder_id="founder-1")
    founder.set_business_budget(str(business["id"]), {"categories": [{"category": "Pilot", "allocated": 250000, "spent": 0}]}, founder_id="founder-1")
    founder.set_approval_policy(str(business["id"]), {"rules": [{"type": "Budget", "mode": "MANUAL", "budgetThreshold": 100000}]}, founder_id="founder-1")
    project = founder.create_project(str(business["id"]), {"title": "Wooden Toy Launch", "description": "Premium educational wooden toys."}, founder_id="founder-1")["project"]
    return business, project


class ProjectLifecycleTests(unittest.TestCase):
    def test_project_dashboard_update_archive_restore_duplicate_readiness_and_timeline(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = JsonStore(directory)
            _, project = _seed_ready_project(store)
            lifecycle = ProjectLifecycleRuntime(store)

            readiness = lifecycle.validate_readiness(str(project["id"]), actor="founder-1")["readiness"]
            self.assertEqual(readiness["outcome"], "READY")
            self.assertEqual(store.get_latest_project_readiness(str(project["id"]))["outcome"], "READY")

            updated = lifecycle.update(str(project["id"]), {"timeline": "45 days", "priority": "HIGH", "targetMarket": "Urban parents"}, actor="founder-1")
            self.assertIn("timeline", updated["changedFields"])
            self.assertGreaterEqual(len(store.list_project_versions(str(project["id"]))), 2)

            workflow = WorkflowEngine(store).create(str(project["id"]), "RESEARCH", created_by="founder-1", idempotency_key="wf-1")
            duplicate_workflow = WorkflowEngine(store).create(str(project["id"]), "RESEARCH", created_by="founder-1", idempotency_key="wf-1")
            self.assertEqual(workflow["id"], duplicate_workflow["id"])
            planned = WorkflowEngine(store).plan(workflow)
            WorkflowEngine(store).pause(planned["id"], reason="founder review")

            dashboard = lifecycle.dashboard(str(project["id"]))
            self.assertEqual(dashboard["reportType"], "PROJECT_DASHBOARD")
            self.assertEqual(dashboard["projectName"], "Wooden Toy Launch")
            self.assertGreaterEqual(dashboard["completionPercent"], 0)
            self.assertEqual(dashboard["activeWorkflow"]["status"], "WAITING")
            self.assertTrue(dashboard["recentActivities"])
            self.assertIn("implementedExtrasForReview", dashboard)

            health = lifecycle.health(str(project["id"]))["health"]
            self.assertGreaterEqual(health["score"], 0)
            self.assertLessEqual(health["score"], 100)
            self.assertIn("workflowSuccess", health["factors"])

            timeline = lifecycle.timeline(str(project["id"]))["timeline"]
            self.assertEqual(timeline, sorted(timeline, key=lambda item: item["timestamp"]))
            self.assertTrue(all(item["immutable"] for item in timeline))

            copy_result = lifecycle.duplicate(str(project["id"]), actor="founder-1", title="Wooden Toy Launch - South India")
            self.assertNotEqual(copy_result["project"]["id"], project["id"])
            self.assertEqual(copy_result["project"]["sourceProjectId"], project["id"])

            archived = lifecycle.archive(str(project["id"]), actor="founder-1", reason="pilot complete")["project"]
            self.assertEqual(archived["status"], "ARCHIVED")
            restored = lifecycle.restore(str(project["id"]), actor="founder-1")["project"]
            self.assertEqual(restored["status"], "ACTIVE")

    def test_workflow_progress_history_and_notifications(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = JsonStore(directory)
            _, project = _seed_ready_project(store)
            engine = WorkflowEngine(store)
            workflow = engine.create(str(project["id"]), "RESEARCH", created_by="founder-1")
            self.assertEqual(workflow["version"], 1)
            self.assertEqual(workflow["businessId"], project["businessId"])

            planned = engine.plan(workflow)
            completed = engine.run(planned, lambda current: {"workflowId": current["id"], "ok": True})

            progress = engine.progress(completed["id"])
            self.assertEqual(progress["progressPercent"], 100)
            history = engine.history(completed["id"])
            self.assertTrue(history["stateHistory"])
            self.assertTrue(history["executionHistory"])
            notifications = engine.notifications(completed["id"])
            self.assertTrue(notifications["configurable"])
            self.assertTrue(notifications["notifications"])

    def test_project_and_workflow_cli_actions(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = JsonStore(directory)
            _, project = _seed_ready_project(store)
            project_id = str(project["id"])

            output = StringIO()
            with patch("sys.stdout", output):
                self.assertEqual(cli_main(["project", project_id, "dashboard", "--data-dir", directory]), 0)
            self.assertEqual(json.loads(output.getvalue())["reportType"], "PROJECT_DASHBOARD")

            output = StringIO()
            with patch("sys.stdout", output):
                self.assertEqual(cli_main(["workflow", "create", project_id, "RESEARCH", "--data-dir", directory, "--idempotency-key", "cli-wf"]), 0)
            workflow_id = json.loads(output.getvalue())["workflow"]["id"]

            output = StringIO()
            with patch("sys.stdout", output):
                self.assertEqual(cli_main(["workflow", "progress", workflow_id, "--data-dir", directory]), 0)
            self.assertEqual(json.loads(output.getvalue())["workflow"]["id"], workflow_id)


if __name__ == "__main__":
    unittest.main()
