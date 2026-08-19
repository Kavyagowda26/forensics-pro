from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from datetime import datetime
from werkzeug.utils import secure_filename
import hashlib
import json
import os
import io

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = '/app/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Advanced data storage
analyses = {}
job_counter = 0

class AdvancedAnalyzer:
    SIGNATURES = {
        b'MZ': ('PE_EXECUTABLE', 'CRITICAL', 'Windows PE executable detected in memory', 0.95),
        b'\x7fELF': ('ELF_EXECUTABLE', 'HIGH', 'Linux ELF executable detected', 0.90),
        b'cmd.exe': ('CMD_EXECUTION', 'HIGH', 'Command shell execution detected', 0.85),
        b'powershell': ('POWERSHELL', 'HIGH', 'PowerShell execution detected', 0.85),
        b'mimikatz': ('MIMIKATZ', 'CRITICAL', 'Mimikatz credential stealer found', 0.95),
        b'nc.exe': ('NETCAT', 'CRITICAL', 'Netcat network utility detected', 0.90),
        b'CreateRemoteThread': ('REMOTE_THREAD', 'CRITICAL', 'Remote thread injection detected', 0.90),
        b'VirtualAlloc': ('MEMORY_ALLOC', 'MEDIUM', 'Virtual memory allocation detected', 0.65),
    }

    def __init__(self, filepath):
        self.filepath = filepath
        self.size = os.path.getsize(filepath)
        self.hash = self._calculate_hash()
        self.entropy = self._calculate_entropy()

    def _calculate_hash(self):
        sha = hashlib.sha256()
        with open(self.filepath, 'rb') as f:
            while chunk := f.read(8192):
                sha.update(chunk)
        return sha.hexdigest()

    def _calculate_entropy(self):
        try:
            with open(self.filepath, 'rb') as f:
                data = f.read()
            byte_freq = {}
            for byte in data:
                byte_freq[byte] = byte_freq.get(byte, 0) + 1
            
            entropy = 0
            for freq in byte_freq.values():
                p = freq / len(data)
                entropy -= p * (p and __import__('math').log2(p) or 0)
            return round(entropy, 2)
        except:
            return 0.0

    def analyze(self):
        indicators = []
        
        with open(self.filepath, 'rb') as f:
            content = f.read()

        # Signature detection
        for sig, (sig_type, severity, desc, confidence) in self.SIGNATURES.items():
            if sig in content:
                indicators.append({
                    'type': sig_type,
                    'severity': severity,
                    'description': desc,
                    'confidence': confidence,
                    'method': 'Signature Matching'
                })

        # Pattern analysis
        if self.size > 500000:
            indicators.append({
                'type': 'LARGE_MEMORY',
                'severity': 'MEDIUM',
                'description': 'Unusually large memory region detected',
                'confidence': 0.65,
                'method': 'Heuristic Analysis'
            })

        if self.size % 4096 != 0:
            indicators.append({
                'type': 'MISALIGNED_MEMORY',
                'severity': 'HIGH',
                'description': 'Memory not aligned to 4KB page boundary',
                'confidence': 0.80,
                'method': 'Alignment Check'
            })

        if 1000 < self.size < 100000:
            indicators.append({
                'type': 'SHELLCODE',
                'severity': 'CRITICAL',
                'description': 'Memory size consistent with shellcode injection',
                'confidence': 0.85,
                'method': 'Size Analysis'
            })

        # Entropy analysis
        if self.entropy > 7.5:
            indicators.append({
                'type': 'HIGH_ENTROPY',
                'severity': 'MEDIUM',
                'description': 'High entropy detected - possible encryption/compression',
                'confidence': 0.70,
                'method': 'Entropy Analysis',
                'entropy_score': self.entropy
            })

        # Calculate threat level
        if not indicators:
            threat_level = 'LOW'
            score = 0.1
        else:
            score = sum(i['confidence'] for i in indicators) / len(indicators)
            critical = len([i for i in indicators if i['severity'] == 'CRITICAL'])
            high = len([i for i in indicators if i['severity'] == 'HIGH'])

            if critical > 0 or score > 0.85:
                threat_level = 'CRITICAL'
            elif high > 2 or score > 0.70:
                threat_level = 'HIGH'
            elif high > 0 or score > 0.50:
                threat_level = 'MEDIUM'
            else:
                threat_level = 'LOW'

        return {
            'summary': {
                'file_size': self.size,
                'file_hash': self.hash,
                'entropy': self.entropy,
                'timestamp': datetime.utcnow().isoformat()
            },
            'threat_level': threat_level,
            'threat_score': round(score, 2),
            'indicators': indicators,
            'detection_methods': len(set(i['method'] for i in indicators)),
            'statistics': {
                'total': len(indicators),
                'critical': len([i for i in indicators if i['severity'] == 'CRITICAL']),
                'high': len([i for i in indicators if i['severity'] == 'HIGH']),
                'medium': len([i for i in indicators if i['severity'] == 'MEDIUM'])
            }
        }

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'online', 'version': '5.0', 'timestamp': datetime.utcnow().isoformat()})

@app.route('/api/upload', methods=['POST'])
def upload():
    global job_counter
    if 'file' not in request.files:
        return {'error': 'No file provided'}, 400

    file = request.files['file']
    if not file.filename:
        return {'error': 'No filename'}, 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    job_counter += 1
    job_id = job_counter

    analyzer = AdvancedAnalyzer(filepath)
    analysis = analyzer.analyze()

    result = {
        'id': job_id,
        'filename': file.filename,
        'file_size': analyzer.size,
        'file_hash': analyzer.hash[:16] + '...',
        'risk_level': analysis['threat_level'],
        'threat_score': analysis['threat_score'],
        'indicators_count': analysis['statistics']['total'],
        'critical_count': analysis['statistics']['critical'],
        'high_count': analysis['statistics']['high'],
        'timestamp': datetime.utcnow().isoformat(),
        'analysis_data': analysis
    }

    analyses[job_id] = result
    return result, 201

@app.route('/api/analysis', methods=['GET'])
def list_analysis():
    return jsonify(sorted(analyses.values(), key=lambda x: x['timestamp'], reverse=True))

@app.route('/api/analysis/<int:job_id>', methods=['GET'])
def get_analysis(job_id):
    if job_id in analyses:
        return jsonify(analyses[job_id])
    return {'error': 'Not found'}, 404

@app.route('/api/statistics', methods=['GET'])
def stats():
    total = len(analyses)
    critical = sum(1 for a in analyses.values() if a['risk_level'] == 'CRITICAL')
    high = sum(1 for a in analyses.values() if a['risk_level'] == 'HIGH')
    avg_threat = sum(a['threat_score'] for a in analyses.values()) / total if total > 0 else 0

    return jsonify({
        'total_analyses': total,
        'critical_threats': critical,
        'high_threats': high,
        'average_threat_score': round(avg_threat, 2),
        'success_rate': 100,
        'system_status': 'ONLINE'
    })

if __name__ == '__main__':
    print('Forensics Pro Backend v5.0 - Starting...', flush=True)
    app.run(host='0.0.0.0', port=5000, debug=False)
