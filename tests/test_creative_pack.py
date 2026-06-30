"""Sprint 4 Creative Pack tests."""

from __future__ import annotations

import base64
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from apps.creative.assets import OpenAIImageClient, generate_creative_assets
from apps.creative.employees import CREATIVE_EMPLOYEES, run_creative_employee, validate_creative_employee_output
from apps.orchestrator import GenesisOrchestrator
from apps.storage import JsonStore
from scripts.validate_creative_pack import validate_creative_pack_payload


class CreativePackTests(unittest.TestCase):
    def _product_blueprint_flow(self, orchestrator: GenesisOrchestrator) -> tuple[dict[str, object], dict[str, object]]:
        research = orchestrator.submit_idea(
            "Build a premium educational wooden toy business for children aged 3-5 in India.",
            country="India",
            budget="300000 INR",
            timeline="45 days",
        )
        product = orchestrator.generate_product_blueprint(research["project"]["id"])
        return research, product["blueprint"]

    def test_creative_employee_contracts_are_executable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            orchestrator = GenesisOrchestrator(JsonStore(directory))
            research, product_blueprint = self._product_blueprint_flow(orchestrator)
            context = {"project": research["project"], "workflow": {"id": "workflow-test"}, "productBlueprint": product_blueprint, "sections": {}}

            for employee_id in CREATIVE_EMPLOYEES:
                output = run_creative_employee(employee_id, context)
                self.assertFalse(validate_creative_employee_output(output))
                context["sections"][output["section"]] = output

    def test_orchestrator_generates_complete_creative_pack(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = JsonStore(directory)
            orchestrator = GenesisOrchestrator(store)
            _, product_blueprint = self._product_blueprint_flow(orchestrator)

            result = orchestrator.generate_creative_pack(product_blueprint["productId"])
            creative_pack = result["creativePack"]

            self.assertEqual(result["project"]["status"], "CREATIVE_PACK_COMPLETED")
            self.assertEqual(creative_pack["reportType"], "CREATIVE_PACK")
            self.assertFalse(validate_creative_pack_payload(creative_pack))
            self.assertEqual(store.get_creative_pack(product_blueprint["productId"])["creativeId"], product_blueprint["productId"])
            self.assertTrue(store.get_brand_report(product_blueprint["productId"])["brandName"])
            self.assertTrue(store.get_logo_report(product_blueprint["productId"])["primaryConcept"])
            self.assertTrue(store.get_creative_packaging_report(product_blueprint["productId"])["panelContent"])
            self.assertTrue(store.get_mockup_report(product_blueprint["productId"])["variantMockups"])
            self.assertTrue(store.get_marketplace_creative_report(product_blueprint["productId"])["imageConcepts"])
            self.assertTrue(store.get_social_creative_report(product_blueprint["productId"])["instagramPosts"])
            self.assertTrue(store.get_copy_report(product_blueprint["productId"])["taglines"])
            generated_assets = creative_pack["generatedAssets"]
            self.assertGreaterEqual(generated_assets["summary"]["svg"], 1)
            self.assertGreaterEqual(generated_assets["summary"]["png"], 1)
            self.assertGreaterEqual(generated_assets["summary"]["pdf"], 1)
            for asset in generated_assets["assets"]:
                asset_path = Path(asset["path"])
                self.assertTrue(asset_path.exists(), asset_path)
                self.assertGreater(asset_path.stat().st_size, 0)
            self.assertTrue(orchestrator.get_creative_assets(product_blueprint["productId"])["assets"])

    def test_founder_acceptance_wooden_toy_creative_pack(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            orchestrator = GenesisOrchestrator(JsonStore(directory))
            _, product_blueprint = self._product_blueprint_flow(orchestrator)
            creative_pack = orchestrator.generate_creative_pack(product_blueprint["productId"])["creativePack"]

            self.assertTrue(creative_pack["brandIdentity"]["brandName"])
            self.assertTrue(creative_pack["brandIdentity"]["brandStory"])
            self.assertTrue(creative_pack["brandIdentity"]["mission"])
            self.assertTrue(creative_pack["brandIdentity"]["vision"])
            self.assertTrue(creative_pack["brandIdentity"]["brandGuidelines"])
            self.assertIn("positioning", creative_pack["brandStrategy"])
            self.assertTrue(creative_pack["logoSystem"]["primaryConcept"])
            self.assertTrue(creative_pack["logoVariants"])
            self.assertTrue(creative_pack["logoUsageRules"])
            self.assertGreaterEqual(len(creative_pack["colorPalette"]), 3)
            self.assertTrue(creative_pack["typography"])
            self.assertTrue(creative_pack["visualSystem"]["iconLibrary"])
            self.assertTrue(creative_pack["visualSystem"]["illustrationStyle"])
            self.assertTrue(creative_pack["visualSystem"]["photographyStyle"])
            self.assertTrue(creative_pack["visualSystem"]["designTokens"])
            self.assertTrue(creative_pack["packagingDesignBrief"]["panelContent"])
            self.assertTrue(creative_pack["packagingProductionAssets"]["printReadyDielines"])
            self.assertTrue(creative_pack["productMockupBrief"]["variantMockups"])
            self.assertTrue(creative_pack["productCreativeDeliverables"]["heroImages"])
            self.assertTrue(creative_pack["productCreativeDeliverables"]["lifestyleImages"])
            self.assertTrue(creative_pack["productCreativeDeliverables"]["explodedViews"])
            self.assertTrue(creative_pack["productCreativeDeliverables"]["productManuals"])
            self.assertTrue(creative_pack["productCreativeDeliverables"]["instructionCards"])
            self.assertTrue(creative_pack["digitalAssets"]["amazonImageSet"])
            self.assertTrue(creative_pack["digitalAssets"]["shopifyImageSet"])
            self.assertTrue(creative_pack["socialMediaCreativePack"]["instagramPosts"])
            self.assertTrue(creative_pack["marketplaceCreativePack"]["imageConcepts"])
            self.assertTrue(creative_pack["launchCopyPack"]["taglines"])
            self.assertTrue(creative_pack["aiDeliverables"]["masterImagePrompts"])
            self.assertTrue(creative_pack["creativeAssetManifest"])
            self.assertTrue(creative_pack["generatedAssets"]["assets"])
            self.assertFalse(creative_pack["productionReadiness"]["requiresBinaryAssetGeneration"])
            self.assertTrue(creative_pack["productionReadiness"]["assetFilesGenerated"])
            self.assertTrue(creative_pack["validationReport"])
            self.assertTrue(creative_pack["creativeQaReport"]["checks"])
            self.assertTrue(creative_pack["founderApprovalChecklist"])

    def test_openai_image_client_writes_png_from_response(self) -> None:
        png_bytes = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAFgwJ/lQpq6wAAAABJRU5ErkJggg==")

        class FakeResponse:
            def __enter__(self) -> "FakeResponse":
                return self

            def __exit__(self, *_args: object) -> None:
                return None

            def read(self) -> bytes:
                return json.dumps({"data": [{"b64_json": base64.b64encode(png_bytes).decode("ascii")}]}).encode("utf-8")

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "openai.png"
            with patch("apps.creative.assets.request.urlopen", return_value=FakeResponse()) as urlopen:
                OpenAIImageClient(api_key="test-key").generate_png(path, "Create a product hero image")

            self.assertEqual(path.read_bytes(), png_bytes)
            requested_url = urlopen.call_args.args[0].full_url
            self.assertEqual(requested_url, "https://api.openai.com/v1/images/generations")

    def test_generate_creative_assets_can_use_openai_for_raster_files(self) -> None:
        class FakeImageClient:
            def __init__(self) -> None:
                self.prompts: list[str] = []

            def generate_png(self, path: Path, prompt: str) -> None:
                self.prompts.append(prompt)
                path.write_bytes(b"fake-openai-png")

        creative_pack = {
            "productId": "product-1",
            "sourceIdea": "Build a premium educational wooden toy business for children aged 3-5 in India.",
            "brandIdentity": {"brandName": "LumaLearn"},
            "colorPalette": [{"name": "Forest", "hex": "#1F6F50"}, {"name": "Marigold", "hex": "#F4B63F"}, {"name": "Ivory", "hex": "#FFF7E6"}],
        }
        with tempfile.TemporaryDirectory() as directory:
            fake_client = FakeImageClient()
            with patch.dict("os.environ", {"GENESIS_CREATIVE_IMAGE_PROVIDER": "openai", "GENESIS_OPENAI_IMAGE_LIMIT": "2"}):
                manifest = generate_creative_assets(Path(directory), creative_pack, image_client=fake_client)  # type: ignore[arg-type]

            self.assertEqual(manifest["provider"], "openai-images")
            self.assertEqual(manifest["openaiImagesGenerated"], 2)
            self.assertEqual(len(fake_client.prompts), 2)
            self.assertGreaterEqual(manifest["summary"]["png"], 1)


if __name__ == "__main__":
    unittest.main()
