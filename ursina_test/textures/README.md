Put texture files in here.

Supported file extensions:
- .jpg
- .png
- .mp4

To convert a .gif to .mp4:

```
ffmpeg -i simpsons-climbing.gif -movflags faststart -pix_fmt yuv420p -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" simpsons-climbing.mp4
```
