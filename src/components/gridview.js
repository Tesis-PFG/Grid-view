import React from 'react';
import './GridView.css';

const GridView = ({ images }) => {
  return (
    <div className="grid-container">
  {images.map((image, index) => (
    <div key={index} className="grid-item">
      <div className="image-container">
        <img src={image} alt={`View ${index}`} />
      </div>
      <div className="button-group">
        <button className="Decrease">Decrease</button>
        <button className="Play">Play</button>
        <button className="Increase">Increase</button>
      </div>
    </div>
  ))}
</div>

  );
};

export default GridView;
