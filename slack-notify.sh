#!/bin/bash

set -e

# Set this to your Slack webhook URL
SLACK_WEBHOOK=""
INTERVAL="${INTERVAL:-300}"

log() {
    echo "[$(date '+%T')] $*"
}

while :; do
    log "Searching for available timeslot..."
    RESULT=$(pipenv run ./curbguide.py "$@")
    echo "$RESULT"

    COUNT=$(grep -c "N/A" <<<"$RESULT")
    if [[ "$COUNT" -lt 5 ]]; then
        log "Pickup found! Sending notification..."
        curl -s "$SLACK_WEBHOOK" --data-urlencode 'payload={"text": "```'"$RESULT"'```"}' > /dev/null
    fi
    sleep "$INTERVAL"
done
