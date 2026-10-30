# backend/scripts/export_dataset.py
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.export_service import ExportService

def main():
    print(f"============================================================")
    print(f" ColdChain IQ Dataset Export & Manifest Utility")
    print(f"============================================================")

    res = ExportService.export_all_datasets()
    print(f"\n Export Status: {res['status']}")
    print(f" Export Directory: {res['export_path']}")
    print("\n Exported Tables & SHA-256 Checksums:")
    for tbl, meta in res["manifest"]["tables"].items():
        print(f"   - {tbl:22s} | Records: {meta['record_count']:6d} | CSV: {meta['csv_file']:25s} | SHA256: {meta['csv_sha256'][:16]}...")

    print(f"\n Manifest saved to: {os.path.join(res['export_path'], 'manifest.json')}")

if __name__ == "__main__":
    main()
