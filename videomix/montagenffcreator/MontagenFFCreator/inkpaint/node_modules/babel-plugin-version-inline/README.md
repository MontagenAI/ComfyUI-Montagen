# babel-plugin-version-inline

Turn `__VERSION__` into the package's version string.

## Example

Given the following _package.json_.

```json
{
  "name": "package-using-babel-plugin-version-inline",
  "version": "1.0.0"
}
```

#### in

```js
__VERSION__
```

#### out

```js
"1.0.0"
```


## Installation

```sh
$ npm install babel-plugin-version-inline
```

## Usage

### Via `.babelrc` (Recommended)

**.babelrc**

```json
{
  "plugins": ["version-inline"]
}
```

### Via CLI

```sh
$ babel --plugins version-inline script.js
```

### Via Node API

```javascript
require("babel-core").transform("code", {
  plugins: ["version-inline"]
});
```
