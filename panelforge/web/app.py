"""
PanelForge Interactive FastAPI Web Studio
Author: Yahya Ali Khan
License: MIT
"""

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import shutil
from panelforge.cli import run_pipeline

app = FastAPI(title="PanelForge Manga & Comic Studio", version="0.1.0")

BASE_DIR = Path(__file__).parent.parent.parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/", response_class=HTMLResponse)
def index():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PanelForge - AI Story-to-Manga Studio</title>
        <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap" rel="stylesheet">
        <style>
            :root {
                --bg: #0d1117;
                --surface: #161b22;
                --border: #30363d;
                --accent: #e5534b;
                --text: #f0f6fc;
                --subtext: #8b949e;
            }
            body {
                margin: 0;
                padding: 0;
                font-family: 'Space Grotesk', sans-serif;
                background-color: var(--bg);
                color: var(--text);
            }
            .header {
                padding: 24px 48px;
                background: var(--surface);
                border-bottom: 1px solid var(--border);
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .logo {
                font-size: 26px;
                font-weight: 700;
                color: var(--text);
                display: flex;
                align-items: center;
                gap: 12px;
            }
            .logo span {
                color: var(--accent);
            }
            .container {
                max-width: 1100px;
                margin: 40px auto;
                padding: 0 24px;
            }
            .hero {
                text-align: center;
                margin-bottom: 40px;
            }
            .hero h1 {
                font-size: 40px;
                margin-bottom: 12px;
            }
            .hero p {
                color: var(--subtext);
                font-size: 18px;
            }
            .card {
                background: var(--surface);
                border: 1px solid var(--border);
                border-radius: 12px;
                padding: 32px;
                box-shadow: 0 8px 24px rgba(0,0,0,0.4);
            }
            textarea {
                width: 100%;
                height: 180px;
                background: #090d13;
                border: 1px solid var(--border);
                border-radius: 8px;
                color: var(--text);
                font-family: inherit;
                font-size: 15px;
                padding: 16px;
                box-sizing: border-box;
                resize: vertical;
            }
            .controls {
                display: flex;
                gap: 20px;
                margin-top: 20px;
                align-items: center;
            }
            select, input[type="text"] {
                background: #090d13;
                border: 1px solid var(--border);
                color: var(--text);
                padding: 12px 16px;
                border-radius: 8px;
                font-size: 15px;
            }
            .btn {
                background: var(--accent);
                color: #fff;
                border: none;
                padding: 14px 28px;
                font-size: 16px;
                font-weight: 600;
                border-radius: 8px;
                cursor: pointer;
                transition: transform 0.15s ease;
            }
            .btn:hover {
                transform: translateY(-2px);
                opacity: 0.95;
            }
            .results {
                margin-top: 40px;
            }
            .gallery {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 24px;
                margin-top: 24px;
            }
            .gallery-item {
                background: var(--surface);
                border: 1px solid var(--border);
                border-radius: 8px;
                overflow: hidden;
            }
            .gallery-item img {
                width: 100%;
                display: block;
            }
            .gallery-caption {
                padding: 12px;
                text-align: center;
                font-size: 14px;
                color: var(--subtext);
            }
            .badge {
                display: inline-block;
                background: #238636;
                color: #fff;
                padding: 4px 10px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 600;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <div class="logo">Panel<span>Forge</span></div>
            <div><span class="badge">Engine v0.1.0</span> By Yahya Ali Khan</div>
        </div>

        <div class="container">
            <div class="hero">
                <h1>Transform Stories into Comic Pages</h1>
                <p>Automated panel pacing, character staging, speech balloon lettering, and publication-ready PDF.</p>
            </div>

            <div class="card">
                <form action="/generate" method="post">
                    <label style="display:block; margin-bottom:8px; font-weight:600;">Your Story Script / Prose:</label>
                    <textarea name="story_text" placeholder="Write or paste your short story here... Include dialogue like: Ren: 'The shadows are closing in!'"></textarea>

                    <div class="controls">
                        <div>
                            <label style="display:block; font-size:13px; color:var(--subtext); margin-bottom:4px;">Title:</label>
                            <input type="text" name="title" value="A Hunter's Dawn">
                        </div>
                        <div>
                            <label style="display:block; font-size:13px; color:var(--subtext); margin-bottom:4px;">Visual Style:</label>
                            <select name="style">
                                <option value="classic_bw">Classic Manga (B&W Screentones)</option>
                                <option value="modern_color">Webtoon Color Tone</option>
                            </select>
                        </div>
                        <div style="margin-left:auto; margin-top:20px;">
                            <button type="submit" class="btn">⚡ Generate Manga</button>
                        </div>
                    </div>
                </form>
            </div>

            <div class="results">
                <h3>Latest Rendered Pages</h3>
                <div class="gallery">
                    <div class="gallery-item">
                        <img src="/output/page_01.png" onerror="this.src='https://placehold.co/600x900/161b22/f0f6fc?text=Page+1+Preview'">
                        <div class="gallery-caption">Page 1</div>
                    </div>
                    <div class="gallery-item">
                        <img src="/output/page_02.png" onerror="this.src='https://placehold.co/600x900/161b22/f0f6fc?text=Page+2+Preview'">
                        <div class="gallery-caption">Page 2</div>
                    </div>
                    <div class="gallery-item">
                        <img src="/output/page_03.png" onerror="this.src='https://placehold.co/600x900/161b22/f0f6fc?text=Page+3+Preview'">
                        <div class="gallery-caption">Page 3</div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.post("/generate")
def generate_from_web(story_text: str = Form(...), title: str = Form("A Hunter's Dawn"), style: str = Form("classic_bw")):
    temp_story = OUTPUT_DIR / "uploaded_story.txt"
    temp_story.write_text(story_text, encoding="utf-8")
    pdf_path, pages = run_pipeline(str(temp_story), output_dir=str(OUTPUT_DIR), art_style=style, title=title)
    return JSONResponse({
        "status": "success",
        "title": title,
        "pdf_download": f"/download/{Path(pdf_path).name}",
        "pages_generated": len(pages)
    })


@app.get("/output/{filename}")
def get_output_file(filename: str):
    file_path = OUTPUT_DIR / filename
    if file_path.exists():
        return FileResponse(file_path)
    return JSONResponse({"error": "File not found"}, status_code=404)


@app.get("/download/{filename}")
def download_pdf(filename: str):
    file_path = OUTPUT_DIR / filename
    if file_path.exists():
        return FileResponse(file_path, filename=filename, media_type="application/pdf")
    return JSONResponse({"error": "PDF not found"}, status_code=404)
