import { app } from "../../../scripts/app.js";
(function (global) {
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

  function parseSRT(srtContent) {
    const entries = [];

    const normalized = srtContent
      .replace(/\r\n/g, "\n")
      .replace(/\r/g, "\n")
      .trim();

    const blocks = normalized.split(/\n{2,}/);

    for (const block of blocks) {
      const lines = block
        .trim()
        .split("\n")
        .map((l) => l.trim())
        .filter(Boolean);

      if (lines.length < 2) continue;

      const idLine = lines[0];
      const timeLine = lines[1];

      const id = parseInt(idLine);
      if (isNaN(id)) continue;

      const timeMatch = timeLine.match(
        /^(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})$/
      );
      if (!timeMatch) continue;

      const [_, startStr, endStr] = timeMatch;
      const text = lines.slice(2).join("\n");

      entries.push({
        index: id,
        start: timeToSeconds(startStr),
        end: timeToSeconds(endStr),
        content: text,
        isSelected: false,
      });
    }

    return entries;
  }

  function timeToSeconds(timeStr) {
    const [h, m, rest] = timeStr.split(":");
    const [s, ms] = rest.split(",");
    return (
      parseInt(h) * 3600 + parseInt(m) * 60 + parseInt(s) + parseInt(ms) / 1000
    );
  }

  function fitHeight(node) {
    const srtEditWidet = node.widgets.find((w) => w.name === "content");
    let contentHeight = 0;

    // 计算 srtEditWidet 的实际高度
    if (srtEditWidet?.entries?.length) {
      if (srtEditWidet && srtEditWidet.container.isConnected) {
        const rect = srtEditWidet.container.getBoundingClientRect();
        contentHeight = rect.height || srtEditWidet.entries.length * 40 + 20; // 每行约40px + 边距
      } else {
        // 回退值：基于 entries 数量估计
        contentHeight = srtEditWidet
          ? srtEditWidet.entries.length * 40 + 20
          : 0;
      }
    } else {
      contentHeight = 0;
    }

    // 获取基础尺寸（标题、其他 widgets 等）
    const baseSize = node.computeSize([node.size[0], node.size[1]]);
    const titleHeight = node.getTitleHeight ? node.getTitleHeight() : 30;
    const otherWidgetsHeight = node.widgets
      .filter((w) => w !== srtEditWidet)
      .reduce((sum, w) => sum + (w.computeSize ? w.computeSize()[1] : 30), 0);

    // 计算目标高度
    const targetHeight = contentHeight + otherWidgetsHeight;
    console.log("fitHeight__________", targetHeight, node);
    // 更新节点尺寸
    node.setSize([node.size[0], targetHeight]);
    node?.graph?.setDirtyCanvas(true);
  }

  function changeWidget() {
    let new_widgets = [];
    new_widgets=[...this.widgets]
    new_widgets.push(
      app.widgets.MontagenTextUpload1(
        this,
        "text",
        [
          {
            name: "text",
            type: "string",
            value: "Hello World",
            default: "Hello World",
            widget_type: "TextWidget",
            options: {},
          },
        ],
        app
      ).widget
    );

    /**************** 新建编辑widgets *********************/
    let element = document.createElement("div");
    element.style.cssText = `
      max-height: 200px;
      overflow-y: auto;
      border: 1px solid #ccc;
      border-radius: 4px;
      padding: 6px 2px;
      font-size: 12px;
      display: none; /* 初始隐藏 */
    `;
    element.addEventListener(
      "contextmenu",
      (e) => {
        e.preventDefault();
        return app.canvas._mousedown_callback(e);
      },
      true
    );
    let srtEditWidet = this.addDOMWidget("content", "srtEditWidet", element, {
      serialize: true,
      hideOnZoom: false,
      getValue() {
        return srtEditWidet.entries || [];
      },
      setValue(v) {
        try {
          console.log("widget value", v, srtEditWidet);
          if (!v) {
            srtEditWidet.entries = [];
            srtEditWidet.updateUI([]);

            return;
          }
          srtEditWidet.updateUI(v);
        } catch (e) {
          console.error("Error parsing widget value:", e);
          srtEditWidet.entries = [];
          srtEditWidet.updateUI([]);
        }
      },
    });
    srtEditWidet.container = document.createElement("div");
    srtEditWidet.container.innerHTML = "";
    const createEntryElement = (entry, index) => {
      const div = document.createElement("div");
      div.style.cssText = `display: flex; margin-bottom: 10px;align-items: flex-start;`;
      div.innerHTML = `
            <input type="checkbox" ${entry.isSelected ? "checked" : ""}></input>
            <div style="flex: 1; margin-left: 6px;border-bottom: 1px solid #eee;">
              <div style="margin-bottom:2rpx">${entry.index}   </div>
              <span style="margin-bottom:2rpx">${entry.start} --> ${
        entry.end
      }</span>
              <textarea  style="width: 100%;height:16px;border:none;outline:none;resize: none;font-size:10px;line-height: 1.2;" >${
                entry.content
              }</textarea>
            </div>
        `;
      const textarea = div.querySelector("textarea");
      setTimeout(() => {
        textarea.style.height = textarea.scrollHeight + "px";
      }, 0);
      textarea.addEventListener("input", () => {
        console.log("textarea value", textarea.value);
        srtEditWidet.entries[index].content = textarea.value;
        // textarea.style.height = 'auto';
        textarea.style.height = textarea.scrollHeight + "px";
      });

      const checkbox = div.querySelector('input[type="checkbox"]');
      checkbox.addEventListener("change", () => {
        console.log("checkbox checked", checkbox.checked);
        srtEditWidet.entries[index].isSelected = checkbox.checked;

        srtEditWidet.updateNodeData();
      });
      return div;
    };
    srtEditWidet.updateUI = function (entries) {
      srtEditWidet.entries = entries;
      srtEditWidet.container.innerHTML = "";
      if (!entries.length) {
        element.style.display = "none";
      } else {
        element.style.display = "block";
        entries.forEach((entry, index) => {
          srtEditWidet.container.appendChild(createEntryElement(entry, index));
        });
      }
    };

    srtEditWidet.updateNodeData = function () {
      // 更新节点数据
      // this.node.widgets[0].value = JSON.stringify(this.entries);
      this.node.setDirtyCanvas(true, true);
      this.adjustNodeSize();
    };

    srtEditWidet.adjustNodeSize = function () {
      fitHeight(this.node);
    };
    element.appendChild(srtEditWidet.container);
    new_widgets.push(srtEditWidet);
    this.widgets = new_widgets;
    console.log("changeWidget_当前node 使用的widgets 组件", this.widgets);
    srtEditWidet.adjustNodeSize();
  }

  app.registerExtension({
    name: "Comfy.Montagen.TextEditor1",
    beforeRegisterNodeDef(nodeType, nodeData) {
      // console.log("registering_TextEditor", nodeType, nodeData);
      if (nodeData.name == "MontagenTimeRangeCreateNode") {
        console.log("找到了这个named 节点", nodeType.prototype, nodeData);
        chainCallback(nodeType.prototype, "onNodeCreated", function () {
          changeWidget.call(this);
        });
      }
    },
    async getCustomWidgets() {
      return {
        MontagenTextUpload1(node, inputName, inputData, app) {
          const fileInput = document.createElement("input");
          Object.assign(fileInput, {
            type: "file",
            accept: ".srt",
            style: "display: none",
            onchange: async (event) => {
              if (fileInput.files && fileInput.files.length) {
                // console.log("fileInput.files", fileInput.files);
                let result = await readFile(fileInput.files[0]).catch(
                  (err) => {}
                );
                // console.log("result_读取出来的文本信息", result);
                console.log("result_读取出来的文本信息", node.widgets);
                // 查找 srtEditWidet
                const srtEditWidet = node.widgets.find(
                  (w) => w.name === "content"
                );
                if (srtEditWidet) {
                  // 更新 UI
                  srtEditWidet.updateUI(result);
                  // 更新节点数据
                  srtEditWidet.updateNodeData();
                } else {
                  console.error("srtEditWidet not found in node.widgets");
                }
                event.target.value = ""; // 清空文件输入框的值
              }
            },
          });
          const readFile = (file) => {
            return new Promise((resolve, reject) => {
              const reader = new FileReader();
              reader.onload = (event) => {
                const jsonData = parseSRT(event.target.result);
                resolve(jsonData);
              };
              reader.onerror = (event) => {
                reject(event.target.error);
              };
              reader.readAsText(file);
            });
          };
          document.body.append(fileInput);
          const uploadWidget = node.addWidget(
            "button",
            inputName,
            "image",
            () => {
              fileInput.click();
            }
          );
          uploadWidget.serialize = false;
          return { widget: uploadWidget };
        },
      };
    },
  });
})(window);
