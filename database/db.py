import sqlite3
import json
from datetime import datetime
import os

class ForensicsDatabase:
    '''SQLite database for storing analysis results and ML training data'''
    
    def __init__(self, db_path='/app/database/forensics.db'):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_database()
    
    def init_database(self):
        '''Initialize database tables'''
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table 1: Analysis History
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                file_hash TEXT UNIQUE,
                file_size INTEGER,
                entropy REAL,
                risk_level TEXT,
                threat_score REAL,
                indicators TEXT,
                analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                analysis_method TEXT,
                ml_confidence REAL,
                user_confirmed INTEGER DEFAULT 0,
                actual_threat INTEGER DEFAULT NULL
            )
        ''')
        
        # Table 2: ML Training Data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ml_training_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_size INTEGER,
                entropy REAL,
                has_pe INTEGER,
                has_elf INTEGER,
                has_malware_sig INTEGER,
                is_misaligned INTEGER,
                null_byte_ratio REAL,
                high_entropy INTEGER,
                label INTEGER,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table 3: Threat Intelligence
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS threat_intelligence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_hash TEXT UNIQUE,
                threat_name TEXT,
                threat_family TEXT,
                severity TEXT,
                first_seen TIMESTAMP,
                last_seen TIMESTAMP,
                detection_count INTEGER DEFAULT 1,
                confidence REAL
            )
        ''')
        
        # Table 4: Model Performance Metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_version TEXT,
                accuracy REAL,
                precision REAL,
                recall REAL,
                f1_score REAL,
                training_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                test_samples INTEGER
            )
        ''')
        
        # Table 5: False Positive/Negative Log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_hash TEXT,
                original_prediction TEXT,
                corrected_prediction TEXT,
                reason TEXT,
                feedback_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print("[DB] Database initialized")
    
    def store_analysis(self, filename, file_hash, file_size, entropy, risk_level, 
                      threat_score, indicators, method, ml_conf):
        '''Store analysis result in database'''
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO analysis_history 
                (filename, file_hash, file_size, entropy, risk_level, threat_score, 
                 indicators, analysis_method, ml_confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (filename, file_hash, file_size, entropy, risk_level, 
                  threat_score, json.dumps(indicators), method, ml_conf))
            
            conn.commit()
            print(f"[DB] Analysis stored for {filename}")
            return True
        except Exception as e:
            print(f"[DB] Error storing analysis: {e}")
            return False
        finally:
            conn.close()
    
    def get_analysis_history(self, limit=100):
        '''Get recent analyses'''
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT filename, file_hash, risk_level, threat_score, analysis_date, 
                   analysis_method, ml_confidence
            FROM analysis_history
            ORDER BY analysis_date DESC
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def check_file_history(self, file_hash):
        '''Check if file was previously analyzed'''
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT risk_level, threat_score, analysis_date, actual_threat
            FROM analysis_history
            WHERE file_hash = ?
            ORDER BY analysis_date DESC
            LIMIT 1
        ''', (file_hash,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'found': True,
                'risk_level': result[0],
                'threat_score': result[1],
                'last_seen': result[2],
                'confirmed_threat': result[3]
            }
        return {'found': False}
    
    def store_ml_training_sample(self, features, label):
        '''Store data for ML training'''
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO ml_training_data 
                (file_size, entropy, has_pe, has_elf, has_malware_sig, 
                 is_misaligned, null_byte_ratio, high_entropy, label)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', tuple(features) + (label,))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"[DB] Error storing training sample: {e}")
            return False
        finally:
            conn.close()
    
    def get_training_data(self, min_samples=100):
        '''Get all training data for model retraining'''
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT file_size, entropy, has_pe, has_elf, has_malware_sig, 
                   is_misaligned, null_byte_ratio, high_entropy, label
            FROM ml_training_data
            ORDER BY created_date DESC
        ''')
        
        data = cursor.fetchall()
        conn.close()
        
        if len(data) < min_samples:
            print(f"[DB] Only {len(data)} samples (need {min_samples})")
            return None
        
        return data
    
    def store_threat_intelligence(self, file_hash, threat_name, severity):
        '''Store threat intelligence'''
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO threat_intelligence 
                (file_hash, threat_name, severity, last_seen, detection_count)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP, 
                       COALESCE((SELECT detection_count FROM threat_intelligence 
                                WHERE file_hash = ?), 0) + 1)
            ''', (file_hash, threat_name, severity, file_hash))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"[DB] Error storing threat intelligence: {e}")
            return False
        finally:
            conn.close()
    
    def store_model_metrics(self, model_version, metrics, test_samples):
        '''Store model performance metrics'''
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO model_metrics 
                (model_version, accuracy, precision, recall, f1_score, test_samples)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (model_version, metrics['accuracy'], metrics['precision'],
                  metrics['recall'], metrics['f1_score'], test_samples))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"[DB] Error storing metrics: {e}")
            return False
        finally:
            conn.close()
    
    def get_statistics(self):
        '''Get database statistics'''
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM analysis_history')
        total_analyses = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM ml_training_data')
        training_samples = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM threat_intelligence')
        threats_found = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT COUNT(*) FROM analysis_history 
            WHERE risk_level = 'CRITICAL'
        ''')
        critical_threats = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_analyses': total_analyses,
            'training_samples': training_samples,
            'threats_found': threats_found,
            'critical_threats': critical_threats
        }
