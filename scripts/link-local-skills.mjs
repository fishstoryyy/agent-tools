import {
  copyFile,
  lstat,
  mkdir,
  readFile,
  readdir,
  readlink,
  rename,
  symlink,
  unlink,
  writeFile,
} from "node:fs/promises";
import { randomUUID } from "node:crypto";
import os from "node:os";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const applyChanges = process.argv.includes("--apply");
const unknownArguments = process.argv
  .slice(2)
  .filter((argument) => argument !== "--apply");

if (unknownArguments.length > 0) {
  throw new Error(`Unknown argument(s): ${unknownArguments.join(", ")}`);
}

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const sourceSkillsDir = path.join(repoRoot, "skills");
const homeDir = process.env.HOME || os.homedir();
const agentSkillsDir = path.join(homeDir, ".agents", "skills");
const claudeSkillsDir = path.join(homeDir, ".claude", "skills");
const codexSkillsDir = path.join(homeDir, ".codex", "skills");
const skillLockPath = path.join(homeDir, ".agents", ".skill-lock.json");
const timestamp = new Date().toISOString().replaceAll(":", "-");
const backupRoot = path.join(homeDir, ".agents", "skill-link-backups", timestamp);
const modePrefix = applyChanges ? "" : "[dry-run] ";

let changeCount = 0;
let backupCount = 0;

async function pathExists(targetPath) {
  try {
    await lstat(targetPath);
    return true;
  } catch (error) {
    if (error.code === "ENOENT") return false;
    throw error;
  }
}

async function listSkills() {
  const entries = await readdir(sourceSkillsDir, { withFileTypes: true });
  const skills = [];

  for (const entry of entries) {
    if (!entry.isDirectory() || entry.name.startsWith(".")) continue;

    const skillPath = path.join(sourceSkillsDir, entry.name);
    if (await pathExists(path.join(skillPath, "SKILL.md"))) {
      skills.push({ name: entry.name, sourcePath: skillPath });
    }
  }

  return skills.sort((left, right) => left.name.localeCompare(right.name));
}

async function pointsTo(linkPath, expectedTarget) {
  try {
    const stats = await lstat(linkPath);
    if (!stats.isSymbolicLink()) return false;

    const currentTarget = await readlink(linkPath);
    return path.resolve(path.dirname(linkPath), currentTarget) === expectedTarget;
  } catch (error) {
    if (error.code === "ENOENT") return false;
    throw error;
  }
}

async function backUpExisting(targetPath, backupGroup) {
  if (!(await pathExists(targetPath))) return null;

  const backupPath = path.join(backupRoot, backupGroup, path.basename(targetPath));
  console.log(`${modePrefix}back up ${targetPath} -> ${backupPath}`);
  backupCount += 1;

  if (!applyChanges) return backupPath;

  await mkdir(path.dirname(backupPath), { recursive: true });
  await rename(targetPath, backupPath);
  return backupPath;
}

async function ensureLink(linkPath, sourcePath, backupGroup) {
  if (await pointsTo(linkPath, sourcePath)) {
    console.log(`ok ${linkPath} -> ${sourcePath}`);
    return;
  }

  changeCount += 1;

  if (!applyChanges) {
    await backUpExisting(linkPath, backupGroup);
    console.log(`${modePrefix}link ${linkPath} -> ${sourcePath}`);
    return;
  }

  await mkdir(path.dirname(linkPath), { recursive: true });
  const stagingPath = path.join(
    path.dirname(linkPath),
    `.${path.basename(linkPath)}.agent-tools-${randomUUID()}.tmp`,
  );
  await symlink(sourcePath, stagingPath, "dir");

  let backupPath = null;
  try {
    backupPath = await backUpExisting(linkPath, backupGroup);
    await rename(stagingPath, linkPath);
    console.log(`link ${linkPath} -> ${sourcePath}`);
  } catch (error) {
    await unlink(stagingPath).catch(() => {});

    if (
      backupPath &&
      !(await pathExists(linkPath)) &&
      (await pathExists(backupPath))
    ) {
      try {
        await rename(backupPath, linkPath);
      } catch (recoveryError) {
        throw new AggregateError(
          [error, recoveryError],
          `Failed to link ${linkPath} and restore its backup`,
        );
      }
    }

    throw error;
  }
}

