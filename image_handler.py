"""
Image handling module for Heritage Report Generator
"""

import os
import re
import requests
import tempfile
import shutil
import logging
from typing import Optional, List, Dict, Tuple
from PIL import Image as PILImage

from exceptions import ImageDownloadError
from constants import DOWNLOAD_TIMEOUT, CHUNK_SIZE, MAX_RETRIES
from utils import extract_drive_file_id, parse_image_links, create_temp_filename

logger = logging.getLogger(__name__)


class ImageHandler:
    """Handles image downloading and processing"""
    
    def __init__(self):
        """Initialize image handler"""
        self.temp_dir = tempfile.mkdtemp()
        self.downloaded_images = {}
        self.session = requests.Session()
        logger.info(f"Created temporary directory: {self.temp_dir}")
        
    def __del__(self):
        """Clean up temporary directory"""
        self.cleanup()
        
    def cleanup(self):
        """Clean up temporary files and directory"""
        try:
            if hasattr(self, 'session'):
                self.session.close()
            
            if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                logger.info(f"Cleaned up temporary directory: {self.temp_dir}")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def download_drive_image(self, url: str, filename_prefix: str = "image") -> Optional[str]:
        """
        Download image from Google Drive
        
        Args:
            url: Google Drive URL
            filename_prefix: Prefix for saved file
            
        Returns:
            Optional[str]: Path to downloaded image or None
        """
        file_id = extract_drive_file_id(url)
        if not file_id:
            logger.warning(f"Could not extract file ID from URL: {url}")
            return None
        
        # Check if already downloaded
        if file_id in self.downloaded_images:
            logger.debug(f"Image already downloaded: {file_id}")
            return self.downloaded_images[file_id]
        
        # Try downloading with retries
        for attempt in range(MAX_RETRIES):
            try:
                logger.info(f"Downloading image: {filename_prefix} (attempt {attempt + 1}/{MAX_RETRIES})")
                
                # Google Drive direct download URL
                download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
                
                response = self.session.get(download_url, stream=True, timeout=DOWNLOAD_TIMEOUT)
                
                # Check for virus scan warning
                if b'confirm=' in response.content[:1000]:
                    confirm_token = self._extract_confirm_token(response.text)
                    if confirm_token:
                        download_url = f"https://drive.google.com/uc?export=download&id={file_id}&confirm={confirm_token}"
                        response = self.session.get(download_url, stream=True, timeout=DOWNLOAD_TIMEOUT)
                
                if response.status_code == 200:
                    # Determine file extension
                    ext = self._get_file_extension(response.headers.get('content-type', ''))
                    
                    # Save to temp directory
                    temp_path = create_temp_filename(filename_prefix, ext.lstrip('.'), self.temp_dir)
                    
                    with open(temp_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                            if chunk:
                                f.write(chunk)
                    
                    # Validate image
                    if self._validate_image(temp_path):
                        self.downloaded_images[file_id] = temp_path
                        logger.info(f"Successfully downloaded: {filename_prefix}")
                        return temp_path
                    else:
                        os.remove(temp_path)
                        logger.warning(f"Downloaded file is not a valid image: {filename_prefix}")
                        return None
                else:
                    logger.warning(f"Failed to download (status {response.status_code}): {url}")
                    
            except requests.exceptions.Timeout:
                logger.warning(f"Download timeout for {filename_prefix} (attempt {attempt + 1})")
            except Exception as e:
                logger.error(f"Error downloading {filename_prefix}: {e}")
        
        return None
    
    def process_image_links(self, links_str: str, prefix: str = "image") -> List[str]:
        """
        Process multiple image links
        
        Args:
            links_str: String containing image links
            prefix: Prefix for downloaded files
            
        Returns:
            List[str]: Paths to downloaded images
        """
        if not links_str:
            return []
        
        links = parse_image_links(links_str)
        images = []
        
        for i, link in enumerate(links):
            if link:
                img_path = self.download_drive_image(link, f"{prefix}_{i+1}")
                if img_path:
                    images.append(img_path)
        
        logger.info(f"Processed {len(images)}/{len(links)} images for {prefix}")
        return images
    
    def resize_image(self, image_path: str, max_width: int, max_height: int) -> Tuple[int, int]:
        """
        Calculate resized dimensions maintaining aspect ratio
        
        Args:
            image_path: Path to image
            max_width: Maximum width in pixels
            max_height: Maximum height in pixels
            
        Returns:
            Tuple[int, int]: New width and height
        """
        try:
            with PILImage.open(image_path) as img:
                width, height = img.size
                aspect_ratio = height / width
                
                # Calculate new dimensions
                if width > max_width:
                    width = max_width
                    height = int(width * aspect_ratio)
                
                if height > max_height:
                    height = max_height
                    width = int(height / aspect_ratio)
                
                return width, height
                
        except Exception as e:
            logger.error(f"Error calculating image dimensions: {e}")
            return max_width, max_height
    
    def get_download_stats(self) -> Dict[str, int]:
        """
        Get download statistics
        
        Returns:
            Dict[str, int]: Download statistics
        """
        stats = {
            'total_downloaded': len(self.downloaded_images),
            'total_size_mb': 0
        }
        
        for path in self.downloaded_images.values():
            if os.path.exists(path):
                stats['total_size_mb'] += os.path.getsize(path) / (1024 * 1024)
        
        stats['total_size_mb'] = round(stats['total_size_mb'], 2)
        return stats
    
    def _extract_confirm_token(self, html: str) -> Optional[str]:
        """Extract confirmation token from Google Drive warning page"""
        match = re.search(r'confirm=([a-zA-Z0-9-_]+)', html)
        return match.group(1) if match else None
    
    def _get_file_extension(self, content_type: str) -> str:
        """Determine file extension from content type"""
        extensions = {
            'image/jpeg': '.jpg',
            'image/jpg': '.jpg',
            'image/png': '.png',
            'image/gif': '.gif',
            'image/webp': '.webp'
        }
        
        for mime, ext in extensions.items():
            if mime in content_type.lower():
                return ext
        
        return '.jpg'  # default
    
    def _validate_image(self, image_path: str) -> bool:
        """Validate if file is a valid image"""
        try:
            with PILImage.open(image_path) as img:
                img.verify()
            return True
        except Exception:
            return False
    
    def copy_to_output_dir(self, output_dir: str, prefix: str = "report_images") -> Dict[str, str]:
        """
        Copy downloaded images to output directory
        
        Args:
            output_dir: Output directory path
            prefix: Prefix for copied files
            
        Returns:
            Dict[str, str]: Mapping of original to copied paths
        """
        copied_files = {}
        
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            for i, (file_id, temp_path) in enumerate(self.downloaded_images.items()):
                if os.path.exists(temp_path):
                    ext = os.path.splitext(temp_path)[1]
                    new_filename = f"{prefix}_{i+1}_{file_id[:8]}{ext}"
                    new_path = os.path.join(output_dir, new_filename)
                    
                    shutil.copy2(temp_path, new_path)
                    copied_files[temp_path] = new_path
                    
            logger.info(f"Copied {len(copied_files)} images to {output_dir}")
            
        except Exception as e:
            logger.error(f"Error copying images: {e}")
        
        return copied_files
