varying vec2 vTextureCoord;
varying vec2 vFilterCoord; // for mask

uniform sampler2D uSampler;
uniform sampler2D uMask;

uniform vec2 uMaskAnchor;
uniform vec2 uMaskSize;
uniform float uMaskRotation;

uniform vec4 maskClamp;
uniform vec4 filterArea;
uniform vec4 filterClamp;
uniform vec2 uFrameSize;

uniform bool useMask;
uniform bool useBinaryMask;
uniform bool useReverseMask;

uniform float uStart;
uniform float uDuration;

${uniforms}

${render}

void main(void) {
  vec4 bg = texture2D(uSampler, vTextureCoord);
  vec4 mask = vec4(1.0);
  float alpha = 1.0;
  if (useMask) {
    float clip = step(3.5,
      step(maskClamp.x, vFilterCoord.x) +
      step(maskClamp.y, vFilterCoord.y) +
      step(vFilterCoord.x, maskClamp.z) +
      step(vFilterCoord.y, maskClamp.w));
    mask = texture2D(uMask, vFilterCoord);
    alpha = clamp(dot(mask.rgb, vec3(1.0, 1.0, 1.0)) * clip, 0.0, 1.0);
    if (useBinaryMask) alpha = step(0.01, alpha);
    if (useReverseMask) alpha = 1.0 - alpha;
  }
  vec4 color = render(uSampler, vTextureCoord, bg, mask, alpha);
  color = mix(bg, color, alpha);
  gl_FragColor = color;
}
