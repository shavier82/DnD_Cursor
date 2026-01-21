#!/usr/bin/env python3
"""
Dynamic battlemap viewer that auto-updates when positions change.
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime

try:
    from PIL import Image, ImageDraw, ImageFont, ImageTk
    import tkinter as tk
    from tkinter import ttk
except ImportError:
    print("ERROR: PIL and tkinter required. Install with: pip install Pillow", file=sys.stderr)
    sys.exit(1)


def get_color(color_name):
    """Convert color name to RGB tuple"""
    colors = {
        "blue": (0, 100, 255),
        "red": (255, 0, 0),
        "orange": (255, 165, 0),
        "green": (0, 255, 0),
        "yellow": (255, 255, 0),
        "purple": (128, 0, 128),
        "gray": (128, 128, 128),
        "darkgray": (64, 64, 64),
        "lightgray": (200, 200, 200),
        "white": (255, 255, 255),
        "black": (0, 0, 0),
    }
    return colors.get(color_name.lower(), (255, 255, 255))


def create_battlemap_image(positions_data, grid_size_pixels=50):
    """Create battlemap image from positions data"""
    grid_width = positions_data.get("map_width_squares", 20)
    grid_height = positions_data.get("map_height_squares", 25)
    
    img_width = grid_width * grid_size_pixels
    img_height = grid_height * grid_size_pixels
    
    img = Image.new('RGB', (img_width, img_height), color=(240, 240, 240))
    draw = ImageDraw.Draw(img)
    
    # Draw grid
    grid_color = get_color("lightgray")
    for x in range(0, img_width, grid_size_pixels):
        draw.line([(x, 0), (x, img_height)], fill=grid_color, width=1)
    for y in range(0, img_height, grid_size_pixels):
        draw.line([(0, y), (img_width, y)], fill=grid_color, width=1)
    
    # Draw terrain
    terrain = positions_data.get("terrain", {})
    for terrain_name, terrain_data in terrain.items():
        x = terrain_data["x"] * grid_size_pixels
        y = terrain_data["y"] * grid_size_pixels
        width = terrain_data.get("width", 1) * grid_size_pixels
        height = terrain_data.get("height", 1) * grid_size_pixels
        color = get_color(terrain_data.get("color", "gray"))
        
        draw.rectangle([x, y, x + width, y + height], fill=color, outline=(0, 0, 0), width=2)
    
    # Load font
    try:
        font = ImageFont.truetype("arial.ttf", 14)
        small_font = ImageFont.truetype("arial.ttf", 10)
    except:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
            small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
        except:
            font = ImageFont.load_default()
            small_font = ImageFont.load_default()
    
    # Draw combatants
    combatants = positions_data.get("combatants", {})
    defeated = positions_data.get("defeated", [])  # List of defeated combatant IDs
    
    for combatant_id, combatant_data in combatants.items():
        # Skip defeated combatants
        if combatant_id in defeated:
            continue
        square_x = combatant_data["x"]
        square_y = combatant_data["y"]
        color = get_color(combatant_data.get("color", "white"))
        label = combatant_data.get("label", combatant_id[0].upper())
        is_elevated = combatant_data.get("elevated", False)
        
        pixel_x = int((square_x * grid_size_pixels) + (grid_size_pixels / 2))
        pixel_y = int((square_y * grid_size_pixels) + (grid_size_pixels / 2))
        
        radius = 18 if is_elevated else 15
        outline_width = 3 if is_elevated else 2
        
        draw.ellipse(
            [pixel_x - radius, pixel_y - radius, pixel_x + radius, pixel_y + radius],
            outline=(0, 0, 0),
            width=outline_width
        )
        
        draw.ellipse(
            [pixel_x - radius + 2, pixel_y - radius + 2,
             pixel_x + radius - 2, pixel_y + radius - 2],
            fill=color
        )
        
        bbox = draw.textbbox((0, 0), label, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = pixel_x - text_width // 2
        text_y = pixel_y - text_height // 2
        
        draw.text((text_x - 1, text_y), label, fill=(0, 0, 0), font=font)
        draw.text((text_x + 1, text_y), label, fill=(0, 0, 0), font=font)
        draw.text((text_x, text_y - 1), label, fill=(0, 0, 0), font=font)
        draw.text((text_x, text_y + 1), label, fill=(0, 0, 0), font=font)
        draw.text((text_x, text_y), label, fill=(255, 255, 255), font=font)
        
        if is_elevated:
            draw.text((pixel_x + radius + 3, pixel_y - 8), "↑20ft", fill=(255, 0, 0), font=small_font)
    
    # Get combat status if available
    combat_status = positions_data.get("combat_status", None)
    current_turn_id = None
    if combat_status:
        current_turn = combat_status.get("current_turn", {})
        current_turn_id = current_turn.get("creature_id") if current_turn else None
    
    # Calculate legend height based on combat status
    legend_height = 100  # Base legend height
    if combat_status:
        # Add space for HP tracker and initiative order
        combatants = combat_status.get("combatants", {})
        legend_height += 20  # "HP TRACKER:" header
        legend_height += len(combatants) * 16  # HP lines
        legend_height += 20  # "INITIATIVE:" header
        initiative_order = combat_status.get("initiative_order", [])
        if not initiative_order:
            # Build initiative order from combatants if not provided
            combatants_list = list(combatants.items())
            initiative_order = [cid for cid, _ in sorted(combatants_list, 
                key=lambda x: combat_status.get("combatants", {}).get(x[0], {}).get("initiative", 0), 
                reverse=True)]
        legend_height += len(initiative_order) * 16  # Initiative lines
        legend_height += 10  # Spacing
    
    # Add legend
    legend_x = img_width - 200  # Make wider for combat info
    legend_y = 10
    draw.rectangle(
        [legend_x - 5, legend_y - 5, legend_x + 195, legend_y + legend_height],
        fill=(255, 255, 255, 240),
        outline=(0, 0, 0),
        width=2
    )
    
    draw.text((legend_x, legend_y), "LEGEND:", fill=(0, 0, 0), font=font)
    legend_y += 20
    
    draw.ellipse([legend_x, legend_y, legend_x + 12, legend_y + 12], fill=get_color("blue"))
    draw.text((legend_x + 15, legend_y - 2), "Party", fill=(0, 0, 0), font=small_font)
    legend_y += 18
    
    draw.ellipse([legend_x, legend_y, legend_x + 12, legend_y + 12], fill=get_color("red"))
    draw.text((legend_x + 15, legend_y - 2), "Malinia", fill=(0, 0, 0), font=small_font)
    legend_y += 18
    
    draw.ellipse([legend_x, legend_y, legend_x + 12, legend_y + 12], fill=get_color("orange"))
    draw.text((legend_x + 15, legend_y - 2), "Gemmules", fill=(0, 0, 0), font=small_font)
    legend_y += 18
    
    draw.rectangle([legend_x, legend_y, legend_x + 12, legend_y + 12], fill=get_color("gray"))
    draw.text((legend_x + 15, legend_y - 2), "Statue", fill=(0, 0, 0), font=small_font)
    legend_y += 25
    
    # Add HP Tracker if combat status available
    if combat_status:
        combatants_status = combat_status.get("combatants", {})
        draw.text((legend_x, legend_y), "HP TRACKER:", fill=(0, 0, 0), font=font)
        legend_y += 18
        
        # Display HP for ALL combatants in combat_status (no hardcoded mapping)
        for combat_id, c_data in combatants_status.items():
            name = c_data.get("name", combat_id)
            hp = c_data.get("hp", "?/?")
            is_alive = c_data.get("is_alive", True)
            
            hp_color = (0, 0, 0) if is_alive else (128, 128, 128)
            draw.text((legend_x + 5, legend_y), f"{name}: {hp}", fill=hp_color, font=small_font)
            legend_y += 16
        
        legend_y += 5
        
        # Add Initiative Order
        draw.text((legend_x, legend_y), "INITIATIVE:", fill=(0, 0, 0), font=font)
        legend_y += 18
        
        # Build initiative order
        initiative_order = combat_status.get("initiative_order", [])
        if not initiative_order:
            # Build from combatants sorted by initiative
            combatants_list = [(cid, c_data) for cid, c_data in combatants_status.items()]
            combatants_list.sort(key=lambda x: x[1].get("initiative", 0), reverse=True)
            initiative_order = [cid for cid, _ in combatants_list]
        
        # Display initiative order
        for i, cid in enumerate(initiative_order):
            if cid in combatants_status:
                c_data = combatants_status[cid]
                name = c_data.get("name", cid)
                initiative = c_data.get("initiative", 0)
                is_current = (cid == current_turn_id)
                
                # Highlight current turn
                if is_current:
                    draw.rectangle(
                        [legend_x - 3, legend_y - 2, legend_x + 185, legend_y + 14],
                        fill=(255, 255, 0, 180),  # Yellow highlight
                        outline=(255, 200, 0),
                        width=2
                    )
                
                turn_indicator = "➤" if is_current else f"{i+1}."
                text_color = (255, 0, 0) if is_current else (0, 0, 0)
                draw.text((legend_x, legend_y), f"{turn_indicator} {name} ({initiative})", 
                         fill=text_color, font=small_font)
                legend_y += 16
    
    return img


class BattlemapViewer:
    def __init__(self, positions_file, update_interval=1.0):
        self.positions_file = Path(positions_file)
        self.update_interval = update_interval
        self.last_modified = 0
        
        # Zoom state
        self.zoom_level = 1.0
        self.min_zoom = 0.25
        self.max_zoom = 4.0
        self.zoom_step = 0.25
        self.original_img = None
        self.original_img_data = None
        
        # Drag-and-drop state
        self.dragging = False
        self.dragged_combatant = None
        self.drag_start_pos = None
        self.combatant_positions = {}  # Store combatant positions for click detection
        self.grid_size_pixels = 50
        self.scale_factor = 1.0  # Initialize to 1.0 to avoid division by zero
        self.image_offset_x = 0
        self.image_offset_y = 0
        
        self.root = tk.Tk()
        self.root.title("Dynamic Battlemap Viewer - Drag & Drop Enabled")
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready - Click and drag blue icons to move")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Canvas for map - set initial size
        self.canvas = tk.Canvas(self.root, bg="white", cursor="crosshair", width=1000, height=800)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bind resize event and mouse wheel for zoom
        self.canvas.bind('<Configure>', self.on_canvas_configure)
        self.canvas.bind('<MouseWheel>', self.on_mouse_wheel)
        self.canvas.focus_set()  # Allow canvas to receive keyboard events
        
        # Bind drag-and-drop events
        self.canvas.bind('<Button-1>', self.on_mouse_click)
        self.canvas.bind('<B1-Motion>', self.on_mouse_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_mouse_release)
        
        # Control panel
        control_frame = ttk.Frame(self.root)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        ttk.Label(control_frame, text="Update Interval (seconds):").pack(side=tk.LEFT, padx=5)
        self.interval_var = tk.DoubleVar(value=update_interval)
        interval_spin = ttk.Spinbox(control_frame, from_=0.1, to=10.0, increment=0.1, 
                                    textvariable=self.interval_var, width=5)
        interval_spin.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="Refresh Now", command=self.update_map).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Auto-Refresh", command=self.toggle_auto_refresh).pack(side=tk.LEFT, padx=5)
        
        # Zoom controls
        ttk.Separator(control_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        ttk.Label(control_frame, text="Zoom:").pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="-", command=self.zoom_out, width=3).pack(side=tk.LEFT, padx=2)
        self.zoom_var = tk.StringVar(value="100%")
        zoom_label = ttk.Label(control_frame, textvariable=self.zoom_var, width=5)
        zoom_label.pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="+", command=self.zoom_in, width=3).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="Reset", command=self.zoom_reset).pack(side=tk.LEFT, padx=5)
        
        self.auto_refresh = True
        self.auto_refresh_btn = None
        
        # Initial load
        self.update_map()
        
        # Start auto-refresh
        self.auto_refresh_loop()
    
    def on_canvas_configure(self, event):
        """Handle canvas resize"""
        # Only update if zoom is at default (fit to window)
        if self.zoom_level == 1.0:
            self.update_map()
        else:
            # Just re-render with current zoom
            self.render_map()
    
    def toggle_auto_refresh(self):
        self.auto_refresh = not self.auto_refresh
        self.status_var.set("Auto-refresh: " + ("ON" if self.auto_refresh else "OFF"))
    
    def zoom_in(self):
        """Zoom in"""
        if self.zoom_level < self.max_zoom:
            self.zoom_level = min(self.zoom_level + self.zoom_step, self.max_zoom)
            self.update_zoom_display()
            self.render_map()
    
    def zoom_out(self):
        """Zoom out"""
        if self.zoom_level > self.min_zoom:
            self.zoom_level = max(self.zoom_level - self.zoom_step, self.min_zoom)
            self.update_zoom_display()
            self.render_map()
    
    def zoom_reset(self):
        """Reset zoom to fit window"""
        self.zoom_level = 1.0
        self.update_zoom_display()
        self.update_map()
    
    def on_mouse_wheel(self, event):
        """Handle mouse wheel zoom"""
        # Windows and Mac use different event deltas
        if event.delta > 0 or event.num == 4:
            self.zoom_in()
        elif event.delta < 0 or event.num == 5:
            self.zoom_out()
    
    def update_zoom_display(self):
        """Update zoom percentage display"""
        zoom_percent = int(self.zoom_level * 100)
        self.zoom_var.set(f"{zoom_percent}%")
    
    def pixel_to_grid(self, pixel_x, pixel_y):
        """Convert canvas pixel coordinates to grid coordinates"""
        # Safety check - if scale_factor not initialized, return invalid
        if not hasattr(self, 'scale_factor') or self.scale_factor == 0:
            return -1, -1
        
        # Account for image offset and scale
        relative_x = pixel_x - self.image_offset_x
        relative_y = pixel_y - self.image_offset_y
        
        # Convert to grid coordinates
        grid_x = int(relative_x / (self.grid_size_pixels * self.scale_factor))
        grid_y = int(relative_y / (self.grid_size_pixels * self.scale_factor))
        
        return grid_x, grid_y
    
    def get_combatant_at_pixel(self, pixel_x, pixel_y):
        """Get combatant ID at pixel coordinates"""
        grid_x, grid_y = self.pixel_to_grid(pixel_x, pixel_y)
        
        # Check each combatant's position
        for combatant_id, pos_data in self.combatant_positions.items():
            if pos_data['x'] == grid_x and pos_data['y'] == grid_y:
                # Check if click is within the icon radius (15 pixels scaled)
                icon_radius = 15 * self.scale_factor
                icon_center_x = self.image_offset_x + (pos_data['x'] * self.grid_size_pixels * self.scale_factor) + (self.grid_size_pixels * self.scale_factor / 2)
                icon_center_y = self.image_offset_y + (pos_data['y'] * self.grid_size_pixels * self.scale_factor) + (self.grid_size_pixels * self.scale_factor / 2)
                
                distance = ((pixel_x - icon_center_x) ** 2 + (pixel_y - icon_center_y) ** 2) ** 0.5
                if distance <= icon_radius:
                    return combatant_id, pos_data.get('color', 'white')
        
        return None, None
    
    def on_mouse_click(self, event):
        """Handle mouse click - start drag if clicking on a player character"""
        combatant_id, color = self.get_combatant_at_pixel(event.x, event.y)
        
        if combatant_id and color == 'blue':  # Only allow dragging player characters (blue)
            self.dragging = True
            self.dragged_combatant = combatant_id
            self.drag_start_pos = (event.x, event.y)
            self.canvas.config(cursor="hand2")
            self.status_var.set(f"Dragging {combatant_id}...")
        else:
            self.dragging = False
            self.dragged_combatant = None
    
    def on_mouse_drag(self, event):
        """Handle mouse drag - update visual feedback"""
        if self.dragging and self.dragged_combatant:
            # Visual feedback - could highlight target square here
            grid_x, grid_y = self.pixel_to_grid(event.x, event.y)
            self.status_var.set(f"Dragging {self.dragged_combatant} to ({grid_x}, {grid_y})")
    
    def on_mouse_release(self, event):
        """Handle mouse release - drop combatant at new position"""
        if self.dragging and self.dragged_combatant:
            grid_x, grid_y = self.pixel_to_grid(event.x, event.y)
            
            # Validate position (within map bounds)
            if grid_x >= 0 and grid_y >= 0:
                # Update position in memory
                if self.dragged_combatant in self.combatant_positions:
                    self.combatant_positions[self.dragged_combatant]['x'] = grid_x
                    self.combatant_positions[self.dragged_combatant]['y'] = grid_y
                    
                    # Save to JSON file
                    self.save_positions()
                    
                    self.status_var.set(f"Moved {self.dragged_combatant} to ({grid_x}, {grid_y})")
                else:
                    self.status_var.set(f"Error: {self.dragged_combatant} not found")
            else:
                self.status_var.set("Invalid position - must be within map bounds")
        
        self.dragging = False
        self.dragged_combatant = None
        self.canvas.config(cursor="crosshair")
    
    def save_positions(self):
        """Save updated positions to JSON file"""
        try:
            # Load current file
            with open(self.positions_file, 'r') as f:
                data = json.load(f)
            
            # Update combatant positions
            for combatant_id, pos_data in self.combatant_positions.items():
                if combatant_id in data.get('combatants', {}):
                    data['combatants'][combatant_id]['x'] = pos_data['x']
                    data['combatants'][combatant_id]['y'] = pos_data['y']
            
            # Save back to file
            with open(self.positions_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Force update
            self.last_modified = 0
            self.update_map()
            
        except Exception as e:
            self.status_var.set(f"Error saving positions: {str(e)}")
    
    def render_map(self):
        """Render the map with current zoom level"""
        if self.original_img is None:
            return
        
        # Get canvas size
        self.root.update_idletasks()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            canvas_width = 1000
            canvas_height = 800
        
        # Calculate new size with zoom
        if self.zoom_level == 1.0:
            # Fit to window
            scale_x = canvas_width / self.original_img.width
            scale_y = canvas_height / self.original_img.height
            scale = min(scale_x, scale_y)
        else:
            # Apply zoom multiplier to fit-to-window scale
            scale_x = canvas_width / self.original_img.width
            scale_y = canvas_height / self.original_img.height
            base_scale = min(scale_x, scale_y)
            scale = base_scale * self.zoom_level
        
        self.scale_factor = scale
        
        new_width = int(self.original_img.width * scale)
        new_height = int(self.original_img.height * scale)
        scaled_img = self.original_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Update canvas
        self.photo = ImageTk.PhotoImage(scaled_img)
        self.canvas.delete("all")
        
        # Center the image on canvas
        canvas_center_x = canvas_width // 2
        canvas_center_y = canvas_height // 2
        
        self.image_offset_x = canvas_center_x - new_width // 2
        self.image_offset_y = canvas_center_y - new_height // 2
        
        self.canvas.create_image(
            canvas_center_x,
            canvas_center_y,
            image=self.photo,
            anchor=tk.CENTER
        )
    
    def update_map(self):
        try:
            # Check if file was modified
            current_modified = self.positions_file.stat().st_mtime
            
            if current_modified > self.last_modified or self.last_modified == 0:
                # Load positions
                with open(self.positions_file, 'r') as f:
                    positions_data = json.load(f)
                
                # Store combatant positions for click detection
                self.combatant_positions = {}
                for combatant_id, combatant_data in positions_data.get('combatants', {}).items():
                    self.combatant_positions[combatant_id] = {
                        'x': combatant_data.get('x', 0),
                        'y': combatant_data.get('y', 0),
                        'color': combatant_data.get('color', 'white')
                    }
                
                # Create image and store as original
                self.original_img = create_battlemap_image(positions_data)
                self.original_img_data = positions_data
                
                # Render with current zoom
                self.render_map()
                
                self.last_modified = current_modified
                if not self.dragging:
                    self.status_var.set(f"Updated: {datetime.now().strftime('%H:%M:%S')} - Drag blue icons to move")
            else:
                # If zoom is not default, still re-render in case window was resized
                if self.zoom_level != 1.0:
                    self.render_map()
                elif not self.dragging:
                    self.status_var.set("No changes detected - Drag blue icons to move")
                
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
    
    def auto_refresh_loop(self):
        if self.auto_refresh:
            self.update_map()
        
        interval = self.interval_var.get() * 1000  # Convert to milliseconds
        self.root.after(int(interval), self.auto_refresh_loop)
    
    def run(self):
        self.root.mainloop()


def main():
    if len(sys.argv) < 2:
        print("Usage: python view_battlemap.py <positions_json> [update_interval]")
        print("\nExample:")
        print("  python view_battlemap.py combat_positions_t17.json")
        print("  python view_battlemap.py combat_positions_t17.json 0.5")
        sys.exit(1)
    
    positions_file = sys.argv[1]
    update_interval = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
    
    if not Path(positions_file).exists():
        print(f"ERROR: Positions file not found: {positions_file}", file=sys.stderr)
        sys.exit(1)
    
    viewer = BattlemapViewer(positions_file, update_interval)
    viewer.run()


if __name__ == "__main__":
    main()
