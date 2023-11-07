#!/bin/bash
# M. Lazecky, Uni of Leeds

if [ -z $SNAPGRAPHS ]; then SNAPGRAPHS=.; fi

if [ -z $2 ]; then
 echo "Usage: geocode_ifg_snap.sh /path/to/input.dim outputdir [band_name]"
 echo "best names after SNAP2STAMPS, e.g. 20220214_20220109_IW1.dim"
 echo "the optional band_name will export only the band starting on given string (e.g. Phase to extract only Phase_... band)"
 exit
fi

input=$1
outputdir=$2
mkdir -p $outputdir
outname=`basename $input | cut -d '.' -f1`

function geocode() {
 # usage: geocode band_name
 echo "geocoding "$1
 /opt/snap/bin/gpt $SNAPGRAPHS/graph_geocoding_s1_geotiff.xml -Psourceband=$bandname -Poutput=$outputdir/$x.$outname.geo.temp.tif -Pinput=$input >/dev/null 2>/dev/null
 gdal_translate -of GTiff -ot Float32 -co COMPRESS=DEFLATE -co PREDICTOR=3 $outputdir/$x.$outname.geo.temp.tif $outputdir/$x.$outname.geo.tif  2>/dev/null
 rm $outputdir/$x.$outname.geo.temp.tif 2>/dev/null
}

if [ ! -z $3 ]; then
 # do only given band
 x=$3;
 bandname=`grep "<BAND_NAME>" $input 2>/dev/null | cut -d '>' -f2 | grep ^$x | cut -d '<' -f 1`
 if [ ! -z $bandname ]; then
   geocode $bandname
 else
   echo "no band name exists for "$x;
 fi
else
  # export all bands in the dim file
  # for x in Phase Intensity; do
  for bandname in `grep "<BAND_NAME>" $input 2>/dev/null | cut -d '>' -f2 | cut -d '<' -f 1`; do    # for all bands. but i,q do not work!
    x=`echo $bandname | cut -d '_' -f 1`
    geocode $bandname
  done
fi
