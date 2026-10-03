# STEP 14 — Release Candidate & Packaging

Status: **IN PROGRESS**

Target RC: `AI Automatic Video Composer 0.1.0-rc1` untuk Windows 11 x64.

Implemented for the RC gate:
- version bumped to `0.1.0rc1`
- PyInstaller onedir packaging includes resources, schemas, licenses and RC release notes
- packaged GUI executable supports file-based foundation smoke verification
- portable verifier checks smoke marker, required schema/release notes and forbidden secret/user files
- dedicated Windows Release Candidate workflow builds ZIP + SHA256SUMS and uploads an Actions artifact

STEP 14 becomes PASS only after the release-candidate workflow produces and verifies the Windows artifact successfully.
