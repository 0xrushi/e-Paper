# E-Paper Display Manual

This guide documents how to use the Waveshare 4.2" e-Paper display on the Radxa Zero as a system terminal.

## 1. Quick Commands

### Map Console to Screen
If the screen is showing "static" or nothing but the e-paper script is running, you may need to map the console to the framebuffer:
```bash
sudo con2fbmap 1 0
```

### Clear the Screen
To wipe existing text/logs from the display:
```bash
sudo sh -c 'TERM=linux setterm -clear all > /dev/tty1'
```

### Write Text to Screen
To send a message directly to the display:
```bash
echo "Hello Radxa" | sudo tee /dev/tty1
```

**Note:** The screen is configured in "Inverted Mode" (White background, Black text) to mimic a paper terminal. To change this, edit the `ImageOps.invert` line in the python script.

### Run the Mirror Script Manually
This script captures the framebuffer (`/dev/fb0`) and sends it to the e-Paper display.
```bash
sudo python3 RadxaZero/python/examples/epd_4in2_V2_test.py
```
*Press `Ctrl+C` to stop.*

---

## 2. Automatic Startup (Systemd Service)

To have the screen work automatically at boot, we use a systemd service.

### Installation

1. **Copy the service file** to the system directory:
   ```bash
   sudo cp epd-mirror.service /etc/systemd/system/
   ```

2. **Reload the service daemon**:
   ```bash
   sudo systemctl daemon-reload
   ```

3. **Enable the service** (starts on next boot):
   ```bash
   sudo systemctl enable epd-mirror.service
   ```

4. **Start it immediately** (to test without rebooting):
   ```bash
   sudo systemctl start epd-mirror.service
   ```

### Status & Logs

Check if the service is running:
```bash
sudo systemctl status epd-mirror.service
```

View logs (useful for debugging):
```bash
sudo journalctl -u epd-mirror.service -f
```

### Uninstallation

To stop and remove the service:
```bash
sudo systemctl stop epd-mirror.service
sudo systemctl disable epd-mirror.service
sudo rm /etc/systemd/system/epd-mirror.service
sudo systemctl daemon-reload
```

## 4. Scrolling (using tmux)

Since a standard terminal doesn't have a scrollbar, use `tmux` to see text that has moved off the top of the screen.

1.  **Start tmux:**
    Type `tmux` and press Enter.
2.  **Enter Scroll Mode:**
    Press `Ctrl + b` then `[`
3.  **Navigate:**
    Use your **Arrow Keys** or **Page Up / Page Down** to scroll through history.
4.  **Exit Scroll Mode:**
    Press `q` to return to the live prompt.

---

## 5. Bluetooth Keyboard Setup

To use a wireless keyboard, you must pair it once via SSH. After that, it will auto-connect at boot.

1.  **Start the Bluetooth tool:**
    ```bash
    sudo bluetoothctl
    ```
2.  **Enable scanning:**
    ```
    [bluetooth]# power on
    [bluetooth]# agent on
    [bluetooth]# scan on
    ```
3.  **Put your keyboard in pairing mode.** You should see it appear in the list (e.g., `Device AA:BB:CC:DD:EE:FF Keychron K2`).
4.  **Pair and Trust:**
    ```
    [bluetooth]# pair AA:BB:CC:DD:EE:FF
    ```
    *(If asked for a PIN, type it on the keyboard and press Enter)*
    ```
    [bluetooth]# trust AA:BB:CC:DD:EE:FF
    [bluetooth]# connect AA:BB:CC:DD:EE:FF
    ```
5.  **Exit:**
    ```
    [bluetooth]# exit
    ```
Your keyboard is now linked. When you reboot, just tap a key to wake it up, and it will type directly onto the e-Paper terminal.
