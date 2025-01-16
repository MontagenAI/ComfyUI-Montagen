"use strict";

const pixify = require('../lib/pixify');
const rimraf = require('rimraf');
const assert = require('assert');

function validate(output, result){
    const lib = require('./bin/' + output);
    assert.strictEqual(result, lib(), 'Library standalone should work');
}

describe('pixify', function(){
    before(function(){
        process.chdir(__dirname);
    });

    after(function(){
        rimraf.sync('./bin');
    });

    it('should be debug mode', function(done){
        const output = 'test.js';
        pixify({
            output: output,
            name: 'test',
            compress: false
        }, function(){
            validate(output, true);
            done();
        });
    });

    it('should be build in release mode', function(done){
        const output = 'test.min.js';
        pixify(output, function(){
            validate(output, false);
            done();
        });
    });
});