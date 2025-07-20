import { useState } from 'react'
import './App.css'
import { MemoList } from './MemoList';

function App() {
  const [reload, setReload] = useState(false);
  
  // setReload(prev => !prev);

  return (
    <>
      <div>
        <MemoList reload={reload} />
      </div>
    </>
  )
}

export default App
