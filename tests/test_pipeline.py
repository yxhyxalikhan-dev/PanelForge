"""
Unit tests for PanelForge Layout, Lettering, and PDF Export
Author: Yahya Ali Khan
License: MIT
"""

import pytest
import os
from PIL import Image, ImageDraw
from panelforge.core.models import DialogueItem, PanelSpec, PageSpec
from panelforge.core.parser import StoryParser
from panelforge.layout.engine import LayoutEngine, PanelBox
from panelforge.lettering.engine import LetteringEngine
from panelforge.generators.art import ProceduralSketchGenerator
from panelforge.export.compositor import PageCompositor, PDFExporter


def test_story_parser_dialogue_extraction():
    parser = StoryParser()
    sample = 'Ren: "We must hurry!" whispered Ren. The storm arrived.'
    narrative, dialogues = parser.extract_dialogue(sample)

    assert len(dialogues) >= 1
    assert dialogues[0].speaker == "Ren"
    assert "We must hurry!" in dialogues[0].text
    assert "The storm arrived." in narrative


def test_layout_engine_templates():
    engine = LayoutEngine()

    # 1 panel splash
    boxes_1 = engine.get_layout("full_splash", 1)
    assert len(boxes_1) == 1
    assert boxes_1[0].width == engine.PAGE_WIDTH - (2 * engine.MARGIN_X)

    # 2 panel vertical
    boxes_2 = engine.get_layout("two_vertical", 2)
    assert len(boxes_2) == 2

    # 3 panel classic
    boxes_3 = engine.get_layout("three_classic", 3)
    assert len(boxes_3) == 3

    # 4 panel grid
    boxes_4 = engine.get_layout("four_grid", 4)
    assert len(boxes_4) == 4

    # Ensure no zero-area boxes
    for b in boxes_4:
        assert b.width > 100
        assert b.height > 100


def test_lettering_engine_auto_fit_and_render():
    engine = LetteringEngine()
    test_img = Image.new("RGB", (400, 400), (200, 200, 200))
    dialogue = DialogueItem(speaker="Ren", text="The barrier is breaking down!", bubble_type="shout")

    result = engine.draw_bubble(test_img, dialogue, bubble_index=0)
    assert result is not None
    assert result.size == (400, 400)


def test_procedural_art_generator():
    gen = ProceduralSketchGenerator()
    bw_panel = gen.generate_panel("Wide angle cliffside", 300, 200, style="classic_bw", camera_angle="wide")
    assert bw_panel.size == (300, 200)

    color_panel = gen.generate_panel("Dramatic strike", 300, 200, style="modern_color", camera_angle="dramatic")
    assert color_panel.size == (300, 200)


def test_full_page_composition_and_pdf(tmp_path):
    gen = ProceduralSketchGenerator()
    comp = PageCompositor(gen)

    dialogues = [DialogueItem(speaker="Hero", text="Let's do this!")]
    panels = [
        PanelSpec(panel_id=1, prompt="Shot 1", setting="Courtyard", dialogue=dialogues),
        PanelSpec(panel_id=2, prompt="Shot 2", setting="Gate", dialogue=[]),
        PanelSpec(panel_id=3, prompt="Shot 3", setting="Sky", dialogue=[]),
    ]
    page = PageSpec(page_number=1, template_name="three_classic", panels=panels)

    rendered_page = comp.render_page(page, art_style="classic_bw")
    assert rendered_page.size == (LayoutEngine.PAGE_WIDTH, LayoutEngine.PAGE_HEIGHT)

    # Save temp image and export PDF
    img_path = str(tmp_path / "test_page_1.png")
    rendered_page.save(img_path)

    pdf_path = str(tmp_path / "test_comic.pdf")
    PDFExporter.export_pdf([img_path], pdf_path, title="Test Comic")

    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 1000
