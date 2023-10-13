#!/bin/bash

if [ -z $SNAPGRAPHS ]; then SNAPGRAPHS=.; fi

if [ ! -f $SNAPGRAPHS/graph_export2tif_rdc.xml ]; then
 echo "ERROR: the SNAP xml graph is not inside the \$SNAPGRAPHS directory - make sure this env variable is set ok"
 exit
fi
if [ -z $3 ]; then
 echo "Usage: export2tif_rd_snap.sh /path/to/input.dim BANDNAME outputdir"
 echo "check bandnames using grep '<BAND_NAME>' input.dim"
 exit
fi

input=$1
bandname=$2
outputdir=$3
outname=`basename $input | cut -d '.' -f1`

echo "exporting "$bandname
/opt/snap/bin/gpt $SNAPGRAPHS/graph_export2tif_rdc.xml -Psourceband=$bandname -Poutput=$outputdir/$x.$outname.geo.tif -Pinput=$input #>/dev/null 2>/dev/null
