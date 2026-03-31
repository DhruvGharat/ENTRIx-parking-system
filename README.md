# ENTRIx — Smart Parking System 🚗

**ENTRIx** is a computer-vision-powered smart parking management system that uses **YOLOv8** for license plate detection and **EasyOCR** for plate reading. It automatically tracks vehicle entry/exit, manages billing, and generates QR codes for a seamless parking experience.

---

## ✨ Features

- 🔍 **Automatic License Plate Detection** — Real-time YOLO-based detection via webcam
- 📖 **OCR Plate Reading** — EasyOCR extracts plate numbers with high accuracy
- 📱 **QR Code Generation** — Auto-generates a QR code at entry linked to a live billing page
- 💰 **Live Billing** — Flask web server shows real-time parking duration and cost
- 🧾 **Final Bill Popup** — Tkinter GUI displays the complete bill at exit
- 🗃️ **SQLite Database** — Persistent session storage for all vehicles
- 🚪 **Dual Gate System** — Separate entry (`live_detect.py`) and exit (`exit_detect.py`) scripts

---

## 🖼️ System Architecture

```
Entry Gate Camera
       │
       ▼
  live_detect.py  ──► YOLOv8 model ──► EasyOCR
       │
       ├──► database.py (start_session)
       │
       └──► QR Code → http://localhost:5000/session/<plate>
                              │
                         server.py (Flask)
                              │
                        session.html (Live Bill)

Exit Gate Camera
       │
       ▼
  exit_detect.py  ──► YOLOv8 model ──► EasyOCR
       │
       ├──► database.py (end_session)
       │
       └──► Tkinter Final Bill Popup
```

---

## 🛠️ Tech Stack

| Component       | Technology                   |
|----------------|------------------------------|
| Plate Detection | YOLOv8 (Ultralytics)         |
| OCR             | EasyOCR                      |
| Web Server      | Flask                        |
| Database        | SQLite3                      |
| GUI Popups      | Tkinter + Pillow             |
| QR Codes        | qrcode library               |
| Camera          | OpenCV                       |

---

## 📁 Project Structure

```
parking-system/
├── live_detect.py        # Entry gate — detects plates, starts session, shows QR
├── exit_detect.py        # Exit gate — detects plates, ends session, shows final bill
├── server.py             # Flask server — serves live billing page
├── database.py           # SQLite session management (start/end/query sessions)
├── session_manager.py    # JSON-based session utility (legacy/helper)
├── read_plate.py         # Standalone image-based plate reader
├── detect_plate.py       # Plate detection helper
├── qr_generator.py       # QR code generation utility
├── cam_test.py           # Camera connectivity test
├── show_image.py         # Image display utility
├── test_imports.py       # Import verification script
├── data.yaml             # YOLOv8 training config (dataset paths & class names)
├── requirements.txt      # Python dependencies
├── templates/
│   └── session.html      # Jinja2 template for live billing webpage
└── static/
    └── payment_qr.png    # Payment QR image shown at exit
```

> **Note:** The `runs/` folder (trained model weights), `dataset/`, `venv/`, and `*.db` files are excluded from this repo — see [Setup](#-setup--installation) below.

---

## 🚀 Setup & Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/parking-system.git
cd parking-system
```

### 2. Create a Virtual Environment

```bash
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Add the Trained Model

Train your own YOLOv8 model or use a pre-trained one:

```bash
# Train on your dataset
yolo detect train data=data.yaml model=yolov8n.pt epochs=50 imgsz=640
```

Place the trained weights at:
```
runs/detect/train/weights/best.pt
```

### 5. Add Payment QR Image

Place your payment QR code image at:
```
static/payment_qr.png
```

---

## ▶️ Running the System

### Start the Flask Web Server (Terminal 1)

```bash
python server.py
```

Server runs at: `http://127.0.0.1:5000`

### Start Entry Gate (Terminal 2)

```bash
python live_detect.py
```

- Opens webcam feed
- Detects license plates
- Starts a session in the database
- Shows QR code popup linking to the live billing page

### Start Exit Gate (Terminal 3)

```bash
python exit_detect.py
```

- Opens webcam feed
- Detects license plates
- Ends the session and calculates the final bill
- Shows a Tkinter popup with the bill and payment QR

### Test on a Static Image

```bash
python read_plate.py
```

Set the `IMAGE_PATH` variable in `read_plate.py` to point to your test image.

---

## ⚙️ Configuration

| Setting              | Location          | Default         |
|---------------------|-------------------|-----------------|
| Billing rate         | `live_detect.py` / `exit_detect.py` | ₹1 per minute |
| Camera index         | `live_detect.py` / `exit_detect.py` | `0` (default cam) |
| Flask port           | `server.py`       | `5000`          |
| Model weights path   | `live_detect.py` / `exit_detect.py` | `runs/detect/train/weights/best.pt` |
| QR code output dir   | `live_detect.py`  | `qr_codes/`     |

---

## 🗃️ Database Schema

The system uses a single SQLite table:

```sql
CREATE TABLE sessions (
    plate      TEXT,
    entry_time TEXT,
    exit_time  TEXT
);
```

- `exit_time` is `NULL` for active (parked) sessions.
- Query active sessions with `WHERE exit_time IS NULL`.

---

## 📋 Requirements

- Python 3.9+
- Webcam (for live detection)
- CUDA GPU *(optional, for faster YOLO inference)*

---

## 🤝 Contributing

1. Fork this repo
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m "Add my feature"`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

## 👨‍💻 Author

Built with ❤️ as part of a smart parking startup project.

> *ENTRIx — Where technology meets smart parking.*
