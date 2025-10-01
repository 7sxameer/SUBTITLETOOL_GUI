const fs = require('fs');
const path = require('path');

/**
 * Create Portable Package Script
 * Bundles the Electron app with Python backend into a portable distribution
 */

console.log('🎬 Creating Video Subtitle Tool Portable Package...\n');

const sourceDir = path.join(__dirname, '..', 'dist-portable');
const portableDir = path.join(__dirname, '..', '..', 'VideoSubtitleTool_Portable_Modern');
const pythonBackendDir = path.join(__dirname, '..', 'backend');

// Create portable directory structure
function createPortableStructure() {
    console.log('📁 Creating portable directory structure...');
    
    if (!fs.existsSync(portableDir)) {
        fs.mkdirSync(portableDir, { recursive: true });
    }
    
    // Copy portable files
    const portableFiles = [
        'README_PORTABLE.md',
        'START_PORTABLE.bat'
    ];
    
    const srcPortableDir = path.join(__dirname, '..', 'portable');
    
    portableFiles.forEach(file => {
        const src = path.join(srcPortableDir, file);
        const dest = path.join(portableDir, file);
        
        if (fs.existsSync(src)) {
            fs.copyFileSync(src, dest);
            console.log(`✅ Copied ${file}`);
        }
    });
}

// Copy the built Electron executable
function copyElectronApp() {
    console.log('\n🚀 Copying Electron application...');
    
    const executableName = 'VideoSubtitleTool_Portable.exe';
    const srcExe = path.join(sourceDir, executableName);
    const destExe = path.join(portableDir, executableName);
    
    if (fs.existsSync(srcExe)) {
        fs.copyFileSync(srcExe, destExe);
        console.log(`✅ Copied ${executableName}`);
    } else {
        console.log(`❌ Executable not found at: ${srcExe}`);
        console.log('   Please run "npm run build-portable" first');
        process.exit(1);
    }
}

// Bundle Python backend requirements
function bundlePythonBackend() {
    console.log('\n🐍 Bundling Python backend...');
    
    // Copy requirements.txt for reference
    const requirementsSrc = path.join(pythonBackendDir, '..', 'Program Files', 'requirements.txt');
    const requirementsDest = path.join(portableDir, 'requirements.txt');
    
    if (fs.existsSync(requirementsSrc)) {
        fs.copyFileSync(requirementsSrc, requirementsDest);
        console.log('✅ Copied requirements.txt');
    }
    
    // Copy faster_whisper module
    const fasterWhisperSrc = path.join(pythonBackendDir, '..', 'faster_whisper');
    const fasterWhisperDest = path.join(portableDir, 'faster_whisper');
    
    if (fs.existsSync(fasterWhisperSrc)) {
        copyRecursiveSync(fasterWhisperSrc, fasterWhisperDest);
        console.log('✅ Copied faster_whisper module');
    }
}

// Create configuration file
function createConfig() {
    console.log('\n⚙️ Creating configuration...');
    
    const config = {
        "version": "2.0.0",
        "portable": true,
        "backend_port": 8000,
        "auto_workspace": true,
        "default_model": "small",
        "created": new Date().toISOString()
    };
    
    const configPath = path.join(portableDir, 'tool_config.json');
    fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
    console.log('✅ Created tool_config.json');
}

// Helper function to copy directories recursively
function copyRecursiveSync(src, dest) {
    if (!fs.existsSync(src)) return;
    
    const stats = fs.statSync(src);
    
    if (stats.isDirectory()) {
        if (!fs.existsSync(dest)) {
            fs.mkdirSync(dest, { recursive: true });
        }
        
        const files = fs.readdirSync(src);
        files.forEach(file => {
            copyRecursiveSync(
                path.join(src, file),
                path.join(dest, file)
            );
        });
    } else {
        fs.copyFileSync(src, dest);
    }
}

// Main execution
async function main() {
    try {
        createPortableStructure();
        copyElectronApp();
        bundlePythonBackend();
        createConfig();
        
        console.log('\n🎉 Portable package created successfully!');
        console.log(`📁 Location: ${portableDir}`);
        console.log('\n📋 Package Contents:');
        console.log('   - VideoSubtitleTool_Portable.exe (main application)');
        console.log('   - START_PORTABLE.bat (launcher script)');
        console.log('   - README_PORTABLE.md (instructions)');
        console.log('   - tool_config.json (configuration)');
        console.log('   - requirements.txt (Python dependencies reference)');
        console.log('   - faster_whisper/ (AI model library)');
        console.log('\n✨ Ready to distribute! Users can run START_PORTABLE.bat');
        
    } catch (error) {
        console.error('\n❌ Error creating portable package:', error);
        process.exit(1);
    }
}

main();