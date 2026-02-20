#!/usr/bin/perl -w
#
#indx#	app.cgi - Watch files for URLs to display
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
#doc#	app.cgi - Watch files for URLs to display
########################################################################

use strict;

use lib "/usr/local/lib/perl";
use cpi_file qw( read_file write_file echodo fatal files_in cleanup
 read_lines new_stderr );
use cpi_cgi qw( CGIreceive CGIheader );
use cpi_arguments qw( parse_arguments );
use cpi_english qw( list_items );
use cpi_compress_integer qw( compress_integer );
use cpi_config qw( read_map );
use cpi_reorder qw( orderer );
use cpi_template qw( template );
use cpi_vars;

#use Data::Dumper;
use JSON;

# Put constants here

my $LOGTAG = $$;
my $LOGFILE = "/var/log/stderr/set_screen";
&new_stderr( ">>$LOGFILE" ) || &fatal("Cannot stderr ${LOGFILE}:  $!");
chmod( 0666, $LOGFILE );

my $TMP			=	"/tmp/$cpi_vars::PROG.$$";
#my $TMP		=	"/tmp/$cpi_vars::PROG";

my $LIBDIR		=	"$cpi_vars::BASEDIR/lib";

my $WWWDIR		=	"%%WWWDIR%%";

my $URLS_SCRIPT		=	"$LIBDIR/URLs.html";
my $MESSAGES_SCRIPT	=	"$LIBDIR/messages.html";

