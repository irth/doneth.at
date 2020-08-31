#!/usr/bin/env bash
SRC=app/static/icon.svg
OUT=app/static/icons
gen_png() {
    inkscape -z -w $1 -h $1 -y 0 $SRC -e $OUT/$2
}

ip() {
    echo $OUT/icon-$1.png
}

g() {
    gen_png $1 icon-$1.png
}

g 16
g 32
g 64
g 120
g 128
g 152
g 167
g 180
g 192
g 196
g 256
g 228
g 512

convert $(ip 16) $(ip 32) $(ip 64) $(ip 128) $(ip 256) $(ip 512) $OUT/favicon.ico
