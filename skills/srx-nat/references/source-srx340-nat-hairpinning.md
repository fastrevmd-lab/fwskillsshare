# SRX

Source: https://community.juniper.net/discussion/srx340-nat-hairpinning
HTTP: 200 OK
Extractor: body
Retrieved: 2026-05-15

---

Skip main navigation (Press Enter).

[](home)

_[Join Elevate](https://userregistration.juniper.net/)_

# SRX

×

  * [ Community Home ](/communities/community-home?communitykey=c1a2ae9d-fa3e-41f5-82dc-a447b7b0da24)
  * [ Discussion 26.2K ](/communities/community-home/digestviewer?communitykey=c1a2ae9d-fa3e-41f5-82dc-a447b7b0da24)
  * [ Library 730 ](/communities/community-home/librarydocuments?communitykey=c1a2ae9d-fa3e-41f5-82dc-a447b7b0da24&LibraryFolderKey=&DefaultView=)
  * [ Blogs 0 ](/communities/community-home/recent-community-blogs?communitykey=c1a2ae9d-fa3e-41f5-82dc-a447b7b0da24)
  * [ Events 0 ](/communities/community-home/recent-community-events?communitykey=c1a2ae9d-fa3e-41f5-82dc-a447b7b0da24)
  * [ Members 1.3K ](/communities/community-home/community-members?communitykey=c1a2ae9d-fa3e-41f5-82dc-a447b7b0da24&Execute=1)

View Only

[__Back to discussions](javascript:void\(0\);)

Expand all | Collapse all sort by most recent sort by thread

##  SRX340 NAT hairpinning

Jump to Best Answer

#### Gabriel-02-05-2020 03:31

Hello, Currently we use source NAT to access the Internet from LAN: pool ...

#### pradkm02-05-2020 04:46Best Answer

Hi Gabriel, Adding the zone trust to the existing destination NAT rule would solve your purpose. ...

#### Gabriel-02-06-2020 00:33

Thank you, it worked for me!

#### JAY ECHOUAFNI08-23-2023 18:33

Hi I am having the same issue not able to ping servers in the trust from themself using their outside ...

  * ####  1\.  SRX340 NAT hairpinning

[Recommend](javascript:__doPostBack\('ctl00$MainCopy$ctl07$ucMessageList$rptMessageList$ctl00$ItemRating$lbLike',''\))

[](https://community.juniper.net/profile?UserKey=4f736bae-d918-43f0-8c07-d2cd186f049e)

[Gabriel-](https://community.juniper.net/profile?UserKey=4f736bae-d918-43f0-8c07-d2cd186f049e)

Posted 02-05-2020 03:31

[Reply](javascript:__doPostBack\('ctl00$MainCopy$ctl07$ucMessageList$rptMessageList$ctl00$ThreadActions$ReplyInlineUnauthenticated',''\)) [Reply Privately](https://community.juniper.net/communities/all-discussions/postreply?SenderKey=4f736bae-d918-43f0-8c07-d2cd186f049e&MessageKey=37474227-f927-43b6-854a-dde69b75fa33&ListKey=59a8ace9-cbfc-4155-beaf-92d16bbf8acd&ReturnUrl=https%3a%2f%2fcommunity.juniper.net%2fdiscussion%2fsrx340-nat-hairpinning) Options Dropdown

Hello,

Currently we use source NAT to access the Internet from LAN:

        pool src-nat-pool-office {
            address {
                1.1.1.2/32;
            }
        }
        rule-set rs1 {
            from zone trust;
            to zone untrust;
            rule office-nat {
                match {
                    source-address 192.168.4.0/24;
                    destination-address 0.0.0.0/0;
                }
                then {
                    source-nat {
                        pool {
                            src-nat-pool-office;
                        }
                    }
                }
            }
        }


In the same time we use destination NAT to access some resources from the Internet using one of our public IP addresses (BGP):

        pool server1 {
            address 192.168.4.123/32;
        }
        rule-set dnat-rs1 {
            from zone untrust;
            rule r1 {
                match {
                    destination-address 1.1.1.3/32;
                    destination-port {
                        80;
                    }
                }
                then {
                    destination-nat {
                        pool {
                            server1;
                        }
                    }
                }
            }

Now, we would like to access the "server1" from LAN using public IP address - 1.1.1.3 (this one from destination NAT). How to do that? I read something about NAT hairpinning, but I'm not sure how to use it here.

Can I ask for help? 🙂




  * ####  2\.  RE: SRX340 NAT hairpinning

Best Answer

[Recommend](javascript:__doPostBack\('ctl00$MainCopy$ctl07$ucMessageList$rptMessageList$ctl01$ItemRating$lbLike',''\))

[](https://community.juniper.net/profile?UserKey=acdce14d-f617-49e4-886a-9d44ea22425b)

[pradkm](https://community.juniper.net/profile?UserKey=acdce14d-f617-49e4-886a-9d44ea22425b)

Posted 02-05-2020 04:46

[Reply](javascript:__doPostBack\('ctl00$MainCopy$ctl07$ucMessageList$rptMessageList$ctl01$ThreadActions$ReplyInlineUnauthenticated',''\)) [Reply Privately](https://community.juniper.net/communities/all-discussions/postreply?SenderKey=acdce14d-f617-49e4-886a-9d44ea22425b&MessageKey=f0fca67e-306a-49d4-aaf2-8be1509cb585&ListKey=59a8ace9-cbfc-4155-beaf-92d16bbf8acd&ReturnUrl=https%3a%2f%2fcommunity.juniper.net%2fdiscussion%2fsrx340-nat-hairpinning) Options Dropdown

Hi Gabriel,

Adding the zone trust to the existing destination NAT rule would solve your purpose.

        set security nat destination rule-set dnat-rs1 from zone trust

This will help to trigger the destination NAT for traffic from internal LAN and the soure NAT will also be done which is necessary. Please refer to the KB at [https://kb.juniper.net/InfoCenter/index?page=content&id=KB24639](https://kb.juniper.net/InfoCenter/index?page=content&id=KB24639) which has an example for hairpin NAT and the requirements.

Hope this helps.

Thanks and Regards,

Pradeep Kumar

[KUDOS PLEASE! If you think I earned it!

If this solution worked for you please flag my post as an "Accepted Solution" so others can benefit..]




  * ####  3\.  RE: SRX340 NAT hairpinning

[Recommend](javascript:__doPostBack\('ctl00$MainCopy$ctl07$ucMessageList$rptMessageList$ctl02$ItemRating$lbLike',''\))

[](https://community.juniper.net/profile?UserKey=4f736bae-d918-43f0-8c07-d2cd186f049e)

[Gabriel-](https://community.juniper.net/profile?UserKey=4f736bae-d918-43f0-8c07-d2cd186f049e)

Posted 02-06-2020 00:33

[Reply](javascript:__doPostBack\('ctl00$MainCopy$ctl07$ucMessageList$rptMessageList$ctl02$ThreadActions$ReplyInlineUnauthenticated',''\)) [Reply Privately](https://community.juniper.net/communities/all-discussions/postreply?SenderKey=4f736bae-d918-43f0-8c07-d2cd186f049e&MessageKey=a61b9116-bea0-4df7-8de7-afb6eda0f05a&ListKey=59a8ace9-cbfc-4155-beaf-92d16bbf8acd&ReturnUrl=https%3a%2f%2fcommunity.juniper.net%2fdiscussion%2fsrx340-nat-hairpinning) Options Dropdown

Thank you, it worked for me!




  * ####  4\.  RE: SRX340 NAT hairpinning

[Recommend](javascript:__doPostBack\('ctl00$MainCopy$ctl07$ucMessageList$rptMessageList$ctl03$ItemRating$lbLike',''\))

[](https://community.juniper.net/profile?UserKey=ae8bf64e-8672-4fa5-ae25-0185666acb86)

[JAY ECHOUAFNI](https://community.juniper.net/profile?UserKey=ae8bf64e-8672-4fa5-ae25-0185666acb86)

Posted 08-23-2023 18:33

[Reply](javascript:__doPostBack\('ctl00$MainCopy$ctl07$ucMessageList$rptMessageList$ctl03$ThreadActions$ReplyInlineUnauthenticated',''\)) [Reply Privately](https://community.juniper.net/communities/all-discussions/postreply?SenderKey=ae8bf64e-8672-4fa5-ae25-0185666acb86&MessageKey=c560ab40-0332-4a69-98bb-018a23fadaeb&ListKey=59a8ace9-cbfc-4155-beaf-92d16bbf8acd&ReturnUrl=https%3a%2f%2fcommunity.juniper.net%2fdiscussion%2fsrx340-nat-hairpinning) Options Dropdown

Hi

I am having the same issue not able to ping servers in the trust from themself using their outside IP. What should I do



\------------------------------
JAY ECHOUAFNI
\------------------------------


[ __Original Message](javascript:__doPostBack\('ctl00$MainCopy$ctl07$ucMessageList$rptMessageList$ctl03$lnkOriginalMessage',''\))

Original Message:
Sent: 02-05-2020 04:45
From: pradkm
Subject: SRX340 NAT hairpinning


Hi Gabriel,

Adding the zone trust to the existing destination NAT rule would solve your purpose.

        set security nat destination rule-set dnat-rs1 from zone trust

This will help to trigger the destination NAT for traffic from internal LAN and the soure NAT will also be done which is necessary. Please refer to the KB at [https://kb.juniper.net/InfoCenter/index?page=content&id=KB24639](https://kb.juniper.net/InfoCenter/index?page=content&id=KB24639) which has an example for hairpin NAT and the requirements.

Hope this helps.

Thanks and Regards,

Pradeep Kumar

[KUDOS PLEASE! If you think I earned it!

If this solution worked for you please flag my post as an "Accepted Solution" so others can benefit..]




×

#### New Best Answer

This thread already has a best answer. Would you like to mark this message as the new best answer?

No

© 2025 Hewlett Packard Enterprise Development LP

[Powered by Higher Logic](http://www.higherlogic.com)
