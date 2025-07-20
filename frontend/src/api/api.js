const BACKEND_URL = 'http://127.0.0.1:9000';

export function Memo(id, title, body, tags) {
    this.id = id;
    this.title = title;
    this.body = body;
    this.tags = tags;
};

// export const MemoListResponse = {
//     memos: Memo
// };

export const getAllMemos = async () => {
    const res = await fetch(`${BACKEND_URL}/memos`, {
        method: 'GET',
        mode: 'cors',
        headers: {
            'Content-Type': 'application/json',
            Accept: 'application/json',
        },
    });
    //TODO: エラーハンドリング追加する
    if (res.status >= 400) {
        const error = await res.json();
        throw new Error(`Failed to fetch memos from the server: ${JSON.stringify(error)}`);
    }
    return res.json();
}