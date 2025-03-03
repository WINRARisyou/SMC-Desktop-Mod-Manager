import ctypes
import os
import tkinter as tk
from tkinter import messagebox, ttk
import json
import requests
ctypes.windll.shcore.SetProcessDpiAwareness(2)
def getUserIDfromToken(token=None):
	tokenHeaders = {
		"Accept": "*/*",
		"Accept-Encoding": "gzip, deflate, br, zstd",
		"Accept-Language": "en-US,en;q=0.9",
		"Authorization": f"Bearer {token}",
		"Connection": "keep-alive",
		"Host": "levelsharesquare.com",
		"If-None-Match": "W/'23-u2YsmurgV+cT8+MNVSYe4Pv0Uvk'",
		"Origin": "https://app.localhost",
		"Referer": "https://app.localhost/",
		"Sec-Fetch-Dest": "empty",
		"Sec-Fetch-Mode": "cors",
		"Sec-Fetch-Site": "cross-site",
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0",
		"sec-ch-ua": '"Chromium";v="133", "Microsoft Edge WebView2";v="133", "Not(A:Brand";v="99", "Microsoft Edge";v="133"',
		"sec-ch-ua-mobile": "?0",
		"sec-ch-ua-platform": "'Windows'"
	}
	tokenResponse = requests.get("https://levelsharesquare.com/api/users/get_id_from_token", headers=tokenHeaders)
	userID = tokenResponse.json().get("user")
	userData = requests.get(f"https://levelsharesquare.com/api/users/{userID}").json()
	print("User from Token Response Status Code:", tokenResponse.status_code)
	displayUserInfo(userData)

def displayUserInfo(userData):
	info_window = tk.Toplevel(window)
	info_window.title("Login Info")
	info_window.geometry("400x400")

	username = ttk.Label(info_window, text=f"Username: {userData["user"]["username"]}")
	username.pack(anchor="center", padx=10, pady=2)
	rank = ttk.Label(info_window, text=f"Rank: {userData["user"]["rank"]}")
	rank.pack(anchor="center", padx=10, pady=2)

	profilePicURL = userData["user"]["avatar"]
	profilePicResponse = requests.get(profilePicURL, stream=True)
	profilePicResponse.raw.decode_content = True
	profilePicImage = tk.PhotoImage(data=profilePicResponse.content)
	profilePicImage = profilePicImage.subsample(profilePicImage.width() // 64)
	profilePicLabel = ttk.Label(info_window, image=profilePicImage)
	profilePicLabel.image = profilePicImage # Keep a reference to avoid garbage collection
	profilePicLabel.pack(anchor="center", padx=10, pady=10)

def login():
	if os.path.exists("DO NOT SHARE.txt"):
		with open("DO NOT SHARE.txt", "r") as file:
			userToken = file.read().strip()
		getUserIDfromToken(userToken)
		#getUserData()
		return
	email = email_entry.get()
	password = password_entry.get()

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

	# save user token to DO NOT SHARE.txt
	try:
		with open("DO NOT SHARE.txt", "w") as file:
			file.write(fetchResponse.json()["token"])
		getUserIDfromToken(fetchResponse.json()["token"])
	except Exception as err:
		os.unlink("DO NOT SHARE.txt")
		messagebox.showerror("Authentication Failure", "Failed to log in. Please ensure your email and password are correct")

def logout():
	if os.path.exists("DO NOT SHARE.txt"):
		os.unlink("DO NOT SHARE.txt")
	submit_button.config(state="normal")
	email_entry.config(state="normal")
	password_entry.config(state="normal")
	logout_button.destroy()

# Create the main window
window = tk.Tk()
window.title("Login")
window.geometry("260x260")

# Create and place the email entry
email_label = ttk.Label(window, text="Email:")
email_label.pack()
email_entry = ttk.Entry(window, show="*")
email_entry.pack()

# Create and place the password entry
password_label = ttk.Label(window, text="Password:")
password_label.pack()
password_entry = ttk.Entry(window, show="*")#show="‎")
password_entry.pack()

# Create and place the submit button
submit_button = ttk.Button(window, text="Submit", command=login)
submit_button.pack()

if os.path.exists("DO NOT SHARE.txt"):
	submit_button.config(state="disabled")
	email_entry.config(state="disabled")
	password_entry.config(state="disabled")
	logout_button = ttk.Button(window, text="Logout", command=logout)
	logout_button.pack()

# Start the Tkinter event loop
window.mainloop()