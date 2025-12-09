# ICSI 524 Computer Security Project : FILE INTEGRITY CHECKER

Team Members:

Prathmesh Kale - 001663411

Rishikesh Sirisilla - 001661448

# 🔒 File Integrity Checker

A powerful and user-friendly security tool designed to monitor file integrity and detect unauthorized modifications, additions, or deletions in your file system. This project provides both command-line and GUI interfaces for maximum flexibility.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [How It Works](#how-it-works)
- [Installation](#installation)
- [Usage](#usage)
  - [GUI Version](#gui-version)
  - [Command-Line Version](#command-line-version)
- [Use Cases](#use-cases)
- [Technical Details](#technical-details)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

File Integrity Checker is a security monitoring tool that helps detect unauthorized changes to files and directories. It creates a cryptographic baseline of your files and can later verify if any files have been modified, added, or deleted. This is crucial for:

- **Security monitoring** - Detect malware or unauthorized access
- **Compliance requirements** - Meet security audit standards
- **Change detection** - Track modifications in critical directories
- **System integrity** - Ensure important files remain untampered

## ✨ Features

### Core Functionality
- ✅ **Baseline Creation** - Create cryptographic snapshots of directory contents
- ✅ **Integrity Verification** - Detect modified, added, and deleted files
- ✅ **Multiple Hash Algorithms** - Support for MD5, SHA1, SHA256, and SHA512
- ✅ **Recursive Scanning** - Automatically scan subdirectories
- ✅ **Large File Support** - Efficiently handle files of any size using chunked reading

### User Interface
- 🖥️ **Dual Interface** - Both GUI and command-line versions available
- 📊 **Progress Tracking** - Real-time progress bars and file-by-file updates
- 🎨 **Color-Coded Output** - Easy-to-read results with visual indicators
- 📝 **Detailed Reports** - Comprehensive breakdown of all changes detected

### Technical Features
- ⚡ **Multi-threaded Processing** - Non-blocking operations in GUI version
- 💾 **JSON Storage** - Human-readable baseline files
- 🔍 **Relative Path Tracking** - Portable baselines across different systems
- 🛡️ **Error Handling** - Robust error management and user feedback

## 🔧 How It Works

### 1. Baseline Creation
The tool scans all files in a specified directory and creates a "baseline" - a snapshot of the current state:

```
For each file:
  1. Calculate cryptographic hash (fingerprint)
  2. Record file size and modification time
  3. Store relative path for portability
  4. Save all data to baseline.json
```

### 2. Integrity Verification
When verifying integrity, the tool compares the current state against the baseline:

```
For each file in baseline:
  - Still exists? → If not, mark as DELETED
  - Hash matches? → If not, mark as MODIFIED

For each current file:
  - In baseline? → If not, mark as ADDED
```

### 3. Cryptographic Hashing
The tool uses cryptographic hash functions to create unique fingerprints:
- Even a single byte change results in a completely different hash
- Computationally infeasible to create two files with the same hash
- Industry-standard algorithms (SHA256 recommended)

## 📥 Installation

### Prerequisites
- Python 3.7 or higher
- Built-in libraries only (no external dependencies required!)

### Steps

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/file-integrity-checker.git
cd file-integrity-checker
```

2. **Verify Python installation**
```bash
python --version
# or
python3 --version
```

That's it! No additional packages needed - everything uses Python's standard library.

## 🚀 Usage

### GUI Version (Recommended for Beginners)

1. **Launch the GUI**
```bash
python file_checker_gui.py
```

2. **Create a Baseline**
   - Click "Browse" to select a directory
   - Choose hash algorithm (SHA256 recommended)
   - Click "Create Baseline"
   - Wait for completion (progress bar shows status)

3. **Verify Integrity**
   - Select the same directory
   - Click "Verify Integrity"
   - Review results in the output window