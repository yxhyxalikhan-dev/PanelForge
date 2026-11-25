"""
PanelForge Intelligent Lettering & Speech Bubble Engine
Author: Yahya Ali Khan
License: MIT
"""

from PIL import Image, ImageDraw, ImageFont
import math
from typing import List, Tuple
from panelforge.core.models import DialogueItem


class LetteringEngine:
    """
    Renders professional comic speech balloons, thought clouds, and shout bubbles
    with automatic word-wrapping, multi-line font scaling, and tail pointers.
    """

    def __init__(self):
        # Locate system font or fallback
        self.font_path = self._find_font()

    def _find_font(self) -> str:
        candidates = [
            "/System/Library/Fonts/Supplemental/Comic Sans MS.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/ArialHB.ttc",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/System/Library/Fonts/Geneva.ttf",
        ]
        for c in candidates:
            import os
            if os.path.exists(c):
                return c
        return "Arial"

    def _get_font(self, size: int) -> ImageFont.FreeTypeFont:
        try:
            return ImageFont.truetype(self.font_path, size)
        except Exception:
            return ImageFont.load_default()

    def wrap_text(self, text: str, font: ImageFont.ImageFont, max_width: int, draw: ImageDraw.Draw) -> List[str]:
        words = text.split()
        if not words:
            return []

        lines = []
        current_line = []

        for word in words:
            test_line = " ".join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            line_w = bbox[2] - bbox[0]
            if line_w <= max_width or not current_line:
                current_line.append(word)
            else:
                lines.append(" ".join(current_line))
                current_line = [word]

        if current_line:
            lines.append(" ".join(current_line))

        return lines

    def auto_fit_text(self, text: str, target_width: int, target_height: int) -> Tuple[ImageFont.ImageFont, List[str], int, int]:
        """
        Dynamically finds the best font size to fill the speech bubble proportionally.
        """
        dummy_img = Image.new("RGBA", (10, 10))
        draw = ImageDraw.Draw(dummy_img)

        best_font = None
        best_lines = []
        best_w = 0
        best_h = 0

        # Try font sizes from 26 down to 14
        for size in range(26, 13, -2):
            font = self._get_font(size)
            lines = self.wrap_text(text, font, target_width - 24, draw)
            if not lines:
                continue

            line_height = int(size * 1.25)
            total_h = len(lines) * line_height

            max_line_w = max((draw.textbbox((0, 0), line, font=font)[2] - draw.textbbox((0, 0), line, font=font)[0]) for line in lines)

            if total_h <= (target_height - 20) and max_line_w <= (target_width - 20):
                return font, lines, max_line_w, total_h

        # Fallback to smallest readable
        font = self._get_font(14)
        lines = self.wrap_text(text, font, target_width - 20, draw)
        line_height = int(14 * 1.25)
        total_h = len(lines) * line_height
        max_line_w = max((draw.textbbox((0, 0), line, font=font)[2] - draw.textbbox((0, 0), line, font=font)[0]) for line in lines)
        return font, lines, max_line_w, total_h

    def draw_bubble(
        self,
        panel_img: Image.Image,
        dialogue: DialogueItem,
        bubble_index: int = 0
    ) -> Image.Image:
        pw, ph = panel_img.size
        # Bubble max bounding constraints
        bubble_max_w = int(pw * 0.48)
        bubble_max_h = int(ph * 0.38)

        # 1. Fit text
        full_text = dialogue.text.upper()
        font, lines, text_w, text_h = self.auto_fit_text(full_text, bubble_max_w, bubble_max_h)

        pad_x = 18
        pad_y = 14
        b_width = max(text_w + (2 * pad_x), 90)
        b_height = max(text_h + (2 * pad_y), 50)

        # 2. Bubble Placement Strategy
        # Distribute dialogue bubbles cleanly so they don't block the visual center
        if dialogue.placement == "top_left" or (dialogue.placement == "auto" and bubble_index == 0):
            bx = 18
            by = 18
            tail_dir = "bottom_right"
        elif dialogue.placement == "top_right" or (dialogue.placement == "auto" and bubble_index == 1):
            bx = pw - b_width - 18
            by = 18
            tail_dir = "bottom_left"
        elif dialogue.placement == "bottom_left":
            bx = 18
            by = ph - b_height - 18
            tail_dir = "top_right"
        else:
            bx = pw - b_width - 18
            by = ph - b_height - 18
            tail_dir = "top_left"

        overlay = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        bubble_rect = [bx, by, bx + b_width, by + b_height]

        # 3. Draw bubble shape depending on type
        bg_col = (255, 255, 255, 255)
        outline_col = (10, 10, 10, 255)

        if dialogue.bubble_type == "shout":
            # Spiky jagged polygon for shout/explosive dialogue
            spikes = 16
            cx = bx + b_width // 2
            cy = by + b_height // 2
            rx = b_width // 2
            ry = b_height // 2
            poly_pts = []
            for i in range(spikes):
                ang = (i / spikes) * 2 * math.pi
                r_mult = 1.2 if (i % 2 == 1) else 0.88
                px = cx + math.cos(ang) * (rx * r_mult)
                py = cy + math.sin(ang) * (ry * r_mult)
                poly_pts.append((px, py))
            draw.polygon(poly_pts, fill=bg_col, outline=outline_col, width=3)

        elif dialogue.bubble_type == "thought":
            # Cloud-like overlapping circles
            draw.rounded_rectangle(bubble_rect, radius=18, fill=bg_col, outline=outline_col, width=2)
            # Little thought bubbles trailing down
            t_cx = bx + b_width // 2
            t_cy = by + b_height + 10
            draw.ellipse([t_cx - 6, t_cy, t_cx + 6, t_cy + 12], fill=bg_col, outline=outline_col, width=2)
            draw.ellipse([t_cx + 8, t_cy + 14, t_cx + 16, t_cy + 22], fill=bg_col, outline=outline_col, width=2)

        else:  # Standard speech balloon with pointer tail
            draw.rounded_rectangle(bubble_rect, radius=14, fill=bg_col, outline=outline_col, width=2)
            # Draw tail
            if tail_dir == "bottom_right":
                tail_pts = [
                    (bx + int(b_width * 0.65), by + b_height),
                    (bx + int(b_width * 0.80), by + b_height + 22),
                    (bx + int(b_width * 0.85), by + b_height),
                ]
            elif tail_dir == "bottom_left":
                tail_pts = [
                    (bx + int(b_width * 0.15), by + b_height),
                    (bx + int(b_width * 0.10), by + b_height + 22),
                    (bx + int(b_width * 0.35), by + b_height),
                ]
            elif tail_dir == "top_right":
                tail_pts = [
                    (bx + int(b_width * 0.70), by),
                    (bx + int(b_width * 0.82), by - 18),
                    (bx + int(b_width * 0.88), by),
                ]
            else:
                tail_pts = [
                    (bx + int(b_width * 0.12), by),
                    (bx + int(b_width * 0.18), by - 18),
                    (bx + int(b_width * 0.30), by),
                ]
            draw.polygon(tail_pts, fill=bg_col, outline=outline_col)
            # Overwrite the inner line of tail
            draw.line([(tail_pts[0][0] + 1, tail_pts[0][1]), (tail_pts[2][0] - 1, tail_pts[2][1])], fill=bg_col, width=3)

        # 4. Render dialogue text inside bubble
        curr_y = by + pad_y
        line_step = int(font.size * 1.25)
        text_color = (10, 10, 15, 255)

        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            lw = bbox[2] - bbox[0]
            curr_x = bx + (b_width - lw) // 2
            draw.text((curr_x, curr_y), line, font=font, fill=text_color)
            curr_y += line_step

        # Speaker label header (small tag)
        if dialogue.speaker:
            s_font = self._get_font(11)
            s_tag = dialogue.speaker.upper()
            draw.text((bx + 10, by - 13), s_tag, font=s_font, fill=(30, 30, 40, 255))

        return Image.alpha_composite(panel_img.convert("RGBA"), overlay).convert("RGB")
