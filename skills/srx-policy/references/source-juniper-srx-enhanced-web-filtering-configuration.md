# Juniper SRX Enhanced Web Filtering Configuration

Source URL: https://rayka-co.com/lesson/juniper-srx-enhanced-web-filtering-configuration/
Final URL: https://rayka-co.com/lesson/juniper-srx-enhanced-web-filtering-configuration/
HTTP status: 200
Extractor: htmlparser
Extracted characters: 16707

## Extracted text

29. Juniper SRX Enhanced Web Filtering Configuration - RAYKA (are you a network engineer?) 

Skip to content 

[email protected] 011 322 44 56 Monday – Friday 10 AM – 8 PM 

cart: $ 0.00 0 

View Cart Checkout 

No products in the cart. 

Subtotal: $ 0.00 

View Cart Checkout 

YouTube page opens in new window Linkedin page opens in new window X page opens in new window 

RAYKA (are you a network engineer?) 

are you a network engineer? 

Courses 
DEVOPS_AUTOMATION devops and automation courses like ansible, cisco devnet and bash scripting 

CISCO NETWORKING cisco networking, security, cloud, devnet and service provider courses 
SERVICE PROVIDER mpls, segment routing,mpls services like mpls vpn, vpls and mpls te 

Cisco Security 

Data Center 

SDN-based NETWORK sd-access, sd-wan and sdn based data center 

Juniper 
Juniper Security 

F5 BIG-IP 

Free Courses 

Shop 
Service Provider 

Security 

DevOps / Automation 

Data Center 

SDN-based Networks 

Juniper 

F5 

About 
About Teachers 

Privacy Policy 

Contact Us 

discount 

Search: 

My-Account 
Login 
Register 

Courses 
DEVOPS_AUTOMATION devops and automation courses like ansible, cisco devnet and bash scripting 

CISCO NETWORKING cisco networking, security, cloud, devnet and service provider courses 
SERVICE PROVIDER mpls, segment routing,mpls services like mpls vpn, vpls and mpls te 

Cisco Security 

Data Center 

SDN-based NETWORK sd-access, sd-wan and sdn based data center 

Juniper 
Juniper Security 

F5 BIG-IP 

Free Courses 

Shop 
Service Provider 

Security 

DevOps / Automation 

Data Center 

SDN-based Networks 

Juniper 

F5 

About 
About Teachers 

Privacy Policy 

Contact Us 

discount 

29. Juniper SRX Enhanced Web Filtering Configuration 

You are here: 

Home 

Lesson 

29. Juniper SRX Enhanced Web… 

Juniper SRX enhanced web filtering is the third method of web filtering implementation which is based on Websense cloud solution and will be discussed in this section. 

Enhanced Web Filtering in juniper website 

Juniper SRX enhanced web filtering Fundamental 

With Juniper SRX enhanced web filtering, in summary, URL addresses are forwarded to the cloud. URL category and URL reputation are returned from the cloud. 

Then In the juniper SRX device, we decide the behaviour based on the URL category and reputation. 

Enhanced web filtering feature requires a license unlike the other two web filtering methods, local and Websense-redirect , which is discussed in the previous section. 

URL reputation returned by the cloud is one of the “very-safe”, “moderately-safe”, “fairly-safe”, “suspicious” and “harmful”. 

URL category returned by the cloud is pre-defined category already exist in the cloud. 

Juniper SRX Enhanced Web Filtering Fundamental 

But there is no decision regarding the action in the cloud. The action is decided on the juniper SRX device itself which is configured by the administrator for each URL category and reputation. 

You can also configure default action for the time when the URL does not belong to any of the categories and there is no reputation history for the URL. 

We can also configure fallback action for the time when the cloud solution is not available. 

The action can be one of the options, “permit”, “block” and “quarantine”. 

The actions “permit” and “block” are clear but the action “quarantine” makes the end user the final decision maker. 

In other words, final user receive a message that the URL can be harmful. Do you want to continue browsing the URL? Based on the end user’s response, the URL is downloaded or blocked by the Juniper SRX device. 

Juniper SRX enhanced web filtering Configuration Steps 

Configuring enhanced web filtering feature is like all other UTM features. 

