# STEP 13 — PERFORMANCE BASELINE

## Established baseline
STEP 13 currently treats performance as a correctness boundary rather than claiming workstation benchmark numbers that have not been measured on the final package.

Verified characteristics:
- UI screenshots are captured from real PySide6 widgets on Windows CI without blocking/failure.
- background-job infrastructure uses a bounded `ThreadPoolExecutor` (default 4 workers) rather than unbounded thread creation.
- child processes have optional explicit timeouts.
- ProjectState/render behavior remains deterministic under the existing test suite.

## Not yet established
The following metrics are intentionally NOT claimed:
- launch time of the packaged RC on a clean Windows 11 PC;
- memory usage for 100/500/1000 scene projects;
- preview FPS under heavy media loads;
- full render speed relative to CapCut/Canva;
- GPU acceleration throughput;
- 4K render benchmark.

## STEP 14/15 acceptance direction
Record candidate version + SHA + PC/runner details before measuring. At minimum capture packaged launch/smoke duration, idle memory where practical, and one deterministic short render. Large-project and 4K benchmarking may remain a documented post-R1 optimization target if correctness is unaffected.
