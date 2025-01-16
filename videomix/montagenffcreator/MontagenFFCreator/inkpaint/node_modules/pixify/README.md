# pixify

[![Build Status](https://travis-ci.org/pixijs/pixify.svg?branch=master)](https://travis-ci.org/pixijs/pixify)

Browserify bundle process for PIXI libraries.

This creates two build files, compressed and uncompressed. Both with sourcemaps and license headers.

## Installation

```bash
npm install pixify --save-dev
```

## Commandline Usage

```bash
pixify --name [library-name]
```

For instance,
```bash
pixify --name my-library
```

### Options

* **--name** or **-n** (required) The name of the output file and Browserify's `standalone` argument.
* **--source** or **-s** (default: `./src/` Application source to build.
* **--dest** or **-d** (default: `./bin/`) Destination folder for building.
* **--exclude** or **-e** (optional) Folder names in `--source` to ignore, for custom builds.
* **--outputName** or **-o** (optional) The name of the output file if different from `--name`.
* **--license** or **-l** (default: `{pixify}/lib/license.js`) License template to use
* **--watch** or **-w** (default: `false`) `true` to run watchify when running bundling.
* **--minify** or **-m** (default: `true`) `false` or `--no-minify` to only generate the uncompressed version of the library
* **--external** or **-x** (default: `true`) `false` or `--no-external` to not bundle external modules.
* **--plugin** or **-p** (optiona) Additional plugin(s) to use for Browserify, such as tsify.
* **--transform** for **-t** (optional) Addtional transform(s) to use for Browserify, such as babelify.

## API Usage

Alternatively, use the Node API:

```js
var pixify = require('pixify');

// Full verbose options
pixify({
	output: 'library.min.js',
	name: 'library',
    source: './src/',
    dest: './bin/',
    license: './lib/license.js',
    compress: true,
    external: true,
    watch: false
});

// Short-hand with all defaults with callback
pixify('library.min.js', function(){
    // done!
});
```

### Parameters

* **options.output** (`String`) Output file name (e.g. "library.js")
* **options.name** (`String`) Standalone name for Browserify (e.g. "library")
* **options.compress** (`Boolean`, default: `true`) `true` to compress output
* **options.source** (`String`, default: `"./src/"`) Output source name
* **options.dest** (`String`, default: `"./bin/"`) Output folder
* **options.license** (`String`, default: `"{pixify}/lib/license.js"`) License template
* **options.exclude** (`String|String[]`)  List of modules to ignore from output. Useful for creating custom builds.
* **options.watch** (`Boolean`, default: `false`)  `true` to run watchify when bundling.
* **options.external** (`Boolean`, default: `true`) `false` to not bundle external modules.
* **callback** (`Function`) Optional callback function when complete
* **plugin** (`String|Array`) Additional plugin(s) to use for Browserify, such as tsify.
* **transform** (`String|Array`) Addtional transform(s) to use for Browserify, such as babelify.

## License

This content is released under the [MIT License](http://opensource.org/licenses/MIT).
