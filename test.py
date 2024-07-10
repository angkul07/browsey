import tkinter as tk
# Function to update the input field
def button_click(char):
    current = entry.get()
    if char == "C":
        entry.delete(0, tk.END)
    elif char == "=":
        try:
            result = eval(current)
            entry.delete(0, tk.END)
            entry.insert(0, result)
        except Exception:
            entry.delete(0, tk.END)
            entry.insert(0, "Error")
    elif char == "←":
        entry.delete(len(current) - 1, tk.END)
    else:
        entry.insert(tk.END, char)

# Create the main window
root = tk.Tk()
root.title("Calculator")

# Create an input field
entry = tk.Entry(root, width=20, font=("Arial", 20))
entry.grid(row=0, column=0, columnspan=5)

# Create buttons for digits (0-9)
buttons = [
    "7", "8", "9", "+",
    "4", "5", "6", "-",
    "1", "2", "3", "*",
    "0", ".", "=", "/"
]
row, col = 1, 0
for button in buttons:
    tk.Button(root, text=button, padx=20, pady=20, font=("Arial", 16),
              command=lambda button=button: button_click(button)).grid(row=row, column=col)
    col += 1
    if col > 3:
        col = 0
        row += 1

# Create a Backspace button
tk.Button(root, text="←", padx=20, pady=20, font=("Arial", 16),
          command=lambda: button_click("←")).grid(row=5, column=3)

# Create a Clear (C) button
tk.Button(root, text="C", padx=20, pady=20, font=("Arial", 16),
          command=lambda: button_click("C")).grid(row=5, column=2)

# Start the Tkinter main loop
root.mainloop()
