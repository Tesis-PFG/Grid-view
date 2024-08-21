import React from 'react';
import './GridView.css'; // Importa el archivo CSS

const GridView = ({ images }) => {
  return (
    <div className="grid-container">
      {images.map((image, index) => (
        <img key={index} src={image} alt={`DICOM ${index}`} className="grid-item" />
      ))}
    </div>
  );
};

export default GridView;
