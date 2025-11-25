import shutil
import os
import subprocess

print(f"OS: {os.name}")
npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
print(f"Checking for: {npm_cmd}")

which_path = shutil.which(npm_cmd)
print(f"shutil.which('{npm_cmd}') -> {which_path}")

try:
    result = subprocess.run([npm_cmd, "--version"], capture_output=True, text=True)
    print(f"subprocess run: return={result.returncode}, stdout={result.stdout.strip()}")
except Exception as e:
    print(f"subprocess failed: {e}")
