#!/usr/bin/env node

"use strict";

const minimist = require('minimist');
const pixify = require('./lib/pixify');

// Get the commandline arguments
const args = minimist(process.argv.slice(2), {
    alias: {
        e: 'exclude',
        d: 'dest',
        l: 'license',
        s: 'source',
        n: 'name',
        o: 'outputName',
        w: 'watch',
        x: 'external',
        p: 'plugin',
        t: 'transform',
        m: 'minify'
    },
    boolean: [
        'watch',
        'external',
        'minify'
    ],
    string: [
        'name',
        'dest',
        'source',
        'outputName',
        'license',
        'plugin',
        'transform'
    ],
    default: {
        dest: './bin/',
        source: './src/',
        watch: false,
        external: true,
        minify: true
    }
});

const outputName = args.outputName || args.name;

if (!outputName) {
    console.log('> ERROR: Must include name for output.');
    process.exit(1);
}

// Bundle and show the timestamps
function bundle(options, callback) {
    // Build time isn't needed using watchify
    // time and size are generated automatically
    let startTime;
    if (!args.watch) {
        startTime = Date.now();
    }
    options = Object.assign({}, options, args);
    pixify(options, function() {
        if (!args.watch) {
            // Display the output, on in non-watch mode
            const sec = (Date.now() - startTime) / 1000;
            console.log('> Built %s in %d seconds', options.output, sec);
        }
        callback();
    });
}

// Do the debug build
bundle({
    cli: true,
    compress: false,
    output: outputName + '.js'
},
function() {
    // Don't do minify release when watching
    // it's too slow because of uglify
    if (!args.watch && args.minify) {
        // Do the release build
        bundle({
            cli: true,
            compress: true,
            output: outputName + '.min.js'
        }, finish);
    }
    else {
        finish();
    }
});

// Adds an extra line
function finish(){
    console.log('');
}
