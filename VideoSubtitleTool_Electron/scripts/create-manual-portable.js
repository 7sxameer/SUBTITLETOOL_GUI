const fs = require('fs');
const path = require('path');

/**
 * Manual Portable Creator
 * Creates a portable distribution without electron-builder
 */

console.log('🎬 Creating Manual Portable Distribution...\n');

const sourceDir = path.join(__dirname, '..');  // Parent directory (VideoSubtitleTool_Electron)
const portableDir = path.join(__dirname, '..', 'VideoSubtitleTool_Portable_Manual');

// Clean and create portable directory
if (fs.existsSync(portableDir)) {
    console.log('🧹 Cleaning existing portable directory...');
    fs.rmSync(portableDir, { recursive: true, force: true });
}

fs.mkdirSync(portableDir, { recursive: true });
console.log('📁 Created portable directory structure');

// Copy all application files
function copyRecursive(src, dest, exclude = []) {
    if (!fs.existsSync(src)) return;
    
    const stats = fs.statSync(src);
    
    if (stats.isDirectory()) {
        const basename = path.basename(src);
        if (exclude.includes(basename)) return;
        
        if (!fs.existsSync(dest)) {
            fs.mkdirSync(dest, { recursive: true });
        }
        
        const files = fs.readdirSync(src);
        for (const file of files) {
            copyRecursive(
                path.join(src, file),
                path.join(dest, file),
                exclude
            );
        }
    } else {
        fs.copyFileSync(src, dest);
    }
}

// Copy main application files
console.log('📦 Copying application files...');

const filesToCopy = [
    { src: 'main.js', dest: 'main.js' },
    { src: 'package.json', dest: 'package.json' },
    { src: 'renderer', dest: 'renderer' },
    { src: 'backend', dest: 'backend' },
    { src: 'portable/README_PORTABLE.md', dest: 'README_PORTABLE.md' }
];

for (const file of filesToCopy) {
    const srcPath = path.join(sourceDir, file.src);
    const destPath = path.join(portableDir, file.dest);
    
    if (fs.existsSync(srcPath)) {
        if (fs.statSync(srcPath).isDirectory()) {
            copyRecursive(srcPath, destPath, ['node_modules', '.git', 'dist-portable', 'scripts']);
        } else {
            fs.copyFileSync(srcPath, destPath);
        }
        console.log(`✅ Copied ${file.src}`);
    }
}

// Copy node_modules (only essential ones)
console.log('📚 Copying essential dependencies...');
const nodeModulesSource = path.join(sourceDir, 'node_modules');
const nodeModulesDest = path.join(portableDir, 'node_modules');

if (fs.existsSync(nodeModulesSource)) {
    const essentialModules = ['axios', 'electron'];
    
    for (const module of essentialModules) {
        const moduleSrc = path.join(nodeModulesSource, module);
        const moduleDest = path.join(nodeModulesDest, module);
        
        if (fs.existsSync(moduleSrc)) {
            copyRecursive(moduleSrc, moduleDest);
            console.log(`✅ Copied ${module}`);
        }
    }
}

// Create portable launcher script
console.log('🚀 Creating portable launcher...');

const launcherScript = `@echo off
title Video Subtitle Tool - Modern Portable Edition

echo.
echo 🎬 Video Subtitle Tool - Modern Portable Edition
echo ================================================
echo.
echo Starting application...
echo.

REM Set portable environment variables
set PORTABLE_MODE=1
set NODE_ENV=production

REM Get the directory where this batch file is located
set APP_DIR=%~dp0

REM Create workspace folder if it doesn't exist
if not exist "%APP_DIR%VideoSubtitleTool_Workspace" (
    mkdir "%APP_DIR%VideoSubtitleTool_Workspace"
    echo ✅ Created workspace folder
)

REM Check if Node.js is available
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is required but not found in PATH
    echo.
    echo Please install Node.js from: https://nodejs.org
    echo Or ensure Node.js is in your system PATH
    echo.
    pause
    exit /b 1
)

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is required but not found in PATH
    echo.
    echo Please install Python from: https://python.org
    echo Or ensure Python is in your system PATH
    echo.
    pause
    exit /b 1
)

REM Navigate to app directory and start
cd /d "%APP_DIR%"

REM Install dependencies if needed
if not exist "node_modules\\electron\\dist\\electron.exe" (
    echo 📦 Installing dependencies...
    npm install --production
)

echo 🎯 Starting Video Subtitle Tool...
echo.

REM Start the application
npm start

REM Handle any errors
if errorlevel 1 (
    echo.
    echo ❌ Application failed to start
    echo.
    echo Troubleshooting:
    echo - Ensure Python and Node.js are installed
    echo - Check that all dependencies are available
    echo - Try running as Administrator
    echo.
    pause
)
`;

fs.writeFileSync(path.join(portableDir, 'START_PORTABLE.bat'), launcherScript);
console.log('✅ Created START_PORTABLE.bat launcher');

// Create portable package.json
const portablePackageJson = {
    "name": "video-subtitle-tool-portable",
    "version": "2.0.0",
    "description": "AI-Powered Video Subtitle Generator - Portable Edition",
    "main": "main.js",
    "scripts": {
        "start": "electron ."
    },
    "dependencies": {
        "axios": "^1.5.0",
        "electron": "^27.0.0"
    },
    "portable": true
};

fs.writeFileSync(
    path.join(portableDir, 'package.json'), 
    JSON.stringify(portablePackageJson, null, 2)
);
console.log('✅ Created portable package.json');

// Create configuration file
const config = {
    "version": "2.0.0",
    "portable": true,
    "backend_port": 8000,
    "auto_workspace": true,
    "default_model": "small",
    "created": new Date().toISOString()
};

fs.writeFileSync(
    path.join(portableDir, 'tool_config.json'), 
    JSON.stringify(config, null, 2)
);
console.log('✅ Created tool_config.json');

// Create installation script
const installScript = `@echo off
title Installing Dependencies - Video Subtitle Tool

echo.
echo 🎬 Video Subtitle Tool - Installing Dependencies
echo ===============================================
echo.

REM Check for Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js not found! Please install Node.js first.
    echo Download from: https://nodejs.org
    pause
    exit /b 1
)

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python first.
    echo Download from: https://python.org
    pause
    exit /b 1
)

echo 📦 Installing Node.js dependencies...
npm install --production

echo.
echo 🐍 Installing Python dependencies...
echo Installing FastAPI, Whisper AI, and other requirements...
pip install fastapi uvicorn faster-whisper

echo.
echo ✅ Installation complete!
echo.
echo You can now run START_PORTABLE.bat to launch the application.
echo.
pause
`;

fs.writeFileSync(path.join(portableDir, 'INSTALL_DEPENDENCIES.bat'), installScript);
console.log('✅ Created INSTALL_DEPENDENCIES.bat');

console.log('\n🎉 Manual portable distribution created successfully!');
console.log(`📁 Location: ${portableDir}`);
console.log('\n📋 Package Contents:');
console.log('   - START_PORTABLE.bat (main launcher)');
console.log('   - INSTALL_DEPENDENCIES.bat (dependency installer)');
console.log('   - README_PORTABLE.md (instructions)');
console.log('   - main.js (Electron main process)');
console.log('   - renderer/ (UI files)');
console.log('   - backend/ (Python API backend)');
console.log('   - tool_config.json (configuration)');
console.log('\n🚀 Usage:');
console.log('1. Run INSTALL_DEPENDENCIES.bat (first time only)');
console.log('2. Run START_PORTABLE.bat to launch the application');
console.log('\n✨ The application will work from any folder location!');