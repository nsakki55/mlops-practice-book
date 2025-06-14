#!/bin/bash

PORT=8080

tail -n +2 './data/test/test.csv' | while read LINE; do
   IFS=',' read impression_id logged_at user_id app_code os_version is_4g <<< "$LINE"

   echo  "{\"impression_id\": \"${impression_id}\", \"logged_at\": \"${logged_at}\", \"user_id\": ${user_id}, \"app_code\": ${app_code}, \"os_version\": \"${os_version}\", \"is_4g\": ${is_4g}}"

   curl -s -X 'POST' "${ALB_DNS}:${PORT}/predict" \
   -H 'accept: application/json' \
   -H 'Content-Type: application/json' \
   -d "{
       \"impression_id\": \"${impression_id}\",
       \"logged_at\": \"${logged_at}\",
       \"user_id\": ${user_id},
       \"app_code\": ${app_code},
       \"os_version\": \"${os_version}\",
       \"is_4g\": ${is_4g}
   }" | tr -d '\n'
   echo

   sleep 0.5
done
