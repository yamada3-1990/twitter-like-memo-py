import os
import logging
import sys
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

# ロギング設定
logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)

# この形式のクラスはPydanticのデータモデル形式
# pydanticによってレスポンスとかリクエストボディの構造を定義、バリデーションが楽に
class Memo(BaseModel):
    title: str
    body: str

class AddMemoResponse(BaseModel):
    message: str

# MARK: - get_db()
db = pathlib.Path(__file__).parent.parent.resolve() / "db" / "memos.sqlite3"
def get_db():
    logger.debug(f"Checking if database exists: {db.exists()}")
    if not db.exists():
        logger.info(f"Database file not found at {db}. Attempting to create and initialize.")
        try:
            conn = sqlite3.connect(db)
            cursor = conn.cursor()
            schema_path = pathlib.Path(__file__).parent.parent.resolve() / "db" / "schema.sql"
            logger.debug(f"Schema path: {schema_path}")
            with open(schema_path, 'r', encoding='utf-8') as f:
                sql_script = f.read()
            cursor.executescript(sql_script)
            conn.commit()
            conn.close()
            logger.info("Database created and schema initialized successfully.")
        except sqlite3.Error as e:
            logger.error(f"Database creation/initialization error: {e}")
            raise HTTPException(status_code=500, detail=f"Database initialization error: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred during database initialization: {e}")
            raise HTTPException(status_code=500, detail=f"Unexpected database initialization error: {e}")

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
    logger.debug(f"Received memo: title='{title}', body='{body}'")
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
    try:
        cursor = db.cursor()
        cursor.execute("INSERT INTO memos (title, body) VALUES (?, ?)", (memo.title, memo.body))
        db.commit()
        logger.debug(f"Memo inserted successfully: title='{memo.title}'")
    except sqlite3.Error as e:
        logger.error(f"Database error during insert_memo: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during insert_memo: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")