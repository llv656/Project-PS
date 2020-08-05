#!/bin/bash

for var in $(ccrypt -d -c settings_contenedor_back_end.env.cpt); do
    export "$var"
done

for var in $(ccrypt -d -c settings_contenedor_front_end.env.cpt); do
    export "$var"
done

docker-compose up
