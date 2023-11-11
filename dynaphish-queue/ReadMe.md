## API URL
LOCALHOST:8000
## END POINT
| Description | Endpoint | Param | Request Methods |
| --- | --- | --- | --- |
| Check Queue Server Health | / | | [GET] |
| And Requests to queue | /<string:queue>/<string:folder> | queue, folder | [POST] | 

## Steps to setup Dynaphish Queue server
```
cd ./app 
docker build -t dynaphish_queue .
cd ..
docker-compose up --build -d
```