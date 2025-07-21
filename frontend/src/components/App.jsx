import { useState } from 'react'
import './App.css'
import { MemoList } from './MemoList';
import { Listing } from './Listing';

function App() {
  const [reload, setReload] = useState(false);

  const handleMemoAdded = () => {
    setReload(prev => !prev);
  };

  return (
    <>
      <div>
        <Listing onMemoAdded={handleMemoAdded} />
      </div>
      <div>
        <MemoList reload={reload} />
      </div>
    </>
  )
}

export default App
