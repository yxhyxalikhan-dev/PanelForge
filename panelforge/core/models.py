"""
PanelForge Core Data Models
Author: Yahya Ali Khan
License: MIT
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
import json


@dataclass
class DialogueItem:
    speaker: str
    text: str
    bubble_type: str = "speech"  # speech, thought, shout, whisper
    placement: str = "auto"  # auto, top_left, top_right, bottom_left, bottom_right


@dataclass
class PanelSpec:
    panel_id: int
    prompt: str
    setting: str
    characters: List[str] = field(default_factory=list)
    action: str = ""
    dialogue: List[DialogueItem] = field(default_factory=list)
    camera_angle: str = "medium"  # close_up, medium, wide, dramatic
    aspect_ratio: str = "square"  # wide, tall, square
    generated_image_path: Optional[str] = None


@dataclass
class PageSpec:
    page_number: int
    template_name: str
    panels: List[PanelSpec] = field(default_factory=list)
    rendered_page_path: Optional[str] = None


@dataclass
class ProjectState:
    title: str
    author: str
    art_style: str = "classic_bw"  # classic_bw, modern_color
    pages: List[PageSpec] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)

    @classmethod
    def from_json(cls, data_str: str) -> "ProjectState":
        data = json.loads(data_str)
        pages = []
        for p in data.get("pages", []):
            panels = []
            for pan in p.get("panels", []):
                dialogues = [DialogueItem(**d) for d in pan.get("dialogue", [])]
                pan_copy = dict(pan)
                pan_copy["dialogue"] = dialogues
                panels.append(PanelSpec(**pan_copy))
            p_copy = dict(p)
            p_copy["panels"] = panels
            pages.append(PageSpec(**p_copy))
        return cls(
            title=data.get("title", "Untitled Story"),
            author=data.get("author", "Yahya Ali Khan"),
            art_style=data.get("art_style", "classic_bw"),
            pages=pages,
            metadata=data.get("metadata", {})
        )
