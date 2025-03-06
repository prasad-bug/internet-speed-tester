import matplotlib
# Set the backend to TkAgg to avoid issues on macOS with matplotlib rendering
matplotlib.use('TkAgg')

import tkinter as tk
from tkinter import messagebox
import speedtest
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from io import BytesIO
from PIL import Image, ImageTk
import requests

# Function to perform the speed test
def run_speedtest():
    st = speedtest.Speedtest()
    st.get_best_server()

    # Get speeds
    download_speed = st.download() / 1_000_000  # Convert to Mbps
    upload_speed = st.upload() / 1_000_000  # Convert to Mbps
    ping = st.results.ping

    # Get ISP logo
    isp = st.results.client['isp']
    logo_url = f"https://www.google.com/s2/favicons?domain={isp}"
    try:
        response = requests.get(logo_url)
        img = Image.open(BytesIO(response.content))
        img = img.resize((30, 30))  # Resize the logo
        isp_logo = ImageTk.PhotoImage(img)
    except requests.exceptions.RequestException:
        isp_logo = None

    return download_speed, upload_speed, ping, isp_logo

# Update speed on the GUI
def update_speed():
    download_speed, upload_speed, ping, isp_logo = run_speedtest()

    # Update the speed display
    download_label.config(text=f"Download: {download_speed:.2f} Mbps")
    upload_label.config(text=f"Upload: {upload_speed:.2f} Mbps")
    ping_label.config(text=f"Ping: {ping} ms")

    # Update ISP logo if found
    if isp_logo:
        isp_label.config(image=isp_logo)
        isp_label.image = isp_logo

    # Update graph
    download_speeds.append(download_speed)
    upload_speeds.append(upload_speed)
    if len(download_speeds) > 10:  # Limit graph length to the last 10 tests
        download_speeds.pop(0)
        upload_speeds.pop(0)

    # Trigger animation for graph update
    ani.event_source.start()

# Animation for live graph plot
def animate(i):
    ax.clear()
    ax.plot(range(len(download_speeds)), download_speeds, label="Download Speed (Mbps)", color="blue")
    ax.plot(range(len(upload_speeds)), upload_speeds, label="Upload Speed (Mbps)", color="green")
    ax.set_title('Speed Test Over Time')
    ax.set_xlabel('Test Number')
    ax.set_ylabel('Speed (Mbps)')
    ax.legend(loc="upper right")
    ax.grid(True)

# Color theme options
def set_theme(theme):
    if theme == "neon":
        root.config(bg="black")
        download_label.config(bg="black", fg="cyan")
        upload_label.config(bg="black", fg="green")
        ping_label.config(bg="black", fg="magenta")
    elif theme == "soft_blue":
        root.config(bg="lightblue")
        download_label.config(bg="lightblue", fg="darkblue")
        upload_label.config(bg="lightblue", fg="darkgreen")
        ping_label.config(bg="lightblue", fg="darkorange")

# Create the main UI window
root = tk.Tk()
root.title("Internet Speed Test")

# Create speed test display labels (define them before calling set_theme)
download_label = tk.Label(root, font=("Helvetica", 12))
download_label.pack(pady=5)

upload_label = tk.Label(root, font=("Helvetica", 12))
upload_label.pack(pady=5)

ping_label = tk.Label(root, font=("Helvetica", 12))
ping_label.pack(pady=5)

isp_label = tk.Label(root)
isp_label.pack(pady=5)

# Set default theme to Tech Neon (now it works as the labels are defined)
set_theme("neon")

# Button to test again
test_button = tk.Button(root, text="Test Again", command=update_speed, font=("Helvetica", 12))
test_button.pack(pady=10)

# Create figure for plotting
fig, ax = plt.subplots(figsize=(5, 3))
ax.set_title('Speed Test Over Time')
ax.set_xlabel('Test Number')
ax.set_ylabel('Speed (Mbps)')
ax.grid(True)

# Data for graph plotting
download_speeds = []
upload_speeds = []

# Set up animation for graph with cache_frame_data=False to suppress warning
ani = animation.FuncAnimation(fig, animate, interval=1000, cache_frame_data=False)
plt.tight_layout()

# Embed the plot into the Tkinter window
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
canvas = FigureCanvasTkAgg(fig, root)
canvas.get_tk_widget().pack()

# Run the first test and update UI
update_speed()

# Start the Tkinter event loop
root.mainloop()
