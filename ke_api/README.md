## API URL
LOCALHOST:8020
## END POINT
| Description | Endpoint | Param | Request Methods |
| --- | --- | --- | --- |
| Check Server Health | / | | [GET] |
| Run Brand Knowledge Expansion Service | /knowledge-expansion-queue/<string:folder> | folder | [POST]  | 

## Steps to build app
```
docker-compose up --build -d --scale app=3
```