import { useState } from 'react'
import './Listing.css'
import { addMemo } from '../api/api'

// Listingコンポーネントで新しいメモが追加されたら、MemoListコンポーネントにも反映させる必要がある
// App.jsxがListingとMemoListの親コンポーネントだから、App.jsxを介して更新する
// Listing->Appに"メモが追加された"通知する、Appがそれを受けてMemoListの再レンダリングをトリガーする
// App内でonMemoAdded={handleMemoAdded} handleMemoAdded関数がonMemoAddedという名前で渡される
// onMemoAddedはAppに通知するためのコールバック関数(合図を送る)
// onMemoAddedはListing.jsx内でわかりやすくするために名前を付けられた関数
export const Listing = ({ onMemoAdded }) => {
    const initialState = {
        title: '',
        body: '',
        tags: '',
    };

    // value: 現在の値
    // setValues: valueを更新するための関数
    const [values, setValues] = useState(initialState);
    // onValueChange: 入力フィールドの値が変更されたときに呼び出されるイベントハンドラ
    const onValueChange = (event) => {
        setValues({
            // 現在の状態をコピーする
            ...values,
            [event.target.name]: event.target.value,
        });
    };

    const listingMemo = async (event) => {
        try {
            // イベントのデフォルトの動作をキャンセルできる(formだったら送信時にページがリロードされたりするやつ)
            // リロードを防いでaddMemoを実行している
            event.preventDefault();
            await addMemo(values);
            alert('メモを追加しました');
            onMemoAdded();
        } catch (error) {
            console.error('POST memo error:', error);
        }
    }

    return (
        <>
            <form onSubmit={listingMemo}>
                <div className='add-memo'>
                    <input
                        className='input-title'
                        name='title'
                        type='text'
                        onChange={onValueChange}
                        value={values.title}
                        placeholder='title'
                    />
                    <input
                        className='input-body'
                        name='body'
                        type='text'
                        onChange={onValueChange}
                        value={values.body}
                        placeholder='body'
                    />
                    <input
                        className='input-tags'
                        name='tags'
                        type='text'
                        onChange={onValueChange}
                        value={values.tags}
                        placeholder='tags'
                    />
                </div>
                <button className='post-button' type="submit">メモを追加</button>
            </form>
        
        </>
    );
};

export default Listing