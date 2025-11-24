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

#use Data::Dumper;
use JSON;

# Put constants here

my $LOGTAG = $$;
my $LOGFILE = "/var/log/stderr/set_screen";
#close( STDERR );
#open( STDERR, ">> $LOGFILE" )
#    || die("Cannot open stderr:  $!");

my $PROJECT		=	"set_screen";
my $PROG		=	( $_ = $0, s+.*/++, s/\.[^\.]*$//, $_ );
my $TMP			=	"/tmp/$PROG.$$";
#my $TMP		=	"/tmp/$PROG";
my @HARD_CODED_SCREENS	=	qw(	6H 6M 5Ul 5Ml 5Uc 5Mc 5L 5Ur 5Mr
					4H 4M 4B 3Ul 3Ml 3Uc 3Mc 3L 3Ur 3Mr
					2H 2M 2Lc 1M );
push( @HARD_CODED_SCREENS, "fs0", "fs1", "fs2", "iphone", "ws0", "macbook", "devel", "ipad1", "ipad4-0", "iPad4-1" );

my @KNOWN_URLS		=
    (
    { name=>"Jeffries",	url=>"http://www.brightsands.com/sto/jeffries.html" },
    { name=>"Clock",	url=>"http://www.brightsands.com/sto/Clock.html" },
    { name=>"Maze",	url=>"http://10.1.0.20/~chris/maze.html" },
    #{ name=>"Slides",	url=>"http://10.1.0.20/~chris/Slide_Show?user=chris&password=ratcatcher" },
    { name=>"CNN",	url=>"https://www.cnn.com" }
    );

my $BASEDIR		=	"%%PROJECTDIR%%";
$BASEDIR		=	"/usr/local/projects/$PROG" if(! -d $BASEDIR);
my $LIBDIR		=	"$BASEDIR/lib";
my $URLS_SCRIPT		=	"$LIBDIR/URLs.html";
my $MESSAGES_SCRIPT	=	"$LIBDIR/messages.html";

my $WWWDIR		=	"%%WWWDIR%%";
$WWWDIR			=	"/home/chris/public_html/$PROG"
				    if( ! -d $WWWDIR );

my $ORIGIN		=	$ENV{SERVER_NAME} || "Not web";
my $IP_BASE		=	"10.1.0";
my $BSCRED		=	"user=chris&password=ratcatcher";
my $REQUEST_SCHEME	=	($ENV{REQUEST_SCHEME}||"");
my $URL			=	"${REQUEST_SCHEME}://$ORIGIN/~chris/set_screen";
#my $MESSAGES_URL	=	"$URL/messages";
my $MESSAGES_URL	=	"$URL";
#my $SCREEN_URL		=	"$URL/URLs";
my $SCREEN_URL		=	"$URL";
my $URL_FILE		=	"/usr/local/projects/octagon/cfg/urls.pl";

my $URL_DIR		=	"$BASEDIR/URLs";
my $MESSAGE_DIR		=	"$BASEDIR/messages";
my $IMAGES_DIR		=	"$WWWDIR/images";
my $BUTTON_DISPATCHER	=	"button_dispatch";

my %ONLY_ONE_DEFAULTS =
    (
    "a"	=>	"",		# Alignment tl tc tr ml mc mr bl bc br
    "b"	=>	"",		# Action if button pressed
    "e"	=>	"",		# Expires
    "i"	=>	"",		# ID
    "r"	=>	"",		# ID to remove
    "s"	=>	"",		# Screen name
    "u"	=>	"",		# URL but keep listening for new URLs
    "U"	=>	"",		# Just replace window with URL
    "f"	=>	"popup",	# window, frame, popup
    "m"	=>	"",		# Background medium (jpg, gif, mov)
    "c"	=>	"white",	# Foreground color
    "C"	=>	"#3030ff",	# Background color
    "t"	=>	"",		# Text in block
    "p"	=>	1,		# Priority of block
    "d"	=>	"1x1",		# Dimensions of block (rows x columns)
    "l"	=>	"",		# Block location (or floating)
    "v"	=>	0
    );

my %SCREEN_MAP =
    (
	"fs0"		=>	"fs0",
	"fs1"		=>	"fs1",
	"fs2"		=>	"fs2",
	"ws0"		=>	"ws0",
	"iPhone-Chris"	=>	"iphone",
	"iphone"	=>	"iphone",
	"iPad-devel"	=>	"devel",
	"ipad-1"	=>	"ipad1",
	"iPad-4-0"	=>	"ipad4-0",
	"ipad-4-0"	=>	"ipad4-0",
	"iPad-4-1"	=>	"ipad4-1",
	"ipad-4-1"	=>	"ipad4-1",
	"macbook"	=>	"macbook",
	"iPad-5Ml"	=>	"5Ml",
	"iPad-5Mc"	=>	"5Mc",
	"iPad-5Mr"	=>	"5Mr",
	"iPad-3Ml"	=>	"3Ml",
	"iPad-3Mc"	=>	"3Mc",
	"iPad-3Mr"	=>	"3Mr",
	"iPad-2Lc"	=>	"2Lc"
    );

my %TABLE_MACROS =
    (	tl	=>	"valign=top align=left",
	tc	=>	"valign=top align=center",
	tr	=>	"valign=top align=right",
	ml	=>	"valign=middle align=left",
	mc	=>	"valign=middle align=center",
	mr	=>	"valign=middle align=right",
	bl	=>	"valign=bottom align=left",
	bc	=>	"valign=bottom align=center",
	br	=>	"valign=bottom align=right",
	top	=>	"valign=top",
	middle	=>	"valign=middle",
	bottom	=>	"valign=bottom",
	left	=>	"align=left",
	center	=>	"align=center",
	right	=>	"align=right"	);

my $SCRIPT_START = <<EOF;
<!doctype html><html lang=en><head>
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate"/>
<meta http-equiv="Pragma" content="no-cache"/>
<meta http-equiv="Expires" content="0"/>
EOF
my $SCRIPT_END = "</head><body></body></html>";

# Put variables here.

my @problems;
my %ARGS;
my @files;
my $exit_stat = 0;
#my $screen;
my $cgi_screen;
my @SCREENS;
my $IS_CGI;

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
    print <<EOF if( $hdrcount++ == 0 );
Content-type:  text/html
Pragma:  no-cache
Access-Control-Allow-Origin:  *

EOF
    }

