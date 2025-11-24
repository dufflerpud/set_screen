#!/usr/local/bin/perl -w
########################################################################
#@HDR@	$Id$
#@HDR@		Copyright 2024 by
#@HDR@		Christopher Caldwell/Brightsands
#@HDR@		P.O. Box 401, Bailey Island, ME 04003
#@HDR@		All Rights Reserved
#@HDR@
#@HDR@	This software comprises unpublished confidential information
#@HDR@	of Brightsands and may not be used, copied or made available
#@HDR@	to anyone, except in accordance with the license under which
#@HDR@	it is furnished.
########################################################################
#	(Replace with brief explanation of what this file is or does)
#
#	2024-04-20 - c.m.caldwell@alumni.unh.edu - Created
########################################################################

use strict;

# Put constants here

my $PROJECT = "set_screen";
my $PROG = ( $_ = $0, s+.*/++, s/\.[^\.]*$//, $_ );
my $TMP = "/tmp/$PROG.$$";
#my $TMP = "/tmp/$PROG";

my $BASEDIR = "%%PROJECTDIR%%";
$BASEDIR = "/usr/local/projects/$PROG" if( ! -d $BASEDIR );

my @ALLOW_EXTS = qw( jpg gif mow );

my %ONLY_ONE_DEFAULTS =
    (
    "a"	=>	"tc",
    "b"	=>	"",		# What to do when button pushed
    "i"	=>	"/dev/stdin",
    "o"	=>	"/dev/stdout",
    "d"	=>	"/home/chris/public_html/$PROJECT/media",
    "m"	=>	"$BASEDIR/messages",
    "p"	=>	"1",
    "c"	=>	"#90c0ff/black",
    "s"	=>	"",
    "u"	=>	"",
    "n"	=>	0,
    "v"	=>	""
    );

# Put variables here.

my @problems;
my %ARGS;
my @files;
my $exit_stat = 0;

# Put interesting subroutines here

#=======================================================================#
#	Verbatim from prototype.pl					#
#=======================================================================#

#########################################################################
#	Print a header if need be.					#
#########################################################################
my $hdrcount = 0;
sub CGIheader
    {
    print "Content-type:  text/html\n\n" if( $hdrcount++ == 0 );
    }

#########################################################################
#	Print out a list of error messages and then exit.		#
#########################################################################
sub fatal
    {
    if( ! $ENV{SCRIPT_NAME} )
        { print join("\n",@_,""); }
    else
        {
	&CGIheader();
	print "<h2>Fatal error:</h2>\n",
	    map { "<dd><font color=red>$_</font>\n" } @_;
	}
    exit(1);
    }


#########################################################################
#	Put <form> information into %FORM (from STDIN or ENV).		#
#########################################################################
my %FORM;
sub CGIreceive
    {
    my ( $name, $value );
    my ( @fields, @ignorefields, @requirefields );
    my ( @parts );
    my $incoming = "";
    return if ! defined( $ENV{'REQUEST_METHOD'} );
    if ($ENV{'REQUEST_METHOD'} eq "POST")
	{ read(STDIN, $incoming, $ENV{'CONTENT_LENGTH'}); }
    else
	{ $incoming = $ENV{'QUERY_STRING'}; }
    
    if( defined($ENV{"CONTENT_TYPE"}) &&
        $ENV{"CONTENT_TYPE"} =~ m#^multipart/form-data# )
	{
	my $bnd = $ENV{"CONTENT_TYPE"};
	$bnd =~ s/.*boundary=//;
	foreach $_ ( split(/--$bnd/s,$incoming) )
	    {
	    if( /^[\r\n]*[^\r\n]* name="([^"]*)"[^\r\n]*\r*\nContent-[^\r\n]*\r*\n\r*\n(.*)[\r]\n/s )
		{
		#### Skip generally blank fields
		next if ($2 eq "");

		#### Allow for multiple values of a single name
		$FORM{$1} .= "," if ($FORM{$1} ne "");

		$FORM{$1} .= $2;

		#### Add to ordered list if not on list already
		push (@fields, $1) unless (grep(/^$1$/, @fields));
		}
	    elsif( /^[\r\n]*[^\r\n]* name="([^"]*)"[^\r\n]*\r*\n\r*\n(.*)[\r]\n/s )
		{
		#### Skip generally blank fields
		next if ($2 eq "");

		#### Allow for multiple values of a single name
		$FORM{$1} .= "," if (defined($FORM{$1}) && $FORM{$1} ne "");

		$FORM{$1} .= $2;

		#### Add to ordered list if not on list already
		push (@fields, $1) unless (grep(/^$1$/, @fields));
		}
	    }
	}
    else
	{
	foreach ( split(/&/, $incoming) )
	    {
	    ($name, $value) = split(/=/, $_);

	    $name  =~ tr/+/ /;
	    $value =~ tr/+/ /;
	    $name  =~ s/%([A-F0-9][A-F0-9])/pack("C", hex($1))/gie;
	    $value =~ s/%([A-F0-9][A-F0-9])/pack("C", hex($1))/gie;

	    #### Strip out semicolons unless for special character
	    $value =~ s/;/$$/g;
	    $value =~ s/&(\S{1,6})$$/&$1;/g;
	    $value =~ s/$$/ /g;

	    #$value =~ s/\|/ /g;
	    $value =~ s/^!/ /g; ## Allow exclamation points in sentences

	    #### Split apart any directive prefixes
	    #### NOTE: colons are reserved to delimit these prefixes
	    @parts = split(/:/, $name);
	    $name = $parts[$#parts];
	    if (grep(/^require$/, @parts))
		{
		push (@requirefields, $name);
		}
	    if (grep(/^ignore$/, @parts))
		{
		push (@ignorefields, $name);
		}
	    if (grep(/^dynamic$/, @parts))
		{
		#### For simulating a checkbox
		#### It may be dynamic, but useless if nothing entered
		next if ($value eq "");
		$name = $value;
		$value = "on";
		}

	    #### Skip generally blank fields
	    next if ($value eq "");

	    #### Allow for multiple values of a single name
	    $FORM{$name} .= "," if( defined($FORM{$name}) && $FORM{$name} ne "");
	    $FORM{$name} .= $value;

	    #### Add to ordered list if not on list already
	    push (@fields, $name) unless (grep(/^$name$/, @fields));
	    }
	}
    }

#########################################################################
#	Print a command and then execute it.				#
#########################################################################
sub echodo
    {
    my $cmd = join(" ",@_);
    if( ! $ARGS{v} )
	{ }	# No need to print commands
    elsif( $ENV{SCRIPT_NAME} )
	{ print "<pre>+ $cmd</pre>\n"; }
    else
        { print "+ $cmd\n"; }
    return system( $cmd );
    }

#########################################################################
#	Read an entire file and return the contents.			#
#	If open fails and a return value is not specified, fail.	#
#########################################################################
sub read_file
    {
    my( $fname, $ret ) = @_;
    if( open(COM_INF,$fname) )
        {
	$ret = do { local $/; <COM_INF> };
	close( COM_INF );
	}
    elsif( scalar(@_) < 2 )
        { &fatal("Cannot open ${fname}:  $!"); }
    return $ret;
    }

#########################################################################
#	Write an entire file.						#
#########################################################################
sub write_file
    {
    my( $fname, @contents ) = @_;
    open( COM_OUT, "> $fname" ) || &fatal("Cannot write ${fname}:  $!");
    print COM_OUT @contents;
    close( COM_OUT );
    }

#=======================================================================#
#	New code not from prototype.pl					#
#		Should at least include:				#
#			parse_arguments()				#
#			CGI_arguments()					#
#			usage()						#
#=======================================================================#

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
#	Parse the arguments						#
#########################################################################
sub parse_arguments
    {
    my $arg;
    while( defined($arg = shift(@ARGV) ) )
	{
	# Put better argument parsing here.

	if( $arg =~ /^-(.)(.*)$/ && defined($ONLY_ONE_DEFAULTS{$1}) )
	    {
	    if( defined($ARGS{$1}) )
		{ push( @problems, "-$1 specified multiple times." ); }
	    else
		{ $ARGS{$1} = ( $2 ne "" ? $2 : shift(@ARGV) ); }
	    }
	elsif( $arg =~ /^-(t)(.*)$/ )
	    {
	    my $val = ( $2 ? $2 : shift(@ARGV) );
	    if( $#files <= 0 )
	        {
		if( defined($files[$#files]->{$1}) )
		    {
		    push( @problems,
			$files[$#files]->{name} .
			    " -$1 specified multiple times." );
		    }
		else
		    { $files[$#files]->{$1} = $val; }
		}
	    elsif( defined( $ARGS{$1} ) )
		{ push( @problems, "-$1 specified multiple times." ); }
	    else
		{ $ARGS{$1} = $val; }
	    }
	elsif( $arg =~ /^-.*/ )
	    { push( @problems, "Unknown argument [$arg]" ); }
	else
	    { push( @files, $arg ); }
	}

    #push( @problems, "No files specified" ) if( ! @files );

    # Put interesting code here.

    grep( $ARGS{$_}=(defined($ARGS{$_})?$ARGS{$_}:$ONLY_ONE_DEFAULTS{$_}),
	keys %ONLY_ONE_DEFAULTS );

    push( @problems, "-s must be specified" ) if( ! $ARGS{s} );

    &usage( @problems ) if( @problems );
    }

#########################################################################
#	Generate list of commands based on the files in the directory.	#
#########################################################################
sub generate_commands
    {
    opendir( D, $ARGS{d} ) || &fatal("Cannot opendir($ARGS{d}):  $!");
    my @files = sort grep( /^\w/, readdir(D) );
    closedir( D );
    my @cmds;
    my @screens;

    if( $ARGS{s} ne "all" )
        { @screens = ( $ARGS{s} ); }
    else
	{
	foreach my $line ( split(/[\r\n]+/,&read_file("set_screen |")))
	    {
	    push( @screens, $1 ) if( $line =~ /^(\w+):.*/ );
	    }
	}

    $ARGS{a} = "'$ARGS{a}'" if( $ARGS{a} =~ /[^\w]/ );
    $ARGS{c} = "'$ARGS{c}'" if( $ARGS{c} =~ /[^\w\/\#]/ );
    $ARGS{p} = "'$ARGS{p}'" if( $ARGS{p} =~ /[^\w]/ );

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
		    "-p$ARGS{p}",
		    "-a$ARGS{a}",
		    "-c$ARGS{c}",
		    "-t'$text'",
		    "-m'media/$file'") );
		}
	    }
	}
    &write_file( $ARGS{o}, map {"$_\n"} @cmds );
    &echodo("chmod 755 $ARGS{o}") if( $ARGS{o} !~ m:^/dev/: );
    }

#########################################################################
#	Main								#
#########################################################################

if( 0 && $ENV{SCRIPT_NAME} )
    { &CGI_arguments(); }
else
    { &parse_arguments(); }

&generate_commands();

exec("rm -rf $TMP");
