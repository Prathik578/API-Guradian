"""Executable evaluation harness for benchmarks."""

import json
import os
import sys
from pathlib import Path


def run_benchmark(benchmark_path: Path) -> dict[str, Any]:
    print(f"Running benchmark {benchmark_path.name}...")
    with open(benchmark_path, "r") as f:
        spec = json.load(f)
        
    fixtures = spec.get("fixtures", {})
    expected_symbols = spec.get("expected_symbols_affected", [])
    expected_impact = spec.get("expected_impact_classification", "confirmed_affected")
    acceptance_criteria = spec.get("acceptance_criteria", [])
    
    # 1. Run Analyzer
    from api_guardian.analysis.javascript.analyzer import JSTSAnalyzer
    analyzer = JSTSAnalyzer()
    
    found_symbols = set()
    for filepath, source_code in fixtures.items():
        if filepath.endswith(".js") or filepath.endswith(".ts"):
            module = analyzer.analyze_file(filepath, source_code)
            for symbol in module.symbols:
                for call_site in symbol.call_sites:
                    found_symbols.add(call_site.target_name)
                    
    # 2. Evaluate Recall/Precision
    true_positives = len([s for s in expected_symbols if s in found_symbols])
    false_positives = len([s for s in found_symbols if s not in expected_symbols])
    false_negatives = len([s for s in expected_symbols if s not in found_symbols])
    
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 1.0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 1.0
    
    print(f"  Precision: {precision:.2f}")
    print(f"  Recall:    {recall:.2f}")
    
    # In a full pipeline we would also run the Migrator and then parse the diff to check acceptance_criteria.
    
    return {
        "name": spec["name"],
        "precision": precision,
        "recall": recall,
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_negatives": false_negatives
    }


def main():
    benchmarks_dir = Path(__file__).parent
    results = []
    
    for provider_dir in benchmarks_dir.iterdir():
        if provider_dir.is_dir() and provider_dir.name != "runner" and provider_dir.name != "__pycache__":
            for bench_file in provider_dir.glob("*.json"):
                res = run_benchmark(bench_file)
                results.append(res)
                
    print("\nBenchmark Summary:")
    for r in results:
        print(f"  {r['name']}: Precision={r['precision']:.2f}, Recall={r['recall']:.2f}")


if __name__ == "__main__":
    main()
