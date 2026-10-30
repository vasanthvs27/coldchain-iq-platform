# backend/tests/test_reproducibility.py
import pytest
import os
import json
from app.services.export_service import ExportService
from app.services.reproducibility_service import ReproducibilityService
from app.config import Config

def test_tc38_csv_export():
    """TC38: Export service produces products.csv, shipments.csv, etc."""
    ExportService.export_all_datasets()
    assert os.path.exists(os.path.join(Config.EXPORTS_DIR, "products.csv"))
    assert os.path.exists(os.path.join(Config.EXPORTS_DIR, "shipments.csv"))

def test_tc39_json_export():
    """TC39: Export service produces valid JSON tables."""
    prod_json = os.path.join(Config.EXPORTS_DIR, "products.json")
    assert os.path.exists(prod_json)
    with open(prod_json, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, list)

def test_tc40_sql_seed_export():
    """TC40: Export service produces executable SQL seed file."""
    sql_seed = os.path.join(Config.EXPORTS_DIR, "seed_operational_dataset.sql")
    assert os.path.exists(sql_seed)
    with open(sql_seed, "r", encoding="utf-8") as f:
        content = f.read()
    assert "INSERT INTO" in content

def test_tc41_fixed_seed_reproducibility():
    """TC41: Identical fixed seed produces matching logical checksums."""
    res = ReproducibilityService.verify_reproducibility(seed=20261022, sample_count=5)
    assert res["reproducibility_match"] is True
    assert res["run_a"]["checksum_sha256"] == res["run_b"]["checksum_sha256"]

def test_tc42_different_seed_variation():
    """TC42: Different seeds generate distinct dataset checksums."""
    res = ReproducibilityService.verify_reproducibility(seed=20261022, sample_count=5)
    assert res["variation_distinctness"] is True
    assert res["run_a"]["checksum_sha256"] != res["run_c_alt_seed"]["checksum_sha256"]

def test_tc43_manifest_generation():
    """TC43: Manifest.json contains table lists and SHA-256 checksums."""
    manifest_file = os.path.join(Config.EXPORTS_DIR, "manifest.json")
    assert os.path.exists(manifest_file)
    with open(manifest_file, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    assert "tables" in manifest
    assert "products" in manifest["tables"]
    assert "csv_sha256" in manifest["tables"]["products"]
