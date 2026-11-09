<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>STEELIA — Evaluador de Corrosión en Acero</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Plus+Jakarta+Sans:wght@300;400;600&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-main: #121016;
            --card-bg: #18151D;
            --card-border: #2B2534;
            --accent-pink: #C48B9F;
            --accent-mauve: #A66E81;
            --text-light: #F3E6EA;
            --text-muted: #A89A9F;
            --safe-green: #88AB94;
            --warn-amber: #D4A373;
            --crit-crimson: #B84A62;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            background-color: var(--bg-main);
            color: var(--text-light);
            font-family: 'Plus Jakarta Sans', sans-serif;
            padding: 2rem;
        }
        header {
            margin-bottom: 2rem;
            border-bottom: 1px solid var(--card-border);
            padding-bottom: 1rem;
        }
        h1 { font-family: 'Playfair Display', serif; color: var(--accent-pink); font-size: 2.5rem; }
        .subtitle { color: var(--text-muted); font-size: 0.95rem; }
        .grid-container {
            display: grid;
            grid-template-columns: 320px 1fr;
            gap: 1.5rem;
        }
        .card {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 1.5rem;
        }
        .form-group { margin-bottom: 1.2rem; }
        label { display: block; font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.4rem; }
        input, select {
            width: 100%;
            padding: 0.6rem;
            background: var(--bg-main);
            border: 1px solid var(--card-border);
            color: var(--text-light);
            border-radius: 6px;
        }
        .matrix-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px;
            margin-top: 1rem;
        }
        .cell {
            background: var(--bg-main);
            border: 1px solid var(--card-border);
            border-radius: 8px;
            padding: 1rem;
            text-align: center;
            font-family: 'JetBrains Mono', monospace;
            transition: all 0.3s ease;
        }
        .cell-status-safe { border-top: 4px solid var(--safe-green); }
        .cell-status-warn { border-top: 4px solid var(--warn-amber); }
        .cell-status-crit { border-top: 4px solid var(--crit-crimson); }
        .btn {
            background: var(--accent-pink);
            color: var(--bg-main);
            border: none;
            padding: 0.7rem 1.2rem;
            font-weight: 600;
            border-radius: 6px;
            cursor: pointer;
            width: 100%;
        }
        .btn:hover { background: var(--accent-mauve); }
    </style>
</head>
<body>
    <header>
        <h1>STEELIA</h1>
        <p class="subtitle">Sistema de Evaluación y Modelado de Corrosión en Acero | Ingeniería Civil</p>
    </header>
    <div class="grid-container">
        <div class="card">
            <h3 style="color: var(--accent-pink); margin-bottom: 1rem;">Parámetros</h3>
            <div class="form-group">
                <label>Diámetro Inicial (mm)</label>
                <input type="number" id="d0" value="16.0">
            </div>
            <div class="form-group">
                <label>Ambiente</label>
                <select id="env">
                    <option value="0.02">Urbano (0.02 mm/año)</option>
                    <option value="0.06">Industrial (0.06 mm/año)</option>
                    <option value="0.12">Marino (0.12 mm/año)</option>
                </select>
            </div>
            <div class="form-group">
                <label>Tiempo de Simulación: <span id="yearVal" style="color:var(--accent-pink)">10</span> años</label>
                <input type="range" id="years" min="0" max="50" value="10" oninput="updateUI()">
            </div>
            <button class="btn" onclick="updateUI()">Calcular</button>
        </div>
        <div class="card">
            <h3 style="color: var(--accent-pink);">Matriz de Inspección (4x4)</h3>
            <div class="matrix-grid" id="matrix"></div>
        </div>
    </div>
    <script>
        function updateUI() {
            const d0 = parseFloat(document.getElementById('d0').value);
            const vc = parseFloat(document.getElementById('env').value);
            const t = parseInt(document.getElementById('years').value);
            document.getElementById('yearVal').innerText = t;

            const grid = document.getElementById('matrix');
            grid.innerHTML = '';
            
            for(let r=0; r<4; r++) {
                for(let c=0; c<4; c++) {
                    const deltaD = vc * t;
                    const dActual = Math.max(0, d0 - deltaD);
                    const loss = (((d0*d0 - dActual*dActual) / (d0*d0)) * 100).toFixed(1);
                    
                    let statusClass = 'cell-status-safe';
                    if(loss > 15) statusClass = 'cell-status-crit';
                    else if(loss > 10) statusClass = 'cell-status-warn';

                    grid.innerHTML += `
                        <div class="cell ${statusClass}">
                            <div style="font-size:0.75rem; color:var(--text-muted)">[${r},${c}]</div>
                            <div style="font-size:1.1rem; font-weight:600">${dActual.toFixed(1)} mm</div>
                            <div style="font-size:0.8rem; color:var(--text-muted)">-${loss}%</div>
                        </div>
                    `;
                }
            }
        }
        updateUI();
    </script>
</body>
</html>
