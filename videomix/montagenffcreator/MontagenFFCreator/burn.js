'use strict';

// const {execSync} = require('child_process');
const path = require('path');
const fs = require('fs');
const { Factory } = require('./lib/index');
const CacheUtil = require('./lib/utils/cache');

const cacheDir = process.env['FFCREATOR_CACHE_DIR'] || path.join(__dirname, './cache/');

function round(x) {
  const PROGRESS_PRECISION = 3;
  const m = Math.pow(10, PROGRESS_PRECISION);
  return Math.round(x * m) / m;
}

const burn = async opts => {
  // execSync(`find ${cacheDir}*  -name '????????????????' -type d -ctime +1 -exec rm -rf {} \\;`);//删除1天以上的缓存目录
  var { customCache, ...rest } = opts;
  opts = rest;
  if (!opts['cacheDir']) opts['cacheDir'] = cacheDir;

  if (!fs.existsSync(opts['cacheDir'])) {
    fs.mkdirSync(opts['cacheDir']);
  }
  Factory.debug = true;
  if (customCache) {
    Factory.cacheNode = customCache.cacheNode;
    customCache.cacheDir = opts['cacheDir'];
  } else {
    Factory.cacheNode = CacheUtil.cacheNode;
    CacheUtil.cacheDir = opts['cacheDir'];
  }

  const { node: creator, cache } = Factory.from(opts.value, opts, pp => {
    console.log('burn.js loading...', pp);
  });
  await cache;

  const onMessage = typeof opts['onMessage'] === 'function' ? opts['onMessage'] : () => {};
  const onComplete = typeof opts['onComplete'] === 'function' ? opts['onComplete'] : () => {};
  const task_id = opts['task_id'];

  let t = Date.now();
  creator
    .on('start', () => {
      console.log(`Burn start.`);
      console.log(`Burn start timestamp: ${Date.now() - t}ms`);
      onMessage({
        task_id,
        status: 'start',
        step: 'start',
      });
    })
    .on('error', event => {
      console.error('creator error', event);
      onMessage({
        task_id,
        step: 'error',
        result: { type: event.type, pos: event.pos, error: event.error },
      });
    })
    .on('progress', e => {
      let number = e.percent || 0;
      console.log(`Burn progress: ${(number * 100) >> 0}%`);
      console.log(`Burn progress timestamp: ${Date.now() - t}ms`);
      onMessage({
        task_id,
        step: 'progress',
        progress: round(0.2 + number * 0.8),
      });
    })
    .on('preloading', evt => {
      console.log(`Burn preloading: ${evt.id}: ${evt.loaded}/${evt.total}`);
      console.log(`Burn preloading timestamp: ${Date.now() - t}ms`);
      onMessage({
        task_id,
        step: 'progress',
        progress: round((evt.loaded / evt.total) * 0.05),
      });
    })
    .on('prepareMaterial', evt => {
      console.log(`Burn prepareMaterial: ${evt.id}: ${evt.prepared}/${evt.total}`);
      console.log(`Burn prepareMaterial timestamp: ${Date.now() - t}ms`);
      onMessage({
        task_id,
        step: 'progress',
        progress: round(0.05 + (evt.prepared / evt.total) * 0.15),
      });
    })
    .on('complete', e => {
      console.log(`Burn completed: \n USEAGE: ${e.useage} \n PATH: ${e.output} `);
      console.log(`Burn completed timestamp: ${Date.now() - t}ms`);
      onMessage({
        task_id,
        step: 'finish',
        result: e.output,
      });
      onComplete();
    })
    .generateOutput()
    .start();
  return creator;
};

module.exports = {
  burn,
  cacheDir,
};
