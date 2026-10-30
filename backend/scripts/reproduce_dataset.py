# backend/scripts/reproduce_dataset.py
import argparse
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.reproducibility_service import ReproducibilityService

def main():
    parser = argparse.ArgumentParser(description="ColdChain IQ Reproducibility Verification CLI")
    parser.add_argument("--seed", type=int, default=20261022, help="Seed to test (default: 20261022)")
    parser.add_argument("--samples", type=int, default=20, help="Sample count per generation pass")
    args = parser.parse_args()

    print(f"============================================================")
    print(f" ColdChain IQ Deterministic Reproducibility Engine")
    print(f" Testing SEED: {args.seed} with sample size: {args.samples}")
    print(f"============================================================")

    res = ReproducibilityService.verify_reproducibility(seed=args.seed, sample_count=args.samples)
    print(f"\n Dual-Pass Verification Status: {res['status']}")
    print(f"   [Run A (Seed {args.seed})] SHA256: {res['run_a']['checksum_sha256']}")
    print(f"   [Run B (Seed {args.seed})] SHA256: {res['run_b']['checksum_sha256']}")
    print(f"   [Run C (Seed {res['alternative_seed']})] SHA256: {res['run_c_alt_seed']['checksum_sha256']}")
    print(f"\n Logical Checksum Match (Run A == Run B): {res['reproducibility_match']}")
    print(f" Meaningful Variation (Run A != Run C): {res['variation_distinctness']}")

if __name__ == "__main__":
    main()
