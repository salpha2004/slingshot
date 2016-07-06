#!/bin/bash
mysql -u slingshot --password=slingshot -e "drop database if exists slingshot;"
mysql -u slingshot --password=slingshot -e "create database slingshot character set utf8;"
mysql -u slingshot --password=slingshot slingshot < ./slingshot/db/init_db_mysql.sql
echo "Done initializing slingshot database."
