#!/bin/bash

if [ -z $SNAPGRAPHS ]; then SNAPGRAPHS=.; fi

if [ -z $2 ]; then
 echo "Usage: geocode_ifg_snap.sh /path/to/input.dim outputdir"
 echo "best names after SNAP2STAMPS, e.g. 20220214_20220109_IW1.dim"
 exit
fi

input=$1
outputdir=$2
outname=`basename $input | cut -d '.' -f1`

# for x in Phase Intensity; do
for bandname in `grep "<BAND_NAME>" $input 2>/dev/null | cut -d '>' -f2 | cut -d '<' -f 1`; do    # for all bands. but i,q do not work!
x=`echo $bandname | cut -d '_' -f 1`
#bandname=`grep "<BAND_NAME>" $input 2>/dev/null | cut -d '>' -f2 | grep ^$x | cut -d '<' -f 1`
if [ ! -z $bandname ]; then
 echo "geocoding "$bandname
 /opt/snap/bin/gpt $SNAPGRAPHS/graph_geocoding_s1_geotiff.xml -Psourceband=$bandname -Poutput=$outputdir/$x.$outname.geo.temp.tif -Pinput=$input >/dev/null 2>/dev/null
 gdal_translate -of GTiff -ot Float32 -co COMPRESS=DEFLATE -co PREDICTOR=3 $outputdir/$x.$outname.geo.temp.tif $outputdir/$x.$outname.geo.tif  2>/dev/null
 rm $outputdir/$x.$outname.geo.temp.tif 2>/dev/null
fi
done
