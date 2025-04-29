import { app } from "../../../scripts/app.js";
import { api } from "../../../scripts/api.js";

(function (globalObj) {
  let list = [];
  let onListChangedCallbacks = [];

  async function updateModel(apiKey) {
    list = [];
    for (let item of onListChangedCallbacks) {
      try {
        item();
      } catch {}
    }
    try {
      const url = `/Montagen/FishAudio/Models?apiKey=${apiKey}`;
      const resp = await api.fetchApi(url);
      let msg = "Failed to fetch models";
      if (resp.status === 200) {
        let data = await resp.json();
        if (data.code == 0) {
          for (let model of data.data) {
            list.push(`${model.title}__${model.id}`);
          }
          for (let item of onListChangedCallbacks) {
            try {
              item();
            } catch {}
          }
          return;
        } else {
          msg = data.msg;
        }
      }
      throw new Error(resp.msg);
    } catch (error) {
      console.error("Error fetching models:", error);
    }
  }

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

  app.registerExtension({
    name: "Comfy.Montagen.FishAudio",
    settings: [
      {
        id: "montagen.fish_audio_api_key",
        category: ["Montagen", "Fish Audio", "Api Key"],
        name: "Api Key",
        tooltip: "Api Key",
        type: "text",
        defaultValue: "",
        onChange: async (newValue, oldValue) => {
          await updateModel(newValue);
        },
      },
      {
        id: "montagen.fish_audio_api_url",
        category: ["Montagen", "Fish Audio", "Api Url"],
        name: "Api Url",
        tooltip: "Api Url",
        type: "text",
        defaultValue: "",
      },
      {
        id: "montagen.humandigital_api_key",
        category: ["Montagen", "Humandigital", "Api Key"],
        name: "Api Key",
        tooltip: "Api Key",
        type: "text",
        defaultValue: "",
      },
      {
        id: "montagen.humandigital_api_enable",
        category: ["Montagen", "Humandigital", "Enable"],
        name: "Enable",
        tooltip: "Enable",
        type: "boolean",
        defaultValue: false,
      },
    ],
    beforeRegisterNodeDef(nodeType, nodeData) {
      if (nodeData.name == "MontagenFishAudioTTSNode") {
        var appkey = app.ui.settings.getSettingValue(
          "montagen.fish_audio_api_key",
          ""
        );
        updateModel(appkey);
        chainCallback(nodeType.prototype, "onNodeCreated", async function () {
          this.onListChangedCallbacks = function () {
            for (let w of this.widgets) {
              {
                if (w.name == "voice") {
                  w.options.values = list;
                  if (list.length > 0 && !w.value) {
                    w.value = list[0];
                  } else {
                    w.value = "";
                  }
                }
              }
            }
          }.bind(this);
          for (let w of this.widgets) {
            {
              if (w.name == "voice") {
                w.options.values = list;
                if (list.length > 0 && !w.value) {
                  w.value = list[0];
                } else {
                  w.value = "";
                }
                onListChangedCallbacks.push(this.onListChangedCallbacks);
              }
              if (w.name == "apiKey") {
                w.callback = async function (newValue) {
                  await updateModel(newValue);
                };
              }
            }
          }
        });
        chainCallback(nodeType.prototype, "onRemoved", async function () {
          onListChangedCallbacks = onListChangedCallbacks.filter(
            (callback) => callback !== this.onListChangedCallbacks
          );
        });
      }
    },
    async getCustomWidgets() {
      return {
        MontageVoice(node3, inputName, inputData, app2) {
          inputData[1].type = "COMBO";
          return app.widgets.COMBO(node3, inputName, inputData, app);
        },
      };
    },
  });
})(window);
