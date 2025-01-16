precision highp float;

varying vec2 _uv;

uniform float progress;
uniform float ratio;
uniform vec2 _offset;

uniform sampler2D fromSampler;
uniform sampler2D toSampler;

vec4 getColor(sampler2D tex, vec2 uv) {
  return texture2D(tex, vec2(uv.x + _offset.x, 1.0 - (uv.y + _offset.y)));
}

vec4 getFromColor(vec2 uv) {
  return getColor(fromSampler, uv);
}

vec4 getToColor(vec2 uv) {
  return getColor(toSampler, uv);
}

${transitionGlsl}

void main(void) {
  gl_FragColor = transition(_uv - _offset);
  //gl_FragColor = getFromColor(_uv);
}
