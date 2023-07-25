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

for x in Phase Intensity; do
bandname=`grep "<BAND_NAME>" $input 2>/dev/null | cut -d '>' -f2 | grep ^$x | cut -d '<' -f 1`
if [ ! -z $bandname ]; then
 echo "geocoding "$bandname
 /opt/snap/bin/gpt $SNAPGRAPHS/graph_geocoding_s1_geotiff.xml -Psourceband=$bandname -Poutput=$outputdir/$x.$outname.geo.tif -Pinput=$input #>/dev/null 2>/dev/null
fi
done
