#!/usr/bin/env node
/*
Create a Qlik Sense app/QVF shell for the Supply Chain Emissions dashboard.

Requirements:
- Run on a machine with Qlik Sense Desktop or another reachable Qlik Engine.
- Node.js 22+ (uses the built-in WebSocket implementation; no npm install needed).
- A data connection or local path that Qlik can read for supply_chain_emissions_suppliers_50.csv.

Examples:
  Qlik Sense Desktop local engine:
    node scripts/create_qvf_local_engine.mjs

  Override engine URL and data connection:
    QLIK_ENGINE_URL="ws://localhost:9076/app/engineData" \
    QLIK_DATA_CONNECTION="lib://SupplyChainData" \
    node scripts/create_qvf_local_engine.mjs

After success, export/copy the app as:
  qvf/Supply_Chain_Emissions_Forecasting_What_If.qvf
*/

import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const repoRoot = resolve(__dirname, '..');
const spec = JSON.parse(readFileSync(resolve(repoRoot, 'qvf/supply_chain_emissions_qvf_spec.json'), 'utf8'));

const engineUrl = process.env.QLIK_ENGINE_URL || 'ws://localhost:9076/app/engineData';
const appName = process.env.QLIK_APP_NAME || spec.app.name;
const dataConnection = process.env.QLIK_DATA_CONNECTION || spec.data.connectionName;
const shouldReload = process.env.QLIK_RELOAD !== 'false';

let loadScript = readFileSync(resolve(repoRoot, 'qlik/supply_chain_emissions_what_if_model.qvs'), 'utf8');
loadScript = loadScript.replace(
  /SET vDataConnection = '.*?';/,
  `SET vDataConnection = '${dataConnection.replaceAll("'", "''")}';`,
);

if (typeof WebSocket === 'undefined') {
  throw new Error('This script requires Node.js 22+ with global WebSocket support.');
}

let nextId = 1;
const pending = new Map();

function connect(url) {
  return new Promise((resolveSocket, reject) => {
    const ws = new WebSocket(url);
    ws.addEventListener('open', () => resolveSocket(ws));
    ws.addEventListener('error', (event) => reject(new Error(`Unable to connect to Qlik Engine at ${url}: ${event.message || 'connection error'}`)));
    ws.addEventListener('message', (event) => {
      const payload = JSON.parse(event.data);
      if (!payload.id || !pending.has(payload.id)) {
        return;
      }
      const { resolve, reject } = pending.get(payload.id);
      pending.delete(payload.id);
      if (payload.error) {
        reject(new Error(`${payload.error.code || 'QlikError'}: ${payload.error.message || JSON.stringify(payload.error)}`));
      } else {
        resolve(payload.result);
      }
    });
  });
}

function rpc(ws, handle, method, params = []) {
  const id = nextId++;
  const body = { jsonrpc: '2.0', id, handle, method, params };
  return new Promise((resolve, reject) => {
    pending.set(id, { resolve, reject });
    ws.send(JSON.stringify(body));
  });
}

async function createOrOpenApp(ws) {
  try {
    await rpc(ws, -1, 'CreateDoc', [appName]);
    console.log(`Created app: ${appName}`);
  } catch (error) {
    console.log(`CreateDoc did not create a new app (${error.message}). Opening existing app if present.`);
  }

  const openResult = await rpc(ws, -1, 'OpenDoc', [appName]);
  const docHandle = openResult.qReturn?.qHandle;
  if (typeof docHandle !== 'number') {
    throw new Error(`OpenDoc did not return a document handle: ${JSON.stringify(openResult)}`);
  }
  return docHandle;
}

async function main() {
  console.log(`Connecting to Qlik Engine: ${engineUrl}`);
  const ws = await connect(engineUrl);

  try {
    const docHandle = await createOrOpenApp(ws);
    console.log('Setting load script...');
    await rpc(ws, docHandle, 'SetScript', [loadScript]);

    if (shouldReload) {
      console.log('Reloading app data model...');
      const reloadResult = await rpc(ws, docHandle, 'DoReload', [0, false, false]);
      if (reloadResult.qSuccess === false) {
        throw new Error(`Qlik reload failed: ${JSON.stringify(reloadResult)}`);
      }
    } else {
      console.log('Skipping reload because QLIK_RELOAD=false.');
    }

    console.log('Saving app/QVF...');
    await rpc(ws, docHandle, 'DoSave', []);
    console.log('Done. The Qlik app/QVF shell was saved by the connected Qlik Engine.');
    console.log(`Target QVF export name: ${spec.app.targetQvfFile}`);
    console.log('Next step: create visual sheet objects from qvf/supply_chain_emissions_qvf_spec.json or the build guide, then export the app as .qvf.');
  } finally {
    ws.close();
  }
}

main().catch((error) => {
  console.error(error.message);
  process.exitCode = 1;
});
