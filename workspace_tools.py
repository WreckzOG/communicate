from pathlib import Path

ROOT = Path("workspace/coffee-site")
ROOT.mkdir(parents=True, exist_ok=True)


def list_files():
    files = []
    for path in ROOT.rglob("*"):
        if path.is_file():
            files.append(str(path.relative_to(ROOT)))
    return files


def read_file(filename):
    path = ROOT / filename

    if not path.exists():
        return f"FILE_NOT_FOUND:{filename}"

    return path.read_text(encoding="utf-8")


def write_file(filename, content):
    path = ROOT / filename
    path.parent.mkdir(parents=True, exist_ok=True)

    path.write_text(content, encoding="utf-8")

    return f"WROTE:{filename}"
