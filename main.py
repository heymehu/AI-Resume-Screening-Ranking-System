from __future__ import annotations

import argparse
from pathlib import Path

from src.pipeline import ResumePipeline


def cli() -> None:
    parser = argparse.ArgumentParser(description="Resume screening and ranking pipeline")
    parser.add_argument("--input", default="./resumes", help="Directory containing resume PDFs or text files")
    parser.add_argument("--output", default="./output/results.json", help="Path to output JSON file")
    args = parser.parse_args()

    pipeline = ResumePipeline(args.input, args.output)
    results = pipeline.run()
    summary = results["batch_summary"]

    print("=" * 60)
    print("AI RESUME SCREENING RESULTS")
    print("=" * 60)
    print(f"Total Resumes:       {summary['total_resumes']}")
    print(f"Successfully Parsed: {summary['successfully_parsed']}")
    print(f"Eligible:            {summary['eligible']}")
    print(f"Rejected:            {summary['rejected']}")
    print(f"Failed:              {summary['failed_or_unreadable']}")

    print("\n" + "=" * 60)
    print("FINAL CANDIDATE RANKING")
    print("=" * 60)
    print(f"{'Rank':<6}{'Candidate':<30}{'Status':<12}{'Score':<9}Breakdown")
    print("-" * 105)
    for candidate in results["candidates"]:
        reason = "; ".join(candidate["rejection_reasons"])
        print(
            f"{candidate['rank']:<6}"
            f"{candidate['candidate_name'][:28]:<30}"
            f"{candidate['status']:<12}"
            f"{candidate['total_score']:>3}/100   "
            f"{candidate['score_display']}"
        )
        if reason:
            print(f"      Rejection reason: {reason}")
    print(f"\nDetailed candidate evidence written to: {Path(args.output)}")


if __name__ == "__main__":
    cli()
