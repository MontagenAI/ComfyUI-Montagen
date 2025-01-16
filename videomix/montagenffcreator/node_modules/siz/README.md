## about siz

This is a simple file unit conversion function with only a few lines of code. Ok, it’s that simple, you can say that it’s useless.

## useage

```
npm i siz --save
```

```
import siz from 'siz';

siz('100kb');
102400

siz('100KB');
102400

siz('100K');
102400

siz('100k');
102400

siz('100mb');
104857600

siz('100m');
104857600

siz('1m');
1048576

siz('1gb');
1073741824

siz('1t');
1099511627776
```