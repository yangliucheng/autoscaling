#!/bin/bash

set -ex

###############################
#        CONSTANT             #
###############################
VERSION_NAME=$1
CURRENT_DIR=$(cd "$(dirname "$0")"; pwd)
HOME_DIR=${CURRENT_DIR}/..
CODE_DIR=${HOME_DIR}/src/Stardigi-Policy
BIN_DIR=${HOME_DIR}/bin
PACKAGE_DIR=${BIN_DIR}/autoscaling
VERSION=${BIN_DIR}/${VERSION_NAME}-v1.1
export GOPATH=$HOME_DIR

###############################
#        FUNCTION             #
###############################
function pre_build() {

	if [ -d "${BIN_DIR}" ];then
		rm -rf ${BIN_DIR}
	fi
	mkdir -p -m 700 ${PACKAGE_DIR}
	mkdir -p -m 700 ${VERSION}
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
	    cp conf/stardigi_policy.json ${VERSION}
	fi
	cd -
	cd ${BIN_DIR}
	if [ -d "autoscaling/" ];then
	    tar -zcvf autoscaling.tgz autoscaling/
	fi
	cd -
}

function package() {
	cd ${HOME_DIR}/deploy
	cp deploy.sh ${VERSION}
	cd -
	cd ${BIN_DIR}
	cp  autoscaling.tgz ${VERSION}
	tar -zcvf ${VERSION}.tgz ${VERSION}
	cd -
}

function main() {
	pre_build
	build
	tar_package
	package
}

###############################
#        EXECUTE              #
###############################
main
