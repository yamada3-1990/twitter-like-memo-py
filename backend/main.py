import os
import logging
import pathlib
from fastapi import FastAPI, Form, HTTPException, Depends
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
from pydantic import BaseModel
from contextlib import asynccontextmanager
from dataclasses import dataclass

# FastAPIアプリケーションの初期化
app = FastAPI()

# この形式のクラスはPydanticのデータモデル形式
# pydanticによってレスポンスとかリクエストボディの構造を定義、バリデーションが楽に
class Memo(BaseModel):
    title: str
    body: str

class AddMemoResponse(BaseModel):
    message: str

# MARK: - get_db()
db = pathlib.Path(__file__).parent.resolve() / "db" / "memos.sqlite3"
def get_db():
    if not db.exists():
        yield

    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    try:
        yield conn
    finally:
        conn.close()

@app.get("/")
def hello():
    return {"message": "Hello, world!"}

# MARK: - get_all_memos()
@app.get("/memos")
def get_all_memos():
    pass
    
# MARK: - add_memo()
@app.post("/memos", response_model=AddMemoResponse)
def add_memo(
    # 引数 Form(...)はこの引数が必須であることを意味する
    title: str = Form(...),
    body: str = Form(...),
    db: sqlite3.Connection = Depends(get_db),
):
    if not title:
        raise HTTPException(status_code=400, detail="title is required")
    if not body:
        raise HTTPException(status_code=400, detail="body is required")
    insert_memo(db, Memo(title=title, body=body))
    return AddMemoResponse(**{"message": f"item received: {title}"})


# MARK: - insert_memo()
# メモをデータベースに格納するための関数
# add_memo()内で引数としてdbコネクションを作って、それをそのままinsert_memoに渡しているので接続が引き継がれる
def insert_memo(db: sqlite3.Connection, memo: Memo):
    cursor = db.cursor()
    cursor.execute("INSERT INTO memos (title, body) VALUES (?, ?)", (memo.title, memo.body))
    db.commit()