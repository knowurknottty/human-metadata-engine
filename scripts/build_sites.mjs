// Package the existing vanilla UI without introducing a second frontend.
import {readFile, mkdir, writeFile} from 'node:fs/promises';
const files = ['index.html', 'styles.css', 'app.js', 'atlas.js', 'tarot.js', 'vendor/tailwind.js'];
const types = {html:'text/html', css:'text/css', js:'text/javascript'};
const assets = {};
for (const file of files) {
  assets['/' + file] = {body:await readFile(`webapp/static/${file}`, 'utf8'), type:types[file.split('.').pop()] + '; charset=utf-8'};
}
const worker = await readFile('scripts/sites_worker.mjs', 'utf8');
await mkdir('dist/server', {recursive:true});
await mkdir('dist/.openai', {recursive:true});
await writeFile('dist/server/index.js', `const assets = ${JSON.stringify(assets)};\n${worker}`);
await writeFile('dist/.openai/hosting.json', await readFile('.openai/hosting.json'));
console.log('Sites Worker built from the shared frontend.');
