(function() {
  "use strict";
  try {
    if (typeof document != "undefined") {
      var elementStyle = document.createElement("style");
      elementStyle.appendChild(document.createTextNode("[data-v-466e15aa] .left-tool-button {\r\n  /* Your styles here */\r\n  height: 40px;\r\n  width: 40px;\r\n  border-radius: 0 !important;\r\n  margin-bottom: 10px;\n&.left-tool-button-select[data-v-466e15aa] {\r\n    border-left: 2px solid #09AAFE;\r\n    box-sizing: border-box;\n}\n}\r\n[data-v-590c40f6] .split-container {\n  border: none;\n  border-radius: 0;\n  width: 100%;\n  height: 100%;\n}\n[data-v-590c40f6] .split-container .split-gutter {\n  background: #181818;\n}\n[data-v-590c40f6] .split-container.left-hidden .split-panel-left {\n  display: none;\n}\n[data-v-590c40f6] .split-container.left-hidden > .split-gutter {\n  display: none;\n}\n.imagen-header[data-v-0dd8d624] {\r\n  font-size: 0.8em;\n}\n.imagen-header h1[data-v-0dd8d624] {\r\n  font-size: 1.2em;\r\n  color: #333;\n}\r\n\n.new-imagen-box[data-v-1de60b9f] {\r\n  position: fixed;\r\n  width: 100%;\r\n  height: 100vh;\r\n  z-index: 600;\r\n  bottom: 0;\r\n  left: 0;\r\n  background: #262626;\r\n  color: #fff;\r\n  grid-template-columns: 40px 1fr;\r\n  grid-template-rows: 40px 1fr;\n}\n.new-imagen-box .image-box-top[data-v-1de60b9f] {\r\n  grid-row: 1;\r\n  grid-column: 1/span 2;\r\n  background-color: #181818;\r\n  order: 1;\r\n  display: flex;\r\n  border-bottom: 1px solid #2b2b2b;\n}\n.new-imagen-box .image-box-left[data-v-1de60b9f] {\r\n  grid-row: 2;\r\n  grid-column: 1;\r\n  background-color: #181818;\r\n  order: 2;\r\n  display: flex;\r\n  border-right: 1px solid #2b2b2b;\n}\n.new-imagen-box .image-box-container[data-v-1de60b9f] {\r\n  grid-row: 2;\r\n  grid-column: 2;\r\n  background-color: goldenrod;\r\n  width: 100%;\r\n  height: 100%;\r\n  order: 3;\r\n  display: flex;\n}"));
      document.head.appendChild(elementStyle);
    }
  } catch (e) {
    console.error("vite-plugin-css-injected-by-js", e);
  }
})();
var _a, _b, _c, _d, _e, _f, _g, _h, _i, _j, _k, _l, _m, _n;
import { d as defineComponent, o as openBlock, c as createElementBlock, a as createBaseVNode, O as Fragment, P as renderList, Q as unref, F as withDirectives, z as createBlock, x as computed, w as watch, r as ref, e as onMounted, R as onBeforeUnmount, D as createVNode, E as withCtx, N as toDisplayString, M as createTextVNode, A as createCommentVNode, S as createApp } from "./assets/vue-PBQkR_Po.js";
import { d as defineStore, s as storeToRefs, a as script, T as Tooltip, b as script$1, c as script$2, u as useToast, e as script$3, C as ConfirmationService, f as ToastService, D as DialogService, g as createPinia } from "./assets/vendor-BGvmUE3P.js";
import "./assets/lodash-BBlPwZSq.js";
import { j as definePreset, k as index, P as PrimeVue } from "./assets/primevue-D2NjrsJ7.js";
import { E as ElementPlusIconsVue } from "./assets/element-plus-Fgh1tvua.js";
import "./assets/primeuix-BGFRwHXQ.js";
const useFileStore = defineStore("fileStore", {
  state: (_) => ({
    selectFiles: [],
    outPutFormat: {
      height: "1280",
      // 图片高度
      width: "720",
      // 图片宽度
      imageLen: 1,
      // 图片张数
      fps: 60
    },
    selectClip: {},
    // 当前选中的clip项
    PlayerInstance: null
    // 初始话收的editor实例对象
  }),
  actions: {
    addFile(file) {
      this.selectFiles.push(file);
      console.log(this.selectFiles);
    },
    removeFile(file) {
      this.selectFiles = this.selectFiles.filter((item) => item.id !== file.id);
      console.log(this.selectFiles);
    },
    clearFiles() {
      this.selectFiles = [];
    },
    setOutFormat(key, value) {
      if (key in this.outPutFormat) {
        this.outPutFormat[key] = value;
      }
    },
    setSelectClip(clip) {
      this.selectClip = clip;
    },
    setPlayerInstance(player) {
      this.PlayerInstance = player;
    }
  }
});
const useMenuStore = defineStore("menuStore", {
  state: (_) => ({
    showPage: false
  }),
  actions: {
    changeShow(flag) {
      this.showPage = flag ?? !this.showPage;
    }
  }
});
let app$1 = ((_b = (_a = window.comfyAPI) == null ? void 0 : _a.app) == null ? void 0 : _b.app) || null;
((_d = (_c = window.comfyAPI) == null ? void 0 : _c.api) == null ? void 0 : _d.api) || null;
((_f = (_e = window.comfyAPI) == null ? void 0 : _e.ui) == null ? void 0 : _f.$el) || null;
((_h = (_g = window.comfyAPI) == null ? void 0 : _g.dialog) == null ? void 0 : _h.ComfyDialog) || null;
((_j = (_i = window.comfyAPI) == null ? void 0 : _i.widgets) == null ? void 0 : _j.ComfyWidgets) || null;
((_l = (_k = window.comfyAPI) == null ? void 0 : _k.utils) == null ? void 0 : _l.applyTextReplacements) || null;
((_n = (_m = window.comfyAPI) == null ? void 0 : _m.groupNode) == null ? void 0 : _n.GroupNodeConfig) || null;
const useLeftToolStore = defineStore("leftToolStore", {
  state: (_) => ({
    menues: [
      {
        name: "home",
        tips: "anything is possible",
        selected: false,
        icon: "pi pi-home"
      },
      {
        name: "mark",
        tips: "anything is bookmark",
        selected: false,
        icon: "pi pi-bookmark"
      }
    ],
    selectedMenu: {}
  }),
  actions: {
    changeSelect(item) {
      this.menues.forEach((ele) => {
        if (item.name == ele.name) {
          ele.selected = !ele.selected;
          this.selectedMenu = ele.selected ? ele : {};
        } else {
          ele.selected = false;
        }
      });
    }
  }
});
const _hoisted_1$3 = { class: "toolbar" };
const _sfc_main$4 = /* @__PURE__ */ defineComponent({
  __name: "leftToolbar",
  setup(__props) {
    const leftToolStore = useLeftToolStore();
    const { menues } = storeToRefs(leftToolStore);
    const onTabClick = (item) => {
      console.log("click", item);
      leftToolStore.changeSelect(item);
    };
    return (_ctx, _cache) => {
      const _directive_tooltip = Tooltip;
      return openBlock(), createElementBlock("div", _hoisted_1$3, [
        createBaseVNode("nav", null, [
          (openBlock(true), createElementBlock(Fragment, null, renderList(unref(menues), (item) => {
            return withDirectives((openBlock(), createBlock(unref(script), {
              icon: item.icon,
              text: "",
              "aria-label": "Save",
              pt: {
                root: {
                  class: `left-tool-button ${item.selected ? "p-button-primary left-tool-button-select" : "p-button-secondary"}`
                }
              },
              onClick: ($event) => onTabClick(item)
            }, null, 8, ["icon", "pt", "onClick"])), [
              [_directive_tooltip, { value: item.tips, showDelay: 300, hideDelay: 300 }]
            ]);
          }), 256))
        ])
      ]);
    };
  }
});
const _export_sfc = (sfc, props) => {
  const target = sfc.__vccOpts || sfc;
  for (const [key, val] of props) {
    target[key] = val;
  }
  return target;
};
const leftToolbar = /* @__PURE__ */ _export_sfc(_sfc_main$4, [["__scopeId", "data-v-466e15aa"]]);
const _hoisted_1$2 = { style: { "min-width": "70px" } };
const _sfc_main$3 = /* @__PURE__ */ defineComponent({
  __name: "boxContainer",
  setup(__props) {
    const leftToolStore = useLeftToolStore();
    const { menues, selectedMenu } = storeToRefs(leftToolStore);
    const showLeftPanel = computed(() => {
      return menues.value.some((item) => item.selected);
    });
    watch(showLeftPanel, () => {
      parentWidth && updateSizes();
    });
    const splitterSizes = ref([20, 80]);
    let observer;
    const parentWidth = ref(0);
    const container = ref(null);
    const updateSizes = () => {
      if (showLeftPanel.value) {
        const leftSize = 200 / parentWidth.value * 100;
        splitterSizes.value = [leftSize, 100 - leftSize];
      } else {
        splitterSizes.value = [0, 100];
      }
    };
    onMounted(() => {
      parentWidth.value = container.value.offsetWidth;
      updateSizes();
      observer = new ResizeObserver((entries) => {
        parentWidth.value = entries[0].contentRect.width;
        updateSizes();
      });
      observer.observe(container.value);
    });
    onBeforeUnmount(() => observer == null ? void 0 : observer.disconnect());
    return (_ctx, _cache) => {
      return openBlock(), createElementBlock("div", {
        class: "w-full h-full",
        ref_key: "container",
        ref: container
      }, [
        createVNode(unref(script$1), {
          sizes: splitterSizes.value,
          "onUpdate:sizes": _cache[0] || (_cache[0] = ($event) => splitterSizes.value = $event),
          dt: { "background": "#262626", "height": "100%", "width": "100%" },
          pt: {
            root: { class: `split-container ${showLeftPanel.value ? "" : "left-hidden"}` },
            gutter: { class: "split-gutter" }
          }
        }, {
          default: withCtx(() => [
            createVNode(unref(script$2), {
              class: "flex items-center justify-center",
              pt: {
                root: { class: "split-panel-left" }
              },
              size: splitterSizes.value[0]
            }, {
              default: withCtx(() => [
                createBaseVNode("div", _hoisted_1$2, " Panel 2 -- " + toDisplayString(unref(selectedMenu).name), 1)
              ]),
              _: 1
            }, 8, ["size"]),
            createVNode(unref(script$2), {
              size: splitterSizes.value[1]
            }, {
              default: withCtx(() => [
                createVNode(unref(script$1), {
                  layout: "vertical",
                  pt: {
                    gutter: { class: "split-gutter" }
                  }
                }, {
                  default: withCtx(() => [
                    createVNode(unref(script$2), { size: 70 }, {
                      default: withCtx(() => [
                        createVNode(unref(script$1), { pt: {
                          gutter: { class: "split-gutter" }
                        } }, {
                          default: withCtx(() => [
                            createVNode(unref(script$2), {
                              class: "flex items-center justify-center",
                              size: 80
                            }, {
                              default: withCtx(() => [
                                createTextVNode(" Panel 3 ")
                              ]),
                              _: 1
                            }),
                            createVNode(unref(script$2), {
                              class: "flex items-center justify-center",
                              size: 20
                            }, {
                              default: withCtx(() => [
                                createTextVNode(" Panel 4 ")
                              ]),
                              _: 1
                            })
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    createVNode(unref(script$2), {
                      class: "flex items-center justify-center",
                      size: 30
                    }, {
                      default: withCtx(() => [
                        createTextVNode(" Panel 2 " + toDisplayString(showLeftPanel.value) + " -- " + toDisplayString(splitterSizes.value), 1)
                      ]),
                      _: 1
                    })
                  ]),
                  _: 1
                })
              ]),
              _: 1
            }, 8, ["size"])
          ]),
          _: 1
        }, 8, ["sizes", "pt"])
      ], 512);
    };
  }
});
const boxContainer = /* @__PURE__ */ _export_sfc(_sfc_main$3, [["__scopeId", "data-v-590c40f6"]]);
const blankGraph = {
  last_node_id: 0,
  last_link_id: 0,
  nodes: [],
  links: [],
  groups: [],
  config: {},
  extra: {},
  version: 0.4
};
const _hoisted_1$1 = { class: "imagen-header flex" };
const _sfc_main$2 = /* @__PURE__ */ defineComponent({
  __name: "imagenHeader",
  setup(__props) {
    const menuStore = useMenuStore();
    const goBack = () => {
      menuStore.changeShow(false);
    };
    const createmode = async () => {
      menuStore.changeShow(false);
      await app$1.loadGraphData(blankGraph);
      setTimeout(() => {
        app$1.addNodeOnGraph(window.montaiData, { pos: app$1.getCanvasCenter() });
      }, 10);
    };
    return (_ctx, _cache) => {
      return openBlock(), createElementBlock("div", _hoisted_1$1, [
        createBaseVNode("h1", {
          class: "mx-2 cursor-pointer",
          onClick: goBack
        }, "返回"),
        createBaseVNode("h1", {
          class: "mx-2 cursor-pointer",
          onClick: createmode
        }, "新建node节点")
      ]);
    };
  }
});
const imagenHeader = /* @__PURE__ */ _export_sfc(_sfc_main$2, [["__scopeId", "data-v-0dd8d624"]]);
const _hoisted_1 = { class: "new-imagen-box grid" };
const _hoisted_2 = { class: "image-box-top" };
const _hoisted_3 = { class: "image-box-left" };
const _hoisted_4 = { class: "image-box-container" };
const _sfc_main$1 = /* @__PURE__ */ defineComponent({
  __name: "index",
  setup(__props) {
    return (_ctx, _cache) => {
      return openBlock(), createElementBlock("div", _hoisted_1, [
        createBaseVNode("div", _hoisted_2, [
          createVNode(imagenHeader)
        ]),
        createBaseVNode("div", _hoisted_3, [
          createVNode(leftToolbar)
        ]),
        createBaseVNode("div", _hoisted_4, [
          createVNode(boxContainer)
        ])
      ]);
    };
  }
});
const newImagenBox = /* @__PURE__ */ _export_sfc(_sfc_main$1, [["__scopeId", "data-v-1de60b9f"]]);
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "App",
  setup(__props) {
    const menuStore = useMenuStore();
    const fileStore = useFileStore();
    useToast();
    const { showPage } = storeToRefs(menuStore);
    const checked = showPage;
    const switchRef = ref(null);
    const switchChange = (_) => {
      menuStore.changeShow(true);
    };
    let originHost = window.location.origin + "/view?filename=";
    const updateMessage = (message) => {
      console.log("updateMessage", message);
      fileStore.clearFiles();
      let file = {
        filepath: `${originHost}${message.addr}`,
        name: message.addr
      };
      fileStore.addFile(file);
      console.log("fileStore.setOutFormat", fileStore.selectFiles);
      fileStore.setOutFormat("height", message.height);
      fileStore.setOutFormat("width", message.width);
      fileStore.setOutFormat("imageLen", message.imageLen);
      fileStore.setOutFormat("fps", message.fps);
      menuStore.changeShow(true);
    };
    function chainCallback(object, property, callback) {
      if (object == void 0) {
        console.error("Tried to add callback to non-existant object");
        return;
      }
      if (property in object && object[property]) {
        const callback_orig = object[property];
        object[property] = function() {
          const r = callback_orig.apply(this, arguments);
          callback.apply(this, arguments);
          return r;
        };
      } else {
        object[property] = callback;
      }
    }
    const addUploadWidget = function(nodeType, nodeData, type, icon) {
      chainCallback(nodeType.prototype, "onNodeCreated", function(...arg) {
        this.addWidget("button", "preview", "image", () => {
          if (sessionStorage.getItem("Montagen-output")) {
            console.log("window.sessionStorage.getItem", sessionStorage.getItem("Montagen-output"));
            updateMessage(JSON.parse(sessionStorage.getItem("Montagen-output")));
          }
          menuStore.changeShow(true);
        });
      });
    };
    const addCustomDom = function(nodeType) {
      chainCallback(nodeType.prototype, "onNodeCreated", function(...arg) {
        var element = document.createElement("div");
        element.innerText = "Montagen哈哈哈";
        console.log("element", this.addDOMWidget, this.size, this.computeSize);
        element.onclick = function() {
          alert("Montagen");
        };
        var previewWidget = this.addDOMWidget("videopreview", "preview", element, {
          serialize: false,
          hideOnZoom: false,
          getValue() {
            return element.value;
          },
          setValue(v) {
            element.value = v;
          }
        });
        return previewWidget;
      });
    };
    let tempNodeType = null;
    const init = () => {
      if (switchRef.value) {
        switchRef.value.style.display = "none";
        app$1.registerExtension({
          name: "EasymskPage",
          setup(ui) {
            console.log("onUIReady", ui);
            window.myUI = ui;
          },
          async beforeRegisterNodeDef(nodeType, nodeData, app2) {
            if ((nodeData == null ? void 0 : nodeData.name) == "MontagenImagesPreview") {
              tempNodeType = nodeType;
              console.log("nodeType 获取node 数据", nodeType, nodeData);
              addCustomDom(nodeType);
              window.montaiData = nodeData;
              addUploadWidget(tempNodeType);
              chainCallback(nodeType.prototype, "onExecuted", async function(message) {
                console.log("onExecuted 函数执行成功后返回的数据", message);
                if (message == null ? void 0 : message.videos) {
                  sessionStorage.setItem("Montagen-output", JSON.stringify(message.videos[0]));
                }
              });
            }
          }
        });
      }
    };
    onMounted(() => {
      try {
        init();
      } catch (e) {
      }
    });
    return (_ctx, _cache) => {
      const _directive_tooltip = Tooltip;
      return openBlock(), createElementBlock(Fragment, null, [
        unref(checked) ? (openBlock(), createBlock(newImagenBox, { key: 0 })) : createCommentVNode("", true),
        withDirectives((openBlock(), createElementBlock("div", {
          ref_key: "switchRef",
          ref: switchRef,
          class: "cursor-pointer text-center",
          onClick: switchChange
        }, [
          createVNode(unref(script$3), {
            src: "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAAAXNSR0IArs4c6QAAAixJREFUaEPtmkuSgjAQhrtB76E30ZvoWsfHbmqwyqFKpmbnY3CtcxK9iRxEyFSkgoQRITFAsHRnEZL++k8/CCDU/Ic1tx+eC2A4W3YIMXYI0NJRGQLgGQTtn6/RntnHKTC0NgcA0tHReGYThdg64/ZNgIG1Punq/bhTXWccOZ5TIA7Q8IP26nvqsRsH1mqHgL3wPx5dZ9RNKjV5X7bOprljKiLBflxuNj4cZ5yi+zHouovp8Z7yQ2tN2HUpgLyLvn1segTJji6WlDtuIL9dbzuEH/8gAJ2sShUeVoACVKmCEoAqVVAGUJUKwgA0gxDDj7IQlyGIOb/WCzwC+nYyg2BgtgIk8ygtI9gAwb9MQ8exoL/kt7R1iXEQykI6F7NcafQJAPBuYSkf8Nri5FIgWYnLN5hfUTiIXwCKJStcAfosQW3OaspkuQoF4Bs4sm/6xI53srJGK2/m0gzhm7ywC0WEX3cx/lRhPJ2jUAWSAMxolSCVAPAgQf+R+KgU4AoiHx9aALCnNJn40AZANj60A4hvq60z6WdlK40BwGv6QTerbmgMQPa1VCCsEflTq14KINiiVVoPAAnDWXBXCiC6XW5lpEoA6t0LPbBdSlcg/jxAT64bvt/PyutZhSt5vdAtdOnXZ8tO4wyeasNLCWJRb8qML1wBGaNE7nkBiHiriLHCChRhhKo5U48W6/Ca9XL2lPaW8nI4xZ39q/KZmnlutSTP9amBGj+VO0vtFfgDiSO5TwE1Yj4AAAAASUVORK5CYII=",
            width: "20"
          })
        ])), [
          [_directive_tooltip, "open MontagenEditor"]
        ])
      ], 64);
    };
  }
});
const ComfyUIPreset = definePreset(index, {
  semantic: {
    primary: index["primitive"].blue
  }
});
const maskpage = document.createElement("div");
maskpage.id = "comfyui-maskpage";
maskpage.style.cssText = `
  position: relative;
  z-index: 1100;
`;
document.body.append(maskpage);
const app = createApp(_sfc_main);
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component);
}
app.use(PrimeVue, {
  theme: {
    preset: ComfyUIPreset,
    options: {
      prefix: "p",
      cssLayer: {
        name: "primevue",
        order: "primevue, tailwind-utilities"
      },
      // This is a workaround for the issue with the dark mode selector
      // https://github.com/primefaces/primevue/issues/5515
      darkModeSelector: ".dark-theme, :root:has(.dark-theme)"
    }
  }
});
app.directive("tooltip", Tooltip);
app.use(ConfirmationService);
app.use(ToastService);
app.use(DialogService);
app.use(createPinia());
app.mount("#" + maskpage.id);
