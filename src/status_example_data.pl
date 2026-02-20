#!/usr/bin/perl -w
#
#indx#	status_example_data.pl - Create a string of commands to exercise set_screen
#@HDR@	$Id$
#@HDR@
#@HDR@	Copyright (c) 2026 Christopher Caldwell (Christopher.M.Caldwell0@gmail.com)
#@HDR@
#@HDR@	Permission is hereby granted, free of charge, to any person
#@HDR@	obtaining a copy of this software and associated documentation
#@HDR@	files (the "Software"), to deal in the Software without
#@HDR@	restriction, including without limitation the rights to use,
#@HDR@	copy, modify, merge, publish, distribute, sublicense, and/or
#@HDR@	sell copies of the Software, and to permit persons to whom
#@HDR@	the Software is furnished to do so, subject to the following
#@HDR@	conditions:
#@HDR@	
#@HDR@	The above copyright notice and this permission notice shall be
#@HDR@	included in all copies or substantial portions of the Software.
#@HDR@	
#@HDR@	THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
#@HDR@	KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
#@HDR@	WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE
#@HDR@	AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
#@HDR@	HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
#@HDR@	WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#@HDR@	FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#@HDR@	OTHER DEALINGS IN THE SOFTWARE.
#
#hist#	2026-02-19 - Christopher.M.Caldwell0@gmail.com - Created
########################################################################
#doc#	status_example_data.pl - Create a string of commands to exercise set_screen
########################################################################

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
