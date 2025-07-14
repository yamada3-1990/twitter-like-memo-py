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
$ Invoke-RestMethod -Method POST -Uri 'http://127.0.0.1:9000/memos' -ContentType 'application/x-www-form-urlencoded' -Body 'title=jacket&body=testbody'
```
