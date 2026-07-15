# Getting Started with ATP Appliance and the SRX Series

Source URL: https://www.juniper.net/documentation/us/en/software/atp-appliance/atp-appliance-srx-integration/topics/concept/atp-appliance-srx-integration-overview.html
Final URL: https://www.juniper.net/documentation/us/en/software/atp-appliance/atp-appliance-srx-integration/topics/concept/atp-appliance-srx-integration-overview.html
HTTP status: 200
Extractor: htmlparser
Extracted characters: 1702

## Extracted text

ATP Appliance and SRX Series Firewall Integration Overview | Juniper Networks

X

Help us improve your experience.

Let us know what you think.

Do you have time for a two-minute survey?

Yes

Maybe Later

ATP Appliance and SRX Series Firewall Integration Overview

The Juniper Advanced Threat Prevention Appliance integrates with the SRX Series Firewall to protect all hosts in your network against evolving security threats by employing ATP Appliance’s threat detection software with a next-generation firewall system.

For this release, the SRX Series Firewall integrates with the ATP Appliance Core to provide the following features:

File scanning with global allowlists and blocklists.

File scanning for administrator-created file profiles for specified file types.

Feeds for infected hosts, command and control servers, and GeoIP.

Email attachment scanning for SMTP and IMAP.

Configuration is required on both ATP Appliance and the SRX Series Firewall for these features.

Note:
ATP Appliance (previously Cyphort) already worked with the SRX Series Firewall for “Auto-Mitigation” of infected hosts using address sets. The integration described in this guide is a more complete solution that requires the SRX Series Firewall to enroll with ATP Appliance to make use of many more features explained here.

See the Operator’s Guide , and the section entitled “Verifying Auto-Mitigation Rule Operations,” for more details about existing options for infected host mitigation using ATP Appliance and the SRX Series, that don’t include enrollment.

Related Documentation

Licensing and Platform Support information

Getting Started with ATP Appliance and the SRX Series Firewall
