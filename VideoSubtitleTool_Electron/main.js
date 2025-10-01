const { app, BrowserWindow, ipcMain, dialog, shell } = require('electron');
const path = require('path');
const { spawn, exec } = require('child_process');
const fs = require('fs');

class VideoSubtitleApp {
    constructor() {
        this.mainWindow = null;
        this.pythonProcess = null;
        this.serverPort = 8000;
        this.isDev = process.argv.includes('--dev');
        this.isPortable = this.detectPortableMode();
        this.appPath = this.getAppPath();
    }

    detectPortableMode() {
        // Check if running in portable mode
        return process.env.PORTABLE_MODE === '1' || 
               fs.existsSync(path.join(process.cwd(), 'START_PORTABLE.bat')) ||
               fs.existsSync(path.join(path.dirname(process.execPath), 'START_PORTABLE.bat'));
    }

    getAppPath() {
        if (this.isPortable) {
            // In portable mode, use the directory where the exe is located
            return path.dirname(process.execPath);
        } else {
            // In development mode, use the current directory
            return __dirname;
        }
    }

    createWindow() {
        // Create the browser window with modern styling
        this.mainWindow = new BrowserWindow({
            width: 1200,
            height: 800,
            minWidth: 900,
            minHeight: 700,
            webPreferences: {
                nodeIntegration: true,
                contextIsolation: false,
                enableRemoteModule: true
            },
            titleBarStyle: 'default',
            frame: true,
            show: false, // Don't show until ready
            backgroundColor: '#ffffff',
            icon: path.join(__dirname, 'assets', 'icon.png') // Add icon if available
        });

        // Load the app
        this.mainWindow.loadFile(path.join(__dirname, 'renderer', 'index.html'));

        // Show window when ready
        this.mainWindow.once('ready-to-show', () => {
            this.mainWindow.show();
            
            // Focus on the window
            if (this.isDev) {
                this.mainWindow.webContents.openDevTools();
            }
        });

        // Handle window closed
        this.mainWindow.on('closed', () => {
            this.mainWindow = null;
            this.cleanup();
        });

        // Start Python backend
        this.startPythonBackend();
    }

    async startPythonBackend() {
        console.log(`Starting Python backend... (Portable: ${this.isPortable})`);
        
        try {
            let backendPath, pythonScript, pythonCmd;
            
            if (this.isPortable) {
                // Portable mode - use resources from the app bundle
                backendPath = path.join(process.resourcesPath, 'backend');
                pythonScript = path.join(backendPath, 'api_server.py');
                
                // In portable mode, we'll embed a Python interpreter or use system Python
                pythonCmd = 'python'; // Assume Python is in PATH or bundled
                
                console.log(`Portable backend path: ${backendPath}`);
            } else {
                // Development mode
                backendPath = path.join(__dirname, 'backend');
                pythonScript = path.join(backendPath, 'api_server.py');
                pythonCmd = 'python';
            }
            
            // Verify backend files exist
            if (!fs.existsSync(pythonScript)) {
                throw new Error(`Backend script not found: ${pythonScript}`);
            }
            
            // Start the FastAPI server
            const env = { 
                ...process.env,
                PORTABLE_MODE: this.isPortable ? '1' : '0',
                APP_PATH: this.appPath
            };
            
            this.pythonProcess = spawn(pythonCmd, [pythonScript], {
                cwd: backendPath,
                stdio: ['pipe', 'pipe', 'pipe'],
                env: env
            });

            this.pythonProcess.stdout.on('data', (data) => {
                console.log(`Backend: ${data.toString()}`);
            });

            this.pythonProcess.stderr.on('data', (data) => {
                const errorMsg = data.toString();
                console.error(`Backend Error: ${errorMsg}`);
                
                // Send error to renderer for user feedback
                if (errorMsg.includes('ModuleNotFoundError') || errorMsg.includes('ImportError')) {
                    this.sendToRenderer('backend-status', { 
                        status: 'error', 
                        error: 'Python dependencies missing. Please install requirements.txt' 
                    });
                }
            });

            this.pythonProcess.on('close', (code) => {
                console.log(`Backend process exited with code ${code}`);
                if (code !== 0) {
                    this.sendToRenderer('backend-status', { 
                        status: 'error', 
                        error: `Backend crashed with exit code ${code}` 
                    });
                }
            });

            // Wait for server to start and test connection
            setTimeout(async () => {
                try {
                    // Test backend connection using IPv4 address explicitly
                    const response = await fetch(`http://127.0.0.1:${this.serverPort}/health`);
                    if (response.ok) {
                        console.log('Backend health check passed');
                        this.sendToRenderer('backend-status', { status: 'ready', port: this.serverPort });
                    } else {
                        throw new Error('Backend health check failed');
                    }
                } catch (error) {
                    console.error('Backend connection test failed:', error);
                    this.sendToRenderer('backend-status', { 
                        status: 'error', 
                        error: 'Failed to connect to backend server' 
                    });
                }
            }, 5000); // Give more time for startup

        } catch (error) {
            console.error('Failed to start Python backend:', error);
            this.sendToRenderer('backend-status', { status: 'error', error: error.message });
        }
    }

    sendToRenderer(channel, data) {
        if (this.mainWindow && this.mainWindow.webContents) {
            this.mainWindow.webContents.send(channel, data);
        }
    }

    cleanup() {
        if (this.pythonProcess) {
            console.log('Terminating Python backend...');
            this.pythonProcess.kill();
            this.pythonProcess = null;
        }
    }
}

// Create app instance
const videoApp = new VideoSubtitleApp();

// App event handlers
app.whenReady().then(() => {
    videoApp.createWindow();

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            videoApp.createWindow();
        }
    });
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('before-quit', () => {
    videoApp.cleanup();
});

// IPC Handlers for file operations
ipcMain.handle('select-videos', async () => {
    const result = await dialog.showOpenDialog(videoApp.mainWindow, {
        title: 'Select Video Files',
        properties: ['openFile', 'multiSelections'],
        filters: [
            { name: 'Video Files', extensions: ['mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'webm', 'm4v'] },
            { name: 'All Files', extensions: ['*'] }
        ]
    });

    return result;
});

ipcMain.handle('select-workspace', async () => {
    const result = await dialog.showOpenDialog(videoApp.mainWindow, {
        title: 'Select Workspace Folder',
        properties: ['openDirectory', 'createDirectory']
    });

    return result;
});

ipcMain.handle('open-folder', async (event, folderPath) => {
    try {
        await shell.openPath(folderPath);
        return { success: true };
    } catch (error) {
        return { success: false, error: error.message };
    }
});

ipcMain.handle('check-python', async () => {
    return new Promise((resolve) => {
        exec('python --version', (error, stdout, stderr) => {
            if (error) {
                resolve({ available: false, error: error.message });
            } else {
                resolve({ available: true, version: stdout.trim() });
            }
        });
    });
});

console.log('Electron main process started');
console.log('App path:', app.getAppPath());
console.log('User data:', app.getPath('userData'));