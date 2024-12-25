"""Script for converting WHUW warband rules to two-sided printable format."""
import math
import sys
import pymupdf
from pymupdf import Rect

# DPI for edge detection and conversions
DPI = 600
PT_PER_INCH = 72
PIXEL_PER_PT = DPI / PT_PER_INCH

# Every coordinate constant is in points (pt)

# Warscroll postition on original PDF
UPPER_SCROLL_X0 = 87.8
UPPER_SCROLL_Y0 = 79.5
UPPER_SCROLL_X1 = 507.5
UPPER_SCROLL_Y1 = 377.4
SCROLL_Y_OFFSET = 450.3 - UPPER_SCROLL_Y0  # 450

SCROLL_WIDTH = UPPER_SCROLL_X1 - UPPER_SCROLL_X0
SCROLL_HEIGHT = UPPER_SCROLL_Y1 - UPPER_SCROLL_Y0

# Unit card positions and size onm the original page
CARD_WIDTH = 214.7 - 36
CARD_HEIGHT = 285.5 - 36

# The X positions are only used as a reference point for edge detection
# The Y positions seem to be consistent at least
UPPER_CARD_X0 = [36, 233.5, 429.8, 627.2]
UPPER_CARD_Y0 = 36
UPPER_CARD_X1 = [UPPER_CARD_X0[0]+CARD_WIDTH,
                 UPPER_CARD_X0[1]+CARD_WIDTH,
                 UPPER_CARD_X0[2]+CARD_WIDTH,
                 UPPER_CARD_X0[3]+CARD_WIDTH]
UPPER_CARD_Y1 = UPPER_CARD_Y0 + CARD_HEIGHT

CARD_Y_OFFSET = 309.8 - UPPER_CARD_Y0  # 308

# Sample position for edge detection
SAMPLE_OFFSET_X = 6  # +/- from the X0 position
SAMPLE_OFFSET_Y = 100  # Somewhere on the top row

# Minimum pixel value change for edge detection
EDGE_DETECT_THRESHOLD = 40

# Output positioning
# A4 page definition
A4_SHORT_EDGE = 595.35
A4_LONG_EDGE = 841.995

# Distance to page edge
OUTPUT_MARGIN = 30
# Distance between cards
OUTPUT_PADDING = 20

saved_aa_settings = pymupdf.TOOLS.show_aa_level()


def disable_aa():
    """Disable AA"""
    pymupdf.TOOLS.set_aa_level(0)


def enable_aa():
    """(Re)enable AA"""
    pymupdf.TOOLS.set_aa_level(saved_aa_settings.get("graphics"))


def check_card(page):
    """Detect card x positions on the page
    Returns the x coordinate of the leading edge of detected cards"""
    # Disable AA to simplify edge detection
    disable_aa()
    pixmap = page.get_pixmap(dpi=600)
    enable_aa()
    pos_y = int(SAMPLE_OFFSET_Y * PIXEL_PER_PT)
    result = []
    for card_no in range(4):
        pos_x_start = int(
            (UPPER_CARD_X0[card_no] - SAMPLE_OFFSET_X) * PIXEL_PER_PT)
        pos_x_end = int(
            (UPPER_CARD_X0[card_no] + SAMPLE_OFFSET_X) * PIXEL_PER_PT)
        previous_value = 0
        max_drop_x = 0
        max_drop_value = 0
        for sample_x in range(pos_x_start, pos_x_end):
            value = sum(pixmap.pixel(sample_x, pos_y))//3
            if previous_value - value > max_drop_value:
                max_drop_x = sample_x
                max_drop_value = previous_value - value
            previous_value = value
        if max_drop_value < 40:
            return result
        result.append((max_drop_x-1)/PIXEL_PER_PT)
    return result


def reverse_portrait(front):
    """Returns rectangle which aligns with the original on the flip side
    for portrait A4"""
    return Rect(A4_SHORT_EDGE - front.x1,
                front.y0 - FLIP_OFFSET,
                A4_SHORT_EDGE - front.x0,
                front.y1 - FLIP_OFFSET)


def reverse_landscape(front):
    """Returns rectangle which aligns with the original on the flip side
    for landscape A4 page when printed on portrait media.
    This also requires rotating the flip side image 180 degrees"""
    return Rect(front.x0 + FLIP_OFFSET,
                A4_SHORT_EDGE - front.y1,
                front.x1 + FLIP_OFFSET,
                A4_SHORT_EDGE - front.y0)


