import { useEffect, useState } from 'react'
import './MemoList.css'
import { getAllMemos, Memo } from '../api/api'

export const MemoList = (props) => {
    const [memos, setMemos] = useState([]);
    const reload = props.reload;

    const getAllMemosList = async () => {
        try {
            const data = await getAllMemos();
            console.debug('GET all memos success:', data);
            setMemos(data.memos || []);
        } catch (error) {
            console.error('GET all memos error:', error);
            setMemos([]);
        }
    };

    useEffect(() => {
        getAllMemosList();
    }, [reload]);

    return (
        <>
        {memos.map((memo) => (
            <div className='memo-content'>
                <h2>{memo.title}</h2>
                {memo.body}
                {memo.tags}
            </div>
        ))}
        </>
    );
};

// function MemoList() {
//     return (
//         <>
//             <h1>Hello</h1>
//         </>
//     )
// }

export default MemoList