Juniper SRX Enhanced Web Filtering Configuration Steps 

In the first step we have to enable enhanced web filtering feature. 

In the second step, we configure enhanced web filtering profile. 

Inside the profile, we configure the action for each URL category and URL reputation. 

We also configure the default action for the URL categories and reputation for which the action is not explicitly configured. Or when the URL is not categorized and there is no history for the reputation. 

It is also optional to configure the IP address and the port to connect to the Websense cloud solution. By default it connects to the address “rp.cloud.threatseeker.com”. 

In the third step we configure enhanced web filtering policy. The only configuration in the policy is to use one of the configured web filtering profiles or the default profile. 

In the last step, enhanced web filtering policy will be applied to a security policy exact like other UTM features. 

Juniper SRX Enhanced Web Filtering Configuration 

Now we can start configuring Enhanced web filtering in the juniper SRX device. 

As you know, enhanced web filtering feature unlike local and websense-redirect methods require license. Here I use 30 days trial license. 

To see if the license exist in my device, I use the command “ show system license ”. 

rayka@vSRX1# run show system license License usage: Licenses Licenses Licenses Expiry Feature name used installed needed anti_spam_key_sbl 1 1 0 21 days idp-sig 0 1 0 30 days appid-sig 0 1 0 30 days av_key_sophos_engine 1 1 0 19 days wf_key_websense_ewf 1 1 0 29 days Virtual Appliance 1 1 0 40 days ... 

As you can see in the output, “ wf_key_websense_ewf ” is activated in my device. “wf” stands for “web filtering” and “ewf” stands for “enhanced web filtering”. 

Enable Enhanced Web Filtering 

In the first step, we have to enable enhanced web filtering. 

With the command “ set security utm default-configuration web-filtering type ? ”, you see that there are four options to be configured as we have discussed earlier. “ juniper-local ”, “ websense-redirect ”, “ juniper-enhanced ” or to disable web filtering with “ web-filtering-none ” option. 

Here we use and enable enhanced web filtering. 

[edit] rayka@vSRX1# set security utm default-configuration web-filtering type ? Possible completions: juniper-enhanced juniper-local web-filtering-none websense-redirect [edit] rayka@vSRX1# set security utm default-configuration web-filtering type juniper-enhanced [edit] rayka@vSRX1# 

Configure Enhanced Web Filtering Profile 

To configure Enhanced web filtering profile, which is optional, we configure the action for each URL category and URL reputation. 

With the command “ set security utm feature-profile web-filtering juniper-enhanced profile ”, we create a profile with the name of “WEB_FILTER_ENHANCED_PROFILE”.  

With the parameter “category”, we can see all pre-defined categories existing in the cloud. 

rayka@vSRX1# set security utm feature-profile web-filtering juniper-enhanced profile WEB_FILTER_ENHANCED_PROFILE category ? Possible completions: <name> Name of Juniper enhanced category BLACKLISTCAT [security utm custom-objects custom-url-category] Enhanced_Abortion [security utm custom-objects custom-url-enhanced-category] Enhanced_Abused_Drugs [security utm custom-objects custom-url-enhanced-category] Enhanced_Adult_Content [security utm custom-objects custom-url-enhanced-category] Enhanced_Adult_Material [security utm custom-objects custom-url-enhanced-category] ... 

For each category, we are allowed to configure one of the action “block”, “permit” or “quarantine”. 

Here as an example, I configure the action “block” for the categories “Enhanced_Games” and “Enhanced_Peer_to_Peer_File_Sharing”. 

I also configure the action “permit” for the category “Enhanced_Educational_Video”. 

set security utm feature-profile web-filtering juniper-enhanced profile WEB_FILTER_ENHANCED_PROFILE category Enhanced_Games action block set security utm feature-profile web-filtering juniper-enhanced profile WEB_FILTER_ENHANCED_PROFILE category Enhanced_Peer_to_Peer_File_Sharing action block set security utm feature-profile web-filtering juniper-enhanced profile WEB_FILTER_ENHANCED_PROFILE category Enhanced_Educational_Video action permit 

We also configure the action for different URL reputation. 

