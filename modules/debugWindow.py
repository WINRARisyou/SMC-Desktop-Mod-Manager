import sys
import tkinter as tk
from tkinter.scrolledtext import ScrolledText

class DebugWindow:
	def __init__(self, parent):
		self.root = tk.Toplevel(parent)
		self.root.title("Debug Window")
		self.text_widget = ScrolledText(self.root, wrap=tk.WORD, width=80, height=20)
		self.text_widget.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
		self.text_widget.config(state=tk.DISABLED)

		# Keep a reference to the original stdout
		self.original_stdout = sys.stdout
		sys.stdout = self

	def write(self, message):
		self.text_widget.config(state=tk.NORMAL)
		self.text_widget.insert(tk.END, message)
		self.text_widget.config(state=tk.DISABLED)
		self.text_widget.yview(tk.END)  # Auto-scroll
		
		# Also print to the console if available
		self.original_stdout.write(message)

	def flush(self):
		self.original_stdout.flush()