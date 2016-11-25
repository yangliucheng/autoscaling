#!/bin/bash

set -ex

###############################
#        CONSTANT             #
###############################

CURRENT_DIR=$(cd "$(dirname "$0")"; pwd)
HOME_DIR=${CURRENT_DIR}/..
CODE_DIR=${HOME_DIR}/src/Stardigi-Policy
BIN_DIR=${HOME_DIR}/bin
PACKAGE_DIR=${BIN_DIR}/autoscaling
export GOPATH=$HOME_DIR

###############################
#        FUNCTION             #
###############################
function pre_build() {

	if [ -d "${BIN_DIR}" ];then
		rm -rf ${BIN_DIR}
	fi
	mkdir -p -m 700 ${PACKAGE_DIR}
}

function build() {
	cd ${CODE_DIR}
	go build .
	cd -
}

function tar_package() {
	cd ${CODE_DIR}
	if [ -f "Stardigi-Policy" ];then
		cp Stardigi-Policy ${PACKAGE_DIR}
	fi
	if [ -d "conf/" ];then
	    cp -rf conf/ ${PACKAGE_DIR}
	fi
	cd -

	cd ${BIN_DIR}
	if [ -d "autoscaling/" ];then
	    tar -zcvf autoscaling.tgz autoscaling/
	fi
	cd -
}

function main() {
	pre_build
	build
	tar_package
}

###############################
#        EXECUTE              #
###############################
main