def process_warscroll():
    """Process the warscroll page (first page)"""
    upper_scroll = Rect(UPPER_SCROLL_X0,
                        UPPER_SCROLL_Y0,
                        UPPER_SCROLL_X1,
                        UPPER_SCROLL_Y1)

    lower_scroll = Rect(upper_scroll.x0,
                        upper_scroll.y0 + SCROLL_Y_OFFSET,
                        upper_scroll.x1,
                        upper_scroll.y1 + SCROLL_Y_OFFSET)

    output_rect_front = Rect(OUTPUT_MARGIN,
                             OUTPUT_MARGIN,
                             OUTPUT_MARGIN + SCROLL_WIDTH,
                             OUTPUT_MARGIN + SCROLL_HEIGHT)

    output_rect_back = reverse_portrait(output_rect_front)

    print("Copying warscroll front page")
    output_scroll_front_page = output_document.new_page(
        width=A4_SHORT_EDGE, height=A4_LONG_EDGE)
    output_scroll_front_page.show_pdf_page(
        output_rect_front, input_document, pno=0, clip=upper_scroll)

    print("Copying warscroll back page")
    output_scroll_back_page = output_document.new_page(
        width=A4_SHORT_EDGE, height=A4_LONG_EDGE)
    output_scroll_back_page.show_pdf_page(
        output_rect_back, input_document, pno=0, clip=lower_scroll)


def process_cards():
    """Process the card pages (2nd page onwards)"""
    card_pos = []
    for input_page_idx in range(1, input_document.page_count):
        print("Checking for cards on page ", input_page_idx + 1)
        card_pos.append(check_card(input_document[input_page_idx]))

    # There are no current warbands with more than 8 cards,
    # so the batching logic is untested
    for batch in range(0, math.ceil(len(card_pos) / 2)):
        process_eight(1 + batch * 2,
                      card_pos[batch * 2:(batch + 1) * 2],
                      True)
        process_eight(1 + batch * 2,
                      card_pos[batch * 2:(batch + 1) * 2],
                      False)


def process_eight(page_idx, card_pos, is_front):
    """Process two pages containing up to eight cards"""
    output_page = output_document.new_page(
        width=A4_LONG_EDGE, height=A4_SHORT_EDGE)
    for card_no in range(8):
        # Also decides which row it goes in the output
        page_offset = card_no // 4
        card_x_pos = card_no % 4
        card_y_pos = 0 if is_front else 1
        if (len(card_pos) - 1) < page_offset or (
                len(card_pos[page_offset]) - 1) < card_x_pos:
            return
        source_rect = Rect(card_pos[page_offset][card_x_pos],
                           UPPER_CARD_Y0 + card_y_pos * CARD_Y_OFFSET,
                           card_pos[page_offset][card_x_pos] + CARD_WIDTH,
                           UPPER_CARD_Y1 + card_y_pos * CARD_Y_OFFSET)
        output_rect = Rect(OUTPUT_MARGIN + card_x_pos
                           * (CARD_WIDTH + OUTPUT_PADDING),
                           OUTPUT_MARGIN + page_offset *
                           (CARD_HEIGHT + OUTPUT_PADDING),
                           OUTPUT_MARGIN + CARD_WIDTH + card_x_pos *
                           (CARD_WIDTH + OUTPUT_PADDING),
                           OUTPUT_MARGIN + CARD_HEIGHT + page_offset
                           * (CARD_HEIGHT + OUTPUT_PADDING))
        if not is_front:
            output_rect = reverse_landscape(output_rect)
        print(
            "Processing ",
            "front" if is_front else "back",
            " of card ",
            card_x_pos + 1,
            " on page",
            page_idx + 1 + page_offset)
        output_page .show_pdf_page(
            output_rect,
            input_document,
            pno=page_idx +
            page_offset,
            clip=source_rect,
            rotate=0 if is_front else 180)


if len(sys.argv) < 3 or len(sys.argv) > 4:
    print("specify source and destination filename, and an optional vertical \
    offset in points (1/72th of and inch) for the reverse side")
    exit(-1)

input_filename = sys.argv[1]
output_filename = sys.argv[2]
if len(sys.argv) == 4:
    FLIP_OFFSET = float(sys.argv[3])
else:
    FLIP_OFFSET = 0.0

print("input: ", input_filename)
print("output: ", output_filename)
print("vertical offset: ", FLIP_OFFSET, "pt")
print()

input_document = pymupdf.open(input_filename)
output_document = pymupdf.Document(filetype=".pdf")

process_warscroll()
process_cards()

with open(output_filename, "wb") as output_file:
    output_document.save(
        output_file, 3, clean=True, deflate=True, deflate_images=True)
print("Wrote ", output_filename)
print("Done")
