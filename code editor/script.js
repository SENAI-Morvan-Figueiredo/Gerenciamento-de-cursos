// --- 1. State Management ---
let currentTab = 'html';
let pyodideReady = false;
let pyodideInstance = null;

// Default Code Snippets

// Initialize Editors
document.getElementById('editor-html').value = defaultCode.html;
document.getElementById('editor-css').value = defaultCode.css;
document.getElementById('editor-js').value = defaultCode.js;
document.getElementById('editor-python').value = defaultCode.python;

// --- 2. Tab Logic ---
function switchTab(tab) {
    currentTab = tab;
    
    // Update Headers
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('border-blue-500', 'text-white', 'bg-slate-800');
        btn.classList.add('border-transparent');
    });
    const activeBtn = document.getElementById(`tab-${tab}`);
    activeBtn.classList.add('border-blue-500', 'text-white', 'bg-slate-800');
    activeBtn.classList.remove('border-transparent');

    // Toggle Textareas
    document.querySelectorAll('.code-input').forEach(el => el.classList.add('hidden'));
    document.getElementById(`editor-${tab}`).classList.remove('hidden');

    // Update Indicator
    document.getElementById('lang-indicator').textContent = tab.toUpperCase() + " Mode";

    // Toggle Output View (Web vs Python)
    const webOutput = document.getElementById('output-web');
    const pythonOutput = document.getElementById('output-python');

    if (tab === 'python') {
        webOutput.classList.add('hidden');
        pythonOutput.classList.remove('hidden');
        initPython(); // Start loading Pyodide if not already
    } else {
        webOutput.classList.remove('hidden');
        pythonOutput.classList.add('hidden');
    }
}

// --- 3. Run Logic ---
async function runCode() {
    if (currentTab === 'python') {
        runPythonCode();
    } else {
        runWebCode();
    }
}

function runWebCode() {
    const html = document.getElementById('editor-html').value;
    const css = document.getElementById('editor-css').value;
    const js = document.getElementById('editor-js').value;

    const frame = document.getElementById('preview-frame');
    
    // Construct the complete HTML document
    const source = `
        <!DOCTYPE html>
        <html>
        <head>
            <style>${css}</style>
        </head>
        <body>
            ${html}
            <script>
                try {
                    ${js}
                } catch (err) {
                    console.error(err);
                    document.body.innerHTML += '<div style="color:red; background:#fee; padding:10px; border:1px solid red; margin-top:20px;">JS Error: ' + err.message + '</div>';
                }
            <\/script>
        </body>
        </html>
    `;

    frame.srcdoc = source;
}

// --- 4. Python Logic (Pyodide) ---
async function initPython() {
    if (pyodideReady) return;
    
    const statusEl = document.getElementById('python-status');
    statusEl.classList.remove('hidden');

    try {
        if(!window.loadPyodide) {
             throw new Error("Pyodide script not loaded yet.");
        }
        pyodideInstance = await loadPyodide();
        pyodideReady = true;
        statusEl.innerHTML = "Python Ready";
        setTimeout(() => statusEl.classList.add('hidden'), 2000);
    } catch (err) {
        statusEl.innerHTML = "Failed to load Python";
        statusEl.classList.add('text-red-500');
        console.error("Pyodide failed:", err);
    }
}

async function runPythonCode() {
    if (!pyodideReady) {
        await initPython();
    }

    const code = document.getElementById('editor-python').value;
    const consoleDiv = document.getElementById('console-logs');
    consoleDiv.innerHTML = ''; // Clear previous run

    // Custom output handler
    const addToConsole = (text) => {
        const line = document.createElement('div');
        line.textContent = text;
        line.className = "text-green-400 font-mono break-all whitespace-pre-wrap";
        consoleDiv.appendChild(line);
    };

    const addError = (text) => {
        const line = document.createElement('div');
        line.textContent = text;
        line.className = "text-red-400 font-mono break-all whitespace-pre-wrap";
        consoleDiv.appendChild(line);
    }

    try {
        // Redirect stdout to our function
        pyodideInstance.setStdout({ batched: (msg) => addToConsole(msg) });
        
        addToConsole(">>> Running...");
        await pyodideInstance.runPythonAsync(code);
        
    } catch (err) {
        addError(err);
    }
}

function clearOutput() {
    if (currentTab === 'python') {
        document.getElementById('console-logs').innerHTML = '';
    } else {
        document.getElementById('preview-frame').srcdoc = '';
    }
}

// Initialize First Run (Web)
switchTab('html');
runWebCode();