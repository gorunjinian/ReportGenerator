@echo off
:: Heritage Site Assessment Report Generator
:: Drag and drop a CSV file onto this batch file to generate a PDF report

if "%~1"=="" (
    echo No file provided. Please drag and drop a CSV file onto this batch file.
    pause
    exit /b 1
)

:: Check if the executable exists
if not exist "%~dp0report_generator.exe" (
    echo Error: report_generator.exe not found in the current directory.
    echo Please ensure the executable is in the same folder as this batch file.
    pause
    exit /b 1
)

:: Run the report generator with the dropped file
"%~dp0report_generator.exe" %1

:: Keep window open to see results
pause
