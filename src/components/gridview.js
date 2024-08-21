import React from 'react';

const GridView = ({ images }) => {
  const gridStyle = {
    display: 'grid',
    gridTemplateColumns: `repeat(${Math.min(images.length, 4)}, 1fr)`,
    gap: '10px',
    padding: '10px',
  };

  return (
    <div style={gridStyle}>
      {images.map((image, index) => (
        <img key={index} src={image} alt={`DICOM ${index}`} style={{ width: '100%' }} />
      ))}
    </div>
  );
};

export default GridView;
