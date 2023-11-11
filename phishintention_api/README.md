
## API URL
LOCALHOST:8030
## END POINT
| Description | Endpoint | Param | Request Methods |
| --- | --- | --- | --- |
| Check Server Health | / | | [GET] |
| Run PhishIntention Service | /phishintention-queue/<string:folder>  | folder | [POST]  | 

## Steps to build PhishIntention Service
```
docker-compose up --build -d
```
This will build 1 instance of PhishIntention Service