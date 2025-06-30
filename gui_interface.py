"""
Simple GUI interface for Heritage Report Generator
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
import threading
from datetime import datetime
import logging

from report_generator import ReportGenerator
from utils import validate_csv_path, generate_output_filename
from exceptions import ReportGeneratorError

class HeritageReportGUI:
    """Simple GUI for Heritage Report Generator"""
    
    def __init__(self):
        """Initialize the GUI"""
        self.root = tk.Tk()
        self.root.title("Heritage Site Assessment Report Generator")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        # Center the window
        self.center_window()
        
        # Variables
        self.selected_csv = tk.StringVar()
        self.csv_files = []
        self.current_generator = None
        
        # Create GUI elements
        self.create_widgets()
        self.refresh_csv_list()
        
        # Configure logging to display in GUI
        self.setup_gui_logging()
        
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_widgets(self):
        """Create all GUI widgets"""
        
        # Configure styles
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="Site Assessment Report Generator",
            font=('Arial', 16, 'bold')
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Subtitle
        subtitle_label = ttk.Label(
            main_frame,
            text="Generate PDF reports from Google Forms CSV data",
            font=('Arial', 10)
        )
        subtitle_label.grid(row=1, column=0, columnspan=3, pady=(0, 20))
        
        # CSV File Selection Section
        csv_frame = ttk.LabelFrame(main_frame, text="Select CSV File", padding="10")
        csv_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        csv_frame.columnconfigure(1, weight=1)
        
        # Available CSV files
        ttk.Label(csv_frame, text="Available CSV files:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # CSV listbox with scrollbar
        listbox_frame = ttk.Frame(csv_frame)
        listbox_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        listbox_frame.columnconfigure(0, weight=1)
        
        self.csv_listbox = tk.Listbox(listbox_frame, height=6, selectmode=tk.SINGLE)
        self.csv_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.csv_listbox.bind('<<ListboxSelect>>', self.on_csv_select)
        
        # Scrollbar for listbox
        scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.csv_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.csv_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Buttons row
        button_frame = ttk.Frame(csv_frame)
        button_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Refresh button
        self.refresh_btn = ttk.Button(
            button_frame, 
            text="🔄 Refresh List", 
            command=self.refresh_csv_list
        )
        self.refresh_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Browse button
        self.browse_btn = ttk.Button(
            button_frame, 
            text="📁 Browse for CSV...", 
            command=self.browse_csv_file
        )
        self.browse_btn.pack(side=tk.LEFT)
        
        # Selected file display
        selected_frame = ttk.Frame(csv_frame)
        selected_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        selected_frame.columnconfigure(1, weight=1)
        
        ttk.Label(selected_frame, text="Selected:").grid(row=0, column=0, sticky=tk.W)
        self.selected_label = ttk.Label(
            selected_frame, 
            textvariable=self.selected_csv,
            foreground="blue",
            font=('Arial', 9, 'bold')
        )
        self.selected_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # Generation Section
        gen_frame = ttk.LabelFrame(main_frame, text="Generate Report", padding="10")
        gen_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        gen_frame.columnconfigure(0, weight=1)
        
        # Generate button
        self.generate_btn = ttk.Button(
            gen_frame,
            text="🚀 Generate PDF Report",
            command=self.generate_report,
            state=tk.DISABLED
        )
        self.generate_btn.grid(row=0, column=0, pady=(0, 10))
        
        # Progress bar
        self.progress = ttk.Progressbar(gen_frame, mode='indeterminate')
        self.progress.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Status label
        self.status_var = tk.StringVar(value="Ready - Select a CSV file to begin")
        self.status_label = ttk.Label(gen_frame, textvariable=self.status_var)
        self.status_label.grid(row=2, column=0)
        
        # Log Section
        log_frame = ttk.LabelFrame(main_frame, text="Progress Log", padding="10")
        log_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(
            log_frame, 
            height=8, 
            wrap=tk.WORD,
            font=('Consolas', 9)
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Footer
        footer_frame = ttk.Frame(main_frame)
        footer_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
        ttk.Label(
            footer_frame, 
            text="Make sure logo files (Biladi logo.jpg, CER Logo.jpg) are in the same folder as your CSV",
            font=('Arial', 8),
            foreground="gray"
        ).pack()
    
    def refresh_csv_list(self):
        """Refresh the list of CSV files in current directory"""
        try:
            current_dir = os.getcwd()
            self.csv_files = [f for f in os.listdir(current_dir) if f.lower().endswith('.csv')]
            
            # Clear and populate listbox
            self.csv_listbox.delete(0, tk.END)
            
            if self.csv_files:
                for csv_file in self.csv_files:
                    self.csv_listbox.insert(tk.END, csv_file)
                self.log(f"Found {len(self.csv_files)} CSV files in current directory")
            else:
                self.csv_listbox.insert(tk.END, "(No CSV files found)")
                self.log("No CSV files found in current directory")
                
        except Exception as e:
            self.log(f"Error refreshing CSV list: {e}")
    
    def on_csv_select(self, event):
        """Handle CSV file selection from listbox"""
        selection = self.csv_listbox.curselection()
        if selection and self.csv_files:
            selected_file = self.csv_files[selection[0]]
            full_path = os.path.abspath(selected_file)
            self.selected_csv.set(selected_file)
            self.generate_btn.config(state=tk.NORMAL)
            self.status_var.set(f"Ready to generate report for: {selected_file}")
            self.log(f"Selected: {selected_file}")
    
    def browse_csv_file(self):
        """Open file dialog to browse for CSV file"""
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            filename = os.path.basename(file_path)
            self.selected_csv.set(f"{filename} (from: {os.path.dirname(file_path)})")
            self.selected_file_path = file_path
            self.generate_btn.config(state=tk.NORMAL)
            self.status_var.set(f"Ready to generate report for: {filename}")
            self.log(f"Selected file: {file_path}")
    
    def generate_report(self):
        """Generate the PDF report in a separate thread"""
        # Get selected file path
        csv_file = None
        
        if hasattr(self, 'selected_file_path'):
            # File was selected via browse
            csv_file = self.selected_file_path
        else:
            # File was selected from list
            selected_name = self.selected_csv.get()
            if selected_name and selected_name in self.csv_files:
                csv_file = os.path.abspath(selected_name)
        
        if not csv_file or not validate_csv_path(csv_file):
            messagebox.showerror("Error", "Please select a valid CSV file")
            return
        
        # Disable button and start progress
        self.generate_btn.config(state=tk.DISABLED)
        self.progress.start()
        self.status_var.set("Generating report...")
        self.log("="*50)
        self.log("Starting report generation...")
        
        # Run generation in separate thread
        thread = threading.Thread(
            target=self.generate_report_thread, 
            args=(csv_file,)
        )
        thread.daemon = True
        thread.start()
    
    def generate_report_thread(self, csv_file):
        """Generate report in background thread"""
        try:
            # Generate output filename
            output_file = generate_output_filename(csv_file)
            
            self.log(f"Input file: {os.path.basename(csv_file)}")
            self.log(f"Output file: {os.path.basename(output_file)}")
            
            # Create generator
            self.current_generator = ReportGenerator(csv_file)
            
            # Update status
            self.root.after(0, lambda: self.status_var.set("Loading data..."))
            
            # Generate report
            stats = self.current_generator.generate_report(output_file)
            
            # Success
            success_msg = f"""
