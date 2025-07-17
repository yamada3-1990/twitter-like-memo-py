最初に
```
$ python3 -m venv .venv
$ .venv/Scripts/activate
$ pip install --upgrade pip setuptools wheel
$ pip install -r requirements.txt
```

backendの実行
```
$ cd backend
$ uvicorn main:app --reload --port 9000
```

APIのテスト
```
$ Invoke-RestMethod -Method GET -Uri 'http://127.0.0.1:9000'
$ Invoke-RestMethod -Method GET -Uri 'http://127.0.0.1:9000/memos'
$ Invoke-RestMethod -Method POST -Uri 'http://127.0.0.1:9000/memos' -ContentType 'application/x-www-form-urlencoded' -Body 'title=test title&body=test body'
$ Invoke-RestMethod -Method POST -Uri 'http://127.0.0.1:9000/memos' -ContentType 'application/x-www-form-urlencoded' -Body 'title=test title&body=test body&tags=greeting,test'
$ Invoke-RestMethod -Method GET -Uri 'http://127.0.0.1:9000/memos' -ContentType 'application/x-www-form-urlencoded' -Body 'title=test title&body=test body&tags=greeting,test'
$ Invoke-RestMethod -Method GET -Uri 'http://127.0.0.1:9000/search/keyword?keyword=test'
$ Invoke-RestMethod -Method GET -Uri 'http://127.0.0.1:9000/search/tags?tags=greeting,test'
```
