# Configure Application Firewalling On A Juniper SRX

Source URL: https://www.redelijkheid.com/blog/2013/5/10/configure-application-firewalling-on-a-juniper-srx
Final URL: https://www.redelijkheid.com/blog/2013/5/10/configure-application-firewalling-on-a-juniper-srx
HTTP status: 200
Extractor: htmlparser
Extracted characters: 14418

## Extracted text

Configure Application Firewalling On A Juniper SRX — REDELIJKHEID

Blogs
Blog

Leica Diary

Instagram

Photography
History

Workflow

My Photos

About
About Me

Switched2Mac

Contact

Search

Blogs
Blog

Leica Diary

Instagram

Photography
History

Workflow

My Photos

About
About Me

Switched2Mac

Contact

Search

REDELIJKHEID

Home of Guillaume Raisonnable

Blog

Leica Diary

Instagram

All

Annoying

Apple

Browsers

Copyrights

Domotica

DRM

Fun

Gadgets

Gaming

Gear

General

Hardware

Holiday

Internet

iPhone

Junos

Leica M9

Linux

Microsoft

Movies

Music

News

No Way!!!

Operating Systems

Opnsense

Personal

Photography

Privacy

Programming

Raspberry Pi

Review

Security

Software

Switched2Mac

Symbian

Tips'n Tricks

TV

Video

Website

WordPress

Configure Application Firewalling On A Juniper SRX

Juniper entered the realm of application firewalling since the release of Junos 11.4 (for SRX platforms). A realm that is mainly dominated by Palo Alto (they basically invented it) and Checkpoint, but more and more vendor's are starting to move in on that territory. And Juniper is one of those vendors that started to implement Application Firewalling (AppFW) on their (SRX) firewalls.

This post will show what needs to be done to enable AppFW, and how to configure those policies by using the J-Web interface and the CLI. The Junos software used in this exercise is version 12.1X44.4

First, we need to add the appropriate license to be able to use AppFW. This can be done by using a temporary trial license. This trial license will work for 30 days, and can be requested through the CLI of the device, or through the Juniper website . As an alternative, you could contact your Juniper contact to generate one for you. The latter has the possibility to generate trial licenses that are valid for a longer period of time.

Downloading a trial license by using the CLI is done by the following command:

root@srx100> request system license update trial

Adding a license by pasting the license information on the CLI is done by using the following command:

root@srx100> request system license add terminal [Type ^D at a new line to end input, enter blank line between each license key] <REDACTED-LICENSE-KEY> <REDACTED-LICENSE-KEY> <REDACTED-LICENSE-KEY>

You can review the imported licenses by issuing the following command:

root@srx100> show system license License usage: Licenses Licenses Licenses Expiry Feature name used installed needed idp-sig 1 1 0 2014-04-08 02:00:00 CEST dynamic-vpn 0 2 0 permanent ax411-wlan-ap 0 2 0 permanent mem-upg 0 1 0 permanent appid-sig 0 1 0 2014-04-08 02:00:00 CEST Licenses installed: License identifier: <REDACTED-LICENSE-KEY> License version: 2 Valid for device: AU4910AF0665 Features: mem-upg - Memory Upgrade permanent License identifier: <REDACTED-LICENSE-KEY> License version: 2 Valid for device: AU4910AF0665 Features: idp-sig - IDP Signature date-based, 2013-04-08 02:00:00 CEST - 2014-04-08 02:00:00 CEST License identifier: <REDACTED-LICENSE-KEY> License version: 2 Valid for device: AU4910AF0665 Features: appid-sig - APPID Signature date-based, 2013-04-08 02:00:00 CEST - 2014-04-08 02:00:00 CEST

Now that the licenses are available on the SRX, we need to download the AppFW security packages from the Juniper back-end.

root@srx100> request services application-identification download Please use command "request services application-identification download status" to check status root@srx100> request services application-identification download status Fetching/Uncompressing https://services.netscreen.com/xmlupdate/226/Applications/2260/applications.xml.gz root@srx100> request services application-identification download status Downloading application package 2260 succeed.

If you also have an IDP (trial) license, you can issue the IDP signature download command by entering:

