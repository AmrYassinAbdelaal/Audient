#!/usr/bin/env python3
"""
Evaluate the accuracy of the AI Audience Agent against the test dataset.

This script:
1. Loads the test dataset
2. Runs each prompt through the agent
3. Compares results with expected output
4. Calculates accuracy metrics
5. Generates a detailed report
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple
from collections import defaultdict
import argparse

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.agent import build_agent_graph


def load_dataset(dataset_path: Path) -> List[Dict[str, Any]]:
    """Load the test dataset from JSON file."""
    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("test_cases", [])


def normalize_filter(filter_dict: Dict[str, Any]) -> Tuple:
    """Normalize a filter to a comparable tuple."""
    field = filter_dict.get("field", "").lower()
    operator = filter_dict.get("operator", "")
    value = filter_dict.get("value")
    
    # Normalize value for comparison
    if isinstance(value, str):
        value = value.lower()
    elif isinstance(value, list):
        value = tuple(sorted([v.lower() if isinstance(v, str) else v for v in value]))
    
    return (field, operator, value)


def compare_filters(expected: List[Dict[str, Any]], actual: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compare expected and actual filters.
    
    Returns:
        Dictionary with comparison results
    """
    # Normalize filters for comparison
    expected_normalized = {normalize_filter(f) for f in expected}
    actual_normalized = {normalize_filter(f) for f in actual}
    
    # Calculate metrics
    correct = len(expected_normalized & actual_normalized)
    missing = expected_normalized - actual_normalized
    extra = actual_normalized - expected_normalized
    
    return {
        "expected_count": len(expected),
        "actual_count": len(actual),
        "correct_count": correct,
        "missing_count": len(missing),
        "extra_count": len(extra),
        "missing": list(missing),
        "extra": list(extra),
        "accuracy": correct / len(expected) if expected else 0,
    }


def evaluate_test_case(
    test_case: Dict[str, Any],
    agent_graph,
    language: str = "en"
) -> Dict[str, Any]:
    """Evaluate a single test case.
    
    Args:
        test_case: Test case dictionary
        agent_graph: Compiled agent graph
        language: Language to test ("en" or "ar")
        
    Returns:
        Evaluation results dictionary
    """
    test_id = test_case["id"]
    prompt_key = f"prompt_{language}"
    prompt = test_case.get(prompt_key, "")
    expected_filters = test_case["expected_output"]["filters"]
    
    print(f"  Testing case {test_id} ({language}): {prompt[:50]}...")
    
    try:
        # Run the agent
        result = agent_graph.invoke({"prompt": prompt})
        output = result.get("output", {})
        actual_filters = output.get("filters", [])
        errors = output.get("errors", [])
        
        # Compare results
        comparison = compare_filters(expected_filters, actual_filters)
        
        return {
            "test_id": test_id,
            "language": language,
            "prompt": prompt,
            "expected_filters": expected_filters,
            "actual_filters": actual_filters,
            "errors": errors,
            "success": comparison["accuracy"] >= 0.8,  # 80% match threshold
            "comparison": comparison,
        }
    
    except Exception as e:
        print(f"    ❌ Error: {str(e)}")
        return {
            "test_id": test_id,
            "language": language,
            "prompt": prompt,
            "expected_filters": expected_filters,
            "actual_filters": [],
            "errors": [str(e)],
            "success": False,
            "comparison": {
                "expected_count": len(expected_filters),
                "actual_count": 0,
                "correct_count": 0,
                "missing_count": len(expected_filters),
                "extra_count": 0,
                "accuracy": 0,
            },
        }


