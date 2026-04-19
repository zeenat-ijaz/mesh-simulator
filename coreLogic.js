/**
 * Zeenat Ijaz - Core Mathematical Logic
 * Extracted pure algorithm formulas without side-effects.
 */

export const performCalculations = (totalNodes, qShift) => {
    const dim = Math.sqrt(totalNodes);
    
    // Algorithm calculations
    const rShift = qShift % dim;
    const cShift = Math.floor(qShift / dim);
    
    const ringTotal = Math.min(qShift, totalNodes - qShift);
    const meshTotal = rShift + cShift;
    
    // Grid Generator Function
    const generateLayout = (stepType) => {
        const layout = [];
        for(let r=0; r<dim; r++){
            const row = [];
            for(let c=0; c<dim; c++){
                let origIndex = (r * dim) + c;
                
                if (stepType === 'START') {
                    row.push(origIndex);
                } else if (stepType === 'MID') {
                    // Reverse shift logic to see what data lands here after rows shift
                    // We need the data from node (origIndex - rShift) in same row
                    let sourceC = (c - rShift + dim) % dim;
                    row.push(r * dim + sourceC);
                } else if (stepType === 'END') {
                    // Fully shifted mapping
                    let sourceOverall = (origIndex - qShift + totalNodes) % totalNodes;
                    row.push(sourceOverall);
                }
            }
            layout.push(row);
        }
        return layout;
    };
    
    return {
        rShift, cShift, ringTotal, meshTotal,
        layoutStart: generateLayout('START'),
        layoutMid: generateLayout('MID'),
        layoutEnd: generateLayout('END')
    };
};
