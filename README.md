# Interactive OSC Controller

A desktop GUI application built with Python that listens to serial port commands and triggers columns in Resolume Arena using OSC messages. Perfect for VJs, performers, and interactive installations.

---

## 🚀 Features

- Lists available serial COM ports for easy selection
- Configurable baud rate for serial communication
- User-defined command-to-column mapping (6 commands)
- Sends OSC messages to Resolume Arena to trigger columns
- Real-time log display of incoming serial data and OSC actions
- Start/Stop listening controls
- Intuitive GUI using Tkinter with custom background and logo

---

## 🛠️ Requirements

- Python 3.7 or higher
- Packages:
  - `pyserial`
  - `python-osc`
  - `Pillow`

Install packages using:

```bash
pip install pyserial python-osc Pillow
