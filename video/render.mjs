// Uso: node render.mjs props.json saida.mp4
import {bundle} from '@remotion/bundler';
import {renderMedia, selectComposition} from '@remotion/renderer';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';

const [, , propsArq, saida] = process.argv;
const inputProps = JSON.parse(fs.readFileSync(propsArq, 'utf8'));
const browserExecutable = process.env.CHROME_PATH || undefined;
const serveUrl = await bundle({entryPoint: path.resolve('src/index.js'), publicDir: path.resolve('public')});
const composition = await selectComposition({serveUrl, id: 'Nexus', inputProps, browserExecutable});
let ultimo = -1;
await renderMedia({
  composition, serveUrl, codec: 'h264', outputLocation: saida, inputProps, browserExecutable,
  concurrency: Math.max(1, Math.min(8, os.cpus().length)), crf: 20, audioBitrate: '128k',
  chromiumOptions: {gl: 'swiftshader'},
  onProgress: ({progress}) => { const p = Math.floor(progress * 10); if (p !== ultimo) { ultimo = p; console.error(`render ${p * 10}%`); } },
});
console.log(JSON.stringify({ok: true, saida}));
