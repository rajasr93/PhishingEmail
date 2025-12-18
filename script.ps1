# Root directory
$root = "phishing_agent"

# Create root directory
New-Item -ItemType Directory -Path $root -Force | Out-Null

# Top-level files
New-Item -ItemType File -Path "$root/config.py" -Force | Out-Null
New-Item -ItemType File -Path "$root/main.py" -Force | Out-Null
New-Item -ItemType File -Path "$root/README.md" -Force | Out-Null

# Database
New-Item -ItemType Directory -Path "$root/database" -Force | Out-Null
New-Item -ItemType File -Path "$root/database/queue_db.sqlite" -Force | Out-Null

# Processing module
New-Item -ItemType Directory -Path "$root/processing" -Force | Out-Null
New-Item -ItemType File -Path "$root/processing/__init__.py" -Force | Out-Null
New-Item -ItemType File -Path "$root/processing/ingestion.py" -Force | Out-Null
New-Item -ItemType File -Path "$root/processing/queue_manager.py" -Force | Out-Null
New-Item -ItemType File -Path "$root/processing/worker.py" -Force | Out-Null

# Analysis module
New-Item -ItemType Directory -Path "$root/analysis" -Force | Out-Null
New-Item -ItemType File -Path "$root/analysis/__init__.py" -Force | Out-Null
New-Item -ItemType File -Path "$root/analysis/headers.py" -Force | Out-Null
New-Item -ItemType File -Path "$root/analysis/structural.py" -Force | Out-Null
New-Item -ItemType File -Path "$root/analysis/sandbox.py" -Force | Out-Null
New-Item -ItemType File -Path "$root/analysis/ml_reasoning.py" -Force | Out-Null

# Dashboard
New-Item -ItemType Directory -Path "$root/dashboard" -Force | Out-Null

# Models
New-Item -ItemType Directory -Path "$root/models" -Force | Out-Null

# Utils
New-Item -ItemType Directory -Path "$root/utils" -Force | Out-Null
New-Item -ItemType File -Path "$root/utils/logger.py" -Force | Out-Null

Write-Host "phishing_agent file structure created successfully."
