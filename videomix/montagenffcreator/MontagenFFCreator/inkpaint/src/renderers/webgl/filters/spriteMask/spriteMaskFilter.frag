varying vec2 vMaskCoord;
varying vec2 vTextureCoord;

uniform sampler2D uSampler;
uniform sampler2D mask;
uniform float alpha;
uniform vec4 maskClamp;

uniform bool useBinaryMask;
uniform bool useReverseMask;

void main(void)
{
    float clip = step(3.5,
        step(maskClamp.x, vMaskCoord.x) +
        step(maskClamp.y, vMaskCoord.y) +
        step(vMaskCoord.x, maskClamp.z) +
        step(vMaskCoord.y, maskClamp.w));

    vec4 original = texture2D(uSampler, vTextureCoord);
    vec4 mask = texture2D(mask, vMaskCoord);
    float a = clamp(dot(mask.rgb, vec3(1.0, 1.0, 1.0)) * alpha * clip, 0.0, 1.0);
    if (useBinaryMask) a = step(0.01, alpha);
    if (useReverseMask) a = 1.0 - a;
    original *= a;
    gl_FragColor = original;
}
