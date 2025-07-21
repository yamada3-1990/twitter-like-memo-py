import { useState } from 'react'
import './Listing.css'
import { addMemo } from '../api/api'

export const Listing = ({ onMemoAdded }) => {
    const initialState = {
        title: '',
        body: '',
        tags: '',
    };

    const [values, setValues] = useState(initialState);
    const onValueChange = (event) => {
        setValues({
            ...values,
            [event.target.name]: event.target.value,
        });
    };

    const listingMemo = async (event) => {
        try {
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