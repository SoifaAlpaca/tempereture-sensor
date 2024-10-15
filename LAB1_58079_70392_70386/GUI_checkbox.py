import serial
import time
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd

# Serial connection initialization (Adjust the COM port and baud rate as per your setup)
ser = serial.Serial('COM6', 115200, timeout=2)
time.sleep(2)  # wait for the Serial to initialize

# Global variable to control whether the graph updates
update_graph = True

# Function to read temperature data from serial
ntc_values = []
lm_values = []
ds_values = []


def read_data():
    line = ser.readline()
    if line:
        string = line.decode()  # convert the byte string to a normal string
        values = string.split(',')
        if len(values) == 3:
            try:
                ntc = float(values[0])
                lm = float(values[1])
                ds = float(values[2])
                return ntc, lm, ds
            except ValueError:
                pass
    return None, None, None

# Callback function for the relay control checkbox


def toggle_relay():
    if relay_var.get():
        print('RELAY_ON\n')
        ser.write('RELAY_ON'.encode('utf-8'))
    else:
        print('RELAY_Off\n')
        ser.write('RELAY_OFF'.encode('utf-8'))

# Callback function for automatic mode checkbox


def toggle_automatic():
    if automatic_var.get():
        print('AUTOMATIC\n')
        ser.write('AUTOMATIC'.encode('utf-8'))
    else:
        print('Manual\n')
        ser.write('MANUAL'.encode('utf-8'))

# Update temperature readings and plot


def update_display():
    if update_graph:
        ntc, lm, ds = read_data()
        if ntc is not None:
            ntc_values.append(ntc)
            lm_values.append(lm)
            ds_values.append(ds)

            # Update labels with the latest temperature values
            ntc_label.config(text=f"NTC Temperature: {ntc:.2f} °C")
            lm_label.config(text=f"LM35 Temperature: {lm:.2f} °C")
            ds_label.config(text=f"DS18B20 Temperature: {ds:.2f} °C")

            # Calculate and update temperature differences
            ntc_diff = ntc - ds
            lm_diff = lm - ds
            ntc_diff_label.config(
                text=f"NTC - DS18B20 Difference: {ntc_diff:.2f} °C")
            lm_diff_label.config(
                text=f"LM35 - DS18B20 Difference: {lm_diff:.2f} °C")

            # Update plot
            ax.clear()
            ax.plot(ntc_values, label="NTC", color=(0, 101/255, 189/255))
            ax.plot(lm_values, label="LM35", color="#31a748")
            ax.plot(ds_values, label="DS18B20", color="#f15929")
            ax.set_xlabel('Time (s)')
            ax.set_ylabel('Temperature (°C)')
            ax.set_xlim(0, None)  # X-axis starts at 0

            # Enable the grid
            ax.grid(True)
            ax.legend()
            canvas.draw()

        # Schedule next update
        root.after(5, update_display)

# Function to clear the graph and reset data


def clear_graph():
    ntc_values.clear()
    lm_values.clear()
    ds_values.clear()
    ax.clear()
    canvas.draw()
    ntc_label.config(text="NTC Temperature: N/A")
    lm_label.config(text="LM35 Temperature: N/A")
    ds_label.config(text="DS18B20 Temperature: N/A")
    ntc_diff_label.config(text="NTC - DS18B20 Difference: N/A")
    lm_diff_label.config(text="LM35 - DS18B20 Difference: N/A")

# Function to stop the graph from updating


def stop_graph():
    global update_graph
    update_graph = False
    df = pd.DataFrame({
        'lmdata': ntc_values,
        'ntcdata': lm_values,
        'dsdata': ds_values
    })

    df.to_csv('data.csv', index=False)

# Function to resume the graph update


def start_graph():
    global update_graph
    update_graph = True
    update_display()

# Function to properly close the serial connection and terminate the program


def on_closing():
    global update_graph
    update_graph = False
    ser.close()  # Close the serial connection
    root.destroy()  # Close the tkinter window


# GUI setup
root = tk.Tk()
root.title("Temperature Monitor")

# Set lilac background color for the main window
lilac_color = '#744da9'
light_lilac_color = '#d7bde2'  # Light lilac color for the box
root.configure(bg=lilac_color)

# Define custom styles for ttk widgets
style = ttk.Style()
style.configure("TFrame", background=light_lilac_color)
style.configure("TLabel", background=light_lilac_color)

# Relay control checkbox
relay_var = tk.BooleanVar()
relay_checkbox = ttk.Checkbutton(
    root, text="Relay ON/OFF", variable=relay_var, command=toggle_relay)
relay_checkbox.pack(pady=10)

# Create a frame to contain the temperature info with a light lilac background
info_frame = ttk.Frame(root, padding=10, relief="solid", borderwidth=2)
info_frame.pack(pady=10, padx=10, fill="both", expand=True)

# Temperature labels inside the frame
ntc_label = ttk.Label(info_frame, text="NTC Temperature: N/A")
ntc_label.pack(pady=5)

lm_label = ttk.Label(info_frame, text="LM35 Temperature: N/A")
lm_label.pack(pady=5)

ds_label = ttk.Label(info_frame, text="DS18B20 Temperature: N/A")
ds_label.pack(pady=5)

# Labels for temperature differences inside the frame
ntc_diff_label = ttk.Label(info_frame, text="NTC - DS18B20 Difference: N/A")
ntc_diff_label.pack(pady=5)

lm_diff_label = ttk.Label(info_frame, text="LM35 - DS18B20 Difference: N/A")
lm_diff_label.pack(pady=5)

# Checkbox for automatic mode
automatic_var = tk.BooleanVar()
automatic_checkbox = ttk.Checkbutton(
    root, text="Automatic", variable=automatic_var, command=toggle_automatic)
automatic_checkbox.pack(pady=10)

# Matplotlib plot
fig, ax = plt.subplots()

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(pady=20)

# Create a frame to align the buttons horizontally
button_frame = ttk.Frame(root)
button_frame.pack(pady=10)

# Buttons inside the horizontal button frame
clear_button = ttk.Button(
    button_frame, text="Clear Graph", command=clear_graph)
clear_button.pack(side="left", padx=5)

stop_button = ttk.Button(button_frame, text="Stop Graph", command=stop_graph)
stop_button.pack(side="left", padx=5)

start_button = ttk.Button(
    button_frame, text="Start Graph", command=start_graph)
start_button.pack(side="left", padx=5)


# Handle window close event to terminate the program properly
root.protocol("WM_DELETE_WINDOW", on_closing)

# Start the temperature reading and display update loop
root.after(5, update_display)

# Run the GUI main loop
root.mainloop()

# Close the serial connection when the window is closed
ser.close()
