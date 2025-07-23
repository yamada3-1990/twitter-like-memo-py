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
    if (res.status >= 400) {
        const error = await res.json();
        throw new Error(`Failed to fetch memos from the server: ${JSON.stringify(error)}`);
    }
    return res.json();
}

export const addMemo = async (values) => {
    // FormDataオブジェクトを作成し、フォームの入力値をFormDataオブジェクトに追加していく
    // いろんなフォームデータを扱える便利な箱みたいなイメージ
    const formData = new FormData();
    formData.append('title', values.title);
    formData.append('body', values.body);
    formData.append('tags', values.tags);

    const res = await fetch(`${BACKEND_URL}/memos`, {
        method: 'POST',
        mode: 'cors',
        body: formData,
    });
    if (res.status >= 400) {
        const error = await res.json();
        throw new Error(`Failed to fetch memos from the server: ${JSON.stringify(error)}`);
    }
    return res
}

export const searchMemoByKeyword = async (keyword) => {
    const res = await fetch(`${BACKEND_URL}/search`, {
        method: 'GET',
        mode: 'cors',
        headers: {
            'Content-Type': 'application/json',
            Accept: 'application/json',
        },
    });
    if (res.status >= 400) {
        const error = await res.json();
        throw new Error(`Failed to fetch memos from the server: ${JSON.stringify(error)}`);
    }
    return res
}