from pathlib import Path

spec_path = Path(__file__).resolve().parent.parent / "SPEC_LIST.md"
text = spec_path.read_text(encoding="utf-8")

required_sections = [
    "# Global specification list",
    "## Implemented / satisfied",
    "## Planned / future work",
]
missing = [section for section in required_sections if section not in text]
if missing:
    raise SystemExit(f"SPEC_LIST.md is missing required sections: {missing}")

implemented = text.count("- [x]")
planned = text.count("- [ ]")
if implemented == 0 and planned == 0:
    raise SystemExit("SPEC_LIST.md does not contain any tracked implementation or future items.")

print(f"SPEC_LIST.md OK: {implemented} implemented items, {planned} planned items")
