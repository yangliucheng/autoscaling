#!/bin/bash

APP_NAME=$1

function stop() {

	if [  -z "${APP_NAME}" ];then
       APP_NAME='Stardigi-Policy'
    fi

	kill=`ps | grep ${APP_NAME} | grep -v grep | awk '{print $1}' |xargs kill -9`
	rm /home/paas/autoscaling/run/autoscaling.pid
}

function main() {
	stop
}

main