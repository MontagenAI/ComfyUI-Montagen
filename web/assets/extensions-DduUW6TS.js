var _a, _b, _c, _d, _e, _f, _g, _h, _i, _j, _k, _l, _m, _n;
import { d as defineStore } from "./vendor-MNiR10Nx.js";
let app = ((_b = (_a = window.comfyAPI) == null ? void 0 : _a.app) == null ? void 0 : _b.app) || null;
((_d = (_c = window.comfyAPI) == null ? void 0 : _c.api) == null ? void 0 : _d.api) || null;
((_f = (_e = window.comfyAPI) == null ? void 0 : _e.ui) == null ? void 0 : _f.$el) || null;
((_h = (_g = window.comfyAPI) == null ? void 0 : _g.dialog) == null ? void 0 : _h.ComfyDialog) || null;
((_j = (_i = window.comfyAPI) == null ? void 0 : _i.widgets) == null ? void 0 : _j.ComfyWidgets) || null;
((_l = (_k = window.comfyAPI) == null ? void 0 : _k.utils) == null ? void 0 : _l.applyTextReplacements) || null;
((_n = (_m = window.comfyAPI) == null ? void 0 : _m.groupNode) == null ? void 0 : _n.GroupNodeConfig) || null;
const getUserSettingsValue = (id, defaultValue = void 0) => {
  var _a2, _b2;
  return id ? (_b2 = (_a2 = app == null ? void 0 : app.ui) == null ? void 0 : _a2.settings) == null ? void 0 : _b2.getSettingValue(id, defaultValue) : null;
};
function getSetting(id, storage_key = null, defaultValue = void 0) {
  try {
    let setting = id ? getUserSettingsValue(id, defaultValue) : null;
    if (setting === null || setting === void 0) setting = storage_key ? localStorage[storage_key] : localStorage[id] || null;
    return setting;
  } catch (e) {
    console.error(e);
    return null;
  }
}
function addSetting(settings2) {
  app.ui.settings.addSetting(settings2);
}
function getLocale() {
  return getSetting("AGL.Locale");
}
getLocale();
const settings = {
  // Hotkeys
  // addGroup: {
  //     id: 'MaskPage.Switch.Change',
  //     name: $t('Enable Shift+g to add selected nodes to a group'),
  //     tooltip: "用来测试的数据",
  //     type: 'boolean',
  //     defaultValue: true,
  // },
};
const isMac = /Mac|iPod|iPhone|iPad/.test(navigator.platform);
const normalize = (str) => isMac ? str.replace(/Ctrl/g, "⌘").replace(/Alt/g, "⌥").replace(/Shift/g, "⇧") : str;
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
let prefix = "👽 ";
for (let i in settings) {
  const name = getSetting("Comfy.UseNewMenu") == "Disabled" ? prefix + normalize(settings[i].name) : normalize(settings[i].name);
  const tooltip = settings[i].tooltip ? normalize(settings[i].tooltip) : "";
  addSetting({ ...settings[i], ...{ name, tooltip } });
}
app.registerExtension({
  name: "Comfy.MaskPage.UI",
  setup() {
    var _a2;
    console.log("app.ui.settingsapp.ui.settingsUI设置", app.ui.settings);
    const menuStore = useMenuStore();
    const changeNewMenuPosition = (_a2 = app.ui.settings.settingsLookup) == null ? void 0 : _a2["MaskPage.Switch.Change"];
    if (changeNewMenuPosition) {
      changeNewMenuPosition.onChange = (v) => {
        console.log("changeNewMenuPosition 数据发生了变化", v);
        menuStore.changeShow(v);
      };
    }
  }
});
export {
  app as a,
  useMenuStore as u
};
