from pathlib import Path
import argparse
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from textattack.models.wrappers import HuggingFaceModelWrapper
from textattack.attack_recipes import DeepWordBugGao2018, PWWSRen2019
from textattack import Attacker, AttackArgs
from textattack.datasets import Dataset as TA_Dataset
from datasets import load_dataset
import torch


# Create output directory
OUT_DIR = Path("outputs")
OUT_DIR.mkdir(exist_ok=True)

MODEL = "textattack/bert-base-uncased-SST-2"  

SAMPLE = [
    (ex["sentence"], ex["label"])
    for ex in load_dataset("glue", "sst2", split="validation[:5]")
]

def parse_args():
    parser = argparse.ArgumentParser(
        prog="Model Security Scanner",
        description="A lightweight tool to assess NLP model robustness via adversarial attacks.",
        epilog="Choose an attack to probe vulnerabilities: typos, synonyms, or semantic perturbations.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "--attack",
        choices=["deepwordbug", "pwws"],
        default="deepwordbug",
        help=(
            "Attack recipe:\n"
            "  • deepwordbug: Char-level typos (swap/flip/delete) → tests typo robustness.\n"
            "  • pwws: Word-level synonym swaps (WordNet) → tests lexical robustness."
        ),
    )
    parser.add_argument(
        "--num-examples", type=int, default=5,
        help="Number of samples to attack (default: 5 from SST-2 validation)"
    )
    parser.add_argument(
        "--query-budget", type=int, default=500,
        help="Max model queries per example (default: 500)"
    )

    args = parser.parse_args()

    # Srict validation of attack choice
    valid_attacks = {"deepwordbug", "pwws"}
    attack_clean = args.attack.lower().strip()
    if attack_clean not in valid_attacks:
        print(f"\n❌ Invalid attack: '{args.attack}'", file=sys.stderr)
        print(f"✅ Valid options: {', '.join(valid_attacks)}", file=sys.stderr)
        print("   Run with --help for details.\n", file=sys.stderr)
        sys.exit(1)

    args.attack = attack_clean  # normalize
    return args

# Build TextAttack-compatible model wrapper around HuggingFace model
def build_wrapper(model_name):
    tok = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    
    # Enable MPS (or fallback to CPU)
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    model.to(device)

    return HuggingFaceModelWrapper(model, tok)

# Run attack
def run_attack(attack_name,num_samples, q_budget):
    print(f"\n🔍 Model Security Scanner — Running '{attack_name}' attack...\n")

    wrapper = build_wrapper(MODEL)
    # Convert sample to TextAttack Dataset
    ta_dataset = TA_Dataset(SAMPLE[:num_samples])

    # Configure attack
    attack_args = AttackArgs(
        num_examples=num_samples, # number of samples to attack
        log_to_csv=str(OUT_DIR / "attack_log.csv"), # log results to CSV
        disable_stdout=False, # print progress to console
        query_budget=q_budget  # max number of model queries allowed during attack
    )

# Build attack from recipe
    attack = (
        DeepWordBugGao2018.build(wrapper)
        if attack_name == "deepwordbug"
        else PWWSRen2019.build(wrapper)
    )

    # Create attacker
    attacker = Attacker(attack, ta_dataset, attack_args)

    # Execute attack
    results = attacker.attack_dataset()

    # Print results
    for r in results:
        print("Result:", r)
    print("Attack complete. CSV:", OUT_DIR / "attack_log.csv")

if __name__ == "__main__":
    args = parse_args()
    run_attack(args.attack, args.num_examples, args.query_budget)