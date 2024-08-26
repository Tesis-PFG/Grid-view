import React from 'react';
import './DataBaseScreen.css'; // Importa el archivo CSS

import logo_filtro from '../Assets/filter_5A639C.png'

const DataBaseScreen = ({ images }) => {
  return (
    <div className="baseDBScreen">
        <div className="caja_superior">

            <div className="contenedor_filtro">
                <img
                    src={logo_filtro}
                    className='icono_filtro'
                />
            </div>

            <div className="contenedor_titulo">
                <h1 className="titulo">Base de Datos</h1>
            </div>

        </div>
        <div className="caja_inferior">
        
        </div>
    </div>
  );
};

export default DataBaseScreen;