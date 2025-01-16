varying vec2 vTextureCoord;

uniform sampler2D uSampler;
uniform vec3 uColor;
uniform float uSimilarity;
uniform float uSmoothness;
uniform float uSaturation;
uniform float uShadowness;

vec2 RGBtoUV(vec3 rgb) {
  return vec2(
    rgb.r * -0.169 + rgb.g * -0.331 + rgb.b *  0.5    + 0.5,
    rgb.r *  0.5   + rgb.g * -0.419 + rgb.b * -0.081  + 0.5
  );
}

vec4 ProcessChromaKey(vec2 uv) {
  vec4 rgba = texture2D(uSampler, uv);
  float chromaDist = distance(RGBtoUV(rgba.rgb), RGBtoUV(uColor));

  float diff = chromaDist - uSimilarity;
  float alpha = pow(clamp(diff / uSmoothness, 0., 1.), 1.5);
  rgba *= alpha;

  float sat = pow(clamp(diff / uSaturation, 0., 1.), 1.5);
  float luma = clamp(rgba.r * 0.2126 + rgba.g * 0.7152 + rgba.b * 0.0722, 0., 1.) * uShadowness;
  rgba.rgb = mix(vec3(luma, luma, luma), rgba.rgb, sat);

  return rgba;
}

void main(void) {
  gl_FragColor = ProcessChromaKey(vTextureCoord);
}
