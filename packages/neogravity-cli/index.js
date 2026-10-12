#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const readline = require('readline');

const pkg = require('./package.json');
const TEMPLATE_DIR = path.join(__dirname, 'template');

const HELP = `neogravity ${pkg.version}
Scaffold persistent context files for AI coding assistants.

Usage:
  npx @vibcoder/neogravity init [options]

Options:
  -y, --yes       Do not ask for confirmation
  --dir <path>    Target directory (default: current directory)
  --dry-run       Show what would be created, change nothing
  -v, --version   Print version
  -h, --help      Show this help

Existing files are never overwritten.`;

/** Walk a directory and return file paths relative to it. */
function listFiles(root, rel = '') {
  const out = [];
  for (const entry of fs.readdirSync(path.join(root, rel), { withFileTypes: true })) {
    const next = path.join(rel, entry.name);
    if (entry.isDirectory()) out.push(...listFiles(root, next));
    else out.push(next);
  }
  return out.sort();
}

/**
 * Copy the template into targetDir without overwriting anything.
 * Returns which files were created and which were skipped.
 */
function scaffold(targetDir, { dryRun = false } = {}) {
  const created = [];
  const skipped = [];
  for (const rel of listFiles(TEMPLATE_DIR)) {
    const dest = path.join(targetDir, rel);
    if (fs.existsSync(dest)) {
      skipped.push(rel);
      continue;
    }
    if (!dryRun) {
      fs.mkdirSync(path.dirname(dest), { recursive: true });
      fs.copyFileSync(path.join(TEMPLATE_DIR, rel), dest, fs.constants.COPYFILE_EXCL);
    }
    created.push(rel);
  }
  return { created, skipped };
}

function parseArgs(argv) {
  const opts = { command: null, yes: false, dryRun: false, dir: process.cwd(), help: false, version: false };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '-y' || a === '--yes') opts.yes = true;
    else if (a === '--dry-run') opts.dryRun = true;
    else if (a === '-h' || a === '--help') opts.help = true;
    else if (a === '-v' || a === '--version') opts.version = true;
    else if (a === '--dir') {
      const v = argv[++i];
      if (!v) throw new Error('--dir needs a path');
      opts.dir = path.resolve(v);
    } else if (!a.startsWith('-') && !opts.command) opts.command = a;
    else throw new Error(`Unknown option: ${a}`);
  }
  return opts;
}

function confirm(question) {
  return new Promise((resolve) => {
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
    rl.question(question, (answer) => {
      rl.close();
      resolve(/^y(es)?$/i.test(answer.trim()));
    });
  });
}

async function main(argv) {
  let opts;
  try {
    opts = parseArgs(argv);
  } catch (err) {
    console.error(`${err.message}\n\n${HELP}`);
    return 2;
  }
  if (opts.version) {
    console.log(pkg.version);
    return 0;
  }
  if (opts.help || !opts.command) {
    console.log(HELP);
    return opts.help ? 0 : 2;
  }
  if (opts.command !== 'init') {
    console.error(`Unknown command: ${opts.command}\n\n${HELP}`);
    return 2;
  }
  if (!fs.existsSync(opts.dir) || !fs.statSync(opts.dir).isDirectory()) {
    console.error(`Not a directory: ${opts.dir}`);
    return 1;
  }

  const plan = scaffold(opts.dir, { dryRun: true });
  console.log(`Target: ${opts.dir}`);
  console.log(`Will create ${plan.created.length} file(s); ${plan.skipped.length} already exist and will be kept.`);

  if (opts.dryRun) {
    plan.created.forEach((f) => console.log(`  + ${f}`));
    plan.skipped.forEach((f) => console.log(`  = ${f} (exists)`));
    return 0;
  }
  if (plan.created.length === 0) {
    console.log('Nothing to do.');
    return 0;
  }
  if (!opts.yes) {
    if (!process.stdin.isTTY) {
      console.error('Not an interactive terminal. Re-run with --yes to continue.');
      return 1;
    }
    if (!(await confirm('Proceed? (y/n): '))) {
      console.log('Cancelled.');
      return 0;
    }
  }

  const { created, skipped } = scaffold(opts.dir);
  created.forEach((f) => console.log(`  + ${f}`));
  skipped.forEach((f) => console.log(`  = ${f} (kept)`));
  console.log('\nDone. Next:');
  console.log('  1. Open .knowledge/tasks/active_tasks.md and write your first next step.');
  console.log('  2. Start a chat with your assistant and say: "Run the session-start workflow."');
  return 0;
}

if (require.main === module) {
  main(process.argv.slice(2)).then(
    (code) => process.exit(code),
    (err) => {
      console.error(err);
      process.exit(1);
    },
  );
}

module.exports = { scaffold, listFiles, parseArgs, main, TEMPLATE_DIR };
