import hashlib
import os
import json
import time
from pathlib import Path
from datetime import datetime

class FileIntegrityChecker:
    def __init__(self, baseline_file="baseline.json"):
        """
        Initialize the File Integrity Checker
        
        Args:
            baseline_file: Name of the file to store baseline data
        """
        self.baseline_file = baseline_file
        self.baseline_data = {}

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

    def scan_directory(self, directory, algorithm="sha256"):
        """
        Scan directory and generate hash information for all files
        
        Args:
            directory: Directory path to scan
            algorithm: Hash algorithm to use
        
        Returns:
            Dictionary with file information
        """
        file_data = {}
        directory_path = Path(directory)
        
        if not directory_path.exists():
            print(f"Error: Directory '{directory}' does not exist")
            return file_data
        
        print(f"\nScanning directory: {directory}")
        print("-" * 50)
        
        # Recursively scan all files
        for filepath in directory_path.rglob('*'):
            if filepath.is_file():
                try:
                    # Get file information
                    file_stats = filepath.stat()
                    file_hash = self.calculate_hash(filepath, algorithm)
                    
                    if file_hash:
                        relative_path = str(filepath.relative_to(directory_path))
                        file_data[relative_path] = {
                            'hash': file_hash,
                            'size': file_stats.st_size,
                            'modified': file_stats.st_mtime,
                            'algorithm': algorithm
                        }
                        print(f"Scanned: {relative_path}")
                
                except Exception as e:
                    print(f"Error scanning {filepath}: {e}")
        
        return file_data
    
    def load_baseline(self):
        """
        Load baseline data from file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.baseline_file, 'r') as f:
                baseline_info = json.load(f)
                self.baseline_data = baseline_info['files']
                print(f"Baseline loaded from: {self.baseline_file}")
                print(f"Created: {baseline_info['created']}")
                print(f"Directory: {baseline_info['directory']}")
                print(f"Files in baseline: {len(self.baseline_data)}")
                return True
        except FileNotFoundError:
            print(f"Baseline file '{self.baseline_file}' not found")
            print("Please create a baseline first using option 1")
            return False
        except Exception as e:
            print(f"Error loading baseline: {e}")
            return False
    
        def verify_integrity(self, directory):
        """
        Verify file integrity against baseline
        
        Args:
            directory: Directory to verify
        """
        print(f"\n{'='*50}")
        print("VERIFYING INTEGRITY")
        print(f"{'='*50}")
        
        if not self.load_baseline():
            return
        
        # Get current state
        algorithm = list(self.baseline_data.values())[0]['algorithm'] if self.baseline_data else 'sha256'
        current_data = self.scan_directory(directory, algorithm)
        
        # Compare
        modified = []
        added = []
        deleted = []
        
        # Check for modifications and deletions
        for filename, baseline_info in self.baseline_data.items():
            if filename not in current_data:
                deleted.append(filename)
            elif current_data[filename]['hash'] != baseline_info['hash']:
                modified.append(filename)
        
        # Check for new files
        for filename in current_data:
            if filename not in self.baseline_data:
                added.append(filename)
        
        # Display results
        print(f"\n{'='*50}")
        print("INTEGRITY CHECK RESULTS")
        print(f"{'='*50}")
        
        if not modified and not added and not deleted:
            print("\nALL FILES INTACT - No changes detected!!")
        else:
            print(f"\nCHANGES DETECTED:")
            
            if modified:
                print(f"\nModified Files ({len(modified)}):")
                for f in modified:
                    print(f"  - {f}")
            
            if added:
                print(f"\nNew Files ({len(added)}):")
                for f in added:
                    print(f"  - {f}")
            
            if deleted:
                print(f"\nDeleted Files ({len(deleted)}):")
                for f in deleted:
                    print(f"  - {f}")
        
        print(f"\nSummary: {len(modified)} modified, {len(added)} added, {len(deleted)} deleted")
