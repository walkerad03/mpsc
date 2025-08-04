# MPSC Final Submission

This project provides a complete pipeline for processing, transforming, and analyzing neonatal patient data for growth modeling and prediction. Raw JSON data files are converted to CSV format, then merged and analyzed using Jupyter notebooks.

## Project Management with UV
This project uses [UV](https://docs.astral.sh/uv/) as its package and environment manager, providing fast Python environment setup and script execution.

### UV Installation
UNIX (Linux/macOS):
```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Windows (PowerShell)
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

For detailed installation instructions and troubleshooting, see the [UV Getting Started Guide](https://docs.astral.sh/uv/getting-started/installation/).

## Data Organization
- Place all raw JSON Patient Data in the directory:
```
data/raw/
```
- All processed CSV files will be saved to:
```
data/processed/
```

## Data Conversion Script
To convert your raw JSON files into processed CSV files, run:
```sh
uv run scripts/convert_json_data.py
```
This script acts as a wrapper for all legacy Python utility scripts and ensures that the latest data transformations are applied.

Processed files will automatically be output to the `data/processed/` directory.

## Data Preprocessing and Analysis in Jupyter
Once your JSON data has been converted, you can launch the main analysis notebook (`final.ipynb`) using Jupyter Lab:
```sh
uv run --with jupyter jupyter lab
```
After running the command above, open the link provided in your terminal in your default web browser and navigate to `final.ipynb`.

Note that due to size of dataset and feature list, training can take an extremely long time.

## Summary of Workflow
1. Install UV using the instructions above.
2. Place raw JSON files in `data/raw/`.
3. Convert JSON to CSV with `uv run scripts/convert_json_data.py`.
4. Run analyses in `final.ipynb` using Jupyter Lab.
