import hashlib
import os
import json
import time
from pathlib import Path
from datetime import datetime

class FileIntegrityChecker:
      
    def calculate_hash(self, filepath, algorithm="sha256"):
        """
        Calculate cryptographic hash of a file
        
        Args:
            filepath: Path to the file
            algorithm: Hash algorithm (md5, sha1, sha256, sha512)
        
        Returns:
            Hexadecimal hash string
        """
        hash_func = hashlib.new(algorithm)
        
        try:
            with open(filepath, 'rb') as f:
                # Read file in chunks to handle large files
                while chunk := f.read(8192):
                    hash_func.update(chunk)
            return hash_func.hexdigest()
        except Exception as e:
            print(f"Error hashing {filepath}: {e}")
            return None

    def create_baseline(self, directory, algorithm="sha256"):
        """
        Create a baseline snapshot of files in a directory
        
        Args:
            directory: Directory to create baseline for
            algorithm: Hash algorithm to use
        """
        print(f"\n{'='*50}")
        print("CREATING BASELINE")
        print(f"{'='*50}")
        
        self.baseline_data = self.scan_directory(directory, algorithm)
        
        # Save baseline to file
        baseline_info = {
            'created': datetime.now().isoformat(),
            'directory': str(directory),
            'algorithm': algorithm,
            'files': self.baseline_data
        }
        
        try:
            with open(self.baseline_file, 'w') as f:
                json.dump(baseline_info, f, indent=4)
            print(f"\nBaseline created successfully!")
            print(f"Total files scanned: {len(self.baseline_data)}")
            print(f"Baseline saved to: {self.baseline_file}")
        except Exception as e:
            print(f"Error saving baseline: {e}")
