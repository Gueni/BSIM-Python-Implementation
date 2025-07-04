# set terminal png
# set output ARG2

#set title "HeatMap for circuit $ARG1 written by TSaCt2"


set view map
set size ratio -1
set palette defined (0 "red", 1 "#154aa1", 2 "#eca500", 3 'green')

set key off
unset xtics
unset ytics
unset border # hide graph border
unset colorbox # hide scale box

set ylabel 'Circuit Depth'
set xlabel 'Gate #'


splot ARG1 using 3:2:4 with points pointtype 5 pointsize 1 palette linewidth 0


pause -1 "Hit any key to continue"
