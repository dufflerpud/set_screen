#!/usr/bin/perl -w

use strict;

my $SCREEN="base";
my @COLORS =
    (	'#ff0000','#ff3000','#ff6000','#ff9000','#ffc000','#ffff00',
	'#c0f000','#90ff00','#60ff00','#30ff00','#00ff00','#00ff30',
	'#00ff60','#00ff90','#00ffc0','#00ffff','#00c0ff','#0090ff',
	'#0060ff','#0030ff','#0000ff'	);
my @DIMS = ( [1,1], [2,1], [1,2], [2,2], [1,3] );

my $p = 0;
my $d = 0;
my $sep = "\t";
while( $_ = <STDIN> )
    {
    chomp( $_ );
    s/:/ /g;
    s/\s+$//g;
#    printf( "$sep\{priority:%2d,color:'%7s',dims:%5s,text:'%s'}",
    printf( "${sep}sleep 3; set_screen -s$SCREEN -p%02d -c%7s -h%d -w%d -t'%s'",
	$p, $COLORS[$p], $DIMS[$d][0], $DIMS[$d][1], $_ );
    $sep = "\n\t";
    $p = ($p+1) % scalar(@COLORS);
    $d = ($d+1) % scalar(@DIMS);
    }
print "\n";
