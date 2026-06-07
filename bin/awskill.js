#!/usr/bin/env node
import { spawnSync } from "node:child_process";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = join(__dirname, "..");
const script = join(root, "scripts", "awskill.py");
const args = process.argv.slice(2);

function run(command, commandArgs) {
  const result = spawnSync(command, commandArgs, {
    cwd: root,
    stdio: "inherit",
    env: process.env,
  });

  if (result.error && result.error.code === "ENOENT") return null;
  if (result.error) {
    console.error(result.error.message);
    process.exit(1);
  }
  process.exit(result.status ?? 0);
}

run("python3", [script, ...args]);
run("python", [script, ...args]);

console.error("awskill requires Python 3.8+ to run the CLI.");
process.exit(1);
