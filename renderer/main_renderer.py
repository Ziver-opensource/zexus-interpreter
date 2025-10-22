# renderer/main_renderer.py

import tkinter as tk

class Renderer:
    def __init__(self):
        # Create the main application window
        self.window = tk.Tk()
        self.window.title("Zexus App")
        self.window.geometry("400x600") # Set a default size

    def render(self, screen_node):
        """The main entry point to start rendering the UI."""
        
        # In the future, we will parse the screen_node here to create
        # labels, buttons, etc. For now, we just show the window.
        
        print(f"[RENDER] Rendering screen '{screen_node.name.value}' in a real window...")
        
        # Start the UI event loop
        self.window.mainloop()

