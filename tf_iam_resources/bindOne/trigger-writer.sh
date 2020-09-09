#!/bin/bash

echo "running..."
echo $1, $2, $3

FUNCTION=$1
DATA=$2
REGION=$3




gcloud functions call $FUNCTION --data '{"message": '"$DATA"'}' --region=$REGION | grep SUCCESS

if [ $? -gt 0 ]
then
  echo "CLOUD FUNCTION FAILED - CHECK LOGS"
  exit 1
fi
if [ $? -eq 0 ]
then
  echo "CLOUD FUNCTION OK"
  # add verification check?
fi

echo DONE
exit 0

