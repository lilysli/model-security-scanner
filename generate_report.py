from datetime import datetime
from pathlib import Path

def save_markdown_report(model_name: str, attack_name: str, results, output_dir=Path("outputs")):
    from textattack.attack_results import SuccessfulAttackResult, FailedAttackResult, SkippedAttackResult
    
    output_dir.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = output_dir / f"report_{ts}.md"

    successful = sum(1 for r in results if isinstance(r, SuccessfulAttackResult))
    failed = sum(1 for r in results if isinstance(r, FailedAttackResult))
    skipped = sum(1 for r in results if isinstance(r, SkippedAttackResult))
    total = len(results)

    query_list = [
        r.perturbed_result.num_queries 
        for r in results 
        if hasattr(r, 'perturbed_result') and r.perturbed_result is not None
    ]

    avg_queries = sum(query_list) / len(query_list) if query_list else 0.0

    original_acc = 100.0 * (total - skipped) / total if total else 0.0
    attacked_acc = 100.0 * failed / total if total else 0.0
    success_rate = 100.0 * successful / (successful + failed) if (successful + failed) else 0.0

    # Build report
    lines = [
        f"# 🔍 Model Security Scan Report",
        f"**Model**: `{model_name}` | **Attack**: `{attack_name}` | **Examples**: {total}",
        f"**Date**: {datetime.now():%Y-%m-%d %H:%M:%S}",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Successful | {successful} |",
        f"| Failed | {failed} |",
        f"| Skipped | {skipped} |",
        f"| Original accuracy | {original_acc:.1f}% |",
        f"| Accuracy under attack | {attacked_acc:.1f}% |",
        f"| Attack success rate | {success_rate:.1f}% |",
        f"| Avg. queries | {avg_queries:.1f} |",
        "",
        "## 📋 Examples",
    ]

    for i, r in enumerate(results, 1):
        # Status
        status = (
            "✅ **Successful**" if isinstance(r, SuccessfulAttackResult) else
            "❌ **Failed**" if isinstance(r, FailedAttackResult) else
            "⏭️ **Skipped**"
        )

        # Texts (safe extraction)
        orig = r.original_result.attacked_text.text
        pert = r.perturbed_result.attacked_text.text if r.perturbed_result else "—"

        lines.extend([
            f"### Example {i}: {status}",
            "**Original**  ",
            f"`{orig}`",
            "",
            "**Perturbed**  ",
            f"`{pert}`",
            "",
        ])

    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ Report saved to: {path}")