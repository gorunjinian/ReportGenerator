# Heritage Site Assessment Report Generator

This program converts CSV data from Google Forms into formatted PDF reports for heritage site assessments after conflicts or disasters. It automatically downloads images from Google Drive links and includes them in the report.

## Project Structure

```
BuildFolder/
├── report_generator.py      # Main Python script
├── requirements.txt         # Python dependencies
├── build_exe.py            # Script to build the executable
├── run_report_generator.bat # Batch file for drag-and-drop
├── README.md               # This file
└── (Generated files)
    ├── report_generator.exe # Generated executable
    └── *.pdf               # Generated reports
```

## Setup Instructions

### 1. Install Python
- Download and install Python 3.8 or higher from [python.org](https://www.python.org/)
- Make sure to check "Add Python to PATH" during installation

### 2. Set up the project
1. Create a folder named `BuildFolder` on your computer
2. Save all the provided files into this folder:
   - `report_generator.py`
   - `requirements.txt`
   - `build_exe.py`
   - `run_report_generator.bat`

### 3. Install dependencies
Open Command Prompt or Terminal in the BuildFolder directory and run:
```bash
pip install -r requirements.txt
```

### 4. Build the executable
In the same Command Prompt/Terminal, run:
```bash
python build_exe.py
```

This will create `report_generator.exe` in your BuildFolder.

## Usage Instructions

### Method 1: Drag and Drop (Recommended)
1. Place your logo files in the same folder as your CSV file:
2. Drag your CSV file onto `run_report_generator.bat`
3. The program will download images from Google Drive links and generate the PDF report

### Method 2: Direct Execution
1. Open Command Prompt in the folder containing your CSV
2. Run: `path\to\BuildFolder\report_generator.exe "your_file.csv"`

## Features

### Automatic Image Download
- The program automatically downloads images from Google Drive links in the CSV
- Supports various Google Drive URL formats
- Images are properly sized and positioned in the PDF
- Primary display photo is shown prominently
- Additional images are arranged in a grid layout

### Google Drive Link Formats Supported
- `https://drive.google.com/file/d/FILE_ID/view`
- `https://drive.google.com/open?id=FILE_ID`
- Direct file IDs
- Other common Google Drive sharing formats

## CSV File Format

The program expects a CSV file exported from Google Forms with the following columns:
- Timestamp
- Assessor's Name
- Supervisor
- Organization
- Date of Assessment (in YYYY/MM/DD format)
- Monument Reference
- Monument Name
- Ownership
- Governorate
- District
- City-Village
- Location
- Primary Display Photo Upload (Google Drive link)
- Additional images and files (comma-separated Google Drive links)
- (and other damage assessment fields...)

**Important**: When multiple forms are in the CSV, the program automatically selects the entry with the latest "Date of Assessment".

## Output

The program generates a PDF report with:
- Header with two logos (if provided)
- 9 main sections:
  1. General Information
  2. Location Information
  3. Preliminary Conditions
  4. Evidence of Conflict or Damage
  5. Visible Damage
  6. Environmental Concerns
  7. Documentation and Evidence (includes downloaded images)
  8. Risk Assessment
  9. Historical or Cultural Significance

The PDF is saved with the naming format: `[OriginalCSVName]_Report_[Timestamp].pdf`

## Troubleshooting

### Images not downloading
- Check your internet connection
- Ensure the Google Drive links are accessible (not private)
- Verify the links are properly formatted in the CSV

### "No module named 'requests'" error
- Make sure you've installed the requirements: `pip install -r requirements.txt`

### Logos not appearing in PDF
- Ensure `Biladi logo.jpg` and `CER Logo.jpg` are in the same folder as your CSV file
- Check that the file names match exactly (case-sensitive)

### CSV not loading properly
- Ensure your CSV is UTF-8 encoded
- Check that the Date of Assessment column contains valid dates in YYYY/MM/DD format

### Executable not working
- Try rebuilding with console output: Edit `build_exe.py` and keep the `--windowed` line commented
- Check antivirus software isn't blocking the executable
- Ensure you have internet access for downloading images

## For Developers

To modify the report format or add new sections:
1. Edit `report_generator.py`
2. Modify the section dictionaries in the `generate_pdf` method
3. Rebuild the executable using `python build_exe.py`

## Notes

- The program handles Arabic text if present in the CSV
- Empty fields are automatically skipped in the report
- Downloaded images are temporarily cached during report generation
- The report uses A4 page size by default
- Internet connection is required for downloading images from Google Drive
