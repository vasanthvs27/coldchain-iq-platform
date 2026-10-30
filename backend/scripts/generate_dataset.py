# backend/scripts/generate_dataset.py
import argparse
import sys
import os

# Add backend to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.generator_service import DataGeneratorService

def main():
    parser = argparse.ArgumentParser(description="ColdChain IQ Synthetic Dataset Generator CLI")
    parser.add_argument("--mode", choices=["STARTER", "FULL"], default="STARTER", help="Generation mode (STARTER or FULL)")
    parser.add_argument("--shipments", type=int, default=None, help="Number of shipments to generate")
    parser.add_argument("--loggers", type=int, default=None, help="Number of loggers to allocate")
    parser.add_argument("--seed", type=int, default=20261022, help="Fixed random seed (default: 20261022)")
    parser.add_argument("--interval", type=int, default=10, help="Reading interval in minutes (default: 10)")
    
    args = parser.parse_args()
    print(f"============================================================")
    print(f" ColdChain IQ Synthetic Dataset Generator")
    print(f" Mode: {args.mode} | Seed: {args.seed} | Interval: {args.interval}m")
    print(f"============================================================")

    res = DataGeneratorService.run_generation(
        mode=args.mode,
        shipment_count=args.shipments,
        logger_count=args.loggers,
        seed=args.seed,
        reading_interval_minutes=args.interval
    )

    print("\n Generation Complete!")
    print(f" Run ID: {res['run_id']}")
    print(f" Records Generated Summary:")
    for k, v in res["summary"].items():
        print(f"   - {k}: {v:,}")
    print(f" Ground Truth Files:")
    print(f"   - CSV: {res['ground_truth_files']['csv']}")
    print(f"   - JSON: {res['ground_truth_files']['json']}")

if __name__ == "__main__":
    main()
