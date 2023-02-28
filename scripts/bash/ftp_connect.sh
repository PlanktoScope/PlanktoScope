#!/bin/bash
SERVER_IP="plankton.obs-vlfr.fr"
USER="ftp_plankton"
PASSWD="Pl@nkt0n4Ecotaxa"
FTP=/usr/bin/ftp
PATH=/home/pi/data/export/ecotaxa
FILE=$1

cd $PATH
$FTP -n $SERVER_IP << EOF
quote USER $USER
quote PASS $PASSWD

passive
cd Ecotaxa_Data_to_import/Lacoscope/Test
put $FILE
EOF
