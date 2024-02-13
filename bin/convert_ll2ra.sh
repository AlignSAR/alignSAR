#!/bin/bash
# ML 2023: great acknowledgment to GMTSAR and (forever best) GMT!
V=""
ingeo=geo2ra.grd
trans=trans.dat
outra=radarcoded.grd
nsamples=$1
nlines=$2
#spacing=0.08333333333 # 900 m
spacing=0.008333333333 # 90 m
#spacing=0.002777777 # 30 m

if [ -z $nsamples ]; then echo "please set params"; exit; fi

# avoid issues with 0 being NaN. that's ok but need to burn this value here
echo "Preparing data"
gmt grdconvert $ingeo -G$ingeo.0.grd=+n-9999
gmt grdmath $ingeo.0.grd 0 DENAN = $ingeo.ok.grd
gmt grd2xyz $ingeo.ok.grd -s -bo3f -fg > llp
# clean
rm $ingeo.0.grd $ingeo.ok.grd
#
#   make grids of longitude and latitude versus range and azimuth
#
#  Note, we should first perform blockmean to synchronise things (but what resolution to choose? skipping now)
#
if [ ! -f llr.grd ]; then 
 echo "Common llr.grd file not found, regenerating (takes long)"
 gmt gmtconvert $trans -o2,3,0 -bi4f -bo3f > llr
 time gmt surface llr `gmt gmtinfo llp -I$spacing -bi3f` -bi3f -I$spacing -T.50 -Gllr.grd $V # lla/llr is needed to be generated need only once!
fi
if [ ! -f lla.grd ]; then 
 echo "Common lla.grd file not found, regenerating (takes long)"
 gmt gmtconvert $trans -o2,3,1 -bi4f -bo3f > lla
 time gmt surface lla `gmt gmtinfo llp -I$spacing -bi3f` -bi3f -I$spacing -T.50 -Glla.grd $V
fi
#
echo "Linking coordinates and data values"
gmt grdtrack llp -nl -Gllr.grd -bi3f -bo4f > llpr 
gmt grdtrack llpr -nl -Glla.grd -bi4f -bo5f > llpra 
#
gmt gmtconvert llpra -bi5f -bo3f -o3,4,2 > rap
# R=`gmt gmtinfo rap -I1/1 -bi3f`
R="-R0/"$nsamples"/0/"$nlines
#echo "Converting discrete nodes to regular grid"
#gmt xyz2grd rap $R -I1 -r -G$outra -bi3f
echo "Running NN interpolation through the irregular mesh" # setting the tolerance for 5 pixels, that should be fine here
# test showed that -S5 is ~1 min., -S 10 is ~3.5 min. and in the end the loss of values was only 0.02%
time gmt nearneighbor rap $R -G$outra -r -bi3f -I1 -S5

# R="-R0/"`echo $R | cut -d '/' -f2`"/0/"`echo $R | cut -d '/' -f4`
# finally nearest neighbour interpolation to fill the holes (zeroes are values now!)
# good hack but takes AGES (need to optimize above)
#echo "Filling holes by NN interpolation"
#time gmt grdfill $outra -An $R -G$outra.filled.grd

echo "done, cleaning"
# clean
rm lla llp llpr llpra llr rap 
# rm lla.grd llr.grd # takes long to regenerate
