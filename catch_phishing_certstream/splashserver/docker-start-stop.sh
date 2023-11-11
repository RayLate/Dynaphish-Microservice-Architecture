while true; do
	sleep 5
	echo "Starting docker service"
	timeout -s SIGINT 180 docker-compose restart
	echo "waiting for 180s"
	sleep 180
	echo "180s is up"
	docker restart phishing-splashserver-splash0-1
	docker restart phishing-splashserver-splash1-1
	docker restart phishing-splashserver-splash2-1
	docker restart phishing-splashserver-splash3-1
	docker restart phishing-splashserver-splash4-1
	echo "restarting docker images"
done
