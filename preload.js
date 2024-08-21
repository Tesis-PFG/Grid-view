const { contextBridge, ipcRenderer } = require('electron');

// archivo para realizar la comunicación entre el electron y el react en caso de ser necesario

contextBridge.exposeInMainWorld('electron', {
    sendMessage: (channel, data) => {
        ipcRenderer.send(channel, data);
    },
    receiveMessage: (channel, callback) => {
        ipcRenderer.on(channel, (event, ...args) => callback(...args));
    }
});