async function warnAboutCodexCollision(skillName) {
  const collisionPath = path.join(codexSkillsDir, skillName);
  if (!(await pathExists(collisionPath))) return;

  console.warn(
    `warning: ${collisionPath} may duplicate the shared Codex skill; leaving it untouched`,
  );
}

async function cleanStaleRepoLinks(
  targetDirectory,
  activeSkillNames,
  backupGroup,
) {
  if (!(await pathExists(targetDirectory))) return;

  const entries = await readdir(targetDirectory, { withFileTypes: true });
  for (const entry of entries) {
    if (!entry.isSymbolicLink() || activeSkillNames.has(entry.name)) continue;

    const linkPath = path.join(targetDirectory, entry.name);
    const currentTarget = await readlink(linkPath);
    const resolvedTarget = path.resolve(targetDirectory, currentTarget);
    if (path.dirname(resolvedTarget) !== sourceSkillsDir) continue;

    await backUpExisting(linkPath, backupGroup);
    console.log(`${modePrefix}remove stale local skill link ${linkPath}`);
    changeCount += 1;
  }
}

async function detachFromSkillsLock(skillNames) {
  if (!(await pathExists(skillLockPath))) return;

  const rawLock = await readFile(skillLockPath, "utf8");
  const lock = JSON.parse(rawLock);
  if (!lock.skills || typeof lock.skills !== "object") return;

  const detachedNames = skillNames.filter((skillName) =>
    Object.hasOwn(lock.skills, skillName),
  );

  if (detachedNames.length === 0) return;

  console.log(
    `${modePrefix}detach ${detachedNames.join(", ")} from ${skillLockPath}`,
  );
  changeCount += 1;

  if (!applyChanges) return;

  const backupPath = path.join(backupRoot, "agents", ".skill-lock.json");
  await mkdir(path.dirname(backupPath), { recursive: true });
  await copyFile(skillLockPath, backupPath);
  backupCount += 1;

  for (const skillName of detachedNames) {
    delete lock.skills[skillName];
  }

  await writeFile(skillLockPath, `${JSON.stringify(lock, null, 2)}\n`);
}

async function main() {
  const skills = await listSkills();
  if (skills.length === 0) {
    throw new Error(`No skills found in ${sourceSkillsDir}`);
  }

  console.log(
    `${applyChanges ? "Linking" : "Checking"} ${skills.length} local skill(s) from ${sourceSkillsDir}`,
  );

  for (const skill of skills) {
    await ensureLink(
      path.join(agentSkillsDir, skill.name),
      skill.sourcePath,
      "agents",
    );
    await ensureLink(
      path.join(claudeSkillsDir, skill.name),
      skill.sourcePath,
      "claude",
    );
    await warnAboutCodexCollision(skill.name);
  }

  const skillNames = skills.map((skill) => skill.name);
  const activeSkillNames = new Set(skillNames);
  await cleanStaleRepoLinks(agentSkillsDir, activeSkillNames, "agents");
  await cleanStaleRepoLinks(claudeSkillsDir, activeSkillNames, "claude");
  await detachFromSkillsLock(skillNames);

  if (!applyChanges) {
    if (changeCount === 0) {
      console.log("All local skill links are already current.");
    } else {
      console.log(
        `${changeCount} change(s) needed. Run "npm run link:skills" to apply them safely.`,
      );
    }
    return;
  }

  console.log(`Applied ${changeCount} change(s).`);
  if (backupCount > 0) {
    console.log(`Backups saved to ${backupRoot}`);
  }
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
