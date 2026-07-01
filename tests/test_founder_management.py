"""Genesis v1 Epic 01 founder and business management tests."""

from __future__ import annotations

import json
from io import StringIO
import tempfile
from threading import Thread
import unittest
from unittest.mock import patch
from urllib import error, request

from apps.api.app import create_server
from apps.cli.main import main as cli_main
from apps.founder import FounderBusinessRuntime
from apps.storage import JsonStore
from config import RuntimeConfig


class FounderManagementTests(unittest.TestCase):
    def test_business_profile_vision_goals_constraints_budget_policy_and_planning(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = JsonStore(directory)
            runtime = FounderBusinessRuntime(store)

            business_result = runtime.create_business(
                {
                    "name": "Luma Toys",
                    "industry": "Educational Toys",
                    "country": "India",
                    "currency": "INR",
                    "primaryMarket": "Parents of children aged 3-5",
                },
                founder_id="founder-1",
                idempotency_key="business-create-1",
            )
            duplicate = runtime.create_business(
                {"name": "Ignored", "country": "India", "currency": "INR", "primaryMarket": "Ignored"},
                founder_id="founder-1",
                idempotency_key="business-create-1",
            )
            business = business_result["business"]

            self.assertEqual(business["status"], "ACTIVE")
            self.assertEqual(business["creator"], "founder-1")
            self.assertEqual(business["country"], "India")
            self.assertEqual(business["currency"], "INR")
            self.assertEqual(business["primaryMarket"], "Parents of children aged 3-5")
            self.assertEqual(duplicate["business"]["id"], business["id"])
            self.assertTrue(duplicate["idempotent"])
            self.assertTrue(store.list_audit_logs(project_id=business["id"]))

            with self.assertRaises(ValueError):
                runtime.create_business({"country": "India", "currency": "INR", "primaryMarket": "Parents"}, founder_id="founder-1")

            profile_v1 = runtime.upsert_founder_profile(
                {
                    "name": "Dhiya",
                    "language": "en",
                    "timeZone": "Asia/Kolkata",
                    "currency": "INR",
                    "riskAppetite": "Medium",
                    "budgetPreference": "Lean MVP",
                    "experienceLevel": "Beginner",
                    "communicationStyle": "Concise",
                    "workingHours": "10:00-18:00",
                    "approvalPolicy": "Manual for spend",
                },
                founder_id="founder-1",
            )
            profile_v2 = runtime.upsert_founder_profile({"name": "Dhiya", "language": "en", "timeZone": "Asia/Kolkata", "currency": "INR", "riskAppetite": "Low"}, founder_id="founder-1")
            self.assertEqual(profile_v1["profile"]["version"], 1)
            self.assertEqual(profile_v2["profile"]["version"], 2)
            self.assertEqual(len(profile_v2["versions"]), 2)

            vision_v1 = runtime.set_business_vision(business["id"], "Build India's largest educational toy company.", founder_id="founder-1")
            vision_v2 = runtime.set_business_vision(business["id"], "Build India's best educational toy company.", founder_id="founder-1")
            self.assertEqual(vision_v1["activeVision"]["version"], 1)
            self.assertEqual(vision_v2["activeVision"]["version"], 2)
            self.assertEqual(vision_v2["versions"][0]["status"], "SUPERSEDED")

            goal = runtime.add_business_goal(
                business["id"],
                {"type": "Revenue", "targetValue": 100000, "unit": "INR/month", "targetDate": "2026-12-31", "priority": "HIGH"},
                founder_id="founder-1",
            )["goal"]
            updated_goal = runtime.update_business_goal(business["id"], goal["id"], {"priority": "CRITICAL"}, founder_id="founder-1")["goal"]
            self.assertEqual(updated_goal["priority"], "CRITICAL")

            constraint = runtime.add_business_constraint(business["id"], {"type": "Budget", "description": "Keep first batch below INR 50000"}, founder_id="founder-1")["constraint"]
            constraint_v2 = runtime.update_business_constraint(business["id"], constraint["id"], {"description": "Keep first batch below INR 60000"}, founder_id="founder-1")
            self.assertEqual(constraint_v2["constraint"]["version"], 2)
            self.assertEqual(len(constraint_v2["versions"]), 2)

            budget = runtime.set_business_budget(
                business["id"],
                {
                    "currency": "INR",
                    "categories": [
                        {"category": "Research", "allocated": 10000, "spent": 2500},
                        {"category": "Manufacturing", "allocated": 50000, "spent": 10000},
                        {"category": "Marketing", "allocated": 30000, "spent": 5000},
                    ],
                },
                founder_id="founder-1",
            )["budget"]
            self.assertEqual(budget["remainingBudget"], 72500)

            metric = runtime.add_success_metric(business["id"], {"name": "Monthly revenue", "unit": "INR", "targetValue": 100000, "currentValue": 25000, "timeHorizon": "monthly"}, founder_id="founder-1")["metric"]
            self.assertEqual(metric["progressPercent"], 25)

            policy = runtime.set_approval_policy(
                business["id"],
                {"rules": [{"type": "Budget", "mode": "Manual", "budgetThreshold": 10000}, {"type": "Publishing", "mode": "Manual"}]},
                founder_id="founder-1",
            )["approvalPolicy"]
            self.assertEqual(len(policy["rules"]), 2)
            self.assertTrue(policy["approvalHistory"])

            project_result = runtime.create_project(business["id"], {"title": "Educational Wooden Toys", "description": "Launch a premium toy line."}, founder_id="founder-1")
            project = project_result["project"]
            self.assertEqual(project["businessId"], business["id"])
            self.assertEqual(project["status"], "DRAFT")
            self.assertEqual(project["owner"], "founder-1")
            self.assertTrue(project["inheritedConstraints"])
            self.assertEqual(project["founderProfileSnapshot"]["version"], 2)
            self.assertEqual(project["visionSnapshot"]["version"], 2)

            planning = runtime.start_project_planning(business["id"], project["id"], founder_id="founder-1")
            self.assertEqual(planning["project"]["status"], "PLANNING")
            self.assertEqual(planning["workflow"]["status"], "PLANNING")
            self.assertEqual(planning["workflow"]["scheduledDepartment"], "RESEARCH_DEPARTMENT")
            self.assertTrue(planning["dashboard"]["planningReadiness"]["ready"])

            dashboard = runtime.business_dashboard(business["id"])
            self.assertEqual(dashboard["reportType"], "BUSINESS_DASHBOARD")
            self.assertEqual(len(dashboard["projects"]), 1)
            self.assertTrue(any(log["event"] == "business.created" for log in dashboard["auditLogs"]))

    def test_planning_preconditions_report_missing_context(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            runtime = FounderBusinessRuntime(JsonStore(directory))
            business = runtime.create_business({"name": "Tea Co", "country": "India", "currency": "INR", "primaryMarket": "Tea buyers"})["business"]
            project = runtime.create_project(business["id"], {"title": "Premium Tea"})["project"]
            with self.assertRaisesRegex(ValueError, "vision, goals, constraints"):
                runtime.start_project_planning(business["id"], project["id"])

    def test_http_business_creation_is_idempotent_and_dashboard_visible(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config = RuntimeConfig(api_host="127.0.0.1", api_port=0, data_dir=directory, environment="test")
            server = create_server(config)
            host, port = server.server_address
            thread = Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                payload = json.dumps({"name": "Luma Toys", "industry": "Toys", "country": "India", "currency": "INR", "primaryMarket": "Parents"}).encode("utf-8")
                create = request.Request(f"http://{host}:{port}/businesses", data=payload, headers={"Content-Type": "application/json", "Idempotency-Key": "http-business-1"}, method="POST")
                with request.urlopen(create, timeout=10) as response:
                    self.assertEqual(response.status, 201)
                    first = json.loads(response.read().decode("utf-8"))
                duplicate = request.Request(f"http://{host}:{port}/businesses", data=payload, headers={"Content-Type": "application/json", "Idempotency-Key": "http-business-1"}, method="POST")
                with request.urlopen(duplicate, timeout=10) as response:
                    self.assertEqual(response.status, 201)
                    second = json.loads(response.read().decode("utf-8"))
                self.assertEqual(first["business"]["id"], second["business"]["id"])
                self.assertTrue(second["idempotent"])

                business_id = first["business"]["id"]
                with request.urlopen(f"http://{host}:{port}/businesses/{business_id}/dashboard", timeout=10) as response:
                    self.assertEqual(response.status, 200)
                    dashboard = json.loads(response.read().decode("utf-8"))
                self.assertEqual(dashboard["business"]["name"], "Luma Toys")

                invalid = request.Request(f"http://{host}:{port}/businesses", data=json.dumps({"country": "India"}).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
                with self.assertRaises(error.HTTPError) as exc:
                    request.urlopen(invalid, timeout=10)
                self.assertEqual(exc.exception.code, 400)
                body = json.loads(exc.exception.read().decode("utf-8"))
                self.assertIn("Business Name is required", body["error"]["message"])
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

    def test_cli_founder_commands(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = StringIO()
            business_payload = json.dumps({"name": "Luma Toys", "country": "India", "currency": "INR", "primaryMarket": "Parents"})
            with patch("sys.stdout", output):
                exit_code = cli_main(["founder", "--data-dir", directory, "create-business", business_payload, "--idempotency-key", "cli-business-1"])
            self.assertEqual(exit_code, 0)
            business = json.loads(output.getvalue())["business"]

            profile_output = StringIO()
            profile_payload = json.dumps({"name": "Dhiya", "language": "en", "timeZone": "Asia/Kolkata", "currency": "INR"})
            with patch("sys.stdout", profile_output):
                exit_code = cli_main(["founder", "--data-dir", directory, "profile", profile_payload])
            self.assertEqual(exit_code, 0)
            self.assertEqual(json.loads(profile_output.getvalue())["profile"]["name"], "Dhiya")

            dashboard_output = StringIO()
            with patch("sys.stdout", dashboard_output):
                exit_code = cli_main(["founder", "--data-dir", directory, "dashboard", business["id"]])
            self.assertEqual(exit_code, 0)
            self.assertEqual(json.loads(dashboard_output.getvalue())["business"]["id"], business["id"])


if __name__ == "__main__":
    unittest.main()
