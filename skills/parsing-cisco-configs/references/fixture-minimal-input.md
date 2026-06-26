# Minimal Cisco ASA fixture input

```cisco
interface GigabitEthernet0/0
 nameif outside
 security-level 0
 ip address 203.0.113.2 255.255.255.0
interface GigabitEthernet0/1
 nameif inside
 security-level 100
 ip address 10.0.0.1 255.255.255.0
object network WEB
 host 10.0.1.10
object service HTTPS-ALT
 service tcp destination eq 8443
access-list OUTSIDE-IN extended permit tcp any object WEB eq 443 log
access-group OUTSIDE-IN in interface outside
object network INSIDE-NET
 subnet 10.0.0.0 255.255.0.0
 nat (inside,outside) dynamic interface
route outside 0.0.0.0 0.0.0.0 203.0.113.1
```
