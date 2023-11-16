#!/bin/bash

# Enable job control
set -m

# Start Kibana in the background
/usr/local/bin/kibana-docker &

# Wait for Kibana to be ready
while true; do
  status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5601/api/status)
  if [ "$status" -eq 200 ]; then
    break
  fi
  sleep 1
done

# Import ndjson file
curl -X POST http://localhost:5601/api/saved_objects/_import?createNewCopies=true -H "kbn-xsrf: true" --form file=@$(dirname "$0")/export.ndjson

# Bring Kibana to the foreground
fg %1
