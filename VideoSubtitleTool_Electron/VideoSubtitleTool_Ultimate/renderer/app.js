/**
 * Modern Frontend Logic for Video Subtitle Tool
 * Handles UI interactions and communication with Electron main process
 */

const { ipcRenderer } = require('electron');
const axios = require('axios');

class VideoSubtitleApp {
    constructor() {
        this.videos = [];
        this.workspace = null;
        this.isProcessing = false;
        this.backendPort = 8000;
        this.backendReady = false;
        
        this.initializeApp();
    }

    initializeApp() {
        console.log('Initializing Video Subtitle Tool...');
        
        // Setup event listeners
        this.setupEventListeners();
        this.setupDragAndDrop();
        this.setupBackendCommunication();
        
        // Check Python availability
        this.checkPythonAvailability();
        
        // Load saved workspace
        this.loadWorkspace();
        
        console.log('App initialized successfully');
    }

    setupEventListeners() {
        // Workspace buttons
        document.getElementById('configureWorkspaceBtn').addEventListener('click', () => {
            this.configureWorkspace();
        });
        
        document.getElementById('openWorkspaceBtn').addEventListener('click', () => {
            this.openWorkspace();
        });
        
        // Video buttons
        document.getElementById('addVideosBtn').addEventListener('click', () => {
            this.addVideos();
        });
        
        document.getElementById('clearVideosBtn').addEventListener('click', () => {
            this.clearVideos();
        });
        
        // Drop zone click
        document.getElementById('dropZone').addEventListener('click', () => {
            this.addVideos();
        });
        
        // Process button
        document.getElementById('processBtn').addEventListener('click', () => {
            this.startProcessing();
        });
        
        // Modal buttons
        document.getElementById('closeModalBtn').addEventListener('click', () => {
            this.hideModal('successModal');
        });
        
        document.getElementById('openFolderModalBtn').addEventListener('click', () => {
            this.openWorkspace();
            this.hideModal('successModal');
        });
        
        document.getElementById('closeErrorModalBtn').addEventListener('click', () => {
            this.hideModal('errorModal');
        });
    }