With the parameter “ site-reputation-action ? ”, we can see different reputation. “very-safe”, “moderately-safe”, “fairly-safe”, “suspicious” and “harmful”. 

rayka@vSRX1# set security utm feature-profile web-filtering juniper-enhanced profile WEB_FILTER_ENHANCED_PROFILE site-reputation-action ? Possible completions: <[Enter]> Execute this command | Pipe through a command + apply-groups Groups from which to inherit configuration data + apply-groups-except Don't inherit configuration data from these groups very-safe Action when site reputation is very safe moderately-safe Action when site reputation is moderately safe fairly-safe Action when site reputation is fairly safe suspicious Action when site reputation is suspicious harmful Action when site reputation is harmful [edit] rayka@vSRX1# 

I configure the action “block” for the reputation “harmful”. The action “quarantine” for the reputation “suspicious” and the action “log-and-permit” for other reputations. 

I also configure the default action “quarantine”, for the URLs existing no reputation history in the cloud. 

set security utm feature-profile web-filtering juniper-enhanced profile WEB_FILTER_ENHANCED_PROFILE site-reputation-action harmful block set security utm feature-profile web-filtering juniper-enhanced profile WEB_FILTER_ENHANCED_PROFILE site-reputation-action suspicious quarantine set security utm feature-profile web-filtering juniper-enhanced profile WEB_FILTER_ENHANCED_PROFILE site-reputation-action fairly-safe log-and-permit set security utm feature-profile web-filtering juniper-enhanced profile WEB_FILTER_ENHANCED_PROFILE site-reputation-action moderately-safe log-and-permit set security utm feature-profile web-filtering juniper-enhanced profile WEB_FILTER_ENHANCED_PROFILE site-reputation-action very-safe log-and-permit set security utm feature-profile web-filtering juniper-enhanced profile WEB_FILTER_ENHANCED_PROFILE default quarantine 

We also configure optionally the IP address of Websense cloud solution. The address “ rp.cloud.threatseeker.com ” is the default web filtering cloud address and it is not required to be configured. 

set security utm feature-profile web-filtering juniper-enhanced server host rp.cloud.threatseeker.com set security utm feature-profile web-filtering juniper-enhanced server port 80 

Configure Enhanced Web Filtering Policy 

In the next step we configure web filtering policy. 

There is not a lot to configure in web filtering policy. We only configure and enable one of the configured web filtering profile in web filtering policy. 

Here we create a policy with the name of “WEB_FILTER_ENHANCED_POLICY”. 

rayka@vSRX1# set security utm utm-policy WEB_FILTER_ENHANCED_POLICY web-filtering http-profile ? Possible completions: <http-profile> Web-filtering HTTP profile WEB_FILTER_ENHANCED_PROFILE [security utm feature-profile web-filtering juniper-enhanced profile] WEB_FILTER_LOCAL_PROFILE [security utm feature-profile web-filtering juniper-local profile] WEB_FILTER_REDIRECT_PROFILE [security utm feature-profile web-filtering websense-redirect profile] junos-wf-enhanced-default [security utm feature-profile web-filtering juniper-enhanced profile] junos-wf-enhanced-log-only [security utm feature-profile web-filtering juniper-enhanced profile] junos-wf-local-default [security utm feature-profile web-filtering juniper-local profile] junos-wf-websense-default [security utm feature-profile web-filtering websense-redirect profile] [edit] rayka@vSRX1# set security utm utm-policy WEB_FILTER_ENHANCED_POLICY web-filtering http-profile WEB_FILTER_ENHANCED_PROFILE 

In addition to the manually configured profile, there are also options to configure the default “junos-wf-enhanced-default” or “junos-wf-enhanced-log-only” pre-defined profiles in web filtering policy. 

We enable manually configured profile, “WEB_FILTER_ENHANCED_PROFILE” in the policy. 

Enable Web Filtering Policy in Security Policy 

In the last step, we have to apply the web filtering policy in a security policy. 

From untrust zone to trust zone, there is a default default-permit rule that permit everything and we configured in the previous sections. 

At the end of “then” command, we add web filter policy “WEB_FILTER_ENHANCED_POLICY” in default-permit security policy. 

