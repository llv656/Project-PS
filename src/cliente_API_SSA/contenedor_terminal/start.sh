#!/bin/bash
cert=$(echo $PATH_CERT | base64 -d)
key=$(echo $PATH_KEY | base64 -d)
su -c "ttyd -c $USER:$PASS --ssl --ssl-cert $cert --ssl-key $key bash" limitado
