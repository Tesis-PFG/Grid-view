import React, {useState} from 'react';
import './MainMenu.css'; // Importa el archivo CSS

import logoBaseDatos_Morada from '../Assets/database_purple.png'
import logoBaseDatos_Blanco from '../Assets/database_white.png'

import logoVisualizacion_Morada from '../Assets/display_purple.png'
import logoVisualizacion_Blanco from '../Assets/display_white.png'

import logoAñadirDicom_Morada from '../Assets/addDicom_purple.png'
import logoAñadirDicom_Blanco from '../Assets/addDicom_white.png'


const MainMenu = ({ onSelectOption }) => {
    const [selectedImage, setSelectedImage] = useState(2); // Imagen 2 es la seleccionada por defecto
  
    const handleClick = (option) => {
      setSelectedImage(option);
      onSelectOption(option);
    };

    return (
      <div className="mainBox">
        <div className="imageContainer">
          <img
            src={selectedImage  === 1 ? logoBaseDatos_Morada : logoBaseDatos_Blanco}
            alt="Image 1"
            className={`menuImage ${selectedImage  === 1 ? 'selected' : 'normal'}`}
            onClick={() => handleClick(1)}
          />
          <img
            src={selectedImage  === 2 ? logoVisualizacion_Morada : logoVisualizacion_Blanco}
            alt="Image 2"
            className={`menuImage ${selectedImage  === 2 ? 'selected' : 'normal'}`}
            onClick={() => handleClick(2)}
          />
          <img
            src={selectedImage  === 3 ? logoAñadirDicom_Morada : logoAñadirDicom_Blanco}
            alt="Image 3"
            className={`menuImage ${selectedImage  === 3 ? 'selected' : 'normal'}`}
            onClick={() => handleClick(3)}
          />
        </div>
      </div>
    );
  };

export default MainMenu;
