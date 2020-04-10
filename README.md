# curbguide 🚗🛒

## Requirements

 - Python 3.7+
 - Pipenv

## Installation

```
pipenv install
```

## Running

``` bash
# Replace with your zip code
$ pipenv run curbguide.py 78218
```

### Slack notification loop

Make a Slack Custom Integration and set the SLACK_WEBHOOK variable in slack-notify.sh to your new integration's webhook URL. Then run:

``` bash
$ ./slack-notify.sh 78218
```

And it will check for available curbside timeslots every five minutes and send to Slack if there are any available.
