# Vector My Shit MVP

A clean, fast image-to-SVG conversion tool. Upload any raster image (PNG, JPG, GIF, WebP) and get a scalable vector graphic.

## Features

- **Drag & drop upload** — just drop your image
- **Live preview** — see original and vectorized side by side
- **Adjustable settings** — control color precision, smoothing, and more
- **Instant download** — get your SVG immediately

## Tech Stack

- **Backend**: Python Flask + vtracer (Rust-based vectorization)
- **Frontend**: Vanilla HTML/CSS/JS (no build step needed)

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python server.py

# Visit http://localhost:5000
```

## Deployment Options

### Option 1: Railway (Recommended)
Railway makes Python deployment dead simple.

1. Push to GitHub
2. Connect repo to Railway
3. It auto-detects Python and deploys

**Cost**: Free tier available, ~$5/month for light usage

### Option 2: Render

1. Create a new Web Service
2. Connect your GitHub repo
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `gunicorn server:app`

**Cost**: Free tier available (spins down after inactivity)

### Option 3: DigitalOcean App Platform

1. Create new App
2. Link GitHub repo
3. Auto-detects Python

**Cost**: ~$5/month for basic dyno

### Option 4: VPS (Most Control)

For a $5-10/month VPS (DigitalOcean, Linode, Vultr):

```bash
# On your server
sudo apt update
sudo apt install python3-pip python3-venv nginx

# Clone and setup
git clone <your-repo>
cd vector-my-shit-mvp
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run with gunicorn
gunicorn -w 4 -b 127.0.0.1:5000 server:app

# Configure nginx to proxy to localhost:5000
```

## Configuration

The following vtracer parameters can be adjusted via the UI:

| Parameter | Default | Description |
|-----------|---------|-------------|
| colormode | color | 'color' or 'binary' (B&W) |
| filter_speckle | 4 | Remove artifacts smaller than this |
| color_precision | 6 | Color clustering precision (1-10) |
| mode | spline | 'spline' (smooth), 'polygon' (sharp), 'none' (pixel) |
| corner_threshold | 60 | Corner detection sensitivity |
| length_threshold | 4.0 | Path simplification |

## Customization

### Branding

Edit `static/index.html`:
- Update the logo text in `.logo`
- Change accent color in `:root` CSS variables
- Update footer links

### File Limits

In `server.py`:
- `MAX_FILE_SIZE`: Default 10MB
- `ALLOWED_EXTENSIONS`: Supported input formats

## API

### POST /api/convert

Upload an image for conversion.

**Request**: `multipart/form-data`
- `file`: Image file
- Optional: `colormode`, `filter_speckle`, `color_precision`, etc.

**Response**:
```json
{
  "success": true,
  "file_id": "uuid",
  "svg": "<svg>...</svg>",
  "stats": {
    "original_size": 12345,
    "svg_size": 6789
  }
}
```

### GET /api/download/{file_id}

Download the converted SVG file.

---

Built by [Warez](https://warez.agency)
