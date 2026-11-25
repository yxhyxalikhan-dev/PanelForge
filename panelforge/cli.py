"""
PanelForge Command Line Interface & Demo Runner
Author: Yahya Ali Khan
License: MIT
"""

import sys
import os
import argparse
from pathlib import Path
from panelforge.core.parser import StoryParser
from panelforge.generators.art import ProceduralSketchGenerator, APIDiffusionGenerator
from panelforge.export.compositor import PageCompositor, PDFExporter


def run_pipeline(
    story_path: str,
    output_dir: str = "output",
    art_style: str = "classic_bw",
    use_api: bool = False,
    title: str = "A Hunter's Dawn"
):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print(" PanelForge - AI Story-to-Manga/Comic Engine")
    print(f" Author: Yahya Ali Khan | Style: {art_style}")
    print("=" * 60)

    # 1. Read input story
    story_file = Path(story_path)
    if not story_file.exists():
        print(f"❌ Error: Story file '{story_path}' not found!")
        sys.exit(1)

    story_text = story_file.read_text(encoding="utf-8")
    print(f"📖 Loaded story '{story_file.name}' ({len(story_text.split())} words)")

    # 2. Parse into panels & pages
    parser = StoryParser()
    project = parser.parse_story(story_text, title=title, author="Yahya Ali Khan", art_style=art_style)
    print(f"✂️  Parsed story into {len(project.pages)} pages ({sum(len(p.panels) for p in project.pages)} panels total)")

    # Save state
    state_file = output_path / "project_state.json"
    state_file.write_text(project.to_json(), encoding="utf-8")
    print(f"💾 Saved project state to '{state_file}'")

    # 3. Setup art generator
    if use_api:
        print("🎨 Using API Diffusion Generator (with procedural fallback)...")
        generator = APIDiffusionGenerator()
    else:
        print("🎨 Using Procedural Manga Art Generator (clean B&W screentones)...")
        generator = ProceduralSketchGenerator()

    compositor = PageCompositor(generator)

    rendered_page_paths = []

    # 4. Render Pages
    for page in project.pages:
        print(f"  🖼️  Rendering Page {page.page_number} ({page.template_name}, {len(page.panels)} panels)...")
        page_img = compositor.render_page(page, art_style=art_style)
        page_filename = f"page_{page.page_number:02d}.png"
        page_path = output_path / page_filename
        page_img.save(str(page_path), "PNG")
        page.rendered_page_path = str(page_path)
        rendered_page_paths.append(str(page_path))
        print(f"     ✅ Saved: {page_path}")

    # 5. Export PDF
    pdf_filename = f"{title.replace(' ', '_').lower()}.pdf"
    pdf_path = output_path / pdf_filename
    print(f"📄 Compiling pages into publication PDF...")
    PDFExporter.export_pdf(rendered_page_paths, str(pdf_path), title=title)
    print(f"🎉 SUCCESS! Final PDF generated at: {pdf_path}")
    print("=" * 60)
    return str(pdf_path), rendered_page_paths


def main():
    parser = argparse.ArgumentParser(description="PanelForge - Story to Manga/Comic Generator")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Run command
    run_parser = subparsers.add_parser("run", help="Convert story text into manga pages and PDF")
    run_parser.add_argument("story", help="Path to story text file")
    run_parser.add_argument("--output", default="output", help="Output directory")
    run_parser.add_argument("--style", default="classic_bw", choices=["classic_bw", "modern_color"], help="Art visual style")
    run_parser.add_argument("--api", action="store_true", help="Use external image API if configured")
    run_parser.add_argument("--title", default="A Hunter's Dawn", help="Comic title")

    # Demo command
    subparsers.add_parser("demo", help="Run quick demo using built-in original sample story")

    # Web UI command
    subparsers.add_parser("web", help="Launch interactive web studio server")

    args = parser.parse_args()

    if args.command == "demo" or len(sys.argv) == 1:
        # Default demo
        base_dir = Path(__file__).parent.parent
        demo_story = base_dir / "examples" / "story.txt"
        out_dir = base_dir / "output"
        run_pipeline(str(demo_story), output_dir=str(out_dir), art_style="classic_bw", title="A Hunter's Dawn")

    elif args.command == "run":
        run_pipeline(args.story, output_dir=args.output, art_style=args.style, use_api=args.api, title=args.title)

    elif args.command == "web":
        import uvicorn
        print("🌐 Starting PanelForge Web Server on http://127.0.0.1:8000 ...")
        uvicorn.run("panelforge.web.app:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    main()