root@srx100> request security idp security-package download root@srx100> request security idp security-package download status Done;Successfully downloaded from(https://services.netscreen.com/cgi-bin/index.cgi). Version info:2260(Mon May 6 18:12:50 2013 UTC, Detector=12.6.160130325)

After downloading the application-identification package (the AppFW stuff) we need to install it:

root@srx100> request services application-identification install Please use command "request services application-identification install status" to check status root@srx100> request services application-identification install status Checking compatibility of application package version 2260 ... root@srx100> request services application-identification install status Compiling application signatures of package version 2260 ... root@srx100> request services application-identification install status Install application package 2260 succeed root@srx100> show services application-identification version Application package version: 2260

Now that the package has been downloaded and installed, we can check what's tools (application groups and individual applications) we have available to implement the Application Firewall rule-set on our SRX:

root@srx100> show services application-identification group summary Application Group(s): 85 Application Groups Disabled ID junos:infrastructure:networking:ipp No 87 junos:infrastructure:networking:icmp No 86 junos:web:infrastructure:networking No 85 junos:web:social-networking:business No 84 junos:web:infrastructure:encryption No 83 junos:web:remote-access:tunneling No 82 junos:web:infrastructure:mobile No 81 junos:web:infrastructure:software-update No 80 junos:web:infrastructure:database No 79 junos:web:infrastructure No 78 junos:web:gaming:protocols No 77 junos:web:p2p:file-sharing No 76 junos:web:p2p No 75 .. .. root@srx100> show services application-identification application summary Application(s): 241 Nested Application(s): 892 Applications Disabled ID Order junos:AIM-HTTP-API No 1865 33703 junos:ALIBABA-MOBILE-USER-AGENT No 1864 33710 junos:ALIWANGWANG-HTTP No 1863 33709 junos:ALIWANGWANG-USER-AGENT No 1861 33711 junos:TAOBAO-CDN No 1860 33713 junos:BAIDU-HI-HTTP No 1859 33708 junos:BAOFENG No 1857 33707 junos:AIM-USERAGENT No 1856 33705 junos:AIM-WEB-API No 1855 33704 .. ..

In our experiment we will disable the video (stream) first option (access to the YouTube website, but no access to the actual video's).

First we need to figure out which signatures we need to address in our ruleset. The following command shows the available applications:

root@srx100> show services application-identification application summary | match youtube junos:YOUTUBE-COMMENT No 833 32813 junos:FACEBOOK-YOUTUBEBOX No 603 33221 junos:FACEBOOK-YOUTUBEVIDEOBOX No 577 33108 junos:YOUTUBE-STREAM No 527 32814 junos:YOUTUBE No 315 32815

Is there a group associated with the YouTube streaming option? This group will most likely disable any streaming video from the web.

root@srx100> show services application-identification group summary | match youtube root@srx100>

No group association, but we can check the details of the junos:YOUTUBE-STREAM application to see if it's associated with any application groups:

root@srx100> show services application-identification application detail junos:YOUTUBE-STREAM Application Name: junos:YOUTUBE-STREAM Application type: YOUTUBE-STREAM Description: This signature detects video streaming from Youtube.com, a video sharing site. Application ID: 527 Disabled: No Number of Parent Group(s): 1 Application Groups: junos:web:multimedia:web-based Application Tags: characteristic : Loss of Productivity characteristic : Bandwidth Consumer risk : 2 subcategory : Multimedia category : Web Signature NestedApplication:YOUTUBE-STREAM Layer-7 Protocol: HTTP Chain Order: no Maximum Transactions: 15 Order: 32814 Member(s): 2 Member 0 Context: http-header-host Pattern: (.*\.)?(youtube|googlevideo)\.com Direction: CTS Member 1 Context: http-header-content-type Pattern: .*video/.* Direction: STC

Looks like the YOUTUBE-STREAM application is part of the junos:web:multimedia:web-based group. So let's check that group:

root@srx100> show services application-identification group detail junos:web:multimedia:web-based | match youtube junos:YOUTUBE-COMMENT junos:YOUTUBE junos:YOUTUBE-STREAM

No we can decide to block just YouTube video's by using the application ( junos:YOUTUBE-STREAM ), or we can block all streaming video by using the application group ( junos:web:multimedia:web-based ).

In this example we'll be using the application only.

[edit security application-firewall] root@srx100# set rule-sets my-appfw rule youtubevideo-block match dynamic-application junos:YOUTUBE-STREAM [edit security application-firewall] root@srx100# set rule-sets my-appfw rule youtubevideo-block then deny [edit security application-firewall] root@srx100# set rule-sets my-appfw default-rule permit [edit security application-firewall] root@srx100# show | compare [edit security application-firewall] + rule-sets my-appfw { + rule youtubevideo-block { + match { + dynamic-application junos:YOUTUBE-STREAM; + } + then { + deny; + } + } + default-rule { + permit; + } + } root@srx100# commit commit complete

Now that the rule-set has been created we can assign it to a security policy in the firewall. In this case we're gonna add it to the trust-to-untrust security policy. The following configuration has no AppFW config:

root@srx100# run show configuration security policies from-zone trust to-zone untrust policy trust-to-untrust { match { source-address Internal-Network; destination-address any-ipv4; application any; } then { permit; log { session-init; session-close; } count; } }

Now we add the AppFW part to it:

[edit security policies from-zone trust to-zone untrust] root@srx100# set policy trust-to-untrust then permit application-services application-firewall rule-set my-appfw [edit security policies from-zone trust to-zone untrust] root@srx100# show | compare [edit security policies from-zone trust to-zone untrust policy trust-to-untrust then permit] + application-services { + application-firewall { + rule-set my-appfw; + } + } [edit security policies from-zone trust to-zone untrust] root@srx100# commit commit complete [edit security policies from-zone trust to-zone untrust] root@srx100# run show configuration security policies from-zone trust to-zone untrust policy trust-to-untrust match { source-address Internal-Network; destination-address any-ipv4; application any; } then { permit { application-services { application-firewall { rule-set my-appfw; } } } log { session-init; session-close; } count; }

When we open a browser and visit YouTube.com, we see the video placeholder and all the video controls, but the video refuses to play.

View fullsize

The YouTube video's will not play with the created Application Firewall policy.​

To verify that the blocking of the YouTube video actually occurred we use the following command:

root@srx100> show security application-firewall rule-set my-appfw Rule-set: my-appfw Rule: youtubevideo-block Dynamic Applications: junos:YOUTUBE-STREAM Action:deny Number of sessions matched: 361 Default rule:permit Number of sessions matched: 1356 Number of sessions with appid pending: 0

As we can see, the AppFW rule-set my-appfw denied 361 matching sessions.

As a precaution, we can check if e.g. vimeo.com video's still work properly.

View fullsize

Video's on Vimeo work just fine with the created Application Firewall policy.

We succeeded in our quest to deny YouTube video's by using the Juniper SRX Application Firewall functionality.

We did all this by usinfg the CLI, but this can also be achieved by using the J-Web interface. Note that the initial part (the downloading part) needs to be done by using the CLI.

In the J-Web interface, go to Configure -> Security -> Policy -> Define AppFW Policy . Here you can create the rule-set and the associated rules in that set.

View fullsize

View fullsize

View fullsize

View fullsize

Adding the created Application Firewall rule-set to the firewall policy is done by adding it to the actual policy rule under Configure -> Security -> Policy -> Apply Policy .

View fullsize

View fullsize

The problem with the J-Web way of creating AppFW rules and applying them is that there's no way of dis-associating the AppFW rule-set with the security policy. That needs to be done by using the CLI, or by removing the policy rule and re-create it.

Below is the deny logging visible from within Splunk (the excellent log analyser tool).

View fullsize

The YouTube deny rule in Splunk

Finally the set commands combined for creating the actual rule-set and policy:

set security application-firewall rule-sets my-appfw rule youtubevideo-block match dynamic-application junos:YOUTUBE-STREAM set security application-firewall rule-sets my-appfw rule youtubevideo-block then deny set security application-firewall rule-sets my-appfw default-rule permit set security policies from-zone trust to-zone untrust policy trust-to-untrust match source-address Internal-Network set security policies from-zone trust to-zone untrust policy trust-to-untrust match source-address VPN-Network set security policies from-zone trust to-zone untrust policy trust-to-untrust match destination-address any-ipv4 set security policies from-zone trust to-zone untrust policy trust-to-untrust match application any set security policies from-zone trust to-zone untrust policy trust-to-untrust then permit application-services application-firewall rule-set my-appfw set security policies from-zone trust to-zone untrust policy trust-to-untrust then log session-init set security policies from-zone trust to-zone untrust policy trust-to-untrust then log session-close set security policies from-zone trust to-zone untrust policy trust-to-untrust then count

Posted on May 10, 2013 by Willem and filed under Security , Tips'n Tricks , Junos and tagged AppFW Juniper YouTube block srx application firewall example config configuration .
