# Minimal PAN-OS fixture input

```xml
<config>
  <devices><entry name="localhost.localdomain"><vsys><entry name="vsys1">
    <zone><entry name="trust"><network><layer3><member>ethernet1/2</member></layer3></network></entry><entry name="untrust"><network><layer3><member>ethernet1/1</member></layer3></network></entry></zone>
    <address><entry name="WEB"><ip-netmask>10.0.1.10/32</ip-netmask></entry></address>
    <service><entry name="HTTPS-ALT"><protocol><tcp><port>8443</port></tcp></protocol></entry></service>
    <rulebase><security><rules><entry name="ALLOW-WEB"><from><member>trust</member></from><to><member>untrust</member></to><source><member>any</member></source><destination><member>WEB</member></destination><application><member>ssl</member></application><service><member>application-default</member></service><action>allow</action></entry></rules></security></rulebase>
  </entry></vsys></entry></devices>
</config>
```
