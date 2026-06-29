import { readdir, readFile, stat } from "node:fs/promises";
import path from "node:path";
import process from "node:process";

const repoRoot = process.cwd();
const skillsDir = path.join(repoRoot, "skills");
const allowedFrontmatterKeys = new Set(["name", "description"]);
const allowedResourceDirs = new Set(["scripts", "references", "assets", "agents"]);
const skillNamePattern = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;

function parseFrontmatter(content, filePath) {
  if (!content.startsWith("---\n")) {
    throw new Error(`${filePath}: missing YAML frontmatter`);
  }

  const end = content.indexOf("\n---", 4);
  if (end === -1) {
    throw new Error(`${filePath}: unterminated YAML frontmatter`);
  }

  const frontmatter = content.slice(4, end).trim();
  const values = {};

  for (const [index, rawLine] of frontmatter.split("\n").entries()) {
    const line = rawLine.trim();
    if (!line || line.startsWith("#")) continue;

    const match = /^([A-Za-z0-9_-]+):\s*(.*)$/.exec(line);
    if (!match) {
      throw new Error(`${filePath}: unsupported frontmatter line ${index + 1}: ${rawLine}`);
    }

    const key = match[1];
    let value = match[2].trim();

    if (
      (value.startsWith('"') && value.endsWith('"')) ||
      (value.startsWith("'") && value.endsWith("'"))
    ) {
      value = value.slice(1, -1);
    }

    values[key] = value;
  }

  return values;
}

async function pathExists(targetPath) {
  try {
    await stat(targetPath);
    return true;
  } catch (error) {
    if (error.code === "ENOENT") return false;
    throw error;
  }
}

async function validateSkill(skillName) {
  const skillPath = path.join(skillsDir, skillName);
  const skillStat = await stat(skillPath);
  if (!skillStat.isDirectory()) return [];

  const errors = [];
  const relativeSkillPath = path.relative(repoRoot, skillPath);

  if (!skillNamePattern.test(skillName)) {
    errors.push(`${relativeSkillPath}: folder name must be lowercase hyphen-case`);
  }

  const skillMdPath = path.join(skillPath, "SKILL.md");
  if (!(await pathExists(skillMdPath))) {
    errors.push(`${relativeSkillPath}: missing SKILL.md`);
    return errors;
  }

  const content = await readFile(skillMdPath, "utf8");
  let frontmatter;
  try {
    frontmatter = parseFrontmatter(content, path.relative(repoRoot, skillMdPath));
  } catch (error) {
    errors.push(error.message);
    return errors;
  }

  for (const key of Object.keys(frontmatter)) {
    if (!allowedFrontmatterKeys.has(key)) {
      errors.push(`${relativeSkillPath}: unexpected frontmatter key "${key}"`);
    }
  }

  if (!frontmatter.name) {
    errors.push(`${relativeSkillPath}: missing frontmatter name`);
  } else if (frontmatter.name !== skillName) {
    errors.push(`${relativeSkillPath}: frontmatter name must match folder name`);
  } else if (!skillNamePattern.test(frontmatter.name)) {
    errors.push(`${relativeSkillPath}: frontmatter name must be lowercase hyphen-case`);
  }

  if (!frontmatter.description) {
    errors.push(`${relativeSkillPath}: missing frontmatter description`);
  } else if (frontmatter.description.length > 1024) {
    errors.push(`${relativeSkillPath}: description must be 1024 characters or fewer`);
  }

  const entries = await readdir(skillPath, { withFileTypes: true });
  for (const entry of entries) {
    if (!entry.isDirectory()) continue;
    if (!allowedResourceDirs.has(entry.name)) {
      errors.push(
        `${relativeSkillPath}/${entry.name}: unexpected resource directory; expected scripts/, references/, assets/, or agents/`,
      );
    }
  }

  return errors;
}

async function main() {
  if (!(await pathExists(skillsDir))) {
    throw new Error("skills/ directory not found");
  }

  const entries = await readdir(skillsDir, { withFileTypes: true });
  const skillNames = entries
    .filter((entry) => entry.isDirectory() && !entry.name.startsWith("."))
    .map((entry) => entry.name);

  if (skillNames.length === 0) {
    throw new Error("No skills found under skills/");
  }

  const errors = [];
  for (const skillName of skillNames) {
    errors.push(...(await validateSkill(skillName)));
  }

  if (errors.length > 0) {
    console.error("Skill validation failed:");
    for (const error of errors) {
      console.error(`- ${error}`);
    }
    process.exit(1);
  }

  console.log(`Validated ${skillNames.length} skill(s).`);
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
