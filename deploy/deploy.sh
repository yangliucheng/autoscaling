#!/bin/bash

set -ex

###############################
#        CONSTANT             #
###############################
IF_ENABLE_SYSTEMD=$1
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

function sytemd() {
	if ${IF_ENABLE_SYSTEMD};then
		return
	fi
		touch /etc/sytemd/stardigi.service
		cat >> /etc/sytemd/stardigi.service <<EOF
		[Unit]
		[Service]
		PIDFile=/home/paas/autoscaling/run/autoscaling.pid
		ExecStop=/home/paas/autoscaling/cmd/scli.sh start
		ExecStart=/home/paas/autoscaling/cmd/scli.sh stop
		[Install]
        WantedBy=multi-user.target
EOF	 

    systemctl enable stardigi.service
}

function main() {
	pre
	install_
	sytemd $1
}

###############################
#        FUNCTION             #
###############################
main