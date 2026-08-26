import argparse
import re
import sys
from pathlib import Path


FLAG_RE = re.compile(r"\b((?:flag|ctf|bitctf|bctf|picoCTF|HTB|DUCTF|CSCTF|SEKAI)[A-Za-z0-9_-]*\{\{?[^}\n\r]{4,}\}?\})", re.I)
COMMAND_RE = re.compile(r"^(?:PS [^>]+>|[$#>])\s*(.+)$|^(curl|python|python3|nc|ncat|sqlmap|ffuf|openssl|node)\b(.+)$")


def main():
    parser = argparse.ArgumentParser(description="Create a first-pass enriched CTF report skeleton from raw notes.")
    parser.add_argument("input", nargs="?", help="Raw notes/log file. Reads stdin when omitted.")
    parser.add_argument("--challenge", default="UNKNOWN", help="Challenge name")
    parser.add_argument("--category", default="UNKNOWN", help="CTF category or vulnerability class")
    args = parser.parse_args()

    text = Path(args.input).read_text(encoding="utf-8", errors="replace") if args.input else sys.stdin.read()
    flags = unique(FLAG_RE.findall(text))
    commands = extract_commands(text)

    print(f"# {args.challenge}\n")
    print(f"- Category: {args.category}")
    print(f"- Confirmed flag: {flags[-1] if flags else 'TODO: verify from real output'}")
    print("\n## Concept\n")
    print("TODO: Explain the vulnerability or puzzle primitive and why it exposes the flag.\n")
    print("## Reproducible Steps\n")
    print("1. TODO: Inspect the target or attachment.")
    print("2. TODO: Prove the primitive with a small payload or check.")
    print("3. TODO: Run the final exploit and verify the flag.\n")
    print("## Commands / Script\n")
    if commands:
        print("```bash")
        for command in commands[-12:]:
            print(command)
        print("```")
    else:
        print("TODO: Add exact commands or link the solve script.")
    print("\n## Evidence\n")
    print("- TODO: Paste or summarize the key verified output.")
    if flags:
        print(f"- Flag pattern observed {len(flags)} time(s).")


def unique(items):
    seen = set()
    out = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def extract_commands(text):
    commands = []
    for line in text.splitlines():
        line = line.strip()
        match = COMMAND_RE.match(line)
        if not match:
            continue
        if match.group(1):
            commands.append(match.group(1).strip())
        else:
            commands.append((match.group(2) + match.group(3)).strip())
    return unique(commands)


if __name__ == "__main__":
    main()