set security policies from-zone untrust to-zone trust policy default-permit match source-address any set security policies from-zone untrust to-zone trust policy default-permit match destination-address any set security policies from-zone untrust to-zone trust policy default-permit match application any set security policies from-zone untrust to-zone trust policy default-permit then permit set security policies from-zone untrust to-zone trust policy default-permit then permit application-services utm-policy WEB_FILTER_ENHANCED_POLICY 

Monitor Web Filtering Policy 

To make sure that enhanced web filtering policy is configured and activated, we have two main monitoring commands. 

With the command “ show security utm web-filtering status ”, you can make sure that web filtering is activated. It also shows the type of web filtering policy, which is “Enhanced” in this scenario. 

[edit] rayka@vSRX1# run show security utm web-filtering status UTM web-filtering status: Server status: Juniper Enhanced using Websense server UP 

# Command10 

With the command “ show security utm web-filtering statistics ”, you can follow and monitor statistics related to web filtering policy. The number of hits based on URL categories and URL reputations. 

[edit] rayka@vSRX1# run show security utm web-filtering statistics UTM web-filtering statistics: Total requests: 0 White list hit: 0 Black list hit: 0 Default action hit: 0 No license permit: 0 Queries to server: 0 Server reply permit: 0 Server reply block: 0 Server reply quarantine: 0 Server reply quarantine block: 0 Server reply quarantine permit: 0 Custom category permit: 0 Custom category block: 0 Custom category quarantine: 0 Custom category qurantine block: 0 Custom category quarantine permit: 0 Site reputation permit: 0 Site reputation block: 0 Site reputation quarantine: 0 Site reputation quarantine block: 0 Site reputation quarantine permit: 0 Site reputation by Category 0 Site reputation by Global 0 Cache hit permit: 0 Cache hit block: 0 Cache hit quarantine: 0 Cache hit quarantine block: 0 Cache hit quarantine permit: 0 Safe-search redirect: 0 Safe-search rewrite: 0 SNI pre-check queries to server: 0 SNI pre-check server responses: 0 Web-filtering sessions in total: 128000 Web-filtering sessions in use: 0 Fallback: log-and-permit block Default 0 0 Timeout 0 0 Connectivity 0 0 Too-many-requests 0 0 [edit] rayka@vSRX1# 

Back to: Juniper Security Associate (JNCIA-SEC) based on vSRX version 22.1R1.10 > Unified Threat Management (UTM) 

Leave a Reply Cancel reply 

Your email address will not be published. Required fields are marked * 

Comment 

Name * Email * Website 

Save my name, email, and website in this browser for the next time I comment. 

Post comment 

discount until November 7, 2024, at 23:59 (UTC+1, CEST) 

 

Get 85% discount 

Coupon: halloween2024 

until November 7, 2024, at 23:59 (UTC+1, CEST) 

discount subscription 

RAYKA 

Cisco Networking 

YouTube Video VVVUcmdvbF9fbllTclFCaF9qMlBjTjRRLldDMEJSRjVlcGtR 

Load More... Subscribe 

LATEST COURSES 

Docker Container and GitLab CI/CD for Network Engineers (in Progress) 4 Lessons 

MPLS & MPLS VPN Fundamental 22 Lessons 

Network Automation with pyATS & Genie 22 Lessons 

IPv6 35 Lessons 

F5 BIG-IP AWAF (formerly ASM) 27 Lessons 

LATEST LESSONS 

4. Docker Commands in Practice Part of: Docker Container and GitLab CI/CD for Network Engineers (in Progress) 

3. Docker Image vs Docker Container Part of: Docker Container and GitLab CI/CD for Network Engineers (in Progress) 

2. Install Docker on Ubuntu Part of: Docker Container and GitLab CI/CD for Network Engineers (in Progress) 

1. Containers and CI/CD in Network Automation : Definition and Applications Part of: Docker Container and GitLab CI/CD for Network Engineers (in Progress) 

22. Carrier Supporting Carriers Part of: MPLS & MPLS VPN Fundamental 

More Lessons 

Go to Top 

We noticed you're visiting from United States (US). We've updated our prices to United States (US) dollar for your shopping convenience. Use Euro instead. Dismiss