my $ORIGIN		=	$ENV{SERVER_NAME} || "Not web";
my $REQUEST_SCHEME	=	($ENV{REQUEST_SCHEME}||"");
my $REQUEST_SCRIPT	=	($ENV{REQUEST_URI}||"");
$REQUEST_SCRIPT		=~	s:/*\?.*::;
my $URL			=	"${REQUEST_SCHEME}://$ORIGIN$REQUEST_SCRIPT";
#my $MESSAGES_URL	=	"$URL/messages";
my $MESSAGES_URL	=	"$URL";
#my $SCREEN_URL		=	"$URL/URLs";
my $SCREEN_URL		=	"$URL";
my $URL_FILE		=	"/usr/local/projects/octagon/cfg/urls.pl";

my $URL_DIR		=	"$WWWDIR/URLs";
my $MESSAGE_DIR		=	"$WWWDIR/messages";
my $IMAGES_DIR		=	"$WWWDIR/images";
my $BUTTON_DISPATCHER	=	"button_dispatch";

my %ONLY_ONE_DEFAULTS =
    (
    "alignment"	=>	[ "tl","tc","tr","ml","mc","mr","bl","bc","br" ],
    "button"	=>	"",		# Action if button pressed
    "expires"	=>	"",		# Expires
    "id"	=>	"",		# ID
    "removeid"	=>	"",		# ID to remove
    "screen"	=>	"",		# Screen name
    "url"	=>	"",		# URL but keep listening for new URLs
    "replaceurl"=>	"",		# Just replace window with URL
    "windowin"	=>	[ "popup", "frame", "window" ],
    "media"	=>	"",		# Background medium (jpg, gif, mov)
    "fgcolor"	=>	"white",	# Foreground color
    "bgcolor"	=>	"#3030ff",	# Background color
    "text"	=>	"",		# Text in block
    "priority"	=>	1,		# Priority of block
    "dimensions" =>	"1x1",		# Dimensions of block (rows x columns)
    "location"	=>	"",		# Block location (or floating)
    "smap"	=>	"$LIBDIR/screens.map",
    "umap"	=>	"$LIBDIR/URLs.map",
    "verbosity"	=>	0,		# Location of screen map file
    );

my %SCREEN_MAP;

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

our @problems;
our %ARGS;
our @files;
our $exit_stat = 0;
#my $screen;
my $cgi_screen;
my @SCREENS;
my $IS_CGI;

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
	"Usage:  $cpi_vars::PROG <possible arguments>","",
	"where <possible arguments> is:",
	"    -alignment	<td cell attributes>",
	"    -button	<action on button press>",
	"    -screen	<screen name>",
	"    -removeid <message id to remove",
	"    -text	<text in block>",
	"    -media	<background image URL>",
	"    -fgcolor	<text color>",
	"    -bgcolor	<background color>",
	"    -priority	<priority>",
	"    -dimensions <rows>x<cols>",
	"    -location <row>,<col>",
	"    -url	<url to send screen to>",
	"    -verbosity	<flag> where 0=quiet, 1=verbose",
	"",
	"If -s is not specified, list screens",
	"If -s specified, but not -t, -c or -i, list attributes of block"
	);
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
	" style=\"background-image:url('media/background.gif');",
	"background-size:cover;background-repeat:no-repeat;",
	"background-position:center center;\">",
	"<form><center><table>" );
    foreach my $screen (
	&orderer(
	    {before=>[$cgi_screen]},
	    &selected_screens()
	    ) )
	{
	print STDERR __LINE__, " screen=$screen\n";
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
	    foreach my $uline ( &read_lines( $ARGS{umap} ) )
		{
		my( $name, $url ) = split(/\s+/,$uline);
		push( @s,
		    "<td><input type=button onClick='window.location.href=\"",
		    $url, "\";' value='$name'",
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
    print &template( $URLS_SCRIPT,
    	"%%URL%%",$URL,
    	"%%SCREEN_URL%%",$SCREEN_URL,
    	"%%SCREEN%%",$cgi_screen,
    	"%%SPAWN_METHOD%%",$ARGS{windowin} );
    }

#########################################################################
#	Read the url file for the specified screen.			#
#########################################################################
sub screen_to_url
    {
    my( $screen ) = @_;
    my $ret;
    #if( $ret = &read_file("$URL_DIR/$screen.html",undef) )
    if( $ret = &read_file("$URL_DIR/$screen.html","") )
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
#	foreach my $fn ( ( &files_in($URL_DIR), &files_in($MESSAGE_DIR) ) )
#	    {
#	    $seen_screen{$1}=1 if($fn =~ /^([^\.]+)\.(html|html\.daemon)$/);
#	    }
	%seen_screen = map { ($_,1) } values %SCREEN_MAP;
	@SCREENS = sort keys %seen_screen;
	}
    return ( ( ! $ARGS{screen} || $ARGS{screen} eq "all" )
 	? @SCREENS
	: grep( $seen_screen{$_}, split(/,/,$ARGS{screen}) ) );
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
	my $filename = "$URL_DIR/$ARGS{screen}.html";
	print "Writing\t$new_url\nto\t$filename\n" if( $ARGS{verbosity} );

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
    #print "[ $MESSAGES_SCRIPT ]\n";
    print &template( $MESSAGES_SCRIPT,
	"%%MESSAGES_URL%%",$MESSAGES_URL,
	"%%URL%%",$URL,
	"%%SCREEN%%",$cgi_screen);
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

    $cpi_vars::FORM{since} ||= $DELETED_FILE;
    &mplog("Last updated $cpi_vars::FORM{since} waiting on $filename...");
    my $keep_alive = 0;
    my $current_locker;
    while( ($mtime = ((stat($filename))[9])||$DELETED_FILE)==$cpi_vars::FORM{since} )
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
    &wait_for_file_change( "$MESSAGE_DIR/$cpi_vars::FORM{screen}.html" );
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
		    $messages{$id}{dimensions}[0], $messages{$id}{dimensions}[1],
		    scalar( @{$messages{$id}{location}} ) >= 2
			? ($messages{$id}{location}[0].",".$messages{$id}{location}[1]) : "?",
		    ($messages{$id}{media} || "?"),
		    $messages{$id}{text} || "" );
		}
	    }
	}
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
#	Remove the specified message from the screen list.		#
#########################################################################
sub remove_messages
    {
    my @screens;
    if( $ARGS{screen} && $ARGS{screen} ne "all" )
	{ push( @screens, &screen_name_of($ARGS{screen}) ); }
    else
	{
	opendir( D, $MESSAGE_DIR ) || &fatal("Cannot open ${MESSAGE_DIR}:  $!");
	@screens = sort grep( /^\w.*\.html/, readdir(D) );
	closedir( D );
	s/\.html$// for @screens;
	}

    my @ids_to_remove = split(/,/,$ARGS{removeid});
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
	print ucfirst( &list_items( "id", "nor", @ids_to_remove ) ),
	    ( scalar(@ids_to_remove)==1 ? " was not" : " were" ),
	    " found in ",
	    &list_items( "screen", "or", @screens ),
	    ".\n";
	}
    }

#########################################################################
#	Write message for a status handler.				#
#########################################################################
sub add_message
    {
    $ARGS{alignment} = join(" ",(map {$TABLE_MACROS{$_}||$_} split(/[ ,]/,$ARGS{alignment})));
    $ARGS{fgcolor}=$1, $ARGS{bgcolor}=$2 if( $ARGS{fgcolor} =~ m:^(.*)/(.*)$: );
    my $idname = ( $ARGS{id} ? $ARGS{id} : &compress_integer( time() ) . "." . &compress_integer( $$ ) );
    foreach my $screen ( &selected_screens() )
	{
	my %messages = &read_messages($screen);
	$messages{$idname} =
	    {
	    id		=>	$idname,
	    attributes	=>	$ARGS{alignment},
	    priority	=>	$ARGS{priority}*1,
	    fgcolor	=>	$ARGS{fgcolor},
	    bgcolor	=>	$ARGS{bgcolor},
	    dimensions	=>	[ map {$_*1} split( /[x,]/, $ARGS{dimensions} ) ],
	    location	=>	[ map {$_*1} split( /[x,]/, $ARGS{location} ) ],
	    media	=>	$ARGS{media},
	    button	=>	$ARGS{button},
	    text	=>	$ARGS{text}
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
    return $cgi_screen if( ($cgi_screen=$cpi_vars::FORM{screen}) && &is_screen($cgi_screen) );
    return $cgi_screen if( ($cgi_screen=$ARGS{screen}) && &is_screen($cgi_screen) );

    my $ip = $ENV{REMOTE_ADDR};
    &fatal("Screen $cgi_screen unknown and cannot determine ip address.") if( ! $ip );
    # return undef if( ! $ip );

    return $cgi_screen if( $cgi_screen=$SCREEN_MAP{$ip} );

    my $hostname = &ip_to_host( $ip );
    fatal("Cannot determine hostname from $ip.") if( ! $hostname );

    return $cgi_screen if( $cgi_screen=$SCREEN_MAP{$hostname} );

    return $cgi_screen if( $cgi_screen=$SCREEN_MAP{default} );

    &fatal("Cannot determine screen from $hostname and there is no default.");
    }

#########################################################################
#	Main								#
#########################################################################

if( !@ARGV && $ENV{SCRIPT_NAME} )
    {
    $IS_CGI = 1;
    &CGI_arguments();
    &CGIheader();
#    grep( $ARGS{$_}=(defined($ARGS{$_})?$ARGS{$_}:$ONLY_ONE_DEFAULTS{$_}),
#	keys %ONLY_ONE_DEFAULTS );

    # Note that this will simply set everything to default values as
    # ARGV will be empty.
    %ARGS = &parse_arguments({
	switches	=> \%ONLY_ONE_DEFAULTS,
	leftovers	=> \@files
	});

    ( $_, %SCREEN_MAP ) = &read_map( $ARGS{smap} );
    &get_screen();

    #$hdrcount++;
    $cpi_vars::FORM{func} ||= "list";
    if( $cpi_vars::FORM{func} eq "messages" )
        {
	#print "FORM{$_}=[$cpi_vars::FORM{$_}]<br>\n" for sort keys %cpi_vars::FORM;
	if( ! $cpi_vars::FORM{uniqid} )
	    { &message_page(); }
	elsif( $cpi_vars::FORM{screen} && $cpi_vars::FORM{id} && $cpi_vars::FORM{action} )
	    { &do_action( $cgi_screen, $cpi_vars::FORM{id}, $cpi_vars::FORM{action} ); }
	else
	    { &send_messages(); }
	}
    elsif( $cpi_vars::FORM{func} eq "urls" || $cpi_vars::FORM{func} eq "startup" )
        {
	if( $cpi_vars::FORM{uniqid} )
	    { &send_url(); }
	else
	    { &url_page(); }
	}
    elsif( $cpi_vars::FORM{func} eq "list" )
	{
        &CGI_show_screens();
	}
    else
	{ &fatal("Unknown function [$cpi_vars::FORM{func}]"); }
    }
else
    {
    if( scalar(@ARGV)==2 && ($ARGV[0] eq "initdb" || $ARGV[0] eq "-initdb" ))
	{
	print "$cpi_vars::PROG does not have any database to init.\n";
	&cleanup(0);
	}
    %ARGS = &parse_arguments({
	switches	=> \%ONLY_ONE_DEFAULTS,
	leftovers	=> \@files
	});
    ( $_, %SCREEN_MAP ) = &read_map($ARGS{smap});
    if( $ARGS{removeid} )
	{ &remove_messages(); }
    elsif( $ARGS{text} || $ARGS{media} )
	{ &add_message(); }
    elsif( ! $ARGS{screen} )
	{ &cmd_show_screens(); }
    else
	{
	&get_screen();
	if( $ARGS{url} || $ARGS{replaceurl} )
	    { &set_screen( ($ARGS{url}||$ARGS{replaceurl}), ($ARGS{replaceurl}?1:0) ); }
	else
	    { &list_messages(); }
	}
    }

exec("rm -rf $TMP");
