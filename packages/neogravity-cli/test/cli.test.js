'use strict';

const test = require('node:test');
const assert = require('node:assert');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { scaffold, listFiles, parseArgs, TEMPLATE_DIR } = require('../index.js');

const tmp = () => fs.mkdtempSync(path.join(os.tmpdir(), 'ng-'));

test('scaffold creates every template file', () => {
  const dir = tmp();
  const { created, skipped } = scaffold(dir);
  assert.strictEqual(skipped.length, 0);
  assert.deepStrictEqual(created, listFiles(TEMPLATE_DIR));
  for (const rel of created) assert.ok(fs.existsSync(path.join(dir, rel)), rel);
});

test('scaffold never overwrites existing files', () => {
  const dir = tmp();
  const target = path.join(dir, '.knowledge', 'tasks', 'active_tasks.md');
  fs.mkdirSync(path.dirname(target), { recursive: true });
  fs.writeFileSync(target, 'MINE');
  const { skipped } = scaffold(dir);
  assert.ok(skipped.includes(path.join('.knowledge', 'tasks', 'active_tasks.md')));
  assert.strictEqual(fs.readFileSync(target, 'utf8'), 'MINE');
});

test('dry run changes nothing', () => {
  const dir = tmp();
  const { created } = scaffold(dir, { dryRun: true });
  assert.ok(created.length > 0);
  assert.deepStrictEqual(fs.readdirSync(dir), []);
});

test('template contains no personal paths or secrets', () => {
  const bad = [/[A-Za-z]:\\/, /ghp_[A-Za-z0-9]/, /sk-[A-Za-z0-9]{20}/, /password\s*[:=]/i];
  for (const rel of listFiles(TEMPLATE_DIR)) {
    const text = fs.readFileSync(path.join(TEMPLATE_DIR, rel), 'utf8');
    for (const re of bad) assert.ok(!re.test(text), `${rel} matches ${re}`);
  }
});

test('parseArgs handles flags and rejects unknown ones', () => {
  const o = parseArgs(['init', '--yes', '--dry-run']);
  assert.strictEqual(o.command, 'init');
  assert.ok(o.yes && o.dryRun);
  assert.throws(() => parseArgs(['init', '--nope']));
});
