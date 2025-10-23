import os
import logging
import zipfile
from datetime import datetime
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)


def create_zip_from_directory(input_dir, output_dir=".", file_filter=".txt"):
    """
    Create a zip file containing all files matching the filter in a directory.
    
    Args:
        input_dir (str): Directory containing files to zip
        output_dir (str): Directory where zip file will be saved
        file_filter (str): File extension to include (e.g., ".txt")
        
    Returns:
        str: Path to the created zip file
        
    Raises:
        ValueError: If input directory doesn't exist or has no matching files
        Exception: If zip creation fails
    """
    try:
        # Validate input directory exists
        if not os.path.isdir(input_dir):
            error_msg = f"Input directory does not exist: {input_dir}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Get all files matching the filter
        files_to_zip = [
            f for f in os.listdir(input_dir)
            if f.endswith(file_filter)
        ]
        
        if not files_to_zip:
            error_msg = f"No {file_filter} files found in {input_dir}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info(f"Found {len(files_to_zip)} file(s) to zip")
        
        # Create output directory if it doesn't exist
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Generate timestamp-based filename
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        zip_filename = f"transcriptions_{timestamp}.zip"
        zip_path = os.path.join(output_dir, zip_filename)
        
        # Create zip file
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file_name in files_to_zip:
                file_path = os.path.join(input_dir, file_name)
                # Add file to zip with just the filename (not full path)
                zipf.write(file_path, arcname=file_name)
        
        logger.info(f"Successfully created zip file: {zip_path}")
        return zip_path
        
    except ValueError as e:
        raise ValueError(f"Zip creation error: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to create zip file: {str(e)}")


def cleanup_directory(directory_path):
    """
    Delete all files in a directory (for cleanup purposes).
    
    Args:
        directory_path (str): Path to directory to clean
        
    Returns:
        bool: True if successful
        
    Raises:
        Exception: If cleanup fails
    """
    try:
        if not os.path.isdir(directory_path):
            raise ValueError(f"Directory does not exist: {directory_path}")
        
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
        
        return True
        
    except Exception as e:
        raise Exception(f"Failed to cleanup directory: {str(e)}")
