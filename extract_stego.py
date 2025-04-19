import cv2
import struct
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
import zigzag as zz
import image_preparation as img
import data_embedding as stego

class SteganographyExtractionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PixelPhantom : Implementasi Steganografi Berbasis DCT dalam Citra JPEG - Extraction")
        self.root.geometry("800x650")
        self.root.configure(bg="#f0f0f0")
        
        self.stego_image_path = None
        
        # Create main frames
        self.create_frames()
        self.create_input_section()
        self.create_image_display()
        self.create_message_display()
        self.create_console()
        
    def create_frames(self):
        # Header frame
        header_frame = tk.Frame(self.root, bg="#4a7abc", height=60)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = tk.Label(header_frame, text="PixelPhantom : Implementasi Steganografi Berbasis DCT dalam Citra JPEG - Extraction", 
                              font=("Arial", 18, "bold"), bg="#4a7abc", fg="white")
        title_label.pack(pady=10)
        
        # Main content frame
        self.main_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
    def create_input_section(self):
        # Input frame
        input_frame = tk.LabelFrame(self.main_frame, text="Input Controls", bg="#f0f0f0", font=("Arial", 12))
        input_frame.pack(fill=tk.X, pady=10)
        
        # Stego image selection
        stego_frame = tk.Frame(input_frame, bg="#f0f0f0")
        stego_frame.pack(fill=tk.X, pady=5)
        
        stego_label = tk.Label(stego_frame, text="Stego Image:", bg="#f0f0f0", width=12, anchor="w")
        stego_label.pack(side=tk.LEFT, padx=5)
        
        self.stego_path_var = tk.StringVar()
        stego_path_entry = tk.Entry(stego_frame, textvariable=self.stego_path_var, width=50)
        stego_path_entry.pack(side=tk.LEFT, padx=5)
        
        stego_browse_btn = tk.Button(stego_frame, text="Browse", command=self.browse_stego_image)
        stego_browse_btn.pack(side=tk.LEFT, padx=5)
        
        # Process button
        process_frame = tk.Frame(input_frame, bg="#f0f0f0")
        process_frame.pack(fill=tk.X, pady=10)
        
        process_btn = tk.Button(process_frame, text="Extract Message", command=self.extract_message,
                              bg="#4a7abc", fg="white", font=("Arial", 10, "bold"), height=2)
        process_btn.pack(pady=5)
        
    def create_image_display(self):
        # Image display frame
        image_frame = tk.LabelFrame(self.main_frame, text="Stego Image Preview", bg="#f0f0f0", font=("Arial", 12))
        image_frame.pack(fill=tk.X, pady=10)
        
        self.image_display_frame = tk.Frame(image_frame, bg="#f0f0f0", height=250)
        self.image_display_frame.pack(expand=True, padx=10, pady=10)
        
        self.image_label = tk.Label(self.image_display_frame, text="Stego Image\n(No image selected)", bg="#f0f0f0")
        self.image_label.pack(fill=tk.BOTH, expand=True)
    
    def create_message_display(self):
        # Message display frame
        message_frame = tk.LabelFrame(self.main_frame, text="Extracted Message", bg="#f0f0f0", font=("Arial", 12))
        message_frame.pack(fill=tk.X, pady=10)
        
        self.message_text = scrolledtext.ScrolledText(message_frame, height=6, bg="white", font=("Consolas", 12))
        self.message_text.pack(fill=tk.X, padx=5, pady=5)
    
    def create_console(self):
        # Console output frame
        console_frame = tk.LabelFrame(self.main_frame, text="Console Output", bg="#f0f0f0", font=("Arial", 12))
        console_frame.pack(fill=tk.X, pady=10)
        
        self.console = scrolledtext.ScrolledText(console_frame, height=8, bg="#000000", fg="#00FF00", font=("Consolas", 10))
        self.console.pack(fill=tk.X, padx=5, pady=5)
        
    def browse_stego_image(self):
        filetypes = [("Image files", "*.png;*.jpg;*.jpeg"), ("All files", "*.*")]
        filename = filedialog.askopenfilename(title="Select Stego Image", filetypes=filetypes)
        if filename:
            self.stego_image_path = filename
            self.stego_path_var.set(filename)
            self.load_stego_image(filename)
            self.log_message(f"Stego image loaded: {filename}")
    
    def load_stego_image(self, image_path):
        try:
            # Load image and resize for display
            image = Image.open(image_path)
            
            # Resize image for display while maintaining aspect ratio
            display_image = image.copy()
            display_image.thumbnail((600, 200))
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(display_image)
            
            # Update label
            self.image_label.config(image=photo, text="")
            self.image_label.image = photo  # Keep a reference!
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")
    
    def log_message(self, message):
        self.console.insert(tk.END, message + "\n")
        self.console.see(tk.END)
    
    def extract_message(self):
        if not self.stego_image_path:
            messagebox.showwarning("Warning", "Please select a stego image first.")
            return
        
        self.log_message("Extracting hidden message...")
        self.message_text.delete(1.0, tk.END)  # Clear previous message
        
        try:
            # Execute the extraction algorithm
            extracted_message = self.execute_extraction(self.stego_image_path)
            
            # Display the extracted message
            self.message_text.insert(tk.END, extracted_message)
            
            self.log_message("Message extraction completed successfully!")
            
        except Exception as e:
            self.log_message(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Message extraction failed: {str(e)}")
    
    def execute_extraction(self, stego_image_path):
        """Execute the steganography extraction algorithm, keeping the original logic intact"""
        
        # Read the stego image
        self.log_message("Reading stego image...")
        stego_image = cv2.imread(stego_image_path, flags=cv2.IMREAD_COLOR)
        stego_image_f32 = np.float32(stego_image)
        stego_image_YCC = img.YCC_Image(cv2.cvtColor(stego_image_f32, cv2.COLOR_BGR2YCrCb))
        
        self.log_message("Applying DCT transform...")
        # FORWARD DCT STAGE
        dct_blocks = [cv2.dct(block) for block in stego_image_YCC.channels[0]]  # Only care about Luminance layer
        
        # QUANTIZATION STAGE
        dct_quants = [np.around(np.divide(item, img.JPEG_STD_LUM_QUANT_TABLE)) for item in dct_blocks]
        
        # Sort DCT coefficients by frequency
        sorted_coefficients = [zz.zigzag(block) for block in dct_quants]
        
        # DATA EXTRACTION STAGE
        self.log_message("Extracting data from DCT coefficients...")
        recovered_data = stego.extract_encoded_data_from_DCT(sorted_coefficients)
        recovered_data.pos = 0
        
        # Determine length of secret message
        data_len = int(recovered_data.read('uint:32') / 8)
        self.log_message(f"Detected message length: {data_len} bytes")
        
        # Extract secret message from DCT coefficients
        extracted_data = bytes()
        for _ in range(data_len): 
            extracted_data += struct.pack('>B', recovered_data.read('uint:8'))
        
        # Convert bytes to ASCII
        try:
            decoded_message = extracted_data.decode('ascii')
            self.log_message(f"Successfully decoded message: {decoded_message}")
            return decoded_message
        except UnicodeDecodeError:
            self.log_message("Warning: Could not decode as ASCII. Showing raw byte values.")
            return str(extracted_data)

if __name__ == "__main__":
    root = tk.Tk()
    app = SteganographyExtractionApp(root)
    root.mainloop()