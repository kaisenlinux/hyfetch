import json
from pathlib import Path

import requests

if __name__ == '__main__':
    md = requests.get("https://raw.githubusercontent.com/lukas-w/font-logos/refs/heads/master/README.md").text
    md = [[field.strip().strip('`').replace('Linux', '').replace('GNU/', '').strip() for field in line.split('|')[1:-1]]
          for line in md.splitlines() if line.startswith("|") and 'fl-' in line]
    md = {name: chr(int(char, 16)) for name, css, code, char, img in md}
    Path("font_logos.json").write_text(json.dumps(md, indent=2, ensure_ascii=False))
