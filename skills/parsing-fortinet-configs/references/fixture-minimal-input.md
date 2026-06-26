# Minimal FortiGate fixture input

```fortios
config system interface
    edit "port1"
        set ip 203.0.113.2 255.255.255.0
        set role wan
    next
    edit "port2"
        set ip 10.0.0.1 255.255.255.0
        set role lan
    next
end
config firewall address
    edit "WEB"
        set subnet 10.0.1.10 255.255.255.255
    next
end
config firewall service custom
    edit "HTTPS-ALT"
        set tcp-portrange 8443
    next
end
config firewall policy
    edit 1
        set name "ALLOW-WEB"
        set srcintf "port2"
        set dstintf "port1"
        set srcaddr "all"
        set dstaddr "WEB"
        set service "HTTPS-ALT"
        set action accept
        set schedule "always"
        set logtraffic all
    next
end
```
