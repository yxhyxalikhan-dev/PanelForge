"""
PanelForge Story Parser - Parses raw text into scenes, actions, and dialogue.
Author: Yahya Ali Khan
License: MIT
"""

import re
from typing import List, Tuple
from panelforge.core.models import PanelSpec, DialogueItem, PageSpec, ProjectState


class StoryParser:
    """
    Analyzes raw story text paragraphs and structures them into panels and dialogue items.
    """

    def __init__(self):
        # Regex to detect dialogue lines like 'Ren: "We cannot stay here!"' or 'Ren said, "Wait!"'
        self.dialogue_pattern = re.compile(
            r'([A-Z][a-zA-Z0-9_\s]{1,15})\s*(?::|said,|whispered,|shouted,|screamed,)?\s*["“]([^"”]+)["”]'
        )

    def extract_dialogue(self, text: str) -> Tuple[str, List[DialogueItem]]:
        dialogues = []
        clean_text = text

        for match in self.dialogue_pattern.finditer(text):
            speaker = match.group(1).strip()
            spoken_text = match.group(2).strip()
            bubble_type = "speech"
            if "shouted" in match.group(0).lower() or "!" in spoken_text and len(spoken_text) < 25:
                bubble_type = "shout"
            elif "whispered" in match.group(0).lower():
                bubble_type = "whisper"

            dialogues.append(DialogueItem(speaker=speaker, text=spoken_text, bubble_type=bubble_type))

        # Also strip out the quotes from narration
        narrative = self.dialogue_pattern.sub("", text).strip()
        narrative = re.sub(r'\s+', ' ', narrative)
        return narrative, dialogues

    def parse_story(self, raw_text: str, title: str = "A Hunter's Dawn", author: str = "Yahya Ali Khan", art_style: str = "classic_bw") -> ProjectState:
        # Split by double newlines or major paragraph chunks
        raw_paragraphs = [p.strip() for p in raw_text.strip().split("\n\n") if p.strip()]

        if not raw_paragraphs:
            raw_paragraphs = [raw_text.strip()]

        panels: List[PanelSpec] = []
        panel_id = 1

        for p_idx, para in enumerate(raw_paragraphs):
            narrative, dialogues = self.extract_dialogue(para)
            if not narrative and not dialogues:
                continue

            # Determine camera angle based on keywords
            camera = "medium"
            para_lower = para.lower()
            if any(k in para_lower for k in ["sky", "valley", "city", "horizon", "wide", "distance", "world", "tower"]):
                camera = "wide"
            elif any(k in para_lower for k in ["eyes", "whispered", "gazed", "stared", "breath", "tears", "face", "clenched"]):
                camera = "close_up"
            elif any(k in para_lower for k in ["struck", "shattered", "jumped", "leaped", "blaze", "strike", "explosion", "blade"]):
                camera = "dramatic"

            # Detect main character names
            characters = []
            for name in ["Ren", "Aoi", "Kael", "Mira", "Sora", "Elena", "Marcus", "Hana"]:
                if name in para:
                    characters.append(name)
            if not characters and dialogues:
                characters = [d.speaker for d in dialogues]

            prompt_desc = f"{camera.replace('_', ' ')} shot. {narrative[:160]}"
            panels.append(
                PanelSpec(
                    panel_id=panel_id,
                    prompt=prompt_desc,
                    setting=narrative[:80],
                    characters=characters,
                    action=narrative,
                    dialogue=dialogues,
                    camera_angle=camera,
                )
            )
            panel_id += 1

        # Package panels into pages (e.g., 3-4 panels per page)
        pages: List[PageSpec] = []
        panels_per_page_options = [3, 4, 3, 4]
        current_idx = 0
        page_num = 1

        while current_idx < len(panels):
            quota = panels_per_page_options[(page_num - 1) % len(panels_per_page_options)]
            batch = panels[current_idx: current_idx + quota]
            if len(batch) == 1:
                tmpl = "full_splash"
            elif len(batch) == 2:
                tmpl = "two_vertical"
            elif len(batch) == 3:
                tmpl = "three_classic"
            elif len(batch) == 4:
                tmpl = "four_grid"
            else:
                tmpl = "five_dynamic"

            pages.append(PageSpec(page_number=page_num, template_name=tmpl, panels=batch))
            current_idx += quota
            page_num += 1

        return ProjectState(title=title, author=author, art_style=art_style, pages=pages)