def calculate_overall_metrics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate overall accuracy metrics from results."""
    total = len(results)
    successful = sum(1 for r in results if r["success"])
    
    # Field-level metrics
    total_expected_fields = sum(r["comparison"]["expected_count"] for r in results)
    total_correct_fields = sum(r["comparison"]["correct_count"] for r in results)
    
    # Language-specific metrics
    by_language = defaultdict(lambda: {"total": 0, "successful": 0})
    for r in results:
        lang = r["language"]
        by_language[lang]["total"] += 1
        if r["success"]:
            by_language[lang]["successful"] += 1
    
    return {
        "total_tests": total,
        "successful_tests": successful,
        "failed_tests": total - successful,
        "overall_accuracy": (successful / total * 100) if total > 0 else 0,
        "field_extraction_accuracy": (total_correct_fields / total_expected_fields * 100) if total_expected_fields > 0 else 0,
        "by_language": {
            lang: {
                "total": stats["total"],
                "successful": stats["successful"],
                "accuracy": (stats["successful"] / stats["total"] * 100) if stats["total"] > 0 else 0,
            }
            for lang, stats in by_language.items()
        },
    }


def generate_report(results: List[Dict[str, Any]], metrics: Dict[str, Any], output_file: Path = None):
    """Generate and print evaluation report."""
    print("\n" + "="*70)
    print("📊 EVALUATION REPORT")
    print("="*70)
    
    print(f"\n📈 Overall Metrics:")
    print(f"  Total Tests: {metrics['total_tests']}")
    print(f"  Successful: {metrics['successful_tests']} ✅")
    print(f"  Failed: {metrics['failed_tests']} ❌")
    print(f"  Overall Accuracy: {metrics['overall_accuracy']:.2f}%")
    print(f"  Field Extraction Accuracy: {metrics['field_extraction_accuracy']:.2f}%")
    
    print(f"\n🌍 By Language:")
    for lang, stats in metrics["by_language"].items():
        print(f"  {lang.upper()}:")
        print(f"    Total: {stats['total']}")
        print(f"    Successful: {stats['successful']}")
        print(f"    Accuracy: {stats['accuracy']:.2f}%")
    
    # Show failed tests
    failed_tests = [r for r in results if not r["success"]]
    if failed_tests:
        print(f"\n❌ Failed Tests ({len(failed_tests)}):")
        for r in failed_tests[:10]:  # Show first 10 failures
            print(f"\n  Test #{r['test_id']} ({r['language']})")
            print(f"  Prompt: {r['prompt'][:60]}...")
            print(f"  Expected {r['comparison']['expected_count']} filters, got {r['comparison']['actual_count']}")
            if r['comparison']['missing']:
                print(f"  Missing: {r['comparison']['missing']}")
            if r['errors']:
                print(f"  Errors: {r['errors']}")
    
    # Success/Failure summary
    print(f"\n{'='*70}")
    if metrics["overall_accuracy"] >= 90:
        print("✅ SUCCESS: Accuracy target met (≥90%)")
    elif metrics["overall_accuracy"] >= 85:
        print("⚠️  WARNING: Accuracy below target but acceptable (85-90%)")
    else:
        print("❌ FAILURE: Accuracy below acceptable threshold (<85%)")
    print("="*70)
    
    # Save detailed report to file
    if output_file:
        report_data = {
            "metrics": metrics,
            "results": results,
        }
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Detailed report saved to: {output_file}")


def main():
    """Main evaluation function."""
    parser = argparse.ArgumentParser(description="Evaluate AI Audience Agent accuracy")
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path(__file__).parent.parent / "app" / "tests" / "dataset.json",
        help="Path to test dataset JSON file",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Path to save detailed report JSON",
    )
    parser.add_argument(
        "--language",
        choices=["en", "ar", "both"],
        default="both",
        help="Which language(s) to test",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of test cases",
    )
    
    args = parser.parse_args()
    
    print("🤖 AI Audience Agent - Accuracy Evaluation")
    print("="*70)
    
    # Load dataset
    print(f"\n📂 Loading dataset from: {args.dataset}")
    dataset = load_dataset(args.dataset)
    
    if args.limit:
        dataset = dataset[:args.limit]
    
    print(f"✅ Loaded {len(dataset)} test cases")
    
    # Build agent graph
    print("\n🔧 Building agent graph...")
    agent_graph = build_agent_graph()
    print("✅ Agent graph ready")
    
    # Run evaluations
    print("\n🧪 Running evaluations...")
    results = []
    
    for test_case in dataset:
        if args.language in ["en", "both"]:
            result = evaluate_test_case(test_case, agent_graph, "en")
            results.append(result)
        
        if args.language in ["ar", "both"]:
            result = evaluate_test_case(test_case, agent_graph, "ar")
            results.append(result)
    
    # Calculate metrics
    print("\n📊 Calculating metrics...")
    metrics = calculate_overall_metrics(results)
    
    # Generate report
    generate_report(results, metrics, args.output)


if __name__ == "__main__":
    main()

