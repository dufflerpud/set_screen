#!/usr/local/bin/perl -w
#
#indx#	generate_screens.pl - Generate set_screen commands to pickup different media files
#@HDR@	$Id$
#@HDR@
#@HDR@	Copyright (c) 2024-2026 Christopher Caldwell (Christopher.M.Caldwell0@gmail.com)
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
#hist#	2024-04-20 - c.m.caldwell@alumni.unh.edu - Created
#hist#	2026-02-19 - Christopher.M.Caldwell0@gmail.com - Standard header
########################################################################
#doc#	generate_screens.pl - Generate set_screen commands to pickup different media files
########################################################################

use strict;

use lib "/usr/local/lib/perl";
use cpi_file qw( fatal read_file write_file echodo cleanup );
use cpi_arguments qw( parse_arguments );
use cpi_vars;

# Put constants here

my $PROJECT = "set_screen";
my $PROG = ( $_ = $0, s+.*/++, s/\.[^\.]*$//, $_ );
my $TMP = "/tmp/$PROG.$$";
#my $TMP = "/tmp/$PROG";

my $BASEDIR = "%%PROJECTDIR%%";
$BASEDIR = "/usr/local/projects/$PROG" if( ! -d $BASEDIR );

my @ALLOW_EXTS = qw( jpg gif mow );

our %ONLY_ONE_DEFAULTS =
    (
    "alignment"	=>	"tc",
    "button"	=>	"",		# What to do when button pushed
#    "i"	=>	"/dev/stdin",
    "output_file"	=>	"/dev/stdout",
    "media_directory"	=>	"/home/chris/public_html/$PROJECT/media",
    #"m"	=>	"$BASEDIR/messages",
    "priority"	=>	"1",
    "colors"	=>	"#90c0ff/black",
    "screen"	=>	"",
    "u"	=>	"",
#    "n"	=>	0,
    "verbosity"	=>	""
    );

# Put variables here.

our @problems;
our %ARGS;
our @files;
our $exit_stat = 0;

#########################################################################
#	Setup arguments if CGI.						#
#########################################################################
sub CGI_arguments
    {
    &CGIreceive();
    }

#########################################################################
#	Print usage message and die.					#
#########################################################################
sub usage
    {
    &fatal( @_, "",
	"Usage:  $PROG <possible arguments>","",
	"where <possible arguments> is:",
	"    -i <file>",
	"    -o <output file>",
	"    -sall",
	"    -s <screen>",
	"    -u	<comma separated list of extensions to use",
	"    -c	<foreground/background colors>",
	"    -a	<attributes> (see set_screen doc)",
	"    -n <1 or 0>  Show what you would do (v. do it)"
	);
    }

#########################################################################
#	Generate list of commands based on the files in the directory.	#
#########################################################################
sub generate_commands
    {
    opendir( D, $ARGS{media_directory} ) || &fatal("Cannot opendir($ARGS{media_directory}):  $!");
    my @files = sort grep( /^\w/, readdir(D) );
    closedir( D );
    my @cmds;
    my @screens;

    if( $ARGS{screen} ne "all" )
        { @screens = ( $ARGS{screen} ); }
    else
	{
	foreach my $line ( split(/[\r\n]+/,&read_file("set_screen |")))
	    {
	    push( @screens, $1 ) if( $line =~ /^(\w+):.*/ );
	    }
	}

    $ARGS{alignment} = "'$ARGS{alignment}'" if( $ARGS{alignment} =~ /[^\w]/ );
    $ARGS{colors} = "'$ARGS{colors}'" if( $ARGS{colors} =~ /[^\w\/\#]/ );
    $ARGS{priority} = "'$ARGS{priority}'" if( $ARGS{priority} =~ /[^\w]/ );

    foreach my $screen ( @screens )
	{
	$screen = "'$screen'" if( $screen =~ /[^\w]/ );

	my $screen_type =
	    ( ($screen =~ /^[235][TMBL][lcr]$/
		|| $screen eq "devel"
		|| $screen eq "ipad" )
	    ? "low_memory" : "other" );

	my @extlist =
	    ( $ARGS{u}
	    ? split(/,/,$ARGS{u})
	    : $screen_type eq "low_memory"
	    ? qw(jpg)
	    : qw(jpg gif mov) );

	foreach my $file ( @files )
	    {
	    if( $file =~ m:([^/]*)\.(\w+)$: )
		{
		my( $id, $ext ) = ( $1, $2 );
		next if( ! grep( $_ eq $ext, @extlist ) );
		my $text = $id;
		$text =~ s/_/ /g;
		push( @cmds, join(" ",
		    "set_screen",
		    "-s$screen",
		    "-i$id",
		    "-p$ARGS{priority}",
		    "-a$ARGS{alignment}",
		    "-c$ARGS{colors}",
		    "-t'$text'",
		    "-m'media/$file'") );
		}
	    }
	}
    &write_file( $ARGS{output_file}, map {"$_\n"} @cmds );
    &echodo("chmod 755 $ARGS{output_file}") if( $ARGS{output_file} !~ m:^/dev/: );
    }

#########################################################################
#	Main								#
#########################################################################

if( 0 && $ENV{SCRIPT_NAME} )
    { &CGI_arguments(); }
else
    {
    &parse_arguments();
    $cpi_vars::VERBOSITY = $ARGS{verbosity};
    }

&generate_commands();

&cleanup("rm -rf $TMP");
