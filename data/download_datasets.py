"""Download the 3 Bangladesh HuggingFace datasets into data/raw/*.csv."""

import os

from datasets import load_dataset

RAW_DIR = os.path.join(os.path.dirname(__file__), "raw")

DATASETS = {
    "institutions": "Mahadih534/Institutional-Information-of-Bangladesh",
    "hospitals": "Mahadih534/all-bangladeshi-hospitals",
    "restaurants": "Mahadih534/Bangladeshi-Restaurant-Data",
}


def main():
    os.makedirs(RAW_DIR, exist_ok=True)
    for name, repo_id in DATASETS.items():
        print(f"Downloading {repo_id} ...")
        df = load_dataset(repo_id, split="train").to_pandas()
        out_path = os.path.join(RAW_DIR, f"{name}.csv")
        df.to_csv(out_path, index=False)
        print(f"  -> {out_path} ({len(df)} rows, {len(df.columns)} columns)")


if __name__ == "__main__":
    main()
