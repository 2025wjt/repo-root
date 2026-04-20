const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

function loadBrowserScript(filePath, context) {
  const code = fs.readFileSync(filePath, 'utf8');
  vm.runInContext(code, context, { filename: path.basename(filePath) });
}

function run() {
  const root = path.resolve(__dirname, '..');
  const reactPath = path.join(root, 'vendor', 'react.production.min.js');
  const reactDomPath = path.join(root, 'vendor', 'react-dom.production.min.js');

  const context = vm.createContext({
    window: {},
    self: {},
    globalThis: {},
    console,
    setTimeout,
    clearTimeout,
  });
  context.window = context;
  context.self = context;
  context.globalThis = context;

  loadBrowserScript(reactPath, context);
  loadBrowserScript(reactDomPath, context);

  assert.equal(typeof context.React?.useState, 'function');
  assert.equal(typeof context.React?.useEffect, 'function');
  assert.ok(
    typeof context.ReactDOM?.createRoot === 'function' ||
      typeof context.ReactDOM?.render === 'function'
  );

  console.log('frontend vendor compatibility: ok');
}

run();
