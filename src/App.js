import React, { useState } from 'react';
import GridView from './components/gridview';
import './App.css';

function App() {
  const [viewCount, setViewCount] = useState(4);
  const [images, setImages] = useState([
    'path/to/dicom1.png',
    'path/to/dicom2.png',
    'path/to/dicom3.png',
    'path/to/dicom4.png' 
  ]);

  const handleViewChange = (count) => {
    setViewCount(count);
  };

  const displayedImages = images.slice(0, viewCount);

  return (
    <div className="App">
      <div className="button-group">
        <button onClick={() => handleViewChange(1)}>1 View</button>
        <button onClick={() => handleViewChange(2)}>2 Views</button>
        <button onClick={() => handleViewChange(3)}>3 Views</button>
        <button onClick={() => handleViewChange(4)}>4 Views</button>
      </div>
      <GridView images={displayedImages} />
    </div>
  );
}

export default App;
