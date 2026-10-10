import glob
import os

# Sections to remove entirely
STOP_SECTIONS = [
    "== References ==",
    "== See also ==",
    "== Further reading ==",
    "== External links ==",
    "== Notes ==",
    "== Bibliography ==",
]

def clean_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    cleaned_lines = []
    skip = False

    for line in lines:
        # Check if this line starts a section we want to skip
        if any(line.strip().startswith(sec) for sec in STOP_SECTIONS):
            skip = True
            continue
        
        # If we're in a skipped section and hit another header, stop skipping
        if skip:
            if line.strip().startswith("==") and not any(line.strip().startswith(sec) for sec in STOP_SECTIONS):
                skip = False
            else:
                continue
        
        # Remove citation brackets like [1], [2], [citation needed]
        import re
        line = re.sub(r"\[\d+\]", "", line)
        line = line.replace("[citation needed]", "")
        
        cleaned_lines.append(line)

    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(cleaned_lines)
    print(f"✅ Cleaned {filepath}")

# Run on all files in data/
for filepath in glob.glob("data/*.txt"):
    clean_file(filepath)