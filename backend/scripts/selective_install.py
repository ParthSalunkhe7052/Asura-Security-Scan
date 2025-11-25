import sys
import subprocess
import re
import os
from importlib import metadata


def norm_name(n):
    i = n.find("[")
    return n[:i] if i != -1 else n


def parse_req(line):
    s = line.split("#", 1)[0].strip()
    if not s:
        return None, None, None
    m = re.match(r"^([A-Za-z0-9_.\-]+(?:\[[^\]]+\])?)(.*)$", s)
    if not m:
        return None, None, None
    name = m.group(1).strip()
    specs = m.group(2).strip()
    return s, name, specs


def tuple_ver(v):
    n = []
    for x in re.split(r"[._-]", v):
        try:
            n.append(int(x))
        except Exception:
            n.append(x)
    return tuple(n)


def satisfies(ver, spec):
    spec = spec.strip()
    if not spec:
        return True
    ops = [">=","<=","==","!=","<",">","~="]
    op = None
    for o in ops:
        if spec.startswith(o):
            op = o
            break
    if not op:
        return True
    target = spec[len(op):].strip()
    if op == "==":
        return ver == target
    if op == "!=":
        return ver != target
    tv = tuple_ver(ver)
    tt = tuple_ver(target)
    if op == ">=":
        return tv >= tt
    if op == ">":
        return tv > tt
    if op == "<=":
        return tv <= tt
    if op == "<":
        return tv < tt
    if op == "~=":
        pref = target.split(".")
        if len(pref) > 1:
            upper = pref[0] + "." + str(int(pref[1]) + 1)
        else:
            upper = str(int(pref[0]) + 1)
        return tv >= tt and tv < tuple_ver(upper)
    return True


def all_specs_satisfied(ver, specs):
    if not specs:
        return True
    parts = [p.strip() for p in specs.split(",") if p.strip()]
    for p in parts:
        if not satisfies(ver, p):
            return False
    return True


def get_installed():
    d = {}
    for dist in metadata.distributions():
        name = (dist.metadata.get("Name") or dist.metadata.get("Summary") or dist.metadata.get("") or dist.metadata["Name"]).lower()
        d[name] = dist.version
    return d


def main():
    req_path = "requirements.txt"
    if len(sys.argv) > 2 and sys.argv[1] == "-r":
        req_path = sys.argv[2]
    print("Selecting packages to install from", req_path)
    with open(req_path, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
    parsed = []
    for line in lines:
        orig, name, specs = parse_req(line)
        if not orig:
            continue
        parsed.append((orig, name, specs))
    installed = get_installed()
    to_install = []
    skipped = []
    for orig, name, specs in parsed:
        base = norm_name(name).lower()
        ver = installed.get(base)
        if ver and all_specs_satisfied(ver, specs):
            skipped.append(orig)
        else:
            to_install.append(orig)
    total = len(parsed)
    print("Total requirements:", total)
    print("Already satisfied:", len(skipped))
    print("To install:", len(to_install))
    if skipped:
        print("Skipping:")
        for s in skipped:
            print("  ", s)
    if not to_install:
        print("All requirements satisfied")
    pip_exe = sys.executable
    print("Python executable:", pip_exe)
    try:
        out = subprocess.check_output([sys.executable, "-m", "pip", "-V"], text=True)
        print(out.strip())
    except Exception as e:
        print("pip -V failed:", e)
    processed = 0
    total_install = len(to_install)
    for req in to_install:
        processed += 1
        pct = int((processed / total_install) * 100) if total_install else 100
        print(f"Installing ({processed}/{total_install}) {req} [{pct}%]")
        subprocess.check_call([sys.executable, "-m", "pip", "install", req])
    print("Installation complete")
    print("Verifying...")
    installed2 = get_installed()
    missing = []
    for orig, name, specs in parsed:
        base = norm_name(name).lower()
        ver = installed2.get(base)
        if not ver or not all_specs_satisfied(ver, specs):
            missing.append(orig)
    if missing:
        print("Unresolved:")
        for m in missing:
            print("  ", m)
        sys.exit(1)
    print("All requirements satisfied in venv")
    try:
        proc = subprocess.run([sys.executable, "-m", "pip", "check"], capture_output=True, text=True)
        lines = [l.strip() for l in (proc.stdout or proc.stderr or "").splitlines() if l.strip()]
        conflicts = []
        for l in lines:
            m = re.search(r"requires (.+?), but you have ", l)
            if m:
                spec = m.group(1).strip()
                conflicts.append(spec)
        if conflicts:
            print("Resolving transitive dependencies:")
            for i, spec in enumerate(conflicts, 1):
                pct = int((i / len(conflicts)) * 100)
                print(f"Installing ({i}/{len(conflicts)}) {spec} [{pct}%]")
                subprocess.check_call([sys.executable, "-m", "pip", "install", spec])
            proc2 = subprocess.run([sys.executable, "-m", "pip", "check"], capture_output=True, text=True)
            if (proc2.stdout or proc2.stderr or "").strip():
                print((proc2.stdout or proc2.stderr).strip())
            else:
                print("Dependency conflicts resolved")
    except Exception as e:
        print("pip check failed:", e)


if __name__ == "__main__":
    main()