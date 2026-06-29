"""Tests for Genesis workflow state engine and JSON persistence."""

from __future__ import annotations

import tempfile
import unittest

from apps.storage import JsonStore
from apps.workflow import WorkflowEngine


class WorkflowEngineTests(unittest.TestCase):
    def test_workflow_lifecycle_complete_fail_and_retry(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = JsonStore(directory)
            engine = WorkflowEngine(store)
            workflow = engine.create("project-1", "RESEARCH")
            self.assertEqual(workflow["status"], "CREATED")

            completed = engine.run(workflow, lambda current: {"workflowId": current["id"], "ok": True})
            self.assertEqual(completed["status"], "COMPLETED")
            self.assertTrue(store.get_workflow(workflow["id"])["result"]["ok"])

            failed = engine.run(engine.create("project-1", "RESEARCH"), lambda _: (_ for _ in ()).throw(RuntimeError("boom")))
            self.assertEqual(failed["status"], "FAILED")
            retried = engine.retry(failed["id"])
            self.assertEqual(retried["status"], "CREATED")
            self.assertEqual(retried["attempt"], 2)

    def test_resume_recovers_running_workflow_and_records_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = JsonStore(directory)
            engine = WorkflowEngine(store)
            workflow = engine.create("project-1", "RESEARCH")
            workflow["status"] = "RUNNING"
            store.save_workflow(workflow)

            resumed = engine.resume(workflow["id"], lambda current: {"workflowId": current["id"], "attempt": current["attempt"]})

            self.assertEqual(resumed["status"], "COMPLETED")
            self.assertEqual(resumed["attempt"], 2)
            self.assertEqual(resumed["result"]["attempt"], 2)
            metric_types = [metric["type"] for metric in store.list_metrics()]
            self.assertIn("workflow.recovered", metric_types)
            self.assertIn("workflow.completed", metric_types)


if __name__ == "__main__":
    unittest.main()
