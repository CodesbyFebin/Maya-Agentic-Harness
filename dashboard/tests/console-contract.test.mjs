import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

const html = await readFile(new URL('../maya-command-center.html', import.meta.url), 'utf8');
const pagesHtml = await readFile(new URL('../../docs/index.html', import.meta.url), 'utf8');

test('console defaults to MAYA real backend and probes its health route', () => {
  assert.match(html, /const DEFAULT_BACKEND = "http:\/\/127\.0\.0\.1:8001"/);
  assert.match(html, /fetch\(`\$\{backend\}\/health`/);
  assert.match(html, /fetch\(`\$\{backend\}\/v1\/chat\/completions`/);
});

test('Pages copy matches source and opens disconnected showcase mode', () => {
  assert.equal(pagesHtml, html, 'sync docs/index.html whenever the console source changes');
  assert.match(html, /const PAGES_SHOWCASE = location\.hostname\.endsWith\("\.github\.io"\)/);
  assert.match(html, /let backend = PAGES_SHOWCASE \? "" : DEFAULT_BACKEND/);
  assert.match(html, /if \(!backend\) \{[\s\S]*?SHOWCASE MODE/);
});

test('console presents Maya and CodesbyFebin with the actual harness capabilities', () => {
  assert.match(html, /CODESBYFEBIN \/\/ AGENTIC HARNESS/);
  for (const tool of ['list_dir', 'read_file', 'terminal_run']) {
    assert.ok(html.includes(tool), `expected tool ${tool} in capability panel`);
  }
  assert.match(html, /No write tool is registered/);
});

test('history restoration renders without writing duplicate messages back', () => {
  assert.match(html, /addBubble\(message\.role, message\.content, \{persist: false\}\)/);
  assert.match(html, /localStorage\.setItem\(HISTORY_KEY, JSON\.stringify\(messages\)\)/);
});

test('backend response rendering uses safe text nodes and reports evidence honestly', () => {
  assert.match(html, /body\.textContent = String\(content \?\? ""\)/);
  assert.match(html, /maya && maya\.execution_log === "evidence\.v1"/);
  assert.match(html, /does not claim a trace is verified/);
});
