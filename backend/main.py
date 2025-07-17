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
    tags: str = "" # tagsをオプションにするか、Formで受け取る

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
def get_all_memos(db: sqlite3.Connection = Depends(get_db)):
    return Get_all_memos(db)


# MARK: - POST /memos
@app.post("/memos", response_model=AddMemoResponse)
def add_memo(
    # 引数 Form(...)はこの引数が必須であることを意味する
    title: str = Form(...),
    body: str = Form(...),
    tags: str = Form(""), # tagsをFormで受け取る
    db: sqlite3.Connection = Depends(get_db),
):
    logger.debug(f"Received memo: title='{title}', body='{body}'")
    if not title:
        raise HTTPException(status_code=400, detail="title is required")
    if not body:
        raise HTTPException(status_code=400, detail="body is required")
    Add_memo(db, Memo(title=title, body=body, tags=tags))
    return AddMemoResponse(**{"message": f"memo received: {title}"})

# MARK: - DELETE /memos/{id}
@app.delete("/memos/{id}")
def delete_memo(memo: Memo):
    Delete_memo(db, memo)
    return DeleteMemoResponse(**{"message": f"memo deleted: {memo.title}"})

# MARK: - GET /search/keyword
@app.get("/search/keyword")
def search_memo_by_keyword(keyword: str, db: sqlite3.Connection = Depends(get_db)):
    memos = Search_memo_by_keyword(db, keyword=keyword)
    return memos


# MARK: - GET /search/tags
@app.get("/search/tags")
def search_memo_by_tags(tags: str, db: sqlite3.Connection = Depends(get_db)):
    memos = Search_memo_by_tags(db, tags=tags)
    return memos

####################################################


# MARK: - Get_all_memos()
def Get_all_memos(db: sqlite3.Connection):
    try:
        cursor = db.cursor()
        cursor.execute("""
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
            GROUP BY
                memos.id
        """)
        memos = cursor.fetchall()
        logger.debug(f"Retrieved {len(memos)} memos from database.")
        return [dict(memo) for memo in memos]
    except sqlite3.Error as e:
        logger.error(f"Database error during Get_all_memos: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during Get_all_memos: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
    


# MARK: - Add_memo()
# メモをデータベースに格納するための関数
# add_memo()内で引数としてdbコネクションを作って、それをそのままinsert_memoに渡しているので接続が引き継がれる
def Add_memo(db: sqlite3.Connection, memo: Memo):
    try:
        cursor = db.cursor()
        cursor.execute("INSERT INTO memos (title, body) VALUES (?, ?)", (memo.title, memo.body))
        memo_id = cursor.lastrowid # 挿入されたメモのIDを取得

        if memo.tags:
            tag_list = [tag.strip() for tag in memo.tags.split(',') if tag.strip()]
            for tag_name in tag_list:
                # タグが存在するか確認し、存在しない場合は挿入
                cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
                tag_row = cursor.fetchone()
                if tag_row:
                    tag_id = tag_row[0]
                else:
                    cursor.execute("INSERT INTO tags (name) VALUES (?)", (tag_name,))
                    tag_id = cursor.lastrowid
                
                # memo_tags テーブルに挿入
                cursor.execute("INSERT INTO memo_tags (memo_id, tag_id) VALUES (?, ?)", (memo_id, tag_id))
        
        db.commit()
        logger.debug(f"Memo inserted successfully: title='{memo.title}', tags='{memo.tags}'")
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
        cursor.execute(query, (keyword, keyword))
        memos = cursor.fetchall()
        logger.debug(f"{len(memos)} memos hit")
        return [dict(memo) for memo in memos]
    except sqlite3.Error as e:
        logger.error(f"Database error during insert_memo: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during insert_memo: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

# MARK: - Search_memo_by_tags()   
def Search_memo_by_tags(db: sqlite3.Connection, tags: str):
    tag_list = tags.split(',')
    subqueries = []
    args = []
    for tag in tag_list:
        subqueries.append("""
                        EXISTS (
                                SELECT 1 FROM memo_tags mt
                                JOIN tags t ON mt.tag_id = t.id
                                WHERE mt.memo_id = memos.id AND t.name = ?
                                )
                        """)
        args.append(tag)
        
    query = """
                SELECT DISTINCT
                    memos.id,
                    memos.title,
                    memos.body,
                    GROUP_CONCAT(DISTINCT tags.name) AS tags
                FROM
                    memos
                LEFT JOIN
                    memo_tags ON memos.id = memo_tags.memo_id
                LEFT JOIN
                    tags ON memo_tags.tag_id = tags.id
                WHERE
                    """ + " AND ".join(subqueries) + """
                GROUP BY
                    memos.id, memos.title, memos.body;
            """
    try:
        cursor = db.cursor()
        cursor.execute(query, args)
        memos = cursor.fetchall()
        logger.debug(f"{len(memos)} memos hit")
        return [dict(memo) for memo in memos]
    except sqlite3.Error as e:
        logger.error(f"Database error during insert_memo: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during insert_memo: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
