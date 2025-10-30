import storage

storage.disable_usb_drive()  # Disable USB so we can write to the file system


try:
    with open("/sd/power_data.txt", "a") as f:
        f.write("STARTING POWER LOGGING\n")
except OSError:
    with open("/sd/power_data.txt", "w") as f:
        f.write("STARTING POWER LOGGING\n")  # ...existing code...
