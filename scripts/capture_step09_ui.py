from __future__ import annotations
import os
import subprocess
import sys
from pathlib import Path

STATES = ["UI-002","UI-003","UI-010","UI-013","UI-014","UI-027","UI-035","UI-041"]
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "step09_actual"
OUT.mkdir(parents=True, exist_ok=True)
env = os.environ.copy()
env.setdefault("QT_QPA_PLATFORM", "offscreen")
for state in STATES:
    target = OUT / f"{state}_ACTUAL.png"
    cmd = [sys.executable, "-m", "aavc", "--ui-state", state, "--capture-path", str(target)]
    print("RUN", " ".join(cmd))
    subprocess.run(cmd, cwd=ROOT, env=env, check=True)
print(f"Captured {len(STATES)} screenshots in {OUT}")
