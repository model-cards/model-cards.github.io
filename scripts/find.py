"""find.py <provider/id> <regex> : print matches with page numbers (for grounding claims)."""
import re, sys
from pathlib import Path
doc, pat = sys.argv[1], re.compile(sys.argv[2], re.I)
page = None
for line in Path(f"data/md/{doc}.md").read_text().splitlines():
    m = re.match(r"<!-- page (\d+) -->", line)
    if m: page = int(m.group(1)); continue
    for mm in pat.finditer(line):
        s = max(0, mm.start() - 160); print(f"p.{page}: ...{line[s:mm.end() + 200]}...\n"); break
