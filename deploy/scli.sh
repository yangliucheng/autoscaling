#!/bin/bash

CURRENT_DIR=$(cd "$(dirname "$0")"; pwd)

case $1 in
    stop)
        bash ${CURRENT_DIR}/stop.sh
    ;;
    start)
        bash ${CURRENT_DIR}/start.sh
    ;;
esac


