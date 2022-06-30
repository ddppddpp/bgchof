###Flask API###

A **[Flask](https://flask.palletsprojects.com) based API** can be launched by invokig api.py from the CLI
```
% python api/api.py
```
Then a request can be sent i.e.
```
http://127.0.0.1:5000/api/v1/msgForDate?date=2021-12-11
```
**Docker container**
Use the following command to build a docker container and run it on your local system:
```
docker run --publish 5000:5000 python-docker
```