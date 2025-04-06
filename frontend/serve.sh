#!/bin/sh

[ -n "$BASE_URL" ] && sed -i "s|BASE_URL: \".*\"|BASE_URL: \"$BASE_URL\"|" index.html
[ -n "$BASE_URL_UI" ] && sed -i "s|BASE_URL_UI: \".*\"|BASE_URL_UI: \"$BASE_URL_UI\"|" index.html
[ -n "$BASE_URL_WS" ] && sed -i "s|BASE_URL_WS: \".*\"|BASE_URL_WS: \"$BASE_URL_WS\"|" index.html
[ -n "$BASE_URL_WS_SUBSCRIBE" ] && sed -i "s|BASE_URL_WS_SUBSCRIBE: \".*\"|BASE_URL_WS_SUBSCRIBE: \"$BASE_URL_WS_SUBSCRIBE\"|" index.html

http-server -p 8080