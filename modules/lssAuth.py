import ctypes
import tkinter as tk
from tkinter import ttk
import json
import requests
ctypes.windll.shcore.SetProcessDpiAwareness(2)
def sendRequests():
	email = emailEntry.get()
	password = passwordEntry.get()

	# Preflight request
	preflightHeaders = {
		"Accept": "*/*",
		"Accept-Encoding": "gzip, deflate, br, zstd",
		"Accept-Language": "en-US,en;q=0.9",
		"Access-Control-Request-Headers": "content-type",
		"Access-Control-Request-Method": "POST",
		"Connection": "keep-alive",
		"Host": "levelsharesquare.com",
		"Origin": "https://app.localhost",
		"Referer": "https://app.localhost/",
		"Sec-Fetch-Dest": "empty",
		"Sec-Fetch-Mode": "cors",
		"Sec-Fetch-Site": "cross-site",
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0"
	}
	preflightResponse = requests.options("https://levelsharesquare.com/api/users/login", headers=preflightHeaders)
	print("Preflight Response Status Code:", preflightResponse.status_code)

	# Fetch request (POST)
	fetchHeaders = {
		"Accept": "*/*",
		"Accept-Encoding": "gzip, deflate, br, zstd",
		"Accept-Language": "en-US,en;q=0.9",
		"Connection": "keep-alive",
		"Content-Length": "63",
		"Content-Type": "application/json; charset=UTF-8",
		"Host": "levelsharesquare.com",
		"Origin": "https://app.localhost",
		"Referer": "https://app.localhost/",
		"Sec-Ch-Ua": '"Chromium";v="133", "Microsoft Edge WebView2";v="133", "Not(A:Brand";v="99", "Microsoft Edge";v="133"',
		"Sec-Ch-Ua-Mobile": "?0",
		"Sec-Ch-Ua-Platform": '"Windows"',
		"Sec-Fetch-Dest": "empty",
		"Sec-Fetch-Mode": "cors",
		"Sec-Fetch-Site": "cross-site",
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0"
	}
	requestPayload = json.dumps({"email": email, "password": password})
	fetchResponse = requests.post("https://levelsharesquare.com/api/users/login", headers=fetchHeaders, data=requestPayload)
	print("Fetch Response Status Code:", fetchResponse.status_code)

	# Save response to logininfo.json
	with open("logininfo.json", "w") as file:
		json.dump(fetchResponse.json(), file, indent="\t")

# Create the main window
root = tk.Tk()
root.title("Login")
root.geometry("260x260")

# Create and place the email entry
emailLabel = ttk.Label(root, text="Email:")
emailLabel.pack()
emailEntry = ttk.Entry(root, show="*")
emailEntry.pack()

# Create and place the password entry
passwordLabel = ttk.Label(root, text="Password:")
passwordLabel.pack()
passwordEntry = ttk.Entry(root, show="‎")
passwordEntry.pack()

# Create and place the submit button
submit_button = ttk.Button(root, text="Submit", command=sendRequests)
submit_button.pack()

# Start the Tkinter event loop
root.mainloop()