# SRX

Source: https://community.juniper.net/discussion/source-nat-part-1-configuration-design-and-lab-demo-using-juniper-srx
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

##  Source NAT Part 1 - Configuration, Design and Lab Demo using Juniper SRX 

#### Maxim Tveritnev10-26-2024 05:32

Happy Friday evening! While everyone else is out, well… not thinking about Source NAT, I'm here ...

#### Nikolay Semov10-28-2024 11:17

Cool! Are you planning on including IPv6-related src-nat scenarios? ------------------------------ ...

#### Maxim Tveritnev10-28-2024 11:34

Hello Nikolay! IPv6 is not included in this Source NAT video series. I may include it in one of my ...

  * ####  1\.  Source NAT Part 1 - Configuration, Design and Lab Demo using Juniper SRX

[Recommend](javascript:__doPostBack\('ctl00$MainCopy$ctl07$ucMessageList$rptMessageList$ctl00$ItemRating$lbLike',''\))

[](https://community.juniper.net/profile?UserKey=e26c1850-13d3-43ba-b9b6-0192dae6d506)

[Maxim Tveritnev](https://community.juniper.net/profile?UserKey=e26c1850-13d3-43ba-b9b6-0192dae6d506)

Posted 10-26-2024 05:32

[Reply](javascript:__doPostBack\('ctl00$MainCopy$ctl07$ucMessageList$rptMessageList$ctl00$ThreadActions$ReplyInlineUnauthenticated',''\)) [Reply Privately](https://community.juniper.net/communities/all-discussions/postreply?SenderKey=e26c1850-13d3-43ba-b9b6-0192dae6d506&MessageKey=ad6da9ee-a60f-4570-8d65-8f66078c67ee&ListKey=59a8ace9-cbfc-4155-beaf-92d16bbf8acd&ReturnUrl=https%3a%2f%2fcommunity.juniper.net%2fdiscussion%2fsource-nat-part-1-configuration-design-and-lab-demo-using-juniper-srx) Options Dropdown

Happy Friday evening!

While everyone else is out, well…  _not_ thinking about Source NAT, I'm here with a fresh blog post diving into network design for those of us who love a good firewall configuration before the weekend. (Nothing says "Friday night" like optimizing NAT for small business networks, am I right?)

In this first video of a three-part series, we tackle **Source Network Address Translation (NAT)** -specifically **small-scale solutions** ideal for home offices and small businesses using **Juniper SRX firewalls**.

### What's Inside:

    1. **NAT Basics** – Whether you're familiar or new to NAT, we'll cover why it's crucial to our networks and probably something you're already using every day.

    2. **Design Tips** – Two solid design solutions to **enhance performance** and help you scale up without unnecessary upgrades.

    3. **Hands-On Demo** – Follow my lab setup using **Juniper vSRX and vMX** to get practical steps on configuring your own small-scale Source NAT setup.

    4. **Cost-Saving Strategies** – Find out how to tweak your network to **reduce OPEX** without giving up functionality or scalability.

And to make it even more fun, I've included some cool screenshots from the video below.

Ready to dive in? Check out the video here!

#cybermaxlab

[#sourcenat](https://community.juniper.net/search?s=%23source nat&executesearch=true)

  
  
\------------------------------  
Maxim Tveritnev  
Senior Resident Engineer  
Juniper Networks  
JNCIEx4  
<http://www.youtube.com/@CyberMaxLab>  
\------------------------------  

  
  

  * ####  2\.  RE: Source NAT Part 1 - Configuration, Design and Lab Demo using Juniper SRX

[Recommend](javascript:__doPostBack\('ctl00$MainCopy$ctl07$ucMessageList$rptMessageList$ctl01$ItemRating$lbLike',''\))

[](https://community.juniper.net/profile?UserKey=00da1330-3882-4be3-a1ed-68945adf5c42)

[Nikolay Semov](https://community.juniper.net/profile?UserKey=00da1330-3882-4be3-a1ed-68945adf5c42)

Posted 10-28-2024 11:17

[Reply](javascript:__doPostBack\('ctl00$MainCopy$ctl07$ucMessageList$rptMessageList$ctl01$ThreadActions$ReplyInlineUnauthenticated',''\)) [Reply Privately](https://community.juniper.net/communities/all-discussions/postreply?SenderKey=00da1330-3882-4be3-a1ed-68945adf5c42&MessageKey=a7c3be0e-bd74-40d3-922b-0192d3b36256&ListKey=59a8ace9-cbfc-4155-beaf-92d16bbf8acd&ReturnUrl=https%3a%2f%2fcommunity.juniper.net%2fdiscussion%2fsource-nat-part-1-configuration-design-and-lab-demo-using-juniper-srx) Options Dropdown

Cool! Are you planning on including IPv6-related src-nat scenarios?

  
  
\------------------------------  
Nikolay Semov  
\------------------------------  
  

[ __Original Message](javascript:__doPostBack\('ctl00$MainCopy$ctl07$ucMessageList$rptMessageList$ctl01$lnkOriginalMessage',''\))

Original Message:  
Sent: 10-25-2024 18:05  
From: Maxim Tveritnev  
Subject: Source NAT Part 1 - Configuration, Design and Lab Demo using Juniper SRX  
  

Happy Friday evening!

While everyone else is out, well…  _not_ thinking about Source NAT, I'm here with a fresh blog post diving into network design for those of us who love a good firewall configuration before the weekend. (Nothing says "Friday night" like optimizing NAT for small business networks, am I right?)

In this first video of a three-part series, we tackle **Source Network Address Translation (NAT)** -specifically **small-scale solutions** ideal for home offices and small businesses using **Juniper SRX firewalls**.

### What's Inside:

    1. **NAT Basics** – Whether you're familiar or new to NAT, we'll cover why it's crucial to our networks and probably something you're already using every day.

    2. **Design Tips** – Two solid design solutions to **enhance performance** and help you scale up without unnecessary upgrades.

    3. **Hands-On Demo** – Follow my lab setup using **Juniper vSRX and vMX** to get practical steps on configuring your own small-scale Source NAT setup.

    4. **Cost-Saving Strategies** – Find out how to tweak your network to **reduce OPEX** without giving up functionality or scalability.

And to make it even more fun, I've included some cool screenshots from the video below.

Ready to dive in? Check out the video here!

#cybermaxlab

[#sourcenat](https://community.juniper.net/search?s=%23source nat&executesearch=true)

  
  
\------------------------------  
Maxim Tveritnev  
Senior Resident Engineer  
Juniper Networks  
JNCIEx4  
<http://www.youtube.com/@CyberMaxLab>  
\------------------------------  

  
  

  * ####  3\.  RE: Source NAT Part 1 - Configuration, Design and Lab Demo using Juniper SRX

[Recommend](javascript:__doPostBack\('ctl00$MainCopy$ctl07$ucMessageList$rptMessageList$ctl02$ItemRating$lbLike',''\))

[](https://community.juniper.net/profile?UserKey=e26c1850-13d3-43ba-b9b6-0192dae6d506)

[Maxim Tveritnev](https://community.juniper.net/profile?UserKey=e26c1850-13d3-43ba-b9b6-0192dae6d506)

Posted 10-28-2024 11:34

[Reply](javascript:__doPostBack\('ctl00$MainCopy$ctl07$ucMessageList$rptMessageList$ctl02$ThreadActions$ReplyInlineUnauthenticated',''\)) [Reply Privately](https://community.juniper.net/communities/all-discussions/postreply?SenderKey=e26c1850-13d3-43ba-b9b6-0192dae6d506&MessageKey=d32999c6-e0aa-4890-937f-0192d3c2a4a5&ListKey=59a8ace9-cbfc-4155-beaf-92d16bbf8acd&ReturnUrl=https%3a%2f%2fcommunity.juniper.net%2fdiscussion%2fsource-nat-part-1-configuration-design-and-lab-demo-using-juniper-srx) Options Dropdown

Hello Nikolay! IPv6 is not included in this Source NAT video series. I may include it in one of my future videos.

  
  
\------------------------------  
Maxim Tveritnev  
Senior Resident Engineer  
Juniper Networks  
JNCIEx4  
<http://www.youtube.com/@CyberMaxLab>  
\------------------------------  
  

[ __Original Message](javascript:__doPostBack\('ctl00$MainCopy$ctl07$ucMessageList$rptMessageList$ctl02$lnkOriginalMessage',''\))

Original Message:  
Sent: 10-28-2024 11:16  
From: Nikolay Semov  
Subject: Source NAT Part 1 - Configuration, Design and Lab Demo using Juniper SRX  
  

Cool! Are you planning on including IPv6-related src-nat scenarios?

  
  
\------------------------------  
Nikolay Semov  
  
Original Message:  
Sent: 10-25-2024 18:05  
From: Maxim Tveritnev  
Subject: Source NAT Part 1 - Configuration, Design and Lab Demo using Juniper SRX  
  

Happy Friday evening!

While everyone else is out, well…  _not_ thinking about Source NAT, I'm here with a fresh blog post diving into network design for those of us who love a good firewall configuration before the weekend. (Nothing says "Friday night" like optimizing NAT for small business networks, am I right?)

In this first video of a three-part series, we tackle **Source Network Address Translation (NAT)** -specifically **small-scale solutions** ideal for home offices and small businesses using **Juniper SRX firewalls**.

### What's Inside:

    1. **NAT Basics** – Whether you're familiar or new to NAT, we'll cover why it's crucial to our networks and probably something you're already using every day.

    2. **Design Tips** – Two solid design solutions to **enhance performance** and help you scale up without unnecessary upgrades.

    3. **Hands-On Demo** – Follow my lab setup using **Juniper vSRX and vMX** to get practical steps on configuring your own small-scale Source NAT setup.

    4. **Cost-Saving Strategies** – Find out how to tweak your network to **reduce OPEX** without giving up functionality or scalability.

And to make it even more fun, I've included some cool screenshots from the video below.

Ready to dive in? Check out the video here!

#cybermaxlab

[#sourcenat](https://community.juniper.net/search?s=%23source nat&executesearch=true)

  
  
\------------------------------  
Maxim Tveritnev  
Senior Resident Engineer  
Juniper Networks  
JNCIEx4  
<http://www.youtube.com/@CyberMaxLab>  
\------------------------------  

  
  

×

#### New Best Answer

This thread already has a best answer. Would you like to mark this message as the new best answer?

No

© 2025 Hewlett Packard Enterprise Development LP 

[Powered by Higher Logic](http://www.higherlogic.com)
