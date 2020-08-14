#!/bin/bash

for var in $(ccrypt -d -c settings_contenedor_back_end.env.cpt); do
    export "$var"
done

for var in $(ccrypt -d -c settings_contenedor_front_end.env.cpt); do
    export "$var"
done

iptables -t nat -A POSTROUTING -o enp2s0 -j MASQUERADE
iptables -A INPUT -s 10.0.0.0/24 -i br-1fec80074986 -j ACCEPT

docker-compose up
