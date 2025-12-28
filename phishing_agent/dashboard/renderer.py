# dashboard/renderer.py
import os
import datetime

def render_dashboard(results, output_dir="dashboard"):
    """
    Generates a static HTML dashboard from the analysis results.
    """
    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Phishing Agent Dashboard</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 20px; background: #f0f2f5; color: #333; }
            .container { max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
            header { border-bottom: 2px solid #eaecf0; padding-bottom: 20px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }
            h1 { margin: 0; font-size: 24px; color: #1a1f36; }
            .meta { font-size: 14px; color: #667085; }
            
            table { width: 100%; border-collapse: collapse; margin-top: 10px; }
            th { text-align: left; padding: 12px; background-color: #f9fafb; color: #475467; font-weight: 600; font-size: 14px; }
            td { padding: 16px 12px; border-bottom: 1px solid #eaecf0; vertical-align: top; }
            tr:last-child td { border-bottom: none; }
            
            /* Verdict Badges */
            .badge { padding: 4px 10px; border-radius: 16px; font-weight: 600; font-size: 12px; display: inline-block; }
            .SAFE { background-color: #ecfdf3; color: #027a48; border: 1px solid #abefc6; }
            .SUSPICIOUS { background-color: #fffaeb; color: #b54708; border: 1px solid #fedf89; }
            .PHISHING { background-color: #fef3f2; color: #b42318; border: 1px solid #fecdca; }

            /* Risk Score */
            .score-high { color: #b42318; font-weight: bold; }
            .score-med { color: #b54708; font-weight: bold; }
            .score-low { color: #027a48; font-weight: bold; }

            ul { margin: 0; padding-left: 20px; font-size: 14px; color: #475467; }
            li { margin-bottom: 4px; }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <div>
                    <h1>🛡️ Phishing Detection Agent</h1>
                    <div class="meta">Local Analysis Report</div>
                </div>
                <div class="meta">Generated: """ + timestamp + """</div>
            </header>
            
            <!-- Legend / Methodology -->
            <div style="background:#f9fafb; padding:20px; border-radius:12px; margin-bottom:25px; border:1px solid #eaecf0; color:#475467;">
                <h3 style="margin-top:0; font-size:16px; color:#101828;">🔍 How Scores are Calculated</h3>
                
                <div style="display:flex; gap:30px; margin-bottom:20px;">
                    <div style="flex:1;">
                        <div style="font-weight:600; margin-bottom:10px; color:#344054;">1. Verdict Thresholds</div>
                        <div style="font-size:13px; line-height:1.6;">
                            <div style="margin-bottom:4px;"><span class="badge PHISHING">PHISHING</span> <strong>Score ≥ 50</strong></div>
                            <div style="margin-bottom:4px;"><span class="badge SUSPICIOUS">SUSPICIOUS</span> <strong>Score ≥ 30</strong></div>
                            <div><span class="badge SAFE">SAFE</span> <strong>Score &lt; 30</strong></div>
                        </div>
                    </div>
                    
                    <div style="flex:2;">
                        <div style="font-weight:600; margin-bottom:10px; color:#344054;">2. Risk Rules (Points Added)</div>
                        <table style="width:100%; font-size:13px;">
                            <tr style="border-bottom:1px solid #eee;">
                                <td style="padding:4px 0;"><strong>High Urgency</strong></td>
                                <td style="color:#b42318; font-weight:bold;">+40 pts</td>
                                <td style="color:#667085;">Phrases like "Immediate Action Required"</td>
                            </tr>
                            <tr style="border-bottom:1px solid #eee;">
                                <td style="padding:4px 0;"><strong>Reply-To Mismatch</strong></td>
                                <td style="color:#b54708; font-weight:bold;">+30 pts</td>
                                <td style="color:#667085;">Sender email ≠ Reply-To email</td>
                            </tr>
                            <tr style="border-bottom:1px solid #eee;">
                                <td style="padding:4px 0;"><strong>URL Shortener</strong></td>
                                <td style="color:#b54708; font-weight:bold;">+20 pts</td>
                                <td style="color:#667085;">Hidden destination (e.g., bit.ly, short.ly)</td>
                            </tr>
                            <tr>
                                <td style="padding:4px 0;"><strong>Auth Failure</strong></td>
                                <td style="color:#b42318; font-weight:bold;">Variable</td>
                                <td style="color:#667085;">SPF/DKIM/DMARC failure</td>
                            </tr>
                        </table>
                    </div>
                </div>
                <div style="font-size:12px; color:#667085; background:#f2f4f7; padding:10px; border-radius:6px;">
                    <strong>💡 Worst-Link Logic:</strong> If an email fails Authentication AND uses High Urgency, score is elevated to <strong>85 (Critical Phishing)</strong> automatically.
                </div>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th style="width: 25%">Subject</th>
                        <th style="width: 20%">Sender</th> <!-- New Column -->
                        <th style="width: 10%">Verdict</th>
                        <th style="width: 10%">Score</th>
                        <th style="width: 45%">Risk Factors</th>
                    </tr>
                </thead>
                <tbody>
                    <!--ROWS_PLACEHOLDER-->
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """

    rows = ""
    for res in results:
        # Determine score color class
        score_class = "score-low"
        if res['score'] >= 50: score_class = "score-high"
        elif res['score'] >= 30: score_class = "score-med"

        # Format reasons list
        reasons_html = ""
        if res['reasons']:
            reasons_html = "<ul>" + "".join([f"<li>{r}</li>" for r in res['reasons']]) + "</ul>"
        else:
            reasons_html = "<span style='color:#98a2b3; font-size:13px;'>No specific risks detected</span>"
        
        # Handle missing sender if old result
        sender = res.get('sender', 'Unknown')

        # Extract Subject from headers if available, or fallback
        subject = res.get('subject', 'No Subject')
        
        # Format Date/ID for tooltip
        email_id = res['id']

        rows += f"""
        <tr>
            <td><strong>{subject}</strong></td>
            <td>{sender}</td>
            <td><span class="badge {res['verdict']}">{res['verdict']}</span></td>
            <td class="{score_class}">{res['score']}/100</td>
            <td>{reasons_html}</td>
        </tr>
        """

    final_html = html_template.replace("<!--ROWS_PLACEHOLDER-->", rows)
    
    # Save the file
    output_path = os.path.join(output_dir, "report.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_html)
    
    return output_path