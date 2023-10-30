#!/bin/bash
# ML 2023: great acknowledgment to GMTSAR and (forever best) GMT!
V=""
ingeo=geo2ra.grd
trans=trans.dat
outra=outra.grd
nsamples=$1
nlines=$2

if [ -z $nsamples ]; then echo "please set params"; exit; fi

gmt grd2xyz $ingeo -s -bo3f -fg > llp
#
#   make grids of longitude and latitude versus range and azimuth
#
gmt gmtconvert $trans -o2,3,0 -bi4f -bo3f > llr
gmt gmtconvert $trans -o2,3,1 -bi4f -bo3f > lla
#
gmt surface llr `gmt gmtinfo llp -I0.08333333333 -bi3f` -bi3f -I.00083333333333 -T.50 -Gllr.grd $V
gmt surface lla `gmt gmtinfo llp -I0.08333333333 -bi3f` -bi3f -I.00083333333333 -T.50 -Glla.grd $V
#
gmt grdtrack llp -nl -Gllr.grd -bi3f -bo4f > llpr 
gmt grdtrack llpr -nl -Glla.grd -bi4f -bo5f > llpra 
#
gmt gmtconvert llpra -bi5f -bo3f -o3,4,2 > rap
# R=`gmt gmtinfo rap -I1/1 -bi3f`
R="-R0/"$nsamples"/0/"$nlines
gmt xyz2grd rap $R -I1/1 -r -G$outra -bi3f
# R="-R0/"`echo $R | cut -d '/' -f2`"/0/"`echo $R | cut -d '/' -f4`
gmt grdfill $outra -An $R -G$outra.filled.grd

# clean
rm lla llp lla.grd llpr llpra llr llr.grd rap
