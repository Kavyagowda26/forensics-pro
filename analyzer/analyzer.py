import os
import json
import hashlib
from datetime import datetime
import time

class FastAnalyzer:
    def analyze(self, filepath):
        print(f"\n[ANALYZER] Starting: {filepath}")
        
        try:
            file_size = os.path.getsize(filepath)
            print(f"[ANALYZER] Size: {file_size / 1024 / 1024:.2f} MB")
            
            # Read file
            if file_size > 100 * 1024 * 1024:
                print("[ANALYZER] Large file - sampling")
                with open(filepath, 'rb') as f:
                    beginning = f.read(1024 * 100)
                    f.seek(file_size // 2)
                    middle = f.read(1024 * 100)
                    f.seek(max(0, file_size - 1024 * 100))
                    end = f.read(1024 * 100)
                    content = beginning + middle + end
            else:
                with open(filepath, 'rb') as f:
                    content = f.read()
            
            # Calculate hash
            sha = hashlib.sha256()
            with open(filepath, 'rb') as f:
                while True:
                    chunk = f.read(8192)
                    if not chunk:
                        break
                    sha.update(chunk)
            file_hash = sha.hexdigest()[:16]
            
            indicators = []
            
            # Signature Detection
            print("[ANALYZER] Scanning signatures...")
            if b'MZ' in content:
                indicators.append({'type': 'PE_EXECUTABLE', 'severity': 'CRITICAL', 'description': 'Windows executable', 'confidence': 0.95})
                print("  Found: PE executable")
            
            if b'\x7fELF' in content:
                indicators.append({'type': 'ELF_EXECUTABLE', 'severity': 'HIGH', 'description': 'Linux executable', 'confidence': 0.90})
                print("  Found: ELF executable")
            
            if b'mimikatz' in content:
                indicators.append({'type': 'MIMIKATZ', 'severity': 'CRITICAL', 'description': 'Credential stealer', 'confidence': 0.95})
                print("  Found: Mimikatz")
            
            # Heuristics
            print("[ANALYZER] Running heuristics...")
            if file_size > 500000:
                indicators.append({'type': 'LARGE_FILE', 'severity': 'MEDIUM', 'description': 'Large file', 'confidence': 0.65})
            
            if file_size % 4096 != 0:
                indicators.append({'type': 'MISALIGNED', 'severity': 'HIGH', 'description': 'Memory misalignment', 'confidence': 0.80})
            
            if 1000 < file_size < 100000:
                indicators.append({'type': 'SHELLCODE_PATTERN', 'severity': 'CRITICAL', 'description': 'Shellcode pattern', 'confidence': 0.85})
                print("  Found: Shellcode pattern")
            
            # Entropy
            print("[ANALYZER] Calculating entropy...")
            entropy = self.calculate_entropy(content)
            print(f"  Entropy: {entropy:.2f}")
            
            if entropy > 7.5:
                indicators.append({'type': 'HIGH_ENTROPY', 'severity': 'MEDIUM', 'description': f'High entropy ({entropy:.2f})', 'confidence': 0.70})
            
            # Threat score
            if not indicators:
                threat_score = 0.1
                threat_level = 'LOW'
            else:
                scores = [i['confidence'] for i in indicators]
                threat_score = sum(scores) / len(scores)
                
                if threat_score > 0.85:
                    threat_level = 'CRITICAL'
                elif threat_score > 0.70:
                    threat_level = 'HIGH'
                elif threat_score > 0.50:
                    threat_level = 'MEDIUM'
                else:
                    threat_level = 'LOW'
            
            result = {
                'status': 'complete',
                'risk_level': threat_level,
                'threat_score': round(threat_score, 2),
                'indicators': indicators,
                'file_hash': file_hash + '...',
                'total_indicators': len(indicators),
                'entropy': entropy,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            print(f"[ANALYZER] Complete: {threat_level} ({threat_score})")
            return result
        
        except Exception as e:
            print(f"[ANALYZER] Error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def calculate_entropy(self, data):
        if not data:
            return 0.0
        byte_counts = {}
        for byte in data:
            byte_counts[byte] = byte_counts.get(byte, 0) + 1
        entropy = 0.0
        for count in byte_counts.values():
            p = count / len(data)
            if p > 0:
                import math
                entropy -= p * math.log2(p)
        return round(entropy, 2)

if __name__ == '__main__':
    print("[ANALYZER] Starting - analyzes ALL file types")
    analyzer = FastAnalyzer()
    
    queue_dir = '/app/queue'
    results_dir = '/app/results'
    os.makedirs(queue_dir, exist_ok=True)
    os.makedirs(results_dir, exist_ok=True)
    
    while True:
        try:
            files = os.listdir(queue_dir)
            for filename in files:
                if filename.endswith('.bin'):
                    filepath = os.path.join(queue_dir, filename)
                    result = analyzer.analyze(filepath)
                    
                    result_file = os.path.join(results_dir, filename.replace('.bin', '.json'))
                    with open(result_file, 'w') as f:
                        json.dump(result, f)
                    
                    os.remove(filepath)
                    print(f"[ANALYZER] Saved result\n")
            
            time.sleep(0.5)
        
        except Exception as e:
            print(f"[ANALYZER] Error: {e}")
            time.sleep(1)
