const { app, BrowserWindow } = require('electron');
const path = require('path');

function createWindow() {
  const win = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),  // Carga el archivo preload.js
      nodeIntegration: false,  // Esto debe ser false cuando uses contextBridge
      contextIsolation: true,  // Asegura que el contexto esté aislado
    },
  });

  win.loadURL('http://localhost:3000');  // O el path a tu build de React
}

app.whenReady().then(createWindow);
