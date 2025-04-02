import { app } from "../../../scripts/app.js";
import { api } from "../../../scripts/api.js";

(function (globalObj) {
  let list = ["Untitled Clip_0_20250401094527.gif", "1.mp4"];
  let listCallBack = [];
  let supportedTypes = {
    video: [".mp4", ".webm"],
    audio: [".mp3", ".wav", ".aac"],
    image: [".jpg", ".jpeg", ".png"],
    gif: [".gif"],
  };
  function fitHeight(node) {
    node.setSize([
      node.size[0],
      node.computeSize([node.size[0], node.size[1]])[1],
    ]);
    node?.graph?.setDirtyCanvas(true);
  }
  let supportedMimeTypes =
    "video/mp4,video/webm,audio/mpeg,audio/wav,audio/aac,image/jpeg,image/png,image/gif";
  function getFileType(fileName) {
    const ext = fileName.split(".").pop().toLowerCase();
    for (const [fileType, extensions] of Object.entries(supportedTypes)) {
      if (extensions.includes(`.${ext}`)) {
        return fileType;
      }
    }
    return null;
  }
  globalObj.setMontagenAssetsList = function (listAssets) {
    list = listAssets;
    for (const cb of listCallBack) {
      try {
        cb();
      } catch (e) {
        console.log(e);
      }
    }
  };
  function chainCallback(object, property, callback) {
    if (object == undefined) {
      //This should not happen.
      console.error("Tried to add callback to non-existant object");
      return;
    }
    if (property in object && object[property]) {
      const callback_orig = object[property];
      object[property] = function () {
        const r = callback_orig.apply(this, arguments);
        callback.apply(this, arguments);
        return r;
      };
    } else {
      object[property] = callback;
    }
  }

  function changeWidget() {
    let new_widgets = [];
    if (this.widgets) {
      let widgets = [...this.widgets];
      for (let w of widgets) {
        let input = this.constructor.nodeData.input;
        let config = input?.required[w.name] ?? input.optional[w.name];
        if (!config) {
          continue;
        }
        if (config[1]?.montagen_upload) {
          let comboValue = w.value;
          let new_widget = app.widgets.COMBO(this, w.name, [
            list,
            config[1],
          ]).widget;
          new_widget.value = comboValue;
          new_widgets.push(new_widget);
        } else if (w?.name == "upload") {
          new_widgets.push(
            app.widgets.MONTAGENFILEUPLOAD(
              this,
              w.name,
              config,
              app,
              new_widgets
            ).widget
          );
        } else {
          new_widgets.push(w);
        }
      }
      if (!this.previewWidget) {
        var element = document.createElement("div");
        const previewNode = this;
        var previewWidget = this.addDOMWidget(
          "mon_videopreview",
          "mon_preview",
          element,
          {
            serialize: false,
            hideOnZoom: false,
            getValue() {
              return element.value;
            },
            setValue(v) {
              element.value = v;
            },
          }
        );
        previewWidget.computeSize = function (width) {
          if (this.aspectRatio && !this.parentEl.hidden) {
            let height = (previewNode.size[0] - 20) / this.aspectRatio + 10;
            if (!(height > 0)) {
              height = 0;
            }
            this.computedHeight = height + 10;
            return [width, height];
          }
          return [width, -4]; //no loaded src, widget should not display
        };
        element.addEventListener(
          "contextmenu",
          (e) => {
            e.preventDefault();
            return app.canvas._mousedown_callback(e);
          },
          true
        );
        element.addEventListener(
          "pointerdown",
          (e) => {
            e.preventDefault();
            return app.canvas._mousedown_callback(e);
          },
          true
        );
        element.addEventListener(
          "mousewheel",
          (e) => {
            e.preventDefault();
            return app.canvas._mousewheel_callback(e);
          },
          true
        );
        previewWidget.value = {
          hidden: false,
          paused: false,
          params: {},
        };
        previewWidget.parentEl = document.createElement("div");
        previewWidget.parentEl.className = "Mon_preview";
        previewWidget.parentEl.style["width"] = "100%";
        element.appendChild(previewWidget.parentEl);
        previewWidget.videoEl = document.createElement("video");
        previewWidget.videoEl.controls = false;
        previewWidget.videoEl.loop = true;
        previewWidget.videoEl.muted = true;
        previewWidget.videoEl.style["width"] = "100%";
        previewWidget.videoEl.addEventListener("loadedmetadata", () => {
          previewWidget.aspectRatio =
            previewWidget.videoEl.videoWidth /
            previewWidget.videoEl.videoHeight;
          fitHeight(previewNode);
        });
        previewWidget.videoEl.addEventListener("error", () => {
          //TODO: consider a way to properly notify the user why a preview isn't shown.
          previewWidget.parentEl.hidden = true;
          fitHeight(previewNode);
        });
        previewWidget.videoEl.onmouseenter = () => {
          previewWidget.videoEl.muted = previewWidget.value.muted;
        };
        previewWidget.videoEl.onmouseleave = () => {
          previewWidget.videoEl.muted = true;
        };

        previewWidget.updateSource = function (src, type) {
          if (type == "video" || type == "audio") {
            this.videoEl.autoplay = !this.value.paused && !this.value.hidden;
            let target_width = 256;
            if (element.style?.width) {
              //overscale to allow scrolling. Endpoint won't return higher than native
              target_width = element.style.width.slice(0, -2) * 2;
            }
            previewWidget.videoEl.src = src;
            this.videoEl.hidden = false;
            this.parentEl.hidden = false;
          } else {
            this.videoEl.hidden = true;
            this.parentEl.hidden = true;
          }
        };
        previewWidget.parentEl.appendChild(previewWidget.videoEl);
        this.previewWidget = previewWidget;
      }
      new_widgets.push(this.previewWidget);
      this.widgets = new_widgets;
    }
  }

  app.registerExtension({
    name: "Comfy.Montagen.UploadFile",
    beforeRegisterNodeDef(nodeType, nodeData) {
      const fileInputSpec = nodeData?.input?.required?.file;
      const config = fileInputSpec?.[1] ?? {};
      const { montagen_upload = false } = config;
      if (montagen_upload) {
        nodeData.input.optional.upload = ["MONTAGENFILEUPLOAD"];
        nodeType.isMontagenUpload = true;
      }
      chainCallback(nodeType.prototype, "onNodeCreated", function () {
        if (this.constructor.isMontagenUpload) {
          listCallBack.push(() => {
            changeWidget.call(this);
          });
          changeWidget.call(this);
        }
      });
    },
    async getCustomWidgets() {
      return {
        MONTAGENFILEUPLOAD(node3, inputName, inputData, app2, new_widgets) {
          const imageWidget = (new_widgets ?? node3.widgets)?.find(
            (w2) => w2.name === (inputData[1]?.widget ?? "file")
          );

          function showImage(name2, type) {
            let projId = app2.graph.extra.MontagenProj?.projectId ?? "1";
            let src = api.apiURL(
              `/Montagen/Proj/${projId}/File/${encodeURIComponent(name2)}`
            );
            if (type == "image" || type == "gif") {
              const img = new Image();
              img.onload = () => {
                node3.imgs = [img];
                app2.graph.setDirtyCanvas(true);
              };
              img.src = src;
              node3.setSizeForImage?.();
              node3.previewWidget.updateSource(src, type);
            } else {
              node3.imgs = null;
              node3.previewWidget.updateSource(src, type);
            }
          }
          const default_value = imageWidget.value;
          Object.defineProperty(imageWidget, "value", {
            set: function (value4) {
              this._real_value = value4;
              this.montagen_type = getFileType(value4);
            },
            get: function () {
              if (!this._real_value) {
                return default_value;
              }
              return this._real_value;
            },
          });
          const cb = node3.callback;
          imageWidget.callback = function (...args) {
            showImage(imageWidget.value, imageWidget.montagen_type);
            if (cb) {
              return cb.apply(this, args);
            }
          };
          requestAnimationFrame(() => {
            if (imageWidget.value) {
              showImage(imageWidget.value, imageWidget.montagen_type);
            }
          });
          async function uploadFile2(file, updateNode) {
            try {
              const body = new FormData();
              body.append("f", file);
              let projId = app2.graph.extra.MontagenProj?.projectId ?? "1";
              const url = `/Montagen/Proj/${projId}/Assets/Upload`;
              const resp = await api.fetchApi(url, {
                method: "POST",
                body,
              });
              if (resp.status === 200) {
                const data26 = await resp.json();
                let path = data26.data[0];
                if (!imageWidget.options) {
                  imageWidget.options = { values: [] };
                }
                if (!imageWidget.options.values) {
                  imageWidget.options.values = [];
                }
                if (!imageWidget.options.values.includes(path)) {
                  imageWidget.options.values.push(path);
                }
                setTimeout(() => {
                  setMontagenAssetsList(imageWidget.options.values);
                }, 1000);
                imageWidget.value = path;
                showImage(path, imageWidget.montagen_type);
              } else {
                useToastStore().addAlert(resp.status + " - " + resp.statusText);
              }
            } catch (error2) {
              useToastStore().addAlert(String(error2));
            }
          }
          const fileInput2 = document.createElement("input");
          Object.assign(fileInput2, {
            type: "file",
            accept: supportedMimeTypes,
            style: "display: none",
            onchange: async () => {
              if (fileInput2.files && fileInput2.files.length) {
                await uploadFile2(fileInput2.files[0], true);
              }
            },
          });
          document.body.append(fileInput2);
          const uploadWidget = node3.addWidget(
            "button",
            inputName,
            "image",
            () => {
              fileInput2.click();
            }
          );
          uploadWidget.label = "choose file to upload";
          uploadWidget.serialize = false;
          node3.onDragOver = function (e2) {
            if (e2.dataTransfer && e2.dataTransfer.items) {
              const image2 = [...e2.dataTransfer.items].find(
                (f2) => f2.kind === "file"
              );
              return !!image2;
            }
            return false;
          };
          node3.onDragDrop = function (e2) {
            console.log("onDragDrop called");
            let handled = false;
            if (e2.dataTransfer?.files) {
              for (const file of e2.dataTransfer.files) {
                if (supportedMimeTypes.includes(file.type)) {
                  uploadFile2(file, !handled);
                  handled = true;
                }
              }
            }
            return handled;
          };
          node3.pasteFile = function (file) {
            if (supportedMimeTypes.includes(file.type)) {
              uploadFile2(file, true);
              return true;
            }
            return false;
          };
          return { widget: uploadWidget };
        },
      };
    },
    async beforeConfigureGraph(graphData, missingNodeTypes) {
      listCallBack = [];
    },
  });
})(window);
