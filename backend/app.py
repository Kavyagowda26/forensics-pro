from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import json
import hashlib
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# INCREASE FILE SIZE LIMIT
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 * 1024

UPLOAD_FOLDER = '/app/uploads'
QUEUE_FOLDER = '/app/queue'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(QUEUE_FOLDER, exist_ok=True)

analyses = {}
counter = 0

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'online',
        'version': '5.0',
        'max_file_size': '2GB',
        'accepted_files': 'ALL',
        'creator': 'Dharshan Kavya'
    })

@app.route('/api/upload', methods=['POST'])
def upload():
    global counter
    
    print("\n" + "="*60)
    print("FILE UPLOAD")
    print("="*60)
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file'}), 400
        
        file = request.files['file']
        if not file or file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        filename = secure_filename(file.filename)
        print(f"File: {filename}")
        
        # Save file
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        file_size = os.path.getsize(filepath)
        print(f"Size: {file_size / 1024 / 1024:.2f} MB")
        
        # Calculate hash
        sha = hashlib.sha256()
        with open(filepath, 'rb') as f:
            while True:
                chunk = f.read(8192)
                if not chunk:
                    break
                sha.update(chunk)
        file_hash = sha.hexdigest()
        
        # Queue for analysis
        counter += 1
        job_id = counter
        
        import shutil
        queue_path = os.path.join(QUEUE_FOLDER, f'{job_id}.bin')
        shutil.copy(filepath, queue_path)
        
        result = {
            'id': job_id,
            'filename': filename,
            'file_size': file_size,
            'file_hash': file_hash[:16] + '...',
            'status': 'processing',
            'risk_level': 'ANALYZING...',
            'threat_score': 0.0,
            'indicators': [],
            'timestamp': datetime.utcnow().isoformat()
        }
        
        analyses[job_id] = result
        print(f"Status: QUEUED (Job #{job_id})")
        print("="*60 + "\n")
        
        return jsonify(result), 201
    
    except Exception as e:
        print(f"ERROR: {e}")
        print("="*60 + "\n")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analysis', methods=['GET'])
def get_analyses():
    # Check for completed analyses
    for job_id in list(analyses.keys()):
        result_file = os.path.join('/app/results', f'{job_id}.json')
        if os.path.exists(result_file):
            with open(result_file, 'r') as f:
                result = json.load(f)
                analyses[job_id].update(result)
                analyses[job_id]['status'] = 'complete'
    
    return jsonify(list(analyses.values()))

@app.route('/api/statistics', methods=['GET'])
def stats():
    total = len(analyses)
    critical = sum(1 for a in analyses.values() if a.get('risk_level') == 'CRITICAL')
    high = sum(1 for a in analyses.values() if a.get('risk_level') == 'HIGH')
    
    return jsonify({
        'total_analyses': total,
        'critical_threats': critical,
        'high_threats': high,
        'max_file_size_mb': 2048
    })

if __name__ == '__main__':
    print('Backend starting - accepts ALL file types')
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
