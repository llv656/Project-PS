#!/bin/bash
[[ $3  ]] || { exit; }
TOKEN_TELEGRAM=$1
CHATID_TELEGRAM=$2
TEXT="$3"
TIME="10"
URL="https://api.telegram.org/bot$TOKEN_TELEGRAM/sendMessage"
curl -s --max-time $TIME -d "chat_id=$CHATID_TELEGRAM&disable_web_page_preview=1&text=$TEXT" $URL > /dev/null
