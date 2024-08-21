import React, { useState } from 'react';
import GridView from './components/gridview';
import './App.css';

// Importa las imágenes
import defaultImage from './Assets/add-file.png';

function App() {
  const [viewCount, setViewCount] = useState(4);
  const [images, setImages] = useState([
    defaultImage,
    defaultImage,
    defaultImage,
    defaultImage 
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
