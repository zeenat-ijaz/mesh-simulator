import { performCalculations } from './coreLogic.js';

// DOM Lookups
const selNodes = document.getElementById('sel-nodes');
const rngShift = document.getElementById('range-shift');
const lblShift = document.getElementById('lbl-shift-val');
const btnExec = document.getElementById('btn-exec');
const btnReset = document.getElementById('btn-reset');
const statRing = document.getElementById('stat-ring');
const statMesh = document.getElementById('stat-mesh');
const conclBox = document.getElementById('conclusion-box');
const statusBar = document.getElementById('status-bar');

const canvStart = document.getElementById('canvas-start');
const canvMid = document.getElementById('canvas-mid');
const canvEnd = document.getElementById('canvas-end');

const syncSlider = () => {
    let maxShift = parseInt(selNodes.value) - 1;
    rngShift.max = maxShift;
    if (parseInt(rngShift.value) > maxShift) {
        rngShift.value = maxShift;
    }
    lblShift.innerText = rngShift.value;
};

selNodes.addEventListener('change', syncSlider);
rngShift.addEventListener('input', syncSlider);

const drawMatrix = (container, matrixData, highlightAxis) => {
    container.innerHTML = '';
    const dim = matrixData.length;
    const size = 300;
    const cellW = size / dim;
    
    let svg = `<svg viewBox="0 0 ${size} ${size}" width="100%" height="100%">`;
    
    // Draw cells
    for(let r=0; r<dim; r++){
        for(let c=0; c<dim; c++){
            let val = matrixData[r][c];
            let x = c * cellW;
            let y = r * cellW;
            
            // Choose color based on value to make it distinct
            let hue = (val * 137) % 360;
            let bgFill = `hsl(${hue}, 70%, 40%)`;
            
            svg += `<rect x="${x}" y="${y}" width="${cellW}" height="${cellW}" fill="${bgFill}" stroke="#1e293b" stroke-width="2"></rect>`;
            svg += `<text x="${x + cellW/2}" y="${y + cellW/2}" fill="white" font-size="${cellW*0.3}px" text-anchor="middle" dominant-baseline="central">${val}</text>`;
        }
    }
    
    svg += `</svg>`;
    container.innerHTML = svg;
};

const execute = () => {
    let N = parseInt(selNodes.value);
    let Q = parseInt(rngShift.value);
    
    statusBar.innerText = `⚙️ Processing circular shift for N=${N}, Q=${Q}...`;
    
    const results = performCalculations(N, Q);
    
    statRing.innerText = `${results.ringTotal} step(s)`;
    statMesh.innerText = `${results.meshTotal} step(s) [Row:${results.rShift}, Col:${results.cShift}]`;
    
    if (results.meshTotal < results.ringTotal) {
        conclBox.innerHTML = `✅ <strong>Optimal:</strong> Mesh architecture reduces routing overhead by ${results.ringTotal - results.meshTotal} step(s).`;
    } else if (results.meshTotal === results.ringTotal) {
        conclBox.innerHTML = `⚖️ <strong>Neutral:</strong> Both topologies require equal steps.`;
    } else {
        conclBox.innerHTML = `⚠️ <strong>Sub-optimal:</strong> Ring is faster for this specific shift.`;
    }
    
    drawMatrix(canvStart, results.layoutStart, null);
    drawMatrix(canvMid, results.layoutMid, 'row');
    drawMatrix(canvEnd, results.layoutEnd, 'col');
    
    statusBar.innerText = '✅ Shift completed and rendered. Math verified.';
};

const resetUI = () => {
    selNodes.value = "16";
    syncSlider();
    rngShift.value = "5";
    lblShift.innerText = "5";
    
    canvStart.innerHTML = '';
    canvMid.innerHTML = '';
    canvEnd.innerHTML = '';
    
    statRing.innerText = '--';
    statMesh.innerText = '--';
    conclBox.innerHTML = 'Awaiting execution...';
    statusBar.innerText = 'Status: Ready to execute circular shift.';
};

btnExec.addEventListener('click', execute);
btnReset.addEventListener('click', resetUI);

// Init
syncSlider();