#########################################################################
#	Print out a list of error messages and then exit.		#
#########################################################################
sub fatal
    {
    if( ! $IS_CGI )
        { print STDERR join("\n",@_,""); }
    else
        {
	&CGIheader();
	print STDERR "<h2>Fatal error:</h2>\n",
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
    elsif( $IS_CGI )
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
	"    -a	<td cell attributes>",
	"    -b	<action on button press>",
	"    -s	<screen name>",
	"    -r <message id to remove",
	"    -a	<action if block is pressed",
	"    -t	<text in block>",
	"    -i	<background image URL>",
	"    -c	<text color>",
	"    -C	<background color>",
	"    -p	<priority>",
	"    -d <rows>x<cols>",
	"    -l <row>,<col>",
	"    -h	<height>",
	"    -u	<url to send screen to>",
	"    -v	<flag> where 0=quiet, 1=verbose",
	"",
	"If -s is not specified, list screens",
	"If -s specified, but not -t, -c or -i, list attributes of block"
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

    # Put interesting code here.

    grep( $ARGS{$_}=(defined($ARGS{$_})?$ARGS{$_}:$ONLY_ONE_DEFAULTS{$_}),
	keys %ONLY_ONE_DEFAULTS );

    #push( @problems, "No files specified" ) if( ! @files );
    
    if( $ARGS{f} =~ /^w/i )
	{ $ARGS{f} = "window"; }
    elsif( $ARGS{f} =~ /^f/i )
	{ $ARGS{f} = "frame"; }
    elsif( $ARGS{f} =~ /^p/i )
	{ $ARGS{f} = "popup"; }
    else
	{ push(@problems,"-f must be 'window', 'frame', or 'popup'."); }

    foreach my $fn ( @files )
	{
	if( (! $ARGS{s}) && &is_screen( $fn ) )
	    { $ARGS{s} = $fn; }
	elsif( ! $ARGS{u} )
	    { $ARGS{u} = $fn; }
	else
	    { push( @problems, "Unrecognized argument '$fn'." ); }
	}

     push( @problems, "-l ($ARGS{l}) is not in n,n or ?,? format" )
	if( $ARGS{l} && $ARGS{l} !~ /^\d+,\d+$/ );
     push( @problems, "-d ($ARGS{d}) is not in nxn format" )
	if( $ARGS{d} !~ /^\d+x\d+$/ );

    &usage( @problems ) if( @problems );
    }

#########################################################################
#	Add info to log file.  Use sparingly.				#
#########################################################################
sub mplog
    {
    my $str = join( " ", $LOGTAG, " ", time().": ", @_, "\n" );
    open(LF, ">> $LOGFILE") || &fatal("Cannot append to ${LOGFILE}:  $!");
    print LF $str;
    close(LF);
    #print STDERR $str;
    }

#########################################################################
#	Print a web page to allow you to see things from other screens.	#
#########################################################################
sub CGI_show_screens
    {
    my @s = ( "<body",
	" style=\"background-image:url('media/Quantum.gif');",
	"background-size:cover;background-repeat:no-repeat;",
	"background-position:center center;\">",
	"<form><center><table>" );
    my @screen_order = sort &selected_screens();
    @screen_order = ( $cgi_screen, grep( $_ ne $cgi_screen, @screen_order ) )
	if( $cgi_screen && grep( $_ eq $cgi_screen, @screen_order ) );
    foreach my $screen ( @screen_order )
	{
	my $bgcolor = ( $screen eq $cgi_screen ? "#c0d8ff" : "#c0c0c0" );
	push( @s,
	    "<tr bgcolor='$bgcolor'>",
	    "<th align=left>${screen}:</th>" );
	foreach my $fnc ( "urls", "messages" )
	    {
	    push( @s,
	        "<td><input type=button onClick='window.location.href=\"",
		"?func=$fnc&screen=$screen\";' value='$fnc'",
		" style='background-color:$bgcolor'></td>" );
	    }
	if( $screen eq $cgi_screen )
	    {
	    foreach my $up ( @KNOWN_URLS )
		{
		push( @s,
		    "<td><input type=button onClick='window.location.href=\"",
		    $up->{url}, "\";' value='$up->{name}'",
		    " style='background-color:$bgcolor'></td>" );
		}
	    }
	}
    push( @s, "</table></center></form></body></html>\n" );
    print join("",@s);
    }

#########################################################################
#	Scriptlet which tracks files to redirect frame to.		#
#########################################################################
sub url_page
    {
    my $ip;
    my $url;

    my $text = &read_file( $URLS_SCRIPT );
    $text =~ s/%%URL%%/$URL/gms;
    #$text =~ s/%%SCREEN_URL%%:$SCREEN_URL\/$cgi_screen.html/gms;
    $text =~ s/%%SCREEN_URL%%/$SCREEN_URL/gms;
    $text =~ s/%%SCREEN%%/$cgi_screen/gms;
    $text =~ s/%%SPAWN_METHOD%%/$ARGS{f}/gms;
    print $text;
    }

#########################################################################
#	Read the url file for the specified screen.			#
#########################################################################
sub screen_to_url
    {
    my( $screen ) = @_;
    my $ret;
    if( $ret = &read_file("$URL_DIR/$screen.html",undef) )
	{
	return $1 if( $ret =~ /set_url\('(.*?)',[01]\)/ );
	return $1 if( $ret =~ /set_url\('(.*?)'\)/ );
	chomp( $ret );
	}
    return $ret;
    }

#########################################################################
#	Text to send to browser when we have a new URL request.		#
#########################################################################
sub send_url
    {
    &wait_for_file_change( "$URL_DIR/$cgi_screen.html" );
    }

#########################################################################
#########################################################################
sub files_in
    {
    my( $dname ) = @_;
    opendir( D, $dname ) || &fatal("Cannot opendir($dname):  $!");
    my @ret = readdir(D);
    closedir( D );
    return @ret;
    }

#########################################################################
#	Returns a list of valid screen names determined by sockets	#
#	or if no sockets are available, by a hard coded list.		#
#########################################################################
sub selected_screens
    {
    my %seen_screen;
    if( @SCREENS )
	{ %seen_screen = map { ($_,1) } @SCREENS; }
    else
	{
	foreach my $fn ( ( &files_in($URL_DIR), &files_in($MESSAGE_DIR) ) )
	    {
	    $seen_screen{$1}=1 if($fn =~ /^([^\.]+)\.(html|html\.daemon)$/);
	    }
	@SCREENS = sort keys %seen_screen;
	}
    return ( ( ! $ARGS{s} || $ARGS{s} eq "all" )
 	? @SCREENS
	: grep( $seen_screen{$_}, split(/,/,$ARGS{s}) ) );
    }

#########################################################################
#	Show URLs last specified for each screen.			#
#########################################################################
sub cmd_show_screens
    {
    foreach my $screen ( sort &selected_screens() )
	{
	printf("%-10s %s\n",$screen.":",
	    &screen_to_url( $screen ) || "(Not set)" );
	}
    }

#########################################################################
#	Map a screen name, ip address or hostname to a screen name.	#
#########################################################################
sub screen_name_of
    {
    my ( $thing ) = @_;
    my $hostname;
    if( &is_screen($cgi_screen=$thing) )
	{ return $cgi_screen; }
    if( $cgi_screen = $SCREEN_MAP{$thing} )
	{ return $cgi_screen }
    if( $thing =~ /^\d+\.\d+\.\d+\.\d+$/ && ($hostname=&ip_to_host($thing)) )
	{
	return $cgi_screen if( $cgi_screen=$SCREEN_MAP{$hostname} );
	&fatal("Neither $thing nor $hostname is a screen.");
	}
    &fatal("Cannot map $thing to a screen name.");
    }

#########################################################################
#	Returns true if the specified text is actually a screen.	#
#########################################################################
sub is_screen
    {
    return grep( $_[0] eq $_, &selected_screens());
    }

#########################################################################
#	Write URL setter for screen to read.				#
#########################################################################
sub set_screen
    {
    my( $new_url, $replace_flag ) = @_;
    if( $new_url !~ /^http/ )
        {
	do $URL_FILE;
	my %URLS = &get_urls( $URL_FILE );
	my ( @matching ) = grep( $_ =~ /$new_url/, keys %URLS );
	&fatal("Cannot find $new_url in $URL_FILE.") if( ! @matching );
	$new_url = $URLS{ shift(@matching) };
	}
    foreach my $screen ( &selected_screens() )
	{
	my $filename = "$URL_DIR/$ARGS{s}.html";
	print "Writing\t$new_url\nto\t$filename\n" if( $ARGS{v} );

	&write_file( $filename, <<EOF );
$SCRIPT_START
<script>parent.set_url('$new_url',$replace_flag,'%%MODIFY_TIME%%');</script>
$SCRIPT_END
EOF
	system("chmod 666 $filename");
	}
    }

#########################################################################
#	Print the template with substitutions for a status page.	#
#########################################################################
sub message_page
    {
    my $text = &read_file( $MESSAGES_SCRIPT );
    #$text =~ s:%%MESSAGES_URL%%:$MESSAGES_URL/$cgi_screen.html:gms;
    $text =~ s:%%MESSAGES_URL%%:$MESSAGES_URL:gms;
    $text =~ s/%%URL%%/$URL/gms;
    $text =~ s/%%SCREEN%%/$cgi_screen/gms;
    print $text;
    }

#########################################################################
#	Handle disposition of error.					#
#########################################################################
my $locker;
sub wffc_done
    {
    my( $excode, @msg ) = @_;
    unlink( $locker ) if( $locker && -l $locker && (readlink($locker) eq $$) );
    &mplog( @msg );
    exit( $excode );
    }

#########################################################################
#	Wait until a file changes from whatever has been specified	#
#	in the form variable, and then print the file.  Client will	#
#	then request the next file and we can hang until it changes	#
#	again.  Cuts waaaaay down on client-server communication.	#
#########################################################################
sub wait_for_file_change
    {
    my $DELETED_FILE = 0;
    my ( $filename ) = @_;
    my $mtime;
    my $contents;

    $locker = "$filename.daemon";
    unlink($locker) || &fatal("Cannot unlink ${locker}:  $!") if( -l $locker );
    symlink( $$, $locker ) || &fatal("Cannot create $locker link:  $!");
    &wffc_done(2,"Apparently the locker $locker failed.  Later:  $!")
        if( ! readlink($locker) );

    $| = 1;	# Try to avoid buffering to web client
    		# so that keep alive works.

    $FORM{since} ||= $DELETED_FILE;
    &mplog("Last updated $FORM{since} waiting on $filename...");
    my $keep_alive = 0;
    my $current_locker;
    while( ($mtime = ((stat($filename))[9])||$DELETED_FILE)==$FORM{since} )
	{
	# Wish we could detect if the client has died.
        if( 0 )
	    { &wffc_done(0,"Web browser has exited.  Ciao."); }
	elsif( !( $current_locker = readlink($locker) ) )
	    { &wffc_done(1,"Somebody deleted my lock!  $!"); }
	elsif( $current_locker ne $$ )
            { &wffc_done(1,"$current_locker has taken over.  I can tell when I'm not wanted..."); }
	#&mplog("Tick (mtime=$mtime)...");	#CMC debug
	if( ++$keep_alive >= 10 )
	    {
	    #&mplog("I'm alive!");		#CMC debug
	    $keep_alive = 0;
	    &wffc_done(1,"Keepalive failed.  I am SO out of here.")
	        if( ! print "\n" );
	    }
	sleep(3);
	}
    if( ! $mtime )
	{
	$contents =
	    $SCRIPT_START
	    . "<script>parent.update_blocks({},$DELETED_FILE);</script>"
	    . $SCRIPT_END;
	&mplog("Send DELETED_FILE");
	}
    else
	{
        $contents = &read_file( $filename );
	$contents =~ s/%%MODIFY_TIME%%/$mtime/ms;
	&mplog("Send $filename modified $mtime");
	}
    print $contents;
    &wffc_done(0,"Buy-bye.");
    }

#########################################################################
#	Status page has requested the list of current messages for a	#
#	particular screen.						#
#########################################################################
sub send_messages
    {
    &wait_for_file_change( "$MESSAGE_DIR/$FORM{screen}.html" );
    }

#########################################################################
#	Called when the user clicks on something clickable.		#
#########################################################################
sub do_action
    {
    my( $screen, $id, $action ) = @_;
    my $result = &read_file( "$BUTTON_DISPATCHER '$action' |", undef );
    my %messages = &read_messages( $screen );
    $messages{$id}{"status_index"}++;
    &write_messages( $screen, %messages );
    &send_messages();
    }

#########################################################################
#	Show all the messages associated with a screen.			#
#########################################################################
sub list_messages
    {
    foreach my $screen ( &selected_screens() )
	{
	my %messages = &read_messages($screen);
	if( %messages )
	    {
	    print "Messages for screen $screen:\n";
	    foreach my $id ( sort keys %messages )
		{
		printf(" %-12s %2d %7s %7s %dx%d %3s %-10s %s\n",
		    $id,
		    $messages{$id}{priority},
		    ($messages{$id}{fgcolor} || "?"),
		    ($messages{$id}{bgcolor} || "?"),
		    $messages{$id}{dims}[0], $messages{$id}{dims}[1],
		    scalar( @{$messages{$id}{location}} ) >= 2
			? ($messages{$id}{location}[0].",".$messages{$id}{location}[1]) : "?",
		    ($messages{$id}{media} || "?"),
		    $messages{$id}{text} || "" );
		}
	    }
	}
    }

#########################################################################
#	Your basic "convert to an arbitrary base"			#
#########################################################################
my @OI_DIGITS = ( '0'..'9', 'A'..'Z', 'a'..'z' );
my $OI_N_DIGITS = scalar(@OI_DIGITS);
sub one_id
    {
    my( $id ) = @_;
    my @res;
    while( $id || ! @res )
        {
	push( @res, $OI_DIGITS[ $id % $OI_N_DIGITS ] );
	$id = int( $id / $OI_N_DIGITS );
	#last if( $id == 0 );
	}
    return join("",reverse @res);
    }

#########################################################################
#	Read messages into an hash to return;				#
#########################################################################
sub read_messages
    {
    my( $screen ) = @_;
    my $filename = "$MESSAGE_DIR/$screen.html";
    my %messages;
    if( -r $filename )
	{
        my $json = &read_file($filename);

	# Turn "relaxed json" back to uptight json for decode.
	$json =~ s/^\s*([^'"][\w_\.\-]*?)\s*:/"$1":/gms;
	%messages = %{ decode_json( $1 ) }
	    if( $json =~ /<script>.*?update_blocks\((.*),'.+'\);<\/script>/ms );
	}
    return %messages;
    }

#########################################################################
#	Write messages hash to filename.				#
#########################################################################
sub write_messages
    {
    my( $screen, %messages ) = @_;
    my $filename = "$MESSAGE_DIR/$screen.html";
    #my $json = encode_json( \%messages );
    my $jsonp = JSON->new->allow_nonref;

    # Convert %messages to relaxed JSON.  Would be great if this could
    # be indented by one space rather than pretty->encode's 3.
    my $json = $jsonp->pretty->encode( \%messages );
    $json =~ s/^(\s*)"([a-zA-Z][\w_]*?)"\s*:\s*/${1}${2}: /gms;

    &write_file( $filename, <<EOF );
$SCRIPT_START
<script>parent.update_blocks($json,'%%MODIFY_TIME%%');</script>
$SCRIPT_END
EOF
    system("chmod 644 $filename");
    }

#########################################################################
#	Wrote this to avoid ever having to write it again.		#
#########################################################################
sub plurals
    {
    my( $arg1, $arg2 ) = @_;

    return "1 $arg1" if( $arg2 eq "1" );
    return "$arg2 ${arg1}s" if( $arg2 =~ /^\d+$/ );
    return "1 $arg2" if( $arg1 eq "1" );
    return "$arg1 ${arg2}s" if( $arg1 =~ /^\d+$/ );

    my( $item_type, $fnc, @items ) = @_;
    my $nitems = scalar(@items);
    my @pieces;
    if( $item_type )
        {
	if( $fnc eq "nor" )
	    {
	    if( $nitems==2 )
	        { push( @pieces, "neither" ); }
	    elsif( $nitems > 2 )
	        { push( @pieces, "none of" ); }
	    }
	push( @pieces,
	    $item_type
	    . ( $nitems != 1 ? "s" : "" ) );
	}
    if( $fnc )
        {
	if( $nitems == 2 )
	    { push( @pieces, $items[0] ); }
	elsif( $nitems > 2 )
	    { push( @pieces, join(", ",@items[0..$#items-1]) ); }
	push( @pieces, $fnc ) if( $nitems > 1 );
	push( @pieces, $items[$#items] );
	};
    return join(" ",@pieces);
    }


#########################################################################
#	Remove the specified message from the screen list.		#
#########################################################################
sub remove_messages
    {
    my @screens;
    if( $ARGS{s} && $ARGS{s} ne "all" )
	{ push( @screens, &screen_name_of($ARGS{s}) ); }
    else
	{
	opendir( D, $MESSAGE_DIR ) || &fatal("Cannot open ${MESSAGE_DIR}:  $!");
	@screens = sort grep( /^\w.*\.html/, readdir(D) );
	closedir( D );
	s/\.html$// for @screens;
	}

    my @ids_to_remove = split(/,/,$ARGS{r});
    my $total_changes;
    foreach my $screen ( &selected_screens() )
	{
	my %messages = &read_messages($screen);
	my $changes;
	foreach my $idname ( @ids_to_remove )
	    {
	    next if( ! $messages{$idname} );
	    delete $messages{$idname};
	    print "$idname removed from $screen\n";
	    $changes++;
	    $total_changes++;
	    }
	&write_messages( $screen, %messages ) if( $changes );
	}
    if( ! $total_changes )
        {
	print ucfirst( &plurals( "id", "nor", @ids_to_remove ) ),
	    ( scalar(@ids_to_remove)==1 ? " was not" : " were" ),
	    " found in ",
	    &plurals( "screen", "or", @screens ),
	    ".\n";
	}
    }

#########################################################################
#	Write message for a status handler.				#
#########################################################################
sub add_message
    {
    $ARGS{a} = join(" ",(map {$TABLE_MACROS{$_}||$_} split(/[ ,]/,$ARGS{a})));
    $ARGS{c}=$1, $ARGS{C}=$2 if( $ARGS{c} =~ m:^(.*)/(.*)$: );
    my $idname = ( $ARGS{i} ? $ARGS{i} : &one_id( time() ) . "." . &one_id( $$ ) );
    foreach my $screen ( &selected_screens() )
	{
	my %messages = &read_messages($screen);
	$messages{$idname} =
	    {
	    id		=>	$idname,
	    attributes	=>	$ARGS{a},
	    priority	=>	$ARGS{p}*1,
	    fgcolor	=>	$ARGS{c},
	    bgcolor	=>	$ARGS{C},
	    dims	=>	[ map {$_*1} split( /[x,]/, $ARGS{d} ) ],
	    location	=>	[ map {$_*1} split( /[x,]/, $ARGS{l} ) ],
	    media	=>	$ARGS{m},
	    button	=>	$ARGS{b},
	    text	=>	$ARGS{t}
	    };

	# This will keep the messages files smaller
	grep( delete $messages{$idname}{$_},
	    grep( ! $messages{$idname}{$_},
		keys %{$messages{$idname}} ) );

	&write_messages( $screen, %messages );
	print "$idname updated on screen $screen.\n";
	}
    }

#########################################################################
#	No nice way of changing an IP address to a hostname.		#
#########################################################################
sub ip_to_host
    {
    my( $ip ) = @_;
    my $localname;
    foreach my $hostline ( split( /\n/, &read_file("host $ip |","") ) )
	{
	next if( $hostline !~ /name pointer (.*)\.$/ );
	$localname = $1;
	last if( $localname !~ /\./ );
	}
    if( $localname =~ /^localhost/ )
	{
	$localname = &read_file("hostname |","");
	chomp( $localname );
	$localname =~ s/\.*//;
	}
    return ( $localname ? $localname : undef );
    }

#########################################################################
#########################################################################
#sub useful_error
#    {
#    print "</head><body>\n",
#	"<center><h1>Unknown machine ",
#	    ( $screen || $ip || "(No IP)" ),
#	":</h1><table><tr><th>Variable</th><th>Value</th></tr>\n",
#	( map { "<tr><td>$_</td><td>$ENV{$_}</td></tr>\n" } sort keys %ENV ),
#	"</table></center></body></html>\n";
#    }

#########################################################################
#	Try to figure out what screen we're talking about.		#
#########################################################################
sub get_screen
    {
    return $cgi_screen if( ($cgi_screen=$FORM{screen}) && &is_screen($cgi_screen) );
    return $cgi_screen if( ($cgi_screen=$ARGS{s}) && &is_screen($cgi_screen) );

    my $ip = $ENV{REMOTE_ADDR};
    &fatal("Screen $cgi_screen unknown and cannot determine ip address.") if( ! $ip );
    # return undef if( ! $ip );

    return $cgi_screen if( $cgi_screen=$SCREEN_MAP{$ip} );

    my $hostname = &ip_to_host( $ip );
    fatal("Cannot determine hostname from $ip.") if( ! $hostname );

    return $cgi_screen if( $cgi_screen=$SCREEN_MAP{$hostname} );

    &fatal("Cannot determine screen from $hostname.");
    }

#########################################################################
#	Main								#
#########################################################################

if( !@ARGV && $ENV{SCRIPT_NAME} )
    {
    $IS_CGI = 1;
    &CGI_arguments();
    &CGIheader();
    grep( $ARGS{$_}=(defined($ARGS{$_})?$ARGS{$_}:$ONLY_ONE_DEFAULTS{$_}),
	keys %ONLY_ONE_DEFAULTS );

    &get_screen();

    $hdrcount++;
    $FORM{func} ||= "list";
    if( $FORM{func} eq "messages" )
        {
	#print "FORM{$_}=[$FORM{$_}]<br>\n" for sort keys %FORM;
	if( ! $FORM{uniqid} )
	    { &message_page(); }
	elsif( $FORM{screen} && $FORM{id} && $FORM{action} )
	    { &do_action( $cgi_screen, $FORM{id}, $FORM{action} ); }
	else
	    { &send_messages(); }
	}
    elsif( $FORM{func} eq "urls" || $FORM{func} eq "startup" )
        {
	if( $FORM{uniqid} )
	    { &send_url(); }
	else
	    { &url_page(); }
	}
    elsif( $FORM{func} eq "list" )
	{
        &CGI_show_screens();
	}
    else
	{ &fatal("Unknown function [$FORM{func}]"); }
    }
else
    {
    &parse_arguments();
    if( $ARGS{r} )
	{ &remove_messages(); }
    elsif( $ARGS{t} || $ARGS{m} )
	{ &add_message(); }
    elsif( ! $ARGS{s} )
	{ &cmd_show_screens(); }
    else
	{
	&get_screen();
	if( $ARGS{u} || $ARGS{U} )
	    { &set_screen( ($ARGS{u}||$ARGS{U}), ($ARGS{U}?1:0) ); }
	else
	    { &list_messages(); }
	}
    }

exec("rm -rf $TMP");
