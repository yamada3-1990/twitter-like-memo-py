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
    tags: str

class AddMemoResponse(BaseModel):
    message: str

class DeleteMemoResponse(BaseModel):
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

# MARK: - GET /memos
@app.get("/memos")
def get_all_memos():
    pass
    
# MARK: - POST /memos
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
    Add_memo(db, Memo(title=title, body=body))
    return AddMemoResponse(**{"message": f"memo received: {title}"})

# MARK: - DELETE /memos/{id}
@app.delete("/memos/{id}")
def delete_memo(memo: Memo):
    Delete_memo(db, memo)
    return DeleteMemoResponse(**{"message": f"memo deleted: {memo.title}"})

# MARK: - GET /search/keyword
@app.get("/search/{keyword}")
def search_memo_by_keyword():
    pass


# MARK: - GET /search/tags
@app.get("/search/{tags}")





# MARK: - Add_memo()
# メモをデータベースに格納するための関数
# add_memo()内で引数としてdbコネクションを作って、それをそのままinsert_memoに渡しているので接続が引き継がれる
def Add_memo(db: sqlite3.Connection, memo: Memo):
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

# MARK: - Delete_memo()    
def Delete_memo(db: sqlite3.Connection, memo: Memo):
    try:
        cursor = db.cursor()
        cursor.execute("DELETE FROM memo_tags WHERE memo_id = ?", memo.id)
        cursor.execute("DELETE FROM memos WHERE id = ?", memo.id)
        db.commit()
        logger.debug(f"Memo inserted successfully: title='{memo.title}'")
    except sqlite3.Error as e:
        logger.error(f"Database error during insert_memo: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during insert_memo: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
    
# MARK: - Search_memo_by_keyword()   
def Search_memo_by_keyword(db: sqlite3.Connection, keyword: str):
    query = """
                SELECT
					memos.id,
					memos.title,
					memos.body,
					GROUP_CONCAT(tags.name) AS tags
				FROM
					memos
				LEFT JOIN
					memo_tags ON memos.id = memo_tags.memo_id
				LEFT JOIN
					tags ON memo_tags.tag_id = tags.id
				WHERE
					memos.title LIKE '%' || ? || '%' OR memos.body LIKE '%' || ? || '%'
				GROUP BY
					memos.id;
            """
    # memos = Memo[]
    try:
        cursor = db.cursor()
        cursor.execute(query, keyword, keyword)
        memos = cursor.fetchall()
        db.commit()
        logger.debug(f"{len(memos)} memos hit")
        return memos
    except sqlite3.Error as e:
        logger.error(f"Database error during insert_memo: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during insert_memo: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

# MARK: - Search_memo_by_tags()   
def Search_memo_by_tags(db: sqlite3.Connection, tags: str):
    pass

