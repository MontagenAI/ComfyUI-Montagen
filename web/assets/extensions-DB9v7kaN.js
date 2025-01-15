var _a, _b, _c, _d, _e, _f, _g, _h, _i, _j, _k, _l, _m, _n;
import { d as defineStore } from "./vendor-DkpZT4l8.js";
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
const zhCN = {
  "Workflow created by": "工作流创建者",
  "Watch more video content": "观看更多视频内容",
  "Workflow Guide": "工作流指南",
  // ExtraMenu
  "💎 View Checkpoint Info...": "💎 查看 Checkpoint 信息...",
  "💎 View Lora Info...": "💎 查看 Lora 信息...",
  "🔃 Reload Node": "🔃 刷新节点",
  // ModelInfo
  "Updated At:": "最近更新：",
  "Created At:": "首次发布：",
  "✏️ Edit": "✏️ 编辑",
  "💾 Save": "💾 保存",
  "No notes": "当前还没有备注内容",
  "Saving Notes...": "正在保存备注...",
  "Type your notes here": "在这里输入备注内容",
  "ModelName": "模型名称",
  "Models Required": "所需模型",
  "Download Model": "下载模型",
  "Source Url": "模型源地址",
  "Notes": "备注",
  "Type": "类型",
  "Trained Words": "训练词",
  "BaseModel": "基础算法",
  "Details": "详情",
  "Description": "描述",
  "Download": "下载量",
  "Source": "来源",
  "Saving Preview...": "正在保存预览图...",
  "Saving Succeed": "保存成功",
  "Clean SuccessFully": "清理成功",
  "Clean Failed": "清理失败",
  "Saving Failed": "保存失败",
  "No COMBO link": "沒有找到COMBO连接",
  "Reboot ComfyUI": "重启ComfyUI",
  "Are you sure you'd like to reboot the server?": "是否要重启ComfyUI？",
  // Nodes Map
  "Nodes Map": "管理节点组",
  "Nodes map sorting mode": "管理节点组排序模式",
  "No Nodes": "未找到节点",
  "No nodes found in the map": "在工作流程中没有找到节点",
  "Expand All": "展开所有组",
  "Collapse All": "折叠所有组",
  "Close": "关闭",
  "Default automatic sorting, if set to manual, groups can be dragged and dropped and the sorting results saved.": "默认自动排序，如果设置为手动，组可以拖放并保存排序结果。",
  "For drag and drop sorting, please find Nodes map sorting mode in Settings->EasyUse and change it to manual": "如需拖拽排序请在设置->EasyUse节点中找到管理节点组排序模式并修改成 manual",
  // Queue
  "Queue": "队列",
  "Cleanup Of VRAM Usage": "清理显存占用",
  "Please stop all running tasks before cleaning GPU": "请在清理GPU之前停止所有运行中的任务",
  "Always": "启用中",
  "Bypass": "已忽略",
  "Never": "已停用",
  "Auto Sorting": "自动排序",
  "Toggle `Show/Hide` can set mode of group, LongPress can set group nodes to never": "点击`启用中/已忽略`可设置组模式, 长按可停用该组节点",
  // Settings
  "Enable Shift+Up/Down/Left/Right key and Shift+Ctrl+Alt+Left/Right to align selected nodes": "启用 Shift+上/下/左/右 和 Shift+Ctrl+Alt+左/右 键对齐选中的节点",
  "Enable Shift+Ctrl+Left/Right key to normalize selected nodes": "启用 Shift+Ctrl+左/右 键规范化选中的节点",
  "Enable Shift+g to add selected nodes to a group": "启用 Shift+g 键将选中的节点添加一个组",
  "Enable Shift+r to unload models and node cache": "启用 Shift+r 键卸载模型和节点缓存",
  "Enable Shift+m to toggle nodes map": "启用 Shift+m 键显隐管理节点组",
  "Enable Up/Down/Left/Right key to jump nearest nodes": "启用 上/下/左/右 键跳转到最近的前后节点",
  "Enable Alt+1~9 to paste nodes from nodes template": "启用 Alt+1~9 从节点模板粘贴到工作流中",
  "Enable contextMenu auto nest subdirectories": "启用上下文菜单自动嵌套子目录",
  "Enable right-click menu to add node A~Z sorting": "启用右键菜单中新建节点A~Z排序",
  "Enable model thumbnails display": "启动模型预览图显示",
  "Enable nodes runtime display": "启动节点运行时间显示",
  "Enable chain get node and set node with parent nodes": "启用将获取点和设置点与父节点链在一起",
  "Maximum number of model thumbnails displayed": "显示的模型缩略图的最大数量",
  "Too many thumbnails will affect the first loading time, set the maximum value to not load the thumbnail function when there are too many models's thumbnail": "太多的缩略图会影响首次加载时间，当模型缩略图太多时，设置最大值以不加载缩略图功能",
  "Too many thumbnails, have closed the display": "模型缩略图太多啦，为您关闭了显示",
  "Shift+Up/Down/Left/Right can align selected nodes, Shift+Ctrl+Alt+Left/Right can distribute horizontal/vertical nodes": "Shift+上/下/左/右 可以对齐选中的节点, Shift+Ctrl+Alt+左/右 可以水平/垂直分布节点",
  "Enable Shift+Ctrl+Left key to normalize width and Shift+Ctrl+Right key to normalize height": "启用 Shift+Ctrl+左 键规范化宽度和 Shift+Ctrl+右 键规范化高度",
  "After v1.2.39, Ctrl+g can be used instead of it": "从v1.2.39开始，可以使用Ctrl+g代替",
  "Use three shortcut buttons in the right-click menu": "在右键菜单中使用三个快捷按钮",
  "Enable Nodes Map": "启用节点组管理",
  "You need to refresh the page to update successfully": "您需要刷新页面以成功更新",
  // selector
  "Get styles list Failed": "获取样式列表失败",
  "Get style image Failed": "获取样式图片失败",
  "Empty All": "清空所有",
  "Type here to search styles ...": "在此处输入以搜索样式 ...",
  // account
  "Loading UserInfo...": "正在获取用户信息...",
  "Please set the APIKEY first": "请先设置APIKEY",
  "Setting APIKEY": "设置APIKEY",
  "Save Account Info": "保存账号信息",
  "Choose": "选择",
  "Delete": "删除",
  "Edit": "编辑",
  "At least one account is required": "删除失败: 至少需要一个账户",
  "APIKEY is not Empty": "APIKEY 不能为空",
  "Add Account": "添加账号",
  "Getting Your APIKEY": "获取您的APIKEY",
  // choosers
  "Choose Selected Images": "选择选中的图片",
  "Choose images to continue": "选择图片以继续",
  // seg
  "Background": "背景",
  "Hat": "帽子",
  "Hair": "头发",
  "Body": "身体",
  "Face": "脸部",
  "Clothes": "衣服",
  "Others": "其他",
  "Glove": "手套",
  "Glasses": "眼镜",
  "Sunglasses": "太阳镜",
  "Upper-clothes": "上衣",
  "Top-clothes": "上衣",
  "Bottom-clothes": "下身装",
  "Torso-skin": "皮肤",
  "Dress": "连衣裙",
  "Coat": "外套",
  "Socks": "袜子",
  "Pants": "裤子",
  "Jumpsuits": "连体衣",
  "Scarf": "围巾",
  "Skirt": "裙子",
  "Left-arm": "左臂",
  "Right-arm": "右臂",
  "Left-leg": "左腿",
  "Right-leg": "右腿",
  "Left-foot": "左脚",
  "Right-foot": "右脚",
  "Left-shoe": "左鞋",
  "Right-shoe": "右鞋",
  // setting
  "s": "秒",
  // templates
  "No Node Templates Found": "未找到节点模板预设",
  "Get Node Templates File Failed": "获取节点模板文件失败",
  "Node template with {key} not set": "未设置快捷键为{key}的节点预设",
  // contextmenu
  "ComfyUI Basic": "ComfyUI 基础节点",
  "Recommend Nodes": "推荐节点",
  "Others A~Z": "其他节点 A~Z"
};
const locale = getLocale();
const $t = (key, useNavigator = false) => {
  let _locale = useNavigator ? navigator.language : locale;
  switch (_locale) {
    case "zh-CN":
      return zhCN[key];
    default:
      return key;
  }
};
const settings = {
  // Hotkeys
  addGroup: {
    id: "MaskPage.Switch.Change",
    name: $t("Enable Shift+g to add selected nodes to a group"),
    tooltip: "用来测试的数据",
    type: "boolean",
    defaultValue: true
  }
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
