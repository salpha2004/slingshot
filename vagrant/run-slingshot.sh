#!/bin/bash

TEST_CASE_LIST="sample.tcl"

cd slingshot

while true; do
	read -p "WARNING: Previous results of running slingshot (if any) will be deleted. Continue? " yesNo
	case $yesNo in
		[Yy]* ) ./reinit-db.sh
				read -p "Test case list filename? [default: sample.tcl]" filename
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