const md5 = require("md5");
const fs = require("fs-extra");
const path = require("path");
const url = require("url");
const progressStream = require("progress-stream");
const lockfile = require("proper-lockfile");
const fetch = (...args) =>
  import("node-fetch").then(({ default: fetch }) => fetch(...args));

const CacheUtil = {
  cacheDir: null,
  baseUrl: null,
  localPath: null,
  metadataPath: null,
  metadata: {},
  retries: {
    retries: 1800, // 等待半个小时
    factor: 1, // 重试间隔的指数增长因子
    minTimeout: 1000, // 最小重试间隔，单位为毫秒
    maxTimeout: 1000, // 最大重试间隔，单位为毫秒
  },

  async init(cacheDir, baseUrl, localPath) {
    this.cacheDir = cacheDir;
    this.baseUrl = baseUrl;
    this.localPath = localPath;
    this.metadataPath = path.join(cacheDir, "metadata.json");
    await this.loadMetadata();
  },

  async loadMetadata() {
    try {
      this.metadata = await fs.readJson(this.metadataPath);
    } catch (err) {
      this.metadata = {};
    }
  },

  async saveMetadata() {
    const unlock = await lockfile.lock(this.metadataPath, {
      realpath: false,
      retries: this.retries,
    });
    try {
      var metaData = this.metadata;
      await this.loadMetadata();
      this.metadata = { ...this.metadata, ...metaData };
      await fs.writeJson(this.metadataPath, this.metadata);
    } finally {
      unlock();
    }
  },

  getMetadata(filePath) {
    return (fs.existsSync(filePath) && this.metadata[filePath]) || {};
  },

  async setMetadata(filePath, metadata) {
    this.metadata[filePath] = metadata;
    await this.saveMetadata();
  },

  getFileExtension(filePath) {
    const parts = filePath.split(".");
    if (parts.length > 1) {
      return parts.pop().replace(/[<>:"/\\|?*\x00-\x1F.]/g, "");
    }
    return "";
  },

  async cachedResource(src, progress) {
    if (!src.startsWith("http")) return src;
    if (this.baseUrl && this.localPath) {
      if (src.startsWith(this.baseUrl)) {
        src = src.replace(this.baseUrl, "");
        return path.normalize(path.join(this.localPath, src));
      }
    }
    cacheDir = this.cacheDir;
    await fs.ensureDir(cacheDir);
    const key = md5(`${cacheDir}_${src}`);
    const ext = this.getFileExtension(url.parse(src).pathname);
    const cacheFile = path.join(cacheDir, `${key}${ext ? "." + ext : ""}`);

    return new Promise((resolve, reject) => {
      lockfile
        .lock(cacheFile, {
          realpath: false,
          retries: this.retries,
        })
        .then((unlock) => {
          fetch(src, {
            headers: {
              "If-None-Match": this.getMetadata(cacheFile).etag || "",
              "If-Modified-Since":
                this.getMetadata(cacheFile).lastModified || "",
            },
          })
            .then((res) => {
              let setMetadataInner = async () => {
                const etag = res.headers.get("etag") || "";
                const lastModified = res.headers.get("last-modified") || "";
                await this.setMetadata(cacheFile, { etag, lastModified });
              };
              if (res.status === 304) {
                // Not Modified
                return cacheFile;
              }
              return new Promise((r, j) => {
                let total = Number(res.headers.get("content-length")) || 0;
                try {
                  const stats = fs.statSync(cacheFile);
                  if (stats.size === total) {
                    (async function () {
                      await setMetadataInner();
                      r(cacheFile);
                    })();
                  }
                } catch (e) {}

                const fileStream = fs.createWriteStream(cacheFile);
                // console.log('total:', total);
                let str = progressStream({
                  length: total,
                  time: 100,
                });

                str.on("progress", function (progressData) {
                  progress && progress(progressData.transferred / total);
                });

                fileStream.on("finish", async function () {
                  await setMetadataInner();
                  r(cacheFile);
                });

                fileStream.on("error", function (err) {
                  j(err);
                });

                str.on("error", function (err) {
                  j(err);
                });

                res.body.on("error", function (err) {
                  j(err);
                });

                res.body.pipe(str).pipe(fileStream);
              });
            })
            .then((res) => {
              resolve(res);
            })
            .catch((error) => {
              reject(error);
            })
            .finally(() => {
              unlock();
            });
        })
        .catch((error) => {
          reject(error);
        });
    });
  },
  async cacheNode(node, progress) {
    let { type, src, path, url, fontFamily, font, preload } = node.conf;
    let source = src || path || url;
    // opencv读取video只能是本地的文件
    let cacheDir = node.rootConf("detailedCacheDir");
    // todo: 烧制都预先下载好
    preload = true;
    if (type === "text" && fontFamily?.startsWith("http")) {
      // must preload
      const fontPath = await CacheUtil.cachedResource(fontFamily, progress);
      node.cachedFontFamily = fontPath;
    } else if (type === "richtext" && font) {
      // default preload=true
      const fonts = Array.isArray(font) ? font : [font];
      for (const ft of fonts) {
        ft.format = node.fontFormat(ft);
        const path = await CacheUtil.cachedResource(ft.src, progress);
        ft.cachedSrc = node.base64path(path);
      }
      node.conf.font = fonts;
    } else if (["image", "gif"].includes(type) && source && preload) {
      // default preload=false
      node.conf.cachedSrc = await CacheUtil.cachedResource(
        source,
        progress,
        cacheDir
      );
    } else if (
      ["audio", "video", "speech"].includes(type) &&
      source &&
      preload
    ) {
      // default preload=false
      const ss = Date.now();
      node.conf.cachedSrc = await CacheUtil.cachedResource(
        source,
        progress,
        cacheDir
      );
      const paths = source.split("/");
      node.conf.srcFile = paths[paths.length - 1];
    } else {
      source = null;
    }
  },
};
module.exports = CacheUtil;
