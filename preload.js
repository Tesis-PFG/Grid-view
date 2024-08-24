const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('api', {
  requestImageData: () => ipcRenderer.send('request-image-data'),
  loadImageData: (callback) => ipcRenderer.on('load-image-data', (event, data) => callback(data)),
});
