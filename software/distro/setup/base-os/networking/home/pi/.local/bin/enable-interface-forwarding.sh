#!/bin/bash -eux

# Route packets between wlan0 and eth0
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
iptables -A FORWARD -i eth0 -o wlan0 -m state --state RELATED,ESTABLISHED -j ACCEPT
iptables -A FORWARD -i wlan0 -o eth0 -j ACCEPT
iptables -t nat -A POSTROUTING -o wlan0 -j MASQUERADE
iptables -A FORWARD -i wlan0 -o eth0 -m state --state RELATED,ESTABLISHED -j ACCEPT
iptables -A FORWARD -i eth0 -o wlan0 -j ACCEPT

# Redirect external incoming traffic bound for 192.168.4.1 and 192.168.5.1 to 127.0.0.1
iptables -t nat -A PREROUTING -i eth0 -d 192.168.4.1 -j DNAT --to-destination 127.0.0.1
iptables -t nat -A PREROUTING -i wlan0 -d 192.168.5.1 -j DNAT --to-destination 127.0.0.1
