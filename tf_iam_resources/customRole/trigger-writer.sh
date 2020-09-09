#!/bin/bash

echo "running..."
echo $1, $2, $3

FUNCTION=$1
DATA=$2
REGION=$3

if [ "$FUNCTION" = "role_record_keeper" ]; then
  ACTION=$(echo "$DATA" | jq '.action')
  echo "$ACTION"

  if [ "$ACTION" = '"CREATE"' ]; then
    echo "Role being created... generating lock file"
    echo "TRUE">role.lock
  fi

  if [ "$ACTION" = '"UPDATE"' ]; then
    LOCK=$(cat role.lock)
    if [ "$LOCK" = "TRUE" ]; then
      echo "FALSE">role.lock
      echo "Role just created... unlocking and exiting - no CF call"
      exit 0
    fi
  fi

fi

gcloud functions call $FUNCTION --data '{"message": '"$DATA"'}' --region=$REGION | grep SUCCESS

if [ $? -eq 0 ]
then
  echo "CLOUD FUNCTION OK"
else
  echo "ERROR: $? - CLOUD FUNCTION FAILED - CHECK LOGS"
  exit 1
fi

echo DONE
exit 0

