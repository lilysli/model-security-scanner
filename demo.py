from pathlib import Path
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from textattack.models.wrappers import HuggingFaceModelWrapper
from textattack.attack_recipes import DeepWordBugGao2018  # much faster, char-level
from textattack import Attacker, AttackArgs
from textattack.datasets import Dataset as TA_Dataset

# Create output directory
OUT_DIR = Path("outputs")
OUT_DIR.mkdir(exist_ok=True)

MODEL = "textattack/bert-base-uncased-SST-2"  

SAMPLE = [("I loved the cinematography and the story was touching.", 1)]

# Build TextAttack-compatible model wrapper around HuggingFace model
def build_wrapper(model_name):
    tok = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    return HuggingFaceModelWrapper(model, tok)

# Run attack
def run_attack():
    wrapper = build_wrapper(MODEL)
    # Convert sample to TextAttack Dataset
    ta_dataset = TA_Dataset(SAMPLE)

    # Configure attack
    attack_args = AttackArgs(
        num_examples=1, # number of samples to attack
        log_to_csv=str(OUT_DIR / "attack_log.csv"), # log results to CSV
        disable_stdout=False, # print progress to console
        query_budget=500  # max number of model queries allowed during attack
    )

    # Build attack object from attack recipe
    attack = DeepWordBugGao2018.build(wrapper)

    # Create attacker
    attacker = Attacker(attack, ta_dataset, attack_args)

    # Execute attack
    results = attacker.attack_dataset()

    # Print results
    for r in results:
        print("Result:", r)
    print("Attack complete. CSV:", OUT_DIR / "attack_log.csv")

if __name__ == "__main__":
    run_attack()
