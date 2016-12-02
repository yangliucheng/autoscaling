#!/bin/bash

set -ex

###############################
#        CONSTANT             #
###############################
PROGRAM=autoscaling
CURRENT_DIR=$(cd "$(dirname "$0")"; pwd)
PAAS_DIR=/home/paas
PACKAGE_TO=${PAAS_DIR}/packages
RUN_DIR=${PAAS_DIR}/${PROGRAM}

###############################
#        FUNCTION             #
###############################

function pre() {

	if [ -f "${RUN_DIR}" ];then
		rm -rf ${RUN_DIR}
	fi
	mkdir -p -m 700 ${RUN_DIR}
	mkdir -p -m 700 ${PACKAGE_TO}

	cp ${CURRENT_DIR}/autoscaling.tgz ${PACKAGE_TO}
}

function install_() {

	cd ${PACKAGE_TO}
	tar -xvzf autoscaling.tgz -C ${PAAS_DIR}
	cp ${CURRENT_DIR}/stardigi_policy.json ${RUN_DIR}/conf
	cd -
}

function main() {
	pre
	install_
}

###############################
#        FUNCTION             #
###############################
main