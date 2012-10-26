#!/bin/sh

if [ $# -lt 1 ]
then
  echo "usage: ./render_avatars.sh SVGDIR"
  exit
fi

for svg in $1/*.svg; do
    target=../reddit_about/public/static/about/avatar/`basename $svg .svg`.png
    if [ $svg -nt $target ]; then
        # render oversized and resize with unsharp mask for silky smooth avatars.
        inkscape -e $target -d 1000 $svg
        convert -resize 160x160 $target -unsharp 0x0.5 $target
    fi
done
