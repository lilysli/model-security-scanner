# 🔍 Model Security Scanner
A lightweight CLI tool to assess NLP model robustness via fast, low-resource adversarial attacks — built for researchers and engineers evaluating model security on laptops.

---

This tool uses official attack recipes from [TextAttack](https://textattack.readthedocs.io/), a widely adopted framework for standardized adversarial evaluation in NLP:

- `deepwordbug` → [`DeepWordBugGao2018`](https://arxiv.org/abs/1801.04354):  
  Character-level perturbations (swap, flip, delete, insert). Fast, query-efficient, and model-agnostic — suitable for testing robustness to typographic noise.

- `pwws` → [`PWWSRen2019`](https://arxiv.org/abs/1908.08538):  
  Word-level synonym replacement using WordNet and word importance ranking. Maintains fluency while probing lexical sensitivity.

It supports Hugging Face NLPs — simply provide the model identifier in the arguments when running the tool.

Attack results (original/perturbed texts, predictions, query counts, outcomes) are logged to CSV for reproducible analysis and reporting.

---

## 🚀 Quick Start

### 1. Install dependencies
`pip install -r requirements.txt`

### 2. Run the scanner
Default: test BERT on SST-2 with DeepWordBug
`python scanner.py`

Try PWWS synonym attack
`python scanner.py --attack pwws`

Use your own model (HF ID or local path)
`python scanner.py --model cardiffnlp/twitter-roberta-base-sentiment`

🛠️ Command-Line Interface

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--attack` | `str` | `deepwordbug` | Adversarial recipe: `deepwordbug` (character-level) or `pwws` (word-level synonym substitution). |
| `--model` | `str` | `textattack/bert-base-uncased-SST-2` | Hugging Face model identifier or local path (must support `AutoModelForSequenceClassification`). |
| `--num-examples` | `int` | `5` | Number of validation examples from SST-2 to evaluate. |
| `--query-budget` | `int` | `500` | Maximum model queries per attack instance (enforces efficiency and fairness). |
