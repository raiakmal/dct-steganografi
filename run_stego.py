import cv2
import bitstring
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
import zigzag as zz
import image_preparation as img
import data_embedding as stego

class SteganographyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PixelPhantom : Implementasi Steganografi Berbasis DCT dalam Citra JPEG")
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f0f0")
        
        self.cover_image_path = None
        self.stego_image_path = None
        self.original_image = None
        
        # Create main frames
        self.create_frames()
        self.create_input_section()
        self.create_image_display()
        self.create_console()
        
    def create_frames(self):
        # Header frame
        header_frame = tk.Frame(self.root, bg="#4a7abc", height=60)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = tk.Label(header_frame, text="PixelPhantom : Implementasi Steganografi Berbasis DCT dalam Citra JPEG", 
                              font=("Arial", 18, "bold"), bg="#4a7abc", fg="white")
        title_label.pack(pady=10)
        
        # Main content frame
        self.main_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
    def create_input_section(self):
        # Input frame
        input_frame = tk.LabelFrame(self.main_frame, text="Input Controls", bg="#f0f0f0", font=("Arial", 12))
        input_frame.pack(fill=tk.X, pady=10)
        
        # Cover image selection
        cover_frame = tk.Frame(input_frame, bg="#f0f0f0")
        cover_frame.pack(fill=tk.X, pady=5)
        
        cover_label = tk.Label(cover_frame, text="Cover Image:", bg="#f0f0f0", width=12, anchor="w")
        cover_label.pack(side=tk.LEFT, padx=5)
        
        self.cover_path_var = tk.StringVar()
        cover_path_entry = tk.Entry(cover_frame, textvariable=self.cover_path_var, width=50)
        cover_path_entry.pack(side=tk.LEFT, padx=5)
        
        cover_browse_btn = tk.Button(cover_frame, text="Browse", command=self.browse_cover_image)
        cover_browse_btn.pack(side=tk.LEFT, padx=5)
        
        # Secret message input
        message_frame = tk.Frame(input_frame, bg="#f0f0f0")
        message_frame.pack(fill=tk.X, pady=5)
        
        message_label = tk.Label(message_frame, text="Secret Message:", bg="#f0f0f0", width=12, anchor="w")
        message_label.pack(side=tk.LEFT, padx=5)
        
        self.message_var = tk.StringVar()
        message_entry = tk.Entry(message_frame, textvariable=self.message_var, width=50)
        message_entry.pack(side=tk.LEFT, padx=5)
        
        # Output path
        output_frame = tk.Frame(input_frame, bg="#f0f0f0")
        output_frame.pack(fill=tk.X, pady=5)
        
        output_label = tk.Label(output_frame, text="Output Path:", bg="#f0f0f0", width=12, anchor="w")
        output_label.pack(side=tk.LEFT, padx=5)
        
        self.output_path_var = tk.StringVar(value="./stego_image.png")
        output_path_entry = tk.Entry(output_frame, textvariable=self.output_path_var, width=50)
        output_path_entry.pack(side=tk.LEFT, padx=5)
        
        output_browse_btn = tk.Button(output_frame, text="Browse", command=self.browse_output_path)
        output_browse_btn.pack(side=tk.LEFT, padx=5)
        
        # Process button
        process_frame = tk.Frame(input_frame, bg="#f0f0f0")
        process_frame.pack(fill=tk.X, pady=10)
        
        process_btn = tk.Button(process_frame, text="Encode Message", command=self.process_image,
                              bg="#4a7abc", fg="white", font=("Arial", 10, "bold"), height=2)
        process_btn.pack(pady=5)
        
    def create_image_display(self):
        # Image display frame
        image_frame = tk.LabelFrame(self.main_frame, text="Image Preview", bg="#f0f0f0", font=("Arial", 12))
        image_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Original image
        self.original_frame = tk.Frame(image_frame, bg="#f0f0f0", width=400, height=300)
        self.original_frame.pack(side=tk.LEFT, expand=True, padx=10, pady=10)
        self.original_frame.pack_propagate(0)
        
        self.original_label = tk.Label(self.original_frame, text="Cover Image\n(No image selected)", bg="#f0f0f0")
        self.original_label.pack(fill=tk.BOTH, expand=True)
        
        # Result image
        self.result_frame = tk.Frame(image_frame, bg="#f0f0f0", width=400, height=300)
        self.result_frame.pack(side=tk.RIGHT, expand=True, padx=10, pady=10)
        self.result_frame.pack_propagate(0)
        
        self.result_label = tk.Label(self.result_frame, text="Stego Image\n(Not yet processed)", bg="#f0f0f0")
        self.result_label.pack(fill=tk.BOTH, expand=True)
    
    def create_console(self):
        # Console output frame
        console_frame = tk.LabelFrame(self.main_frame, text="Console Output", bg="#f0f0f0", font=("Arial", 12))
        console_frame.pack(fill=tk.X, pady=10)
        
        self.console = scrolledtext.ScrolledText(console_frame, height=8, bg="#000000", fg="#00FF00", font=("Consolas", 10))
        self.console.pack(fill=tk.X, padx=5, pady=5)
        
    def browse_cover_image(self):
        filetypes = [("Image files", "*.png;*.jpg;*.jpeg"), ("All files", "*.*")]
        filename = filedialog.askopenfilename(title="Select Cover Image", filetypes=filetypes)
        if filename:
            self.cover_image_path = filename
            self.cover_path_var.set(filename)
            self.load_cover_image(filename)
            self.log_message(f"Cover image loaded: {filename}")
            
    def browse_output_path(self):
        filetypes = [("PNG files", "*.png"), ("All files", "*.*")]
        filename = filedialog.asksaveasfilename(title="Save Stego Image As", filetypes=filetypes, defaultextension=".png")
        if filename:
            self.stego_image_path = filename
            self.output_path_var.set(filename)
            self.log_message(f"Output path set: {filename}")
    
    def load_cover_image(self, image_path):
        try:
            # Load image and resize for display
            image = Image.open(image_path)
            self.original_image = image
            
            # Resize image for display if needed
            display_image = image.copy()
            display_image.thumbnail((380, 280))
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(display_image)
            
            # Update label
            self.original_label.config(image=photo, text="")
            self.original_label.image = photo  # Keep a reference!
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")
    
    def load_stego_image(self, image_path):
        try:
            # Load image and resize for display
            image = Image.open(image_path)
            
            # Resize image for display if needed
            display_image = image.copy()
            display_image.thumbnail((380, 280))
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(display_image)
            
            # Update label
            self.result_label.config(image=photo, text="")
            self.result_label.image = photo  # Keep a reference!
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load stego image: {str(e)}")
    
    def log_message(self, message):
        self.console.insert(tk.END, message + "\n")
        self.console.see(tk.END)
    
    def process_image(self):
        if not self.cover_image_path:
            messagebox.showwarning("Warning", "Please select a cover image first.")
            return
        
        secret_message = self.message_var.get()
        if not secret_message:
            messagebox.showwarning("Warning", "Please enter a secret message.")
            return
        
        output_path = self.output_path_var.get()
        if not output_path:
            messagebox.showwarning("Warning", "Please specify an output path.")
            return
        
        self.log_message("Processing image...")
        self.log_message(f"Message to hide: {secret_message}")
        
        try:
            # Here we call the steganography algorithm
            self.execute_steganography(self.cover_image_path, output_path, secret_message)
            
            # Load and display the stego image
            self.load_stego_image(output_path)
            
            self.log_message("Steganography completed successfully!")
            messagebox.showinfo("Success", "Message hidden successfully!")
            
        except Exception as e:
            self.log_message(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Steganography failed: {str(e)}")
    
    def execute_steganography(self, cover_image_path, stego_image_path, secret_message):
        """Execute the steganography algorithm, keeping the original logic intact"""
        NUM_CHANNELS = 3
        
        # Read the cover image
        raw_cover_image = cv2.imread(cover_image_path, flags=cv2.IMREAD_COLOR)
        height, width = raw_cover_image.shape[:2]
        
        # Force Image Dimensions to be 8x8 compliant
        while(height % 8): height += 1  # Rows
        while(width % 8): width += 1  # Cols
        valid_dim = (width, height)
        
        self.log_message(f"Original dimensions: {raw_cover_image.shape[:2]}")
        self.log_message(f"Adjusted dimensions: {valid_dim}")
        
        padded_image = cv2.resize(raw_cover_image, valid_dim)
        cover_image_f32 = np.float32(padded_image)
        cover_image_YCC = img.YCC_Image(cv2.cvtColor(cover_image_f32, cv2.COLOR_BGR2YCrCb))
        
        # Placeholder for holding stego image data
        stego_image = np.empty_like(cover_image_f32)
        
        self.log_message("Applying DCT transform...")
        
        for chan_index in range(NUM_CHANNELS):
            # FORWARD DCT STAGE
            dct_blocks = [cv2.dct(block) for block in cover_image_YCC.channels[chan_index]]
            
            # QUANTIZATION STAGE
            dct_quants = [np.around(np.divide(item, img.JPEG_STD_LUM_QUANT_TABLE)) for item in dct_blocks]
            
            # Sort DCT coefficients by frequency
            sorted_coefficients = [zz.zigzag(block) for block in dct_quants]
            
            # Embed data in Luminance layer
            if (chan_index == 0):
                # DATA INSERTION STAGE
                secret_data = ""
                for char in secret_message.encode('ascii'): 
                    secret_data += bitstring.pack('uint:8', char)
                
                self.log_message(f"Embedding data in channel {chan_index}...")
                embedded_dct_blocks = stego.embed_encoded_data_into_DCT(secret_data, sorted_coefficients)
                desorted_coefficients = [zz.inverse_zigzag(block, vmax=8, hmax=8) for block in embedded_dct_blocks]
            else:
                # Reorder coefficients to how they originally were
                desorted_coefficients = [zz.inverse_zigzag(block, vmax=8, hmax=8) for block in sorted_coefficients]
            
            # DEQUANTIZATION STAGE
            dct_dequants = [np.multiply(data, img.JPEG_STD_LUM_QUANT_TABLE) for data in desorted_coefficients]
            
            # Inverse DCT Stage
            idct_blocks = [cv2.idct(block) for block in dct_dequants]
            
            # Rebuild full image channel
            stego_image[:,:,chan_index] = np.asarray(img.stitch_8x8_blocks_back_together(cover_image_YCC.width, idct_blocks))
        
        self.log_message("Converting color space back to BGR...")
        # Convert back to RGB (BGR) Colorspace
        stego_image_BGR = cv2.cvtColor(stego_image, cv2.COLOR_YCR_CB2BGR)
        
        # Clamp Pixel Values to [0 - 255]
        final_stego_image = np.uint8(np.clip(stego_image_BGR, 0, 255))
        
        # Write stego image
        cv2.imwrite(stego_image_path, final_stego_image)
        self.log_message(f"Stego image saved to: {stego_image_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SteganographyApp(root)
    root.mainloop()