Report generated successfully!

Monument: {stats['monument_name']}
Assessment Date: {stats['assessment_date']}
Images Downloaded: {stats['total_images']}
Output File: {os.path.basename(output_file)}
File Size: {os.path.getsize(output_file) / (1024*1024):.2f} MB

The PDF has been saved in the same directory as your CSV file.
            """.strip()
            
            self.log("✅ REPORT GENERATED SUCCESSFULLY!")
            self.log(f"Monument: {stats['monument_name']}")
            self.log(f"Assessment Date: {stats['assessment_date']}")
            self.log(f"Images: {stats['total_images']}")
            self.log(f"Output: {output_file}")
            
            # Show success dialog
            self.root.after(0, lambda: messagebox.showinfo("Success", success_msg))
            self.root.after(0, lambda: self.status_var.set("Report generated successfully!"))
            
        except ReportGeneratorError as e:
            error_msg = f"Report generation failed:\n\n{str(e)}\n\nPlease check:\n• Internet connection\n• CSV file format\n• Google Drive link permissions"
            self.log(f"❌ ERROR: {e}")
            self.root.after(0, lambda: messagebox.showerror("Generation Error", error_msg))
            self.root.after(0, lambda: self.status_var.set("Generation failed - see log"))
            
        except Exception as e:
            error_msg = f"Unexpected error:\n\n{str(e)}"
            self.log(f"❌ UNEXPECTED ERROR: {e}")
            self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
            self.root.after(0, lambda: self.status_var.set("Error occurred - see log"))
            
        finally:
            # Cleanup and re-enable button
            if self.current_generator:
                self.current_generator.cleanup()
            
            self.root.after(0, lambda: self.progress.stop())
            self.root.after(0, lambda: self.generate_btn.config(state=tk.NORMAL))
    
    def log(self, message):
        """Add message to log display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        def update_log():
            self.log_text.insert(tk.END, log_entry)
            self.log_text.see(tk.END)
        
        if threading.current_thread() == threading.main_thread():
            update_log()
        else:
            self.root.after(0, update_log)
    
    def setup_gui_logging(self):
        """Setup logging to display in GUI"""
        class GUILogHandler(logging.Handler):
            def __init__(self, gui):
                super().__init__()
                self.gui = gui
            
            def emit(self, record):
                msg = self.format(record)
                self.gui.log(msg)
        
        # Add GUI handler to root logger
        gui_handler = GUILogHandler(self)
        gui_handler.setLevel(logging.INFO)
        gui_handler.setFormatter(logging.Formatter('%(name)s - %(levelname)s - %(message)s'))
        
        logging.getLogger().addHandler(gui_handler)
    
    def run(self):
        """Start the GUI application"""
        self.log("Heritage Report Generator started")
        self.log("Select a CSV file to begin generating reports")
        self.root.mainloop()

def run_gui():
    """Run the GUI application"""
    try:
        app = HeritageReportGUI()
        app.run()
    except Exception as e:
        # Fallback error handling
        import traceback
        error_msg = f"GUI Error: {e}\n\n{traceback.format_exc()}"
        
        try:
            import tkinter.messagebox as mb
            mb.showerror("GUI Error", error_msg)
        except:
            print(error_msg)

if __name__ == "__main__":
    run_gui()
