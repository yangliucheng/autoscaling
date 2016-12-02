#!/bin/bash

PROGRAM=autoscaling
PAAS_DIR=/home/paas
RUN_DIR=${PAAS_DIR}/${PROGRAM}
PID_DIR=${RUN_DIR}/run
APP_NAME=Stardigi-Policy

function pre() {
    mkdir -p -m 700 ${PID_DIR}
}

function run() {
	cd ${RUN_DIR}
	kill=`ps | grep ${APP_NAME} | grep -v grep | awk '{print $1}' |xargs kill -9`
	nohup ./Stardigi-Policy &
	echo "$!" > ${PID_DIR}/autoscaling.pid
	cd -
}

function main() {
	pre
	run
}

main