#!/usr/bin/env node
import { spawnSync } from "node:child_process";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = join(__dirname, "..");
const script = join(root, "scripts", "awskill.py");
const args = process.argv.slice(2);

// Try each candidate, verify it's Python >= 3.8 before invoking the script.
function pythonVersionOk(command) {
  const probe = spawnSync(command, ["-c", "import sys; print('%d.%d' % sys.version_info[:2])"], {
    stdio: ["ignore", "pipe", "ignore"],
  });
  if (probe.error || probe.status !== 0) return false;
  const out = String(probe.stdout || "").trim();
  const m = out.match(/^(\d+)\.(\d+)$/);
  if (!m) return false;
  const major = Number(m[1]);
  const minor = Number(m[2]);
  return major > 3 || (major === 3 && minor >= 8);
}

function tryRun(command) {
  if (!pythonVersionOk(command)) return false;
  const result = spawnSync(command, [script, ...args], {
    cwd: root,
    stdio: "inherit",
    env: process.env,
  });
  if (result.error && result.error.code === "ENOENT") return false;
  if (result.error) {
    console.error(result.error.message);
    process.exit(1);
  }
  process.exit(result.status ?? 0);
}

for (const cmd of ["python3", "python"]) {
  tryRun(cmd);
}

console.error("awskill requires Python 3.8+ on PATH (tried: python3, python).");
process.exit(1);
