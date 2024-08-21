# Pasos a seguir:

Una vez tenidos ya los archivos desde git clone:
- cd dicom-viewer
- npm install electron electron-builder --save-dev
- npm install electron concurrently wait-on --save-dev (instala las dependencias necesarias para poder correr electron y react de manera simultanea)

 ## cambios realizados al package.json:

"scripts": {
    "react-start": "react-scripts start",
    "electron-start": "wait-on http://localhost:3000 && electron .",
    "start": "concurrently \"npm run react-start\" \"npm run electron-start\"",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  }

Haciendo uso de concurrently y wait-on se añaden los scripts de start para la app de electron y de react
con concurrently se realiza el npm run react y el npm run electron. 
Teniendo en cuenta que esto se llevara a cabo al tiempo, y que se esperará respuesta del localhost:3000, la aplicacion de electron se abrira cuando react este lista para mostrarse.