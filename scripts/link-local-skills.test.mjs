import assert from "node:assert/strict";
import {
  existsSync,
  lstatSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  readlinkSync,
  readdirSync,
  rmSync,
  symlinkSync,
  writeFileSync,
} from "node:fs";
import os from "node:os";
import path from "node:path";
import process from "node:process";
import { spawnSync } from "node:child_process";
import test from "node:test";
import { fileURLToPath } from "node:url";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const scriptPath = path.join(repoRoot, "scripts", "link-local-skills.mjs");
const sourceSkillsDir = path.join(repoRoot, "skills");
const skillNames = readdirSync(sourceSkillsDir, { withFileTypes: true })
  .filter(
    (entry) =>
      entry.isDirectory() &&
      existsSync(path.join(sourceSkillsDir, entry.name, "SKILL.md")),
  )
  .map((entry) => entry.name)
  .sort();

function createHome() {
  return mkdtempSync(path.join(os.tmpdir(), "agent-tools-link-test-"));
}

function runLinker(home, arguments_ = ["--apply"]) {
  return spawnSync(process.execPath, [scriptPath, ...arguments_], {
    cwd: repoRoot,
    env: { ...process.env, HOME: home },
    encoding: "utf8",
  });
}

function assertRepoLink(home, baseDirectory, skillName) {
  const linkPath = path.join(home, baseDirectory, skillName);
  assert.equal(lstatSync(linkPath).isSymbolicLink(), true);
  assert.equal(
    path.resolve(path.dirname(linkPath), readlinkSync(linkPath)),
    path.join(sourceSkillsDir, skillName),
  );
}

test("links all skills while preserving collisions and unrelated lock records", () => {
  const home = createHome();

  try {
    const oldAgentSkill = path.join(home, ".agents", "skills", "grill-me-light");
    mkdirSync(oldAgentSkill, { recursive: true });
    writeFileSync(path.join(oldAgentSkill, "old.txt"), "old installation");

    const claudeSkills = path.join(home, ".claude", "skills");
    mkdirSync(claudeSkills, { recursive: true });
    symlinkSync(oldAgentSkill, path.join(claudeSkills, "grill-me-light"), "dir");

    const codexCollision = path.join(
      home,
      ".codex",
      "skills",
      "grill-me-light",
    );
    mkdirSync(codexCollision, { recursive: true });
    writeFileSync(path.join(codexCollision, "SKILL.md"), "unrelated skill");

    for (const baseDirectory of [".agents/skills", ".claude/skills"]) {
      const directory = path.join(home, baseDirectory);
      mkdirSync(directory, { recursive: true });
      symlinkSync(
        path.join(sourceSkillsDir, "deleted-skill"),
        path.join(directory, "deleted-skill"),
        "dir",
      );
    }

    const priorBackup = path.join(
      home,
      ".agents",
      "skill-link-backups",
      "prior-run",
      "agents",
      "context-handoff",
    );
    mkdirSync(priorBackup, { recursive: true });
    writeFileSync(path.join(priorBackup, "old.txt"), "recoverable backup");

    const lockPath = path.join(home, ".agents", ".skill-lock.json");
    writeFileSync(
      lockPath,
      `${JSON.stringify(
        {
          version: 3,
          skills: {
            "grill-me-light": { source: "fork-owner/renamed-repo" },
            "other-skill": { source: "someone/else" },
          },
        },
        null,
        2,
      )}\n`,
    );

    const firstRun = runLinker(home);
    assert.equal(firstRun.status, 0, firstRun.stderr || firstRun.stdout);
    assert.match(firstRun.stderr, /leaving it untouched/);

    for (const skillName of skillNames) {
      assertRepoLink(home, ".agents/skills", skillName);
      assertRepoLink(home, ".claude/skills", skillName);
    }

    assert.equal(existsSync(codexCollision), true);
    assert.equal(
      readFileSync(path.join(codexCollision, "SKILL.md"), "utf8"),
      "unrelated skill",
    );
    assert.equal(
      existsSync(path.join(home, ".agents", "skills", "deleted-skill")),
      false,
    );
    assert.equal(
      existsSync(path.join(home, ".claude", "skills", "deleted-skill")),
      false,
    );
    assert.equal(existsSync(path.join(priorBackup, "old.txt")), true);

    const updatedLock = JSON.parse(readFileSync(lockPath, "utf8"));
    assert.equal(updatedLock.skills["grill-me-light"], undefined);
    assert.deepEqual(updatedLock.skills["other-skill"], {
      source: "someone/else",
    });

    const secondRun = runLinker(home);
    assert.equal(secondRun.status, 0, secondRun.stderr || secondRun.stdout);
    assert.match(secondRun.stdout, /Applied 0 change\(s\)\./);
  } finally {
    rmSync(home, { recursive: true, force: true });
  }
});

test("dry run reports changes without modifying installations", () => {
  const home = createHome();

  try {
    const existingSkill = path.join(
      home,
      ".agents",
      "skills",
      "context-handoff",
    );
    mkdirSync(existingSkill, { recursive: true });
    writeFileSync(path.join(existingSkill, "old.txt"), "unchanged");

    const result = runLinker(home, []);
    assert.equal(result.status, 0, result.stderr || result.stdout);
    assert.match(result.stdout, /\[dry-run\]/);
    assert.equal(lstatSync(existingSkill).isDirectory(), true);
    assert.equal(
      readFileSync(path.join(existingSkill, "old.txt"), "utf8"),
      "unchanged",
    );
  } finally {
    rmSync(home, { recursive: true, force: true });
  }
});
