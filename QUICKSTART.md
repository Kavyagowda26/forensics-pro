# 🚀 FORENSICS PRO - Quick Start Guide

## ⚡ Fastest Way to Run (2 Minutes)

### Prerequisites
- Docker & Docker Compose installed
- 2GB free disk space
- 5 minutes

### Step 1: Navigate to Project
```bash
cd forensics-pro
```

### Step 2: Start Everything
```bash
docker-compose up --build
```

### Step 3: Open in Browser
```
Frontend: http://localhost:3000
Backend API: http://localhost:5000
```

**That's it!** ✅

---

## 🎯 What's Running

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | http://localhost:3000 | Web UI (React) |
| **Backend** | http://localhost:5000 | API Server (Flask) |
| **Database** | localhost:5432 | PostgreSQL |
| **C Engine** | Internal | Analysis engine |

---

## 📊 Using the Platform

### 1. Upload a Memory Dump
- Click "📤 Upload & Analyze" tab
- Drag & drop a .DMP or .core file
- Or click to select file

### 2. View Results
- Automatic analysis starts
- Results show in "📋 Results" tab
- View indicators and risk level

### 3. Generate Report
- Click "📄 Generate PDF Report"
- Download professional forensic report

### 4. View Statistics
- Check "📊 Dashboard"
- See all previous analyses

---

## 💻 Manual Setup (Without Docker)

### Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Backend runs on: `http://localhost:5000`

### Frontend Setup
```bash
cd frontend
npm install
REACT_APP_API_URL=http://localhost:5000 npm start
```

Frontend runs on: `http://localhost:3000`

---

## 🧪 Testing

### Test the API
```bash
# Health check
curl http://localhost:5000/api/health

# Upload a dump
curl -F "file=@dump.dmp" http://localhost:5000/api/upload

# Get statistics
curl http://localhost:5000/api/statistics
```

### Test with Sample Dump
```bash
# Copy your dump file
cp notepad.DMP forensics-pro/

# Then upload through web UI
```

---

## 📁 Project Structure

```
forensics-pro/
├── backend/                    # Flask API
│   ├── app.py                 # Main Flask app
│   ├── requirements.txt        # Dependencies
│   └── Dockerfile
├── frontend/                   # React web UI
│   ├── App.js                 # Main app
│   ├── App.css                # Styles
│   └── components/            # UI components
│       ├── Header.js
│       ├── UploadPanel.js
│       ├── Dashboard.js
│       └── AnalysisResults.js
├── core/                       # C forensics engine
│   ├── bin/mdmp_parser        # Executable
│   ├── src/                   # Source code
│   └── Dockerfile
├── docker-compose.yml         # One-command setup
└── docs/                      # Documentation
```

---

## 🎯 Features

### Frontend Features
✅ Drag & drop upload  
✅ Real-time analysis  
✅ Beautiful dashboard  
✅ PDF report generation  
✅ Statistics tracking  
✅ Indicator visualization  
✅ Risk assessment  

### Backend Features
✅ REST API  
✅ Async job processing  
✅ Database storage  
✅ Report generation  
✅ Error handling  
✅ CORS support  

### C Engine Features
✅ Minidump parsing  
✅ ELF core dump parsing  
✅ Code injection detection  
✅ Malware indicators  
✅ Safe memory operations  

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Change port in docker-compose.yml
# Or kill process using port:
lsof -i :5000    # Find process
kill -9 <PID>    # Kill process
```

### Docker Not Starting
```bash
# Check Docker is running
docker --version

# Check logs
docker-compose logs

# Rebuild
docker-compose down
docker-compose up --build
```

### Upload Fails
```bash
# Check file exists and is readable
ls -lh dump.dmp

# Check backend logs
docker-compose logs backend

# Verify API is running
curl http://localhost:5000/api/health
```

---

## 📚 API Endpoints

```
GET  /api/health               # Health check
POST /api/upload               # Upload dump file
GET  /api/analysis             # List all analyses
GET  /api/analysis/<id>        # Get specific analysis
GET  /api/analysis/<id>/report # Generate PDF report
GET  /api/statistics           # Get statistics
```

---

## 🔧 Configuration

### Environment Variables
```bash
# In docker-compose.yml
FLASK_ENV=development
DATABASE_URL=sqlite:///forensics.db
REACT_APP_API_URL=http://localhost:5000
```

### Max File Size
```python
# In backend/app.py
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB
```

---

## 🚀 Deployment

### Production Setup
```bash
# Build images
docker-compose build

# Run detached
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Production Checklist
- [ ] Use PostgreSQL instead of SQLite
- [ ] Set environment variables
- [ ] Enable HTTPS
- [ ] Add authentication
- [ ] Scale workers
- [ ] Setup monitoring
- [ ] Add backup strategy

---

## 📖 Next Steps

1. ✅ Start the platform
2. ✅ Upload a memory dump
3. ✅ Review results
4. ✅ Generate reports
5. ✅ Extend features
6. ✅ Deploy to production

---

## 💡 Tips

### Speed Up Analysis
- Use SSD for uploads
- Scale backend workers
- Cache results
- Optimize C engine

### Improve Detection
- Add more indicators
- Integrate YARA rules
- Add machine learning
- Implement custom plugins

### Better Reports
- Add graphs/charts
- Include timeline
- Add recommendations
- Custom branding

---

## 📞 Support

For issues:
1. Check logs: `docker-compose logs`
2. Verify ports are free
3. Ensure sufficient disk space
4. Check file permissions
5. Review API responses

---

**You're ready to use FORENSICS PRO!** 🎉

Start analyzing memory dumps now!
