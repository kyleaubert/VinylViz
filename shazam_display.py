import time
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from PIL import Image
import os

# files to display
RESULT_FILE = "/home/kyle/VinylViz/shazam_output/result.txt"
ALBUM_ART_FILE = "/home/kyle/VinylViz/shazam_output/album_art_32x32.png"

# theres defintiely a better way to do this
TEXT_AREA_WIDTH = 32
TOTAL_WIDTH = 64
TEXT_AREA_HEIGHT = 32


options = RGBMatrixOptions()
options.rows = 32
options.cols = 64
options.chain_length = 1
options.parallel = 1
options.hardware_mapping = 'adafruit-hat'
matrix = RGBMatrix(options=options)

# Load font, i found 6x10 to be a nice fit on a 32x64 board, but ymmv
font = graphics.Font()
font.LoadFont("6x10.bdf")

def calculate_text_width(text):
    dummy_canvas = matrix.CreateFrameCanvas()
    return graphics.DrawText(dummy_canvas, font, 0, 0, graphics.Color(255, 255, 255), text)

def display_album_art(canvas):
    if os.path.exists(ALBUM_ART_FILE):
        image = Image.open(ALBUM_ART_FILE)
        image = image.convert("RGB")
        image = image.resize((32, 32))
        for y in range(32):
            for x in range(32):
                r, g, b = image.getpixel((x, y))
                canvas.SetPixel(x + TEXT_AREA_WIDTH, y, r, g, b)

def draw_scrolling_text(canvas, text, y_pos, color, scroll_pos, text_width):
    needs_scroll = text_width > TEXT_AREA_WIDTH
    
    if needs_scroll:
        x_pos = TEXT_AREA_WIDTH - scroll_pos
        graphics.DrawText(canvas, font, x_pos, y_pos, graphics.Color(*color), text)
    else:
        x_pos = max(0, (TEXT_AREA_WIDTH - text_width) // 2)
        graphics.DrawText(canvas, font, x_pos, y_pos, graphics.Color(*color), text)
    
    return needs_scroll

def display_text(song, album, artist):
    canvas = matrix.CreateFrameCanvas()
#Text colors
    text_configs = [
        (song, 10, (255, 0, 0)),
        (album, 20, (0, 255, 0)),
        (artist, 30, (0, 0, 255))
    ]

    text_widths = [calculate_text_width(text) for text, _, _ in text_configs]
    needs_scroll = [width > TEXT_AREA_WIDTH for width in text_widths]
    scroll_lengths = [(width + TEXT_AREA_WIDTH) if ns else 0 
                     for width, ns in zip(text_widths, needs_scroll)]
    
    scroll_counter = 0
    max_length = max(scroll_lengths)

    while True:
        canvas.Clear()
        
        all_complete = True
        for i, ((text, y_pos, color), width, length) in enumerate(zip(text_configs, text_widths, scroll_lengths)):
            if length > 0:
                current_pos = min(scroll_counter, length)
                if current_pos < length:
                    all_complete = False
            else:
                current_pos = 0
            draw_scrolling_text(canvas, text, y_pos, color, current_pos, width)
        
        display_album_art(canvas)
        canvas = matrix.SwapOnVSync(canvas)
        
        if all_complete:
            scroll_counter = 0
            time.sleep(1)
        else:
            scroll_counter += 1
            time.sleep(0.03)

def process_result_file():
    last_result = None
    if os.path.exists(RESULT_FILE):
        with open(RESULT_FILE, "r") as f:
            lines = f.readlines()
            if len(lines) >= 3:
                song, album, artist = [line.strip() for line in lines[:3]]
                if (song, album, artist) != last_result:
                    last_result = (song, album, artist)
                    display_text(song, album, artist)

def run_program():
    while True:
        process_result_file()
        time.sleep(1)


if __name__ == "__main__":
    run_program()
