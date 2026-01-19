#!/usr/bin/env node

/**
 * StackFix postinstall script
 * Sets up Python virtual environment and installs dependencies
 */

const { execSync, spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const packageRoot = path.resolve(__dirname, '..');
const venvPath = path.join(packageRoot, '.venv');
const isWindows = process.platform === 'win32';

// ANSI colors
const GREEN = '\x1b[32m';
const YELLOW = '\x1b[33m';
const RED = '\x1b[31m';
const RESET = '\x1b[0m';
const BOLD = '\x1b[1m';

function log(msg) {
    console.log(`${BOLD}[stackfix]${RESET} ${msg}`);
}

function success(msg) {
    console.log(`${GREEN}✓${RESET} ${msg}`);
}

function warn(msg) {
    console.log(`${YELLOW}⚠${RESET} ${msg}`);
}

function error(msg) {
    console.error(`${RED}✗${RESET} ${msg}`);
}

// Find Python 3.9+
function findPython() {
    const candidates = isWindows
        ? ['python', 'python3', 'py -3']
        : ['python3', 'python'];

    for (const cmd of candidates) {
        try {
            const version = execSync(`${cmd} --version 2>&1`, { encoding: 'utf8' }).trim();
            const match = version.match(/Python (\d+)\.(\d+)/);
            if (match) {
                const major = parseInt(match[1], 10);
                const minor = parseInt(match[2], 10);
                if (major === 3 && minor >= 9) {
                    return { cmd, version };
                }
            }
        } catch {
            // Try next candidate
        }
    }
    return null;
}

// Main installation
async function main() {
    log('Setting up StackFix...');

    // Find Python
    const python = findPython();
    if (!python) {
        error('Python 3.9+ is required but not found.');
        console.log('');
        console.log('Please install Python 3.9 or later:');
        console.log('  Windows: https://www.python.org/downloads/');
        console.log('  macOS:   brew install python3');
        console.log('  Linux:   apt install python3 python3-pip');
        process.exit(1);
    }

    success(`Found ${python.version} (${python.cmd})`);

    // Create venv if it doesn't exist
    if (!fs.existsSync(venvPath)) {
        log('Creating virtual environment...');
        try {
            execSync(`${python.cmd} -m venv "${venvPath}"`, {
                cwd: packageRoot,
                stdio: 'inherit'
            });
            success('Virtual environment created');
        } catch (err) {
            error('Failed to create virtual environment');
            console.log('Try running: pip install --user stackfix');
            process.exit(1);
        }
    } else {
        success('Virtual environment exists');
    }

    // Determine pip path
    const pipPath = isWindows
        ? path.join(venvPath, 'Scripts', 'pip.exe')
        : path.join(venvPath, 'bin', 'pip');

    // Install package in editable mode
    log('Installing StackFix...');
    try {
        execSync(`"${pipPath}" install -e "${packageRoot}" --quiet`, {
            cwd: packageRoot,
            stdio: 'inherit'
        });
        success('StackFix installed successfully');
    } catch (err) {
        error('Failed to install StackFix');
        process.exit(1);
    }

    console.log('');
    log('Setup complete! Run "stackfix" to start.');
    console.log('');
    console.log('Quick start:');
    console.log('  stackfix                    # Launch interactive TUI');
    console.log('  stackfix --prompt "..."     # Single prompt mode');
    console.log('  stackfix -- pytest -v       # Wrap and fix a command');
    console.log('');
}

main().catch((err) => {
    error(err.message);
    process.exit(1);
});
