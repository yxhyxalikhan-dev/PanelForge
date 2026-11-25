"""
PanelForge Page Compositor and PDF Exporter
Author: Yahya Ali Khan
License: MIT
"""

from PIL import Image, ImageDraw, ImageFont
import os
from typing import List
from panelforge.core.models import PageSpec, ProjectState
from panelforge.layout.engine import LayoutEngine
from panelforge.generators.art import BaseArtworkGenerator
from panelforge.lettering.engine import LetteringEngine
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


class PageCompositor:
    """
    Assembles generated panel artworks, overlays lettering speech bubbles,
    and paints them cleanly onto full manga-proportioned pages.
    """

    def __init__(self, art_generator: BaseArtworkGenerator, lettering_engine: LetteringEngine = None):
        self.art_generator = art_generator
        self.lettering_engine = lettering_engine or LetteringEngine()
        self.layout_engine = LayoutEngine()

    def render_page(self, page_spec: PageSpec, art_style: str = "classic_bw") -> Image.Image:
        pw = self.layout_engine.PAGE_WIDTH
        ph = self.layout_engine.PAGE_HEIGHT

        # Pure clean white canvas for crisp gutters
        page_img = Image.new("RGB", (pw, ph), (255, 255, 255))
        draw = ImageDraw.Draw(page_img)

        # Compute panel layout boxes
        boxes = self.layout_engine.get_layout(page_spec.template_name, len(page_spec.panels))

        for idx, (panel, box) in enumerate(zip(page_spec.panels, boxes)):
            # 1. Generate artwork for panel
            panel_art = self.art_generator.generate_panel(
                prompt=panel.prompt,
                width=box.width,
                height=box.height,
                style=art_style,
                characters=panel.characters,
                camera_angle=panel.camera_angle
            )

            # 2. Add speech bubbles / lettering
            for b_idx, dialogue in enumerate(panel.dialogue):
                panel_art = self.lettering_engine.draw_bubble(panel_art, dialogue, bubble_index=b_idx)

            # 3. Paste panel onto full page
            page_img.paste(panel_art, (box.x, box.y))

            # 4. Draw outer ink border
            draw.rectangle(box.bounds, outline=(15, 15, 15), width=3)

        # Add page number at bottom right
        font_path = self.lettering_engine.font_path
        try:
            page_font = ImageFont.truetype(font_path, 16)
        except Exception:
            page_font = ImageFont.load_default()

        p_str = f"- {page_spec.page_number} -"
        draw.text((pw // 2 - 15, ph - 45), p_str, font=page_font, fill=(80, 80, 80))

        return page_img


class PDFExporter:
    """
    Exports a sequence of rendered page images into an optimized, high-fidelity PDF.
    """

    @staticmethod
    def export_pdf(image_paths: List[str], output_pdf_path: str, title: str = "PanelForge Graphic Novel"):
        os.makedirs(os.path.dirname(os.path.abspath(output_pdf_path)), exist_ok=True)
        c = canvas.Canvas(output_pdf_path, pagesize=A4)
        c.setTitle(title)
        c.setAuthor("Yahya Ali Khan")

        a4_w, a4_h = A4

        for img_path in image_paths:
            # Draw image spanning A4 dimensions cleanly
            c.drawImage(img_path, 0, 0, width=a4_w, height=a4_h)
            c.showPage()

        c.save()
        return output_pdf_path
