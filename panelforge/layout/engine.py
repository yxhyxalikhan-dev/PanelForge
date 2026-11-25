"""
PanelForge Page Layout System
Author: Yahya Ali Khan
License: MIT
"""

from dataclasses import dataclass
from typing import List, Dict, Tuple


@dataclass
class PanelBox:
    x: int
    y: int
    width: int
    height: int

    @property
    def bounds(self) -> Tuple[int, int, int, int]:
        return (self.x, self.y, self.x + self.width, self.y + self.height)


class LayoutEngine:
    """
    Computes exact pixel coordinates for panels within standard manga page dimensions.
    Standard A4 / Manga Page: 1600 x 2400 (or 1200 x 1800 for high quality fast rendering).
    """

    PAGE_WIDTH = 1200
    PAGE_HEIGHT = 1800
    MARGIN_X = 60
    MARGIN_Y = 80
    GUTTER = 24  # space between panels

    def get_layout(self, template_name: str, panel_count: int) -> List[PanelBox]:
        content_w = self.PAGE_WIDTH - (2 * self.MARGIN_X)
        content_h = self.PAGE_HEIGHT - (2 * self.MARGIN_Y)

        if panel_count == 1 or template_name == "full_splash":
            return [PanelBox(self.MARGIN_X, self.MARGIN_Y, content_w, content_h)]

        if panel_count == 2 or template_name == "two_vertical":
            h = (content_h - self.GUTTER) // 2
            return [
                PanelBox(self.MARGIN_X, self.MARGIN_Y, content_w, h),
                PanelBox(self.MARGIN_X, self.MARGIN_Y + h + self.GUTTER, content_w, h),
            ]

        if panel_count == 3 or template_name == "three_classic":
            # 1 wide top panel (45%), 2 side-by-side bottom panels (55%)
            top_h = int((content_h - self.GUTTER) * 0.45)
            bottom_h = content_h - self.GUTTER - top_h
            bottom_w = (content_w - self.GUTTER) // 2
            return [
                PanelBox(self.MARGIN_X, self.MARGIN_Y, content_w, top_h),
                PanelBox(self.MARGIN_X, self.MARGIN_Y + top_h + self.GUTTER, bottom_w, bottom_h),
                PanelBox(self.MARGIN_X + bottom_w + self.GUTTER, self.MARGIN_Y + top_h + self.GUTTER, bottom_w, bottom_h),
            ]

        if panel_count == 4 or template_name == "four_grid":
            # 2x2 symmetrical grid
            w = (content_w - self.GUTTER) // 2
            h = (content_h - self.GUTTER) // 2
            return [
                PanelBox(self.MARGIN_X, self.MARGIN_Y, w, h),
                PanelBox(self.MARGIN_X + w + self.GUTTER, self.MARGIN_Y, w, h),
                PanelBox(self.MARGIN_X, self.MARGIN_Y + h + self.GUTTER, w, h),
                PanelBox(self.MARGIN_X + w + self.GUTTER, self.MARGIN_Y + h + self.GUTTER, w, h),
            ]

        if panel_count >= 5 or template_name == "five_dynamic":
            # Top panel wide, middle row 2 panels, bottom row 2 panels
            top_h = int(content_h * 0.35)
            rem_h = content_h - top_h - (2 * self.GUTTER)
            row_h = rem_h // 2
            w = (content_w - self.GUTTER) // 2
            return [
                PanelBox(self.MARGIN_X, self.MARGIN_Y, content_w, top_h),
                PanelBox(self.MARGIN_X, self.MARGIN_Y + top_h + self.GUTTER, w, row_h),
                PanelBox(self.MARGIN_X + w + self.GUTTER, self.MARGIN_Y + top_h + self.GUTTER, w, row_h),
                PanelBox(self.MARGIN_X, self.MARGIN_Y + top_h + (2 * self.GUTTER) + row_h, w, row_h),
                PanelBox(self.MARGIN_X + w + self.GUTTER, self.MARGIN_Y + top_h + (2 * self.GUTTER) + row_h, w, row_h),
            ]

        # Default fallback: uniform vertical stack
        h = (content_h - ((panel_count - 1) * self.GUTTER)) // panel_count
        boxes = []
        for i in range(panel_count):
            y = self.MARGIN_Y + i * (h + self.GUTTER)
            boxes.append(PanelBox(self.MARGIN_X, y, content_w, h))
        return boxes
