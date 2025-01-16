attribute vec2 aVertexPosition;
attribute vec2 aTextureCoord;

uniform mat3 projectionMatrix;

varying vec2 vTextureCoord;
varying vec2 _uv;

void main(void) {
  vec2 _p = (projectionMatrix * vec3(aVertexPosition, 1.0)).xy;
  gl_Position = vec4(_p, 0.0, 1.0);
  vTextureCoord = aTextureCoord;
  _uv = vec2(0.5, 0.5) * (_p+vec2(1.0, 1.0));
}