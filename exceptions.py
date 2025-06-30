"""
Custom exceptions for Heritage Report Generator
"""

class ReportGeneratorError(Exception):
    """Base exception for report generator"""
    pass

class CSVLoadError(ReportGeneratorError):
    """Raised when CSV file cannot be loaded"""
    pass

class DataValidationError(ReportGeneratorError):
    """Raised when data validation fails"""
    pass

class ImageDownloadError(ReportGeneratorError):
    """Raised when image download fails"""
    pass

class PDFGenerationError(ReportGeneratorError):
    """Raised when PDF generation fails"""
    pass

class ConfigurationError(ReportGeneratorError):
    """Raised when configuration is invalid"""
    pass
