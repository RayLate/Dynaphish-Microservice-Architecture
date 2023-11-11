## API URL
LOCALHOST:8010
## END POINT
| Description | Endpoint | Param | Request Methods |
| --- | --- | --- | --- |
| Check Server Health | / | | [GET] |
| Run Logo Detection Service | /has-logo-queue/<string:folder> | folder | [GET, POST]  | 

## Steps to build app
```
docker-compose up --build -d --scale app=3
```