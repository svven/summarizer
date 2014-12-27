#!/bin/bash

## Run summarizer/dispatcher.py

echo 'Start dispatcher'

## Activate the virtualenv
. env/bin/activate

python -c "from summarizer import dispatcher; dispatcher.dispatch()"

echo 'End dispatcher'

## Deactivate the virtualenv
deactivate