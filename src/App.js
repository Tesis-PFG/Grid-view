import React, { useState } from 'react';
import GridView from './components/gridview';

function App() {
  const [viewCount, setViewCount] = useState(4); //El valor que esté dentro del useState es la cantidad 
  // de vistas por defecto de la aplicación
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
      <header style={{ padding: '10px', backgroundColor: '#333', color: '#fff' }}>
        <button onClick={() => handleViewChange(1)}>1 View</button>
        <button onClick={() => handleViewChange(2)}>2 Views</button>
        <button onClick={() => handleViewChange(3)}>3 Views</button>
        <button onClick={() => handleViewChange(4)}>4 views</button>
      </header>
      <GridView images={displayedImages} />
    </div>
  );
}

export default App;
