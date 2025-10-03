import os, random
from datetime import datetime, timezone
import pandas as pd

now = datetime.now(timezone.utc)
today = now.strftime('%Y-%m-%d')

# Deterministic daily target between 5 and 20
random.seed(today)
target = random.randint(5, 20)

count = 0
try:
    df = pd.read_csv("iss_positions.csv")
    if "ts" in df.columns:
        count = sum(str(ts).startswith(today) for ts in df["ts"])
except Exception:
    pass

remaining_hours = 24 - now.hour

if count >= target:
    decision = False
    reason = f"already reached target {target} (count={count})"
else:
    remaining_needed = max(0, target - count)
    p = min(1.0, max(0.15, remaining_needed / max(1, remaining_hours)))
    decision = random.random() < p
    reason = (
        f"count={count}, target={target}, remaining_hours={remaining_hours}, p={p:.2f}"
    )

print(f"Decision={decision} ({reason})")

# Write output for GitHub Actions
with open(os.environ["GITHUB_OUTPUT"], "a") as fh:
    fh.write(f"run={'true' if decision else 'false'}\n")
