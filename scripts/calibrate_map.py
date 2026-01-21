#!/usr/bin/env python3
"""
Interactive map calibration tool.
Click on key features to calibrate grid coordinates.
"""

import sys
import json
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont, ImageTk
    import tkinter as tk
    from tkinter import messagebox
except ImportError:
    print("ERROR: PIL and tkinter required. Install with: pip install Pillow", file=sys.stderr)
    sys.exit(1)


class MapCalibrator:
    def __init__(self, image_path, positions_file):
        self.image_path = image_path
        self.positions_file = positions_file
        self.calibration_points = {}
        self.img = Image.open(image_path)
        self.img_width, self.img_height = self.img.size
        
        # Load existing positions or create default
        if Path(positions_file).exists():
            with open(positions_file, 'r') as f:
                self.positions_data = json.load(f)
        else:
            self.positions_data = {
                "grid_size": 5,
                "map_width_squares": 20,
                "map_height_squares": 25,
                "combatants": {},
                "terrain": {}
            }
        
        self.root = tk.Tk()
        self.root.title("Map Calibration - Click on key features")
        self.setup_ui()
    
    def setup_ui(self):
        # Instructions
        instructions = tk.Label(
            self.root,
            text="Click on these features in order:\n1. Top-left corner of grid\n2. Bottom-right corner of grid\n3. Center of T17 room\n4. Center of statue in T17\n5. T16 room center (party entrance)",
            justify=tk.LEFT,
            font=("Arial", 10)
        )
        instructions.pack(pady=10)
        
        # Canvas for image
        self.canvas = tk.Canvas(
            self.root,
            width=min(self.img_width, 1200),
            height=min(self.img_height, 800),
            cursor="crosshair"
        )
        self.canvas.pack()
        
        # Scale image if too large
        scale = min(1200 / self.img_width, 800 / self.img_height, 1.0)
        if scale < 1.0:
            display_width = int(self.img_width * scale)
            display_height = int(self.img_height * scale)
            self.display_img = self.img.resize((display_width, display_height), Image.Resampling.LANCZOS)
        else:
            self.display_img = self.img
            display_width = self.img_width
            display_height = self.img_height
        
        self.photo = ImageTk.PhotoImage(self.display_img)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        
        # Click handler
        self.canvas.bind("<Button-1>", self.on_click)
        
        # Buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Done Calibrating", command=self.save_calibration).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=self.root.quit).pack(side=tk.LEFT, padx=5)
        
        self.click_count = 0
        self.points = []
    
    def on_click(self, event):
        # Convert display coordinates to image coordinates
        scale_x = self.img_width / self.display_img.width
        scale_y = self.img_height / self.display_img.height
        
        img_x = int(event.x * scale_x)
        img_y = int(event.y * scale_y)
        
        self.points.append((img_x, img_y))
        self.click_count += 1
        
        # Draw marker
        self.canvas.create_oval(event.x - 5, event.y - 5, event.x + 5, event.y + 5, fill="red", outline="black", width=2)
        self.canvas.create_text(event.x, event.y - 15, text=str(self.click_count), fill="red", font=("Arial", 12, "bold"))
        
        labels = ["Grid Top-Left", "Grid Bottom-Right", "T17 Center", "Statue Center", "T16 Center"]
        if self.click_count <= len(labels):
            print(f"Point {self.click_count}: {labels[self.click_count-1]} at pixel ({img_x}, {img_y})")
        
        if self.click_count >= 5:
            messagebox.showinfo("Calibration", "All points marked! Click 'Done Calibrating' to save.")
    
    def save_calibration(self):
        if len(self.points) < 5:
            messagebox.showerror("Error", "Please mark all 5 calibration points first!")
            return
        
        # Calculate grid dimensions from calibration points
        grid_tl = self.points[0]  # Top-left of grid
        grid_br = self.points[1]  # Bottom-right of grid
        
        # Calculate pixels per square
        grid_width_pixels = grid_br[0] - grid_tl[0]
        grid_height_pixels = grid_br[1] - grid_tl[1]
        
        # Get expected grid size from positions data
        expected_width = self.positions_data.get("map_width_squares", 20)
        expected_height = self.positions_data.get("map_height_squares", 25)
        
        pixels_per_square_x = grid_width_pixels / expected_width
        pixels_per_square_y = grid_height_pixels / expected_height
        
        # Calculate grid coordinates for T17, statue, T16
        t17_pixel = self.points[2]
        statue_pixel = self.points[3]
        t16_pixel = self.points[4]
        
        def pixel_to_grid(px, py):
            rel_x = px - grid_tl[0]
            rel_y = py - grid_tl[1]
            grid_x = int(rel_x / pixels_per_square_x)
            grid_y = int(rel_y / pixels_per_square_y)
            return grid_x, grid_y
        
        t17_grid = pixel_to_grid(t17_pixel[0], t17_pixel[1])
        statue_grid = pixel_to_grid(statue_pixel[0], statue_pixel[1])
        t16_grid = pixel_to_grid(t16_pixel[0], t16_pixel[1])
        
        print(f"\n=== CALIBRATION RESULTS ===")
        print(f"Grid: {grid_tl} to {grid_br}")
        print(f"Pixels per square: {pixels_per_square_x:.1f} x {pixels_per_square_y:.1f}")
        print(f"T17 center: grid ({t17_grid[0]}, {t17_grid[1]})")
        print(f"Statue center: grid ({statue_grid[0]}, {statue_grid[1]})")
        print(f"T16 center: grid ({t16_grid[0]}, {t16_grid[1]})")
        
        # Update positions based on calibration
        # Party enters from T16, so place them near T16
        party_y = t16_grid[1] + 2  # 2 squares south of T16 center
        
        # Update combatants
        self.positions_data["combatants"] = {
            "brevin": {"x": t16_grid[0] - 4, "y": party_y, "color": "blue", "label": "B"},
            "vandross": {"x": t16_grid[0] - 2, "y": party_y, "color": "blue", "label": "V"},
            "torgga": {"x": t16_grid[0], "y": party_y, "color": "blue", "label": "T"},
            "eglath": {"x": t16_grid[0] + 2, "y": party_y, "color": "blue", "label": "E"},
            "zephyr": {"x": t16_grid[0] + 4, "y": party_y, "color": "blue", "label": "Z"},
            "malinia": {"x": statue_grid[0], "y": statue_grid[1], "color": "red", "label": "M", "elevated": True},
            "gemmule_1": {"x": statue_grid[0] - 2, "y": statue_grid[1] - 1, "color": "orange", "label": "G1"},
            "gemmule_2": {"x": statue_grid[0] + 2, "y": statue_grid[1] - 1, "color": "orange", "label": "G2"},
            "gemmule_3": {"x": statue_grid[0] - 2, "y": statue_grid[1] + 1, "color": "orange", "label": "G3"},
            "gemmule_4": {"x": statue_grid[0] + 2, "y": statue_grid[1] + 1, "color": "orange", "label": "G4"},
        }
        
        # Update terrain
        self.positions_data["terrain"] = {
            "statue": {
                "x": statue_grid[0] - 1,
                "y": statue_grid[1] - 1,
                "width": 2,
                "height": 3,
                "color": "gray"
            }
        }
        
        # Save calibration data
        self.positions_data["calibration"] = {
            "grid_tl": grid_tl,
            "grid_br": grid_br,
            "pixels_per_square_x": pixels_per_square_x,
            "pixels_per_square_y": pixels_per_square_y,
            "t17_center": t17_grid,
            "statue_center": statue_grid,
            "t16_center": t16_grid
        }
        
        # Save to file
        with open(self.positions_file, 'w') as f:
            json.dump(self.positions_data, f, indent=2)
        
        print(f"\nCalibration saved to {self.positions_file}")
        messagebox.showinfo("Success", "Calibration saved! You can now run the annotation script.")
        self.root.quit()


def main():
    if len(sys.argv) < 3:
        print("Usage: python calibrate_map.py <image_path> <positions_json_file>")
        print("\nExample:")
        print("  python calibrate_map.py Talhundereth.png combat_positions_t17.json")
        sys.exit(1)
    
    image_path = sys.argv[1]
    positions_file = sys.argv[2]
    
    if not Path(image_path).exists():
        print(f"ERROR: Image not found: {image_path}", file=sys.stderr)
        sys.exit(1)
    
    app = MapCalibrator(image_path, positions_file)
    app.root.mainloop()


if __name__ == "__main__":
    main()
