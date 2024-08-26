import React, { useState } from 'react';
import './App.css';

//Importa menú principal
import MainMenu from './components/mainMenu';
//Importa las diferentes pantallas principales
import AddDicomScreen from './components/addDicomScreen';
import DisplayScreen from './components/displayScreen';
import DataBaseScreen from './components/dataBaseScreen';


function App() {

  const [selectedScreen, setSelectedScreen] = useState(2); // Opción por defecto

  // Función para manejar la pantalla seleccionada
  const handleMenuSelection = (pantalla) => {
    setSelectedScreen(pantalla);
  };

  const renderContent = () => {
    switch (selectedScreen) {
      case 1:
        return <DataBaseScreen />;
      case 2:
        return <DisplayScreen />;
      case 3:
        return <AddDicomScreen />;
      default:
        return <div>Seleccione una opción del menú</div>;
    }
  };

  return (
    <div className="App">
      <div className="container">
        <div className='menuBox'>
          <MainMenu onSelectOption={handleMenuSelection} />
        </div>
        <div className="content">
          {renderContent()}
        </div>
      </div>
    </div>
  );

}

export default App;
