import React, { useState } from 'react';
import GridView from './components/gridview';
import './App.css';

// Importa las imágenes
import defaultImage from './Assets/add-file.png';
import MainMenu from './components/mainMenu';

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
      <MainMenu></MainMenu>

    </div>
  );
}

export default App;
