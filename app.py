import tkinter as tk

class MyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Click Event Example")
        
        # Bind the left mouse button click event to the self.click method
        self.root.bind("<Button-1>", self.click)
        
    def click(self, event):
        # This method will be called when the left mouse button is clicked
        print(f"Clicked at ({event.x}, {event.y})")
        
# Create the main window
root = tk.Tk()
app = MyApp(root)

# Run the application
root.mainloop()
