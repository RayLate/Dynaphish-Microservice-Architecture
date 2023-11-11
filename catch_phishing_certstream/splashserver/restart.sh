#!/bin/sh
while true
do
	sudo service docker restart
	sleep 1
	sudo timeout -s SIGINT 120 docker-compose up
	sleep 1
done
	

