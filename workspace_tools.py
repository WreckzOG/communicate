from pathlib import Path

ROOT = Path("workspace/coffee-site").resolve()
ROOT.mkdir(parents=True, exist_ok=True)


def safe_path(filename):
    path = (ROOT / filename).resolve()

    if ROOT not in path.parents and path != ROOT:
        raise ValueError("Path outside workspace")

    return path


def snapshot():
    files = []

    for path in ROOT.rglob("*"):
        if path.is_file():
            files.append(path)

    if not files:
        return "[WORKSPACE EMPTY]"

    output = []

    for path in files:
        relative = path.relative_to(ROOT)

        try:
            content = path.read_text(encoding="utf-8")
        except Exception:
            content = "[BINARY/UNREADABLE FILE]"

        output.append(
            f"\n--- FILE: {relative} ---\n"
            f"{content}\n"
            f"--- END FILE ---"
        )

    return "\n".join(output)


def apply_writes(response):
    lines = response.splitlines()

    writing = False
    filename = None
    buffer = []
    written = []

    for line in lines:

        if line.startswith("WRITE:") and not writing:
            filename = line[len("WRITE:"):].strip()
            buffer = []
            writing = True
            continue

        if line.strip() == "ENDWRITE" and writing:
            path = safe_path(filename)

            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("\n".join(buffer), encoding="utf-8")

            written.append(filename)

            writing = False
            filename = None
            buffer = []
            continue

        if writing:
            buffer.append(line)

    return written


def extract_packet(response):
    for line in reversed(response.splitlines()):
        line = line.strip()

        if line.startswith("C0|"):
            return line

    return None
