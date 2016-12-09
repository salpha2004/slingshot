#!/bin/bash

if [ -z "$RTEMS_MAKEFILE_PATH" ]; then
	echo "Please first run the script build-rtems.sh. Exitting..."
	exit 1
fi

TEST_CASE_LIST="sample.tcl"

cd slingshot

while true; do
	read -p "WARNING: Previous results of running Slingshot (if any) will be deleted from the database. Continue? (y/n) " yesNo
	case $yesNo in
		[Yy]* ) ./reinit-db.sh
				read -p "Test case list filename? [default: sample.tcl]" filename
				echo "Please wait while initializing the database for the test case. This takes quite a while..."
				if [ -z "$filename"]; then
					init_db -t $TEST_CASE_LIST
				else
					init_db -t $filename
				fi
				slingshot
				exit;;
		[Nn]* ) exit;;
		* ) echo "Please answer (y)es or (n)o."
	esac
done
