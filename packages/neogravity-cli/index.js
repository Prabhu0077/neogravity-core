#!/usr/bin/env node

const fs = require('fs-extra');
const path = require('path');
const readline = require('readline');

console.log('======================================================');
console.log('   Initializing NeoGravity Core (VibCoder)   ');
console.log('======================================================');

const targetDir = process.cwd();
const templateDir = path.join(__dirname, 'template');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

const scaffold = async () => {
  try {
    console.log(`\n>> Scaffolding Agentic OS into workspace: ${targetDir}`);
    await fs.copy(templateDir, targetDir, {
      overwrite: false,
      errorOnExist: false,
      filter: (src) => {
        const basename = path.basename(src);
        return basename !== 'node_modules';
      },
    });

    console.log('\n======================================================');
    console.log(' Installation Complete! ');
    console.log('======================================================');
    console.log('\nNext Steps:');
    console.log('1. Edit projects.json to register your first project.');
    console.log('2. Open your AI Assistant (Claude/Cursor) and begin your first task.');
    console.log('3. (Optional) Install Sovereign Memory if you require local MoE persistency.\n');
    process.exit(0);
  } catch (err) {
    console.error('Error during installation:', err);
    process.exit(1);
  }
};

rl.question(
  `\nThis will install NeoGravity Core files (.agents, scripts, .knowledge, projects.json) in this directory.\nProceed? (y/n): `,
  (answer) => {
    if (answer.toLowerCase() === 'y' || answer.toLowerCase() === 'yes') {
      scaffold();
    } else {
      console.log('Installation canceled.');
      process.exit(0);
    }
  },
);