    setupDragAndDrop() {
        const dropZone = document.getElementById('dropZone');
        
        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, this.preventDefaults, false);
            document.body.addEventListener(eventName, this.preventDefaults, false);
        });
        
        // Highlight drop zone when item is dragged over it
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => {
                dropZone.classList.add('drag-over');
            }, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => {
                dropZone.classList.remove('drag-over');
            }, false);
        });
        
        // Handle dropped files
        dropZone.addEventListener('drop', (e) => {
            const files = Array.from(e.dataTransfer.files);
            this.handleDroppedFiles(files);
        }, false);
    }

    setupBackendCommunication() {
        // Listen for backend status updates
        ipcRenderer.on('backend-status', (event, data) => {
            console.log('Backend status:', data);
            this.updateBackendStatus(data);
        });
    }

    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    async checkPythonAvailability() {
        try {
            const result = await ipcRenderer.invoke('check-python');
            console.log('Python check result:', result);
            
            if (result.available) {
                this.updateStatus('🟡 Python detected, starting backend...', 'warning');
            } else {
                this.updateStatus('🔴 Python not found - please install Python', 'error');
                this.showError('Python Required', 
                    'Python is required to run this application. Please install Python and restart the app.');
            }
        } catch (error) {
            console.error('Python check failed:', error);
            this.updateStatus('🔴 Failed to check Python installation', 'error');
        }
    }

    updateBackendStatus(data) {
        const statusIndicator = document.getElementById('backendStatus');
        const statusText = document.getElementById('backendText');
        
        if (data.status === 'ready') {
            statusIndicator.textContent = '🟢';
            statusText.textContent = `Backend ready (Port ${data.port})`;
            this.backendReady = true;
            this.backendPort = data.port;
        } else if (data.status === 'error') {
            statusIndicator.textContent = '🔴';
            statusText.textContent = 'Backend failed to start';
            this.backendReady = false;
        } else {
            statusIndicator.textContent = '🟡';
            statusText.textContent = 'Backend starting...';
        }
    }

    updateStatus(message, type = 'info') {
        const statusText = document.getElementById('backendText');
        statusText.textContent = message;
        
        // You can add different styling based on type
        statusText.className = `status-text ${type}`;
    }

    async configureWorkspace() {
        try {
            const result = await ipcRenderer.invoke('select-workspace');
            
            if (!result.canceled && result.filePaths.length > 0) {
                const selectedPath = result.filePaths[0];
                const workspacePath = `${selectedPath}/VideoSubtitleTool`;
                
                // Create workspace subfolder
                await this.createWorkspaceFolder(workspacePath);
                
                this.workspace = workspacePath;
                this.saveWorkspace();
                this.updateWorkspaceDisplay();
                
                this.showSuccess('Workspace Configured', 
                    `Workspace has been set to: ${workspacePath}`);
            }
        } catch (error) {
            console.error('Workspace configuration failed:', error);
            this.showError('Configuration Failed', 
                'Failed to configure workspace. Please try again.');
        }
    }

    async createWorkspaceFolder(path) {
        // This would need to be implemented in the backend or main process
        // For now, we'll just set the workspace path
        console.log('Creating workspace folder:', path);
    }

    updateWorkspaceDisplay() {
        const workspaceDisplay = document.getElementById('workspaceDisplay');
        const workspacePath = document.getElementById('workspacePath');
        
        if (this.workspace) {
            workspaceDisplay.innerHTML = `
                <span class="workspace-text" style="color: var(--success);">${this.workspace}</span>
            `;
            workspacePath.textContent = this.workspace;
        } else {
            workspaceDisplay.innerHTML = `
                <span class="workspace-text">No workspace configured</span>
            `;
            workspacePath.textContent = 'No workspace configured';
        }
    }

    async openWorkspace() {
        if (this.workspace) {
            try {
                await ipcRenderer.invoke('open-folder', this.workspace);
            } catch (error) {
                console.error('Failed to open workspace:', error);
                this.showError('Failed to Open', 
                    'Could not open workspace folder. Please check if it exists.');
            }
        } else {
            this.showError('No Workspace', 
                'Please configure a workspace folder first.');
        }
    }

    async addVideos() {
        try {
            const result = await ipcRenderer.invoke('select-videos');
            
            if (!result.canceled && result.filePaths.length > 0) {
                // Add new videos (avoid duplicates)
                result.filePaths.forEach(filePath => {
                    if (!this.videos.some(video => video.path === filePath)) {
                        this.videos.push({
                            name: this.getFileName(filePath),
                            path: filePath
                        });
                    }
                });
                
                this.updateVideoDisplay();
            }
        } catch (error) {
            console.error('Video selection failed:', error);
            this.showError('Selection Failed', 
                'Failed to select video files. Please try again.');
        }
    }

    handleDroppedFiles(files) {
        const videoExtensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v'];
        
        files.forEach(file => {
            const isVideo = videoExtensions.some(ext => 
                file.name.toLowerCase().endsWith(ext));
            
            if (isVideo && !this.videos.some(video => video.path === file.path)) {
                this.videos.push({
                    name: file.name,
                    path: file.path
                });
            }
        });
        
        this.updateVideoDisplay();
    }

    clearVideos() {
        if (this.videos.length > 0) {
            if (confirm('Remove all selected videos?')) {
                this.videos = [];
                this.updateVideoDisplay();
            }
        }
    }

    updateVideoDisplay() {
        const dropZone = document.getElementById('dropZone');
        const videoList = document.getElementById('videoList');
        const videoCount = document.getElementById('videoCount');
        
        // Update count
        const count = this.videos.length;
        videoCount.textContent = `${count} video${count !== 1 ? 's' : ''} selected`;
        
        if (this.videos.length === 0) {
            // Show drop zone
            dropZone.style.display = 'flex';
            videoList.style.display = 'none';
        } else {
            // Show video list
            dropZone.style.display = 'none';
            videoList.style.display = 'block';
            
            // Generate video list HTML
            videoList.innerHTML = this.videos.map((video, index) => `
                <div class="video-item fade-in">
                    <div class="video-info">
                        <div class="video-name">${index + 1}. ${video.name}</div>
                        <div class="video-path">${video.path}</div>
                    </div>
                    <button class="btn btn-secondary" onclick="app.removeVideo(${index})">
                        ✕
                    </button>
                </div>
            `).join('');
        }
    }

    removeVideo(index) {
        this.videos.splice(index, 1);
        this.updateVideoDisplay();
    }

    getSelectedModel() {
        const modelRadios = document.querySelectorAll('input[name="model"]');
        for (const radio of modelRadios) {
            if (radio.checked) {
                return radio.value;
            }
        }
        return 'small'; // default
    }

    async startProcessing() {
        // Validation
        if (this.videos.length === 0) {
            this.showError('No Videos', 
                'Please select at least one video file.');
            return;
        }
        
        if (!this.workspace) {
            this.showError('No Workspace', 
                'Please configure a workspace folder first.');
            return;
        }
        
        if (!this.backendReady) {
            this.showError('Backend Not Ready', 
                'The processing backend is not ready. Please wait or restart the app.');
            return;
        }
        
        // Start EXACT 4-Step Processing Workflow
        this.isProcessing = true;
        this.updateProcessingUI(true, "Starting 4-step workflow: Stitch → Transcribe → Correct → Burn");
        
        try {
            // EXACT Step 1-2: Stitch and Transcribe (like original GUI)
            await this.executeSteps1And2();
            
        } catch (error) {
            console.error('4-step workflow failed:', error);
            this.handleProcessingError(error.message);
            this.isProcessing = false;
            this.updateProcessingUI(false);
        }
    }

    async executeSteps1And2() {
        // Update UI for Steps 1-2
        this.updateProgressText("Step 1/4: Stitching videos together...");
        
        const processingData = {
            videos: this.videos.map(v => v.path),
            workspace: this.workspace,
            model: this.getSelectedModel()
        };
        
        console.log('Starting EXACT Steps 1-2 with data:', processingData);
        
        // Execute Steps 1-2: Stitch + Transcribe
        const response = await axios.post(`http://localhost:${this.backendPort}/process`, 
            processingData, {
            timeout: 600000, // 10 minutes timeout for stitching + transcription
        });
        
        console.log('Steps 1-2 response:', response.data);
        
        if (response.data.success && response.data.step === "correction") {
            // Steps 1-2 completed, ready for Step 3 (Correction)
            this.workflowData = {
                combined_video: response.data.combined_video,
                initial_srt: response.data.initial_srt,
                base_name: response.data.base_name,
                workspace: response.data.workspace
            };
            
            this.showStep3CorrectionDialog();
            
        } else {
            throw new Error(response.data.error || 'Steps 1-2 failed during stitching or transcription');
        }
    }

    showStep3CorrectionDialog() {
        // Update UI to show completion of Steps 1-2 and prompt for Step 3
        this.updateProgressText("Step 2/4: Transcription complete! Ready for Step 3...");
        
        // Show transcript correction modal (EXACT like original GUI)
        this.showTranscriptCorrectionModal();
    }

    showTranscriptCorrectionModal() {
        // Create modal HTML (EXACT like original GUI dialog)
        const modalHTML = `
            <div class="modal-overlay" id="transcriptModal">
                <div class="modal-content transcript-modal">
                    <div class="modal-header">
                        <h3>📝 Original Transcript Correction</h3>
                    </div>
                    <div class="modal-body">
                        <p>The AI transcription is approximately 80% accurate. To improve accuracy, 
                        please paste your original transcript text below.</p>
                        <p>This will be used to correct the generated subtitles.</p>
                        
                        <label for="originalTranscript">Original Transcript:</label>
                        <textarea id="originalTranscript" rows="15" cols="70" 
                                placeholder="Paste your original transcript here..."></textarea>
                    </div>
                    <div class="modal-footer">
                        <button id="skipCorrectionBtn" class="btn btn-secondary">Skip Correction</button>
                        <button id="applyCorrectionBtn" class="btn btn-primary">✓ Apply Correction</button>
                    </div>
                </div>
            </div>
        `;
        
        // Add modal to page
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        
        // Setup modal event listeners
        document.getElementById('skipCorrectionBtn').addEventListener('click', () => {
            this.executeStep3Skip();
        });
        
        document.getElementById('applyCorrectionBtn').addEventListener('click', () => {
            this.executeStep3Apply();
        });
        
        // Show modal
        document.getElementById('transcriptModal').style.display = 'flex';
    }

    async executeStep3Apply() {
        const transcriptText = document.getElementById('originalTranscript').value.trim();
        
        if (!transcriptText) {
            alert('Please paste your transcript or click Skip to proceed without correction.');
            return;
        }
        
        // Close modal
        this.hideTranscriptModal();
        
        // Update UI for Step 3
        this.updateProgressText("Step 3/4: Applying transcript correction...");
        
        try {
            const correctionData = {
                initial_srt: this.workflowData.initial_srt,
                original_transcript: transcriptText,
                base_name: this.workflowData.base_name,
                workspace: this.workflowData.workspace
            };
            
            const response = await axios.post(`http://localhost:${this.backendPort}/apply-correction`, 
                correctionData, { timeout: 120000 });
            
            if (response.data.success) {
                this.workflowData.final_srt = response.data.final_srt;
                this.workflowData.correction_percentage = response.data.correction_percentage;
                
                this.updateProgressText(`Step 3/4: Correction applied (${response.data.correction_percentage.toFixed(1)}% corrected)`);
                
                // Execute Step 4
                await this.executeStep4();
            } else {
                throw new Error(response.data.error || 'Step 3 correction failed');
            }
            
        } catch (error) {
            console.error('Step 3 apply error:', error);
            this.handleProcessingError('Step 3 failed: ' + error.message);
        }
    }

    async executeStep3Skip() {
        // Close modal
        this.hideTranscriptModal();
        
        // Update UI for Step 3
        this.updateProgressText("Step 3/4: Correction skipped, using AI-generated subtitles...");
        
        try {
            const skipData = {
                initial_srt: this.workflowData.initial_srt,
                base_name: this.workflowData.base_name,
                workspace: this.workflowData.workspace
            };
            
            const response = await axios.post(`http://localhost:${this.backendPort}/skip-correction`, 
                skipData, { timeout: 30000 });
            
            if (response.data.success) {
                this.workflowData.final_srt = response.data.final_srt;
                
                // Execute Step 4
                await this.executeStep4();
            } else {
                throw new Error(response.data.error || 'Step 3 skip failed');
            }
            
        } catch (error) {
            console.error('Step 3 skip error:', error);
            this.handleProcessingError('Step 3 failed: ' + error.message);
        }
    }

    async executeStep4() {
        // Update UI for Step 4
        this.updateProgressText("Step 4/4: Burning subtitles into combined video...");
        
        try {
            const burnData = {
                combined_video: this.workflowData.combined_video,
                final_srt: this.workflowData.final_srt,
                base_name: this.workflowData.base_name,
                workspace: this.workflowData.workspace
            };
            
            const response = await axios.post(`http://localhost:${this.backendPort}/burn-subtitles`, 
                burnData, { timeout: 600000 }); // 10 minutes for burning
            
            if (response.data.success) {
                // Complete workflow success
                this.handle4StepWorkflowSuccess(response.data);
            } else if (response.data.subtitle_burn_failed) {
                // Partial success (SRT + combined video available)
                this.handle4StepWorkflowPartialSuccess(response.data);
            } else {
                throw new Error(response.data.error || 'Step 4 burning failed');
            }
            
        } catch (error) {
            console.error('Step 4 burn error:', error);
            this.handleProcessingError('Step 4 failed: ' + error.message);
        } finally {
            this.isProcessing = false;
            this.updateProcessingUI(false);
        }
    }

    hideTranscriptModal() {
        const modal = document.getElementById('transcriptModal');
        if (modal) {
            modal.remove();
        }
    }

    handle4StepWorkflowSuccess(data) {
        // Complete progress animation
        const progressFill = document.getElementById('progressFill');
        progressFill.style.width = '100%';
        this.updateProgressText("✅ Multi-video processing completed successfully!");
        
        setTimeout(() => {
            // Show success modal with exact messaging from original GUI
            const modalBody = document.getElementById('successModalBody');
            modalBody.innerHTML = `
                <p><strong>🎉 Multi-video processing completed successfully!</strong></p>
                <br>
                <p>Workflow: ✅ Stitch → ✅ Transcribe → ✅ Correct → ✅ Burn</p>
                <br>
                <p>📝 Final subtitle file: ${this.workflowData.base_name}.srt</p>
                <p>🎬 Final video with subtitles: ${this.workflowData.base_name}_with_subtitles.mp4</p>
                <br>
                <p>Processed ${this.videos.length} video clips${this.workflowData.correction_percentage ? ` with transcript correction (${this.workflowData.correction_percentage.toFixed(1)}% corrected)` : ''}!</p>
                <br>
                <p>📁 Files saved in your workspace folder.</p>
            `;
            
            this.showModal('successModal');
        }, 1000);
    }

    handle4StepWorkflowPartialSuccess(data) {
        // Complete progress animation with warning
        const progressFill = document.getElementById('progressFill');
        progressFill.style.width = '100%';
        this.updateProgressText("⚠️ Processing completed with warnings");
        
        setTimeout(() => {
            // Show success modal with warning message from original GUI
            const modalBody = document.getElementById('successModalBody');
            modalBody.innerHTML = `
                <p><strong>🎬 Multi-video processing completed!</strong></p>
                <br>
                <p>Workflow: ✅ Stitch → ✅ Transcribe → ✅ Correct → ⚠️ Burn</p>
                <br>
                <p>📝 Combined subtitle file: ${this.workflowData.base_name}.srt</p>
                <p>🎥 Combined video: ${this.workflowData.base_name}_combined.mp4</p>
                <br>
                <p>⚠️ Note: Subtitle burning failed, but combined video and SRT file are ready.</p>
                <p>You can use external software to add subtitles.</p>
                <br>
                <p>📁 Files saved in your workspace folder.</p>
            `;
            
            this.showModal('successModal');
        }, 1000);
    }

    updateProcessingUI(processing, message = null) {
        const processBtn = document.getElementById('processBtn');
        const progressSection = document.getElementById('progressSection');
        
        if (processing) {
            processBtn.disabled = true;
            processBtn.textContent = '⏳ Processing (4 Steps)...';
            progressSection.style.display = 'block';
            if (message) {
                this.updateProgressText(message);
            }
            this.startProgressAnimation();
        } else {
            processBtn.disabled = false;
            processBtn.textContent = '🚀 Process Videos & Generate Subtitles';
            progressSection.style.display = 'none';
            this.stopProgressAnimation();
        }
    }

    updateProgressText(message) {
        const progressText = document.getElementById('progressText');
        if (progressText) {
            progressText.textContent = message;
        }
        console.log('Progress:', message);
    }

    startProgressAnimation() {
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');
        
        progressText.textContent = 'Processing videos...';
        
        // Simulate progress (you can replace this with actual progress from backend)
        let progress = 0;
        this.progressInterval = setInterval(() => {
            progress += Math.random() * 10;
            if (progress > 90) progress = 90; // Don't complete until actually done
            
            progressFill.style.width = `${progress}%`;
        }, 500);
    }

    stopProgressAnimation() {
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
        }
        
        const progressFill = document.getElementById('progressFill');
        progressFill.style.width = '0%';
    }

    handleProcessingSuccess(data) {
        // Complete progress
        const progressFill = document.getElementById('progressFill');
        progressFill.style.width = '100%';
        
        setTimeout(() => {
            if (data.needs_correction) {
                // SRT generated but needs correction - show correction modal
                this.showCorrectionModal(data);
            } else {
                // Final video completed - show success
                const modalBody = document.getElementById('successModalBody');
                modalBody.innerHTML = `
                    <p><strong>✅ Processing completed successfully!</strong></p>
                    <br>
                    <p>📝 Subtitle file: ${data.srt_file || 'subtitles.srt'}</p>
                    ${data.final_video ? `<p>🎬 Final video: ${data.final_video}</p>` : ''}
                    <br>
                    <p>📁 Files saved in your workspace folder.</p>
                `;
                
                this.showModal('successModal');
            }
        }, 1000);
    }

    showCorrectionModal(data) {
        // Store data for correction step
        this.correctionData = data;
        
        const modalBody = document.getElementById('correctionModalBody');
        modalBody.innerHTML = `
            <p><strong>📝 SRT Generated Successfully!</strong></p>
            <br>
            <p>The AI-generated subtitles are approximately 80% accurate.</p>
            <p>Please paste your <strong>original transcript</strong> below to correct the timing and accuracy:</p>
            <br>
            <textarea id="originalTranscript" placeholder="Paste your original transcript here..." 
                      style="width: 100%; height: 200px; padding: 10px; border-radius: 4px; border: 1px solid #ddd; font-family: monospace; font-size: 0.875rem;"></textarea>
        `;
        
        this.showModal('correctionModal');
    }

    handleProcessingError(error) {
        const modalBody = document.getElementById('errorModalBody');
        modalBody.innerHTML = `
            <p><strong>An error occurred during processing:</strong></p>
            <br>
            <p style="color: var(--error); font-family: monospace; font-size: 0.875rem;">
                ${error}
            </p>
            <br>
            <p>Please check your video files and try again.</p>
        `;
        
        this.showModal('errorModal');
    }

    showModal(modalId) {
        document.getElementById(modalId).style.display = 'flex';
    }

    hideModal(modalId) {
        document.getElementById(modalId).style.display = 'none';
    }

    showSuccess(title, message) {
        // You can implement a toast notification system here
        console.log(`Success: ${title} - ${message}`);
        alert(`${title}\n\n${message}`);
    }

    showError(title, message) {
        console.error(`Error: ${title} - ${message}`);
        alert(`${title}\n\n${message}`);
    }

    async submitCorrection() {
        const originalTranscript = document.getElementById('originalTranscript').value.trim();
        
        if (!originalTranscript) {
            alert('Please paste your original transcript before proceeding.');
            return;
        }
        
        // Hide correction modal and show processing
        this.hideModal('correctionModal');
        this.updateProcessingUI(true);
        
        try {
            console.log('Starting SRT correction...');
            
            // Find the video file path from the original videos
            let videoFile = '';
            if (this.correctionData && this.videos.length > 0) {
                if (this.videos.length > 1) {
                    // Multiple videos - video file would be the stitched video
                    videoFile = this.correctionData.srt_file.replace('.srt', '.mp4'); // Should be stitched_video.mp4
                } else {
                    // Single video
                    videoFile = this.videos[0].path;
                }
            }
            
            const correctionRequest = {
                srt_file: this.correctionData.srt_file,
                original_transcript: originalTranscript,
                video_file: videoFile
            };
            
            console.log('Correction request:', correctionRequest);
            
            const response = await axios.post(`http://localhost:${this.backendPort}/correct-srt`, 
                correctionRequest, {
                timeout: 600000, // 10 minutes timeout for burning
            });
            
            console.log('Correction response:', response.data);
            
            if (response.data.success) {
                this.handleFinalSuccess(response.data);
            } else {
                this.handleProcessingError(response.data.error || 'Correction failed');
            }
            
        } catch (error) {
            console.error('Correction failed:', error);
            this.handleProcessingError(error.message);
        }
        
        this.updateProcessingUI(false);
    }

    handleFinalSuccess(data) {
        // Complete progress
        const progressFill = document.getElementById('progressFill');
        progressFill.style.width = '100%';
        
        setTimeout(() => {
            const modalBody = document.getElementById('successModalBody');
            modalBody.innerHTML = `
                <p><strong>🎉 Complete Workflow Finished Successfully!</strong></p>
                <br>
                <p>✅ SRT corrected with your original transcript</p>
                <p>✅ Lossless quality video with burned subtitles created</p>
                <br>
                <p>🎬 Final video: ${data.final_video}</p>
                <br>
                <p>📁 Files saved in your workspace folder.</p>
            `;
            
            this.showModal('successModal');
        }, 1000);
    }

    getFileName(filePath) {
        return filePath.split(/[\\/]/).pop();
    }

    saveWorkspace() {
        localStorage.setItem('workspace', this.workspace);
    }

    loadWorkspace() {
        const saved = localStorage.getItem('workspace');
        if (saved) {
            this.workspace = saved;
            this.updateWorkspaceDisplay();
        }
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new VideoSubtitleApp();
});

console.log('Video Subtitle Tool frontend loaded');