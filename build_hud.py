import yfinance as yf
import json
import os

# 1. 偵察：ターゲット一括スキャン
targets = {
    "FANG+": "^NYFANG",
    "SMH (Semiconductor)": "SMH",
    "QQQ (NASDAQ100)": "QQQ",
    "Gold (GLDM)": "GLDM"
}

results = []
for name, ticker in targets.items():
    try:
        data = yf.download(ticker, period="6mo", auto_adjust=True)
        # 堅牢な数値抽出
        p_curr = float(data['Close'].iloc[-1].values[0]) if hasattr(data['Close'].iloc[-1], 'values') else float(data['Close'].iloc[-1])
        p_high = float(data['High'].max().values[0]) if hasattr(data['High'].max(), 'values') else float(data['High'].max())
        
        # 30%下落ラインまでの乖離率
        p_alert = p_high * 0.7
        div = ((p_curr - p_alert) / p_alert) * 100
        
        results.append({
            "name": name,
            "div": round(div, 2),
            "price": f"{p_curr:,.2f}",
            "high": f"{p_high:,.2f}"
        })
    except Exception as e:
        print(f"Error scanning {name}: {e}")

# 2. 報告書（HTML）の自動作成
# 前回のHTMLテンプレートをここに流し込む
html_template = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>STRATEGIC COMMAND HUD | ai-kakoujyo.com</title>
    <style>
        :root { --bg-color: #0a0a0a; --panel-bg: #161616; --text-main: #e0e0e0; --safe: #00ff41; --warning: #ffaa00; --danger: #ff0000; }
        body { background-color: var(--bg-color); color: var(--text-main); font-family: 'Courier New', Courier, monospace; margin: 0; display: flex; flex-direction: column; align-items: center; min-height: 100vh; }
        header { width: 100%; padding: 20px; text-align: center; border-bottom: 2px solid #333; background: linear-gradient(180deg, #1a1a1a 0%, #0a0a0a 100%); }
        .dashboard-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; width: 95%; max-width: 1200px; padding: 40px 0; }
        .monitor-card { background: var(--panel-bg); border: 1px solid #333; padding: 20px; border-radius: 4px; box-shadow: 0 0 15px rgba(0,0,0,0.5); }
        .status-safe { border-left: 5px solid var(--safe); }
        .status-warning { border-left: 5px solid var(--warning); }
        .status-danger { border-left: 5px solid var(--danger); animation: pulse 2s infinite; }
        @keyframes pulse { 0% { box-shadow: inset 0 0 10px rgba(255,0,0,0.2); } 50% { box-shadow: inset 0 0 30px rgba(255,0,0,0.5); } 100% { box-shadow: inset 0 0 10px rgba(255,0,0,0.2); } }
        .ticker-name { font-size: 1.2rem; color: #888; margin-bottom: 10px; }
        .divergence { font-size: 3rem; font-weight: bold; margin: 10px 0; text-align: center; }
        .price-info { display: flex; justify-content: space-between; font-size: 0.8rem; color: #555; }
    </style>
</head>
<body>
<header><h1 style="margin:0; letter-spacing: 5px;">STRATEGIC COMMAND HUD</h1></header>
<div class="dashboard-grid" id="hud-container"></div>
<script>
    const marketData = DATA_PLACEHOLDER;
    const container = document.getElementById('hud-container');
    marketData.forEach(item => {
        let statusClass = 'status-safe';
        if (item.div <= 5) statusClass = 'status-warning';
        if (item.div <= 0) statusClass = 'status-danger';
        const card = document.createElement('div');
        card.className = `monitor-card ${statusClass}`;
        card.innerHTML = `<div class="ticker-name">${item.name}</div><div class="divergence">${item.div > 0 ? '+' : ''}${item.div}%</div><div class="price-info"><span>CUR: ${item.price}</span><span>REF HIGH: ${item.high}</span></div>`;
        container.appendChild(card);
    });
</script>
</body>
</html>
"""
final_html = html_template.replace("DATA_PLACEHOLDER", json.dumps(results))

# 3. index.html として出力
with open("index.html", "w", encoding="utf-8") as f:
    f.write(final_html)
