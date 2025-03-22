const functions = require('js-easing-functions');

class KeyFrame {
  constructor({ startTime, endTime, from, to, key, func }) {
    this.startTime = startTime !== undefined ? startTime : 0;
    this.endTime = endTime;
    this.from = from !== undefined ? from : to;
    this.to = to;
    this.key = key;
    this.func = (func && functions[func]) || this.default;
  }

  default(t, from, delta, duration) {
    return from + delta * (t / duration);
  }

  get(t, speed) {
    const duration = (this.endTime - this.startTime) / speed;
    return this.func(
      (t - this.startTime / speed) * 1000,
      this.from,
      this.to - this.from,
      duration * 1000,
    );
  }
}

const D_LIST = ['scale', 'opacity'];

class KeyFrames {
  constructor(conf, convert) {
    this.conf = conf;
    this.keyFrames = {};
    this.keyFramesEntry = {};
    this.convert = convert;
    this.parse();
  }

  /**
   *
   * @param key 需要关键帧动画变化的key
   * @param value 关键帧动画的值, 例如x为300
   * @param index 关键帧的index
   * @param time 关键帧的时间
   * @param func 关键帧动画func的名字
   * @returns {KeyFrame}
   */
  keyFrame(key, value, index, time, func, keyFramesEntry) {
    value = this.convert(value);
    let from = keyFramesEntry[index - 1] && keyFramesEntry[index - 1].value;
    from = this.convert(from);
    const conf = {
      startTime: keyFramesEntry[index - 1]?.time,
      endTime: time,
      to: value,
      key,
      from,
      func,
    };
    return new KeyFrame(conf);
  }

  parse() {
    this.conf
      .sort((a, b) => a.time - b.time)
      .map((item, index) => {
        Object.entries(item).forEach(entry => {
          const [key, value] = entry;
          if (key === 'time' || key === 'innerHTML') return;
          if (!this.keyFramesEntry[key]) {
            this.keyFramesEntry[key] = [];
          }
          const keyFrameEntry = {
            key,
            value,
            index: this.keyFramesEntry[key].length,
            time: item.time,
            easing: item.easing,
          };
          this.keyFramesEntry[key].push(keyFrameEntry);
        });
      });
    for (let [key, keyFramesEntry] of Object.entries(this.keyFramesEntry)) {
      for (const keyFrameEntry of keyFramesEntry) {
        const keyFrame = this.keyFrame(
          keyFrameEntry.key,
          keyFrameEntry.value,
          keyFrameEntry.index,
          keyFrameEntry.time,
          keyFrameEntry.easing,
          keyFramesEntry,
        );
        if (!this.keyFrames[key]) {
          this.keyFrames[key] = [];
        }
        this.keyFrames[key].push(keyFrame);
      }
    }
  }

  update(conf) {
    this.conf = conf;
    this.parse();
  }

  renderAttr(t, node) {
    const attr = {};
    const speed = node.speed || 1;
    for (let [key, keyFrames] of Object.entries(this.keyFrames)) {
      let newValue;
      for (const keyFrame of keyFrames) {
        if (t >= keyFrame.startTime / speed && t <= keyFrame.endTime / speed) {
          newValue = keyFrame.get(t, speed);
          break;
        }
      }

      // 第一个keyframe之前坐标和第一个keyframe的值一样，最后一个和最后一个keyframe的值一样
      if (newValue === undefined && keyFrames.length > 0) {
        if (t < keyFrames[0].startTime / speed) {
          newValue = keyFrames[0].from;
        } else {
          newValue = keyFrames[keyFrames.length - 1].to;
        }
      }

      if (newValue !== undefined) {
        const result = node.toAbs(key, newValue);
        if (Array.isArray(result)) {
          for (const newResult of result) {
            const { relative, key: newKey, value } = newResult;
            if (attr[newKey] !== undefined && relative) continue; // 如果有绝对坐标的话，以绝对坐标为准
            attr[newKey] = value;
          }
        } else {
          const { relative, key: newKey, value } = node.toAbs(key, newValue);
          if (attr[newKey] !== undefined && relative) continue; // 如果有绝对坐标的话，以绝对坐标为准
          attr[newKey] = value;
        }
      }
    }

    // console.log('attr', attr)
    return attr;
  }
}

module.exports = KeyFrames;
