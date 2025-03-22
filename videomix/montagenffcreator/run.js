const { burn } = require("./MontagenFFCreator/burn.js");
const { readFileSync } = require("fs");
const runCache = require("./runCache.js");
const { Command } = require("commander");
const program = new Command();
const path = require("path");
const cacheDir =
  process.env["FFCREATOR_CACHE_DIR"] || path.join(__dirname, "./cache/");
try {
  program
    .requiredOption("-i, --input <path>", "Input project json path")
    .requiredOption("-o, --output <path>", "Output video file path")
    .requiredOption("-p, --port <port>", "project port")
    .parse();
} catch (ex) {
  console.log(ex);
}

const options = program.opts();

const outputExt = getFileExtension(options.output);
if (!outputExt) {
  console.log("output has no extension");
  process.exit(1);
}

const output = path.resolve(options.output);
const input = path.resolve(options.input);

const inputFileContent = readFileSync(input, "utf8");
const creatorOpt = JSON.parse(inputFileContent);
if (creatorOpt.type != "canvas") {
  console.log("invalid input project json file");
  process.exit(1);
}

function getFileExtension(filePath) {
  const parts = filePath.split(".");
  if (parts.length > 1) {
    return parts.pop();
  }
  return "";
}

console.log(`Input project json file: ${input}`);
console.log(`Output video file: ${output}`);

async function run() {
  await runCache.init(cacheDir, options.port);
  await burn({
    value: creatorOpt,
    ext: outputExt,
    output,
    cacheDir,
    customCache: runCache,
  });
}

run();
