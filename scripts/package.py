import os
import zipfile
import json
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPECTED_VERSION = "1.1.0"
DEFAULT_OUT = os.path.abspath(os.path.join(ROOT, os.pardir, os.pardir))

# Files/folders to include in the package (manifest must be at zip root)
INCLUDE = [
    "manifest.json",
    "popup.html",
    "popup.css",
    "popup.js",
    "LICENSE",
    "README.md",
    "_locales",
    "icons",
    "fonts",
]

# Folders/files to exclude from the package
EXCLUDE_DIRS = {".codebuddy", ".git", "scripts", "store-assets"}
EXCLUDE_FILES = {"tinypalette-1.0.0.zip"}


def collect_paths():
    paths = []
    for rel in INCLUDE:
        full = os.path.join(ROOT, rel)
        if os.path.isdir(full):
            for dp, dns, fns in os.walk(full):
                dns[:] = [d for d in dns if d not in EXCLUDE_DIRS]
                for fn in fns:
                    if fn in EXCLUDE_FILES:
                        continue
                    fpath = os.path.join(dp, fn)
                    arc = os.path.relpath(fpath, ROOT)
                    paths.append((fpath, arc))
        elif os.path.isfile(full):
            if os.path.basename(full) in EXCLUDE_FILES:
                continue
            paths.append((full, rel))
    return paths


def main():
    with open(os.path.join(ROOT, "manifest.json"), encoding="utf-8") as f:
        m = json.load(f)

    # 1. version matches expectation
    assert m["manifest_version"] == 3, "manifest_version must be 3"
    assert m["version"] == EXPECTED_VERSION, f"version must be {EXPECTED_VERSION}, got {m['version']}"

    # 2. referenced files exist
    refs = []
    for k in ("default_popup",):
        refs.append(m["action"][k])
    for size in ("16", "48", "128"):
        refs.append(m["action"]["default_icon"][size])
        refs.append(m["icons"][size])
    missing = [r for r in refs if not os.path.exists(os.path.join(ROOT, r))]
    assert not missing, f"missing referenced files: {missing}"

    zip_name = f"tinypalette-{EXPECTED_VERSION}.zip"
    zip_path = os.path.join(ROOT, zip_name)
    paths = collect_paths()

    # 3. write zip with manifest at root
    if os.path.exists(zip_path):
        os.remove(zip_path)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for fpath, arc in paths:
            z.write(fpath, arc)

    # 4. re-read from zip and verify
    with zipfile.ZipFile(zip_path) as z:
        names = z.namelist()
        assert "manifest.json" in names, "manifest.json not at zip root"
        inside = json.loads(z.read("manifest.json").decode("utf-8"))
        assert inside["name"] == m["name"], "manifest name mismatch"
        assert inside["version"] == EXPECTED_VERSION

    print(f"Package built: {zip_path}")
    print(f"Files in zip: {len(names)}")

    # 5. copy to default folder and verify byte-identical
    dst = os.path.join(DEFAULT_OUT, zip_name)
    shutil.copyfile(zip_path, dst)
    with open(zip_path, "rb") as a, open(dst, "rb") as b:
        assert a.read() == b.read(), "copy mismatch"
    print(f"Copied to default folder: {dst}")


if __name__ == "__main__":
    main()
