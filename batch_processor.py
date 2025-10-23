import os
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from transcription_service import transcribe_mp3

# Configure logging
logger = logging.getLogger(__name__)


def process_batch(uploaded_files, output_dir="outputs", api_key=None, language="en", smart_format=True, punctuate=True):
    """
    Process a batch of MP3 files and save transcriptions as txt files.
    
    Args:
        uploaded_files (list): List of uploaded file objects from Streamlit
        output_dir (str): Directory to save output txt files
        api_key (str): Deepgram API key
        language (str): Language code for transcription
        smart_format (bool): Enable smart formatting
        punctuate (bool): Enable punctuation
        
    Returns:
        dict: Dictionary containing:
            - 'success': List of successfully processed files (with paths)
            - 'errors': List of errors with file names
            - 'output_dir': Path to output directory
    """
    # Validate file count
    if len(uploaded_files) == 0:
        error_msg = "No files provided for transcription."
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    logger.info(f"Starting batch processing of {len(uploaded_files)} file(s)")
    
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    results = {
        'success': [],
        'errors': [],
        'output_dir': output_dir
    }
    
    def process_single_file(uploaded_file):
        """
        Process a single file and return the result.
        """
        try:
            # Get file name and create temporary file path
            file_name = uploaded_file.name
            temp_file_path = os.path.join(output_dir, file_name)
            
            # Save uploaded file temporarily
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Transcribe the file
            transcript = transcribe_mp3(temp_file_path, api_key=api_key, language=language, smart_format=smart_format, punctuate=punctuate)
            
            # Generate output txt filename (same name as input but with .txt extension)
            txt_filename = Path(file_name).stem + ".txt"
            txt_file_path = os.path.join(output_dir, txt_filename)
            
            # Save transcription to txt file
            with open(txt_file_path, "w", encoding="utf-8") as f:
                f.write(transcript)
            
            # Clean up temporary mp3 file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            
            return {
                'status': 'success',
                'input_file': file_name,
                'output_file': txt_filename,
                'output_path': txt_file_path
            }
                
        except Exception as e:
            return {
                'status': 'error',
                'file': uploaded_file.name,
                'error': str(e)
            }
    
    # Process files concurrently with ThreadPoolExecutor
    max_workers = min(len(uploaded_files), 10)  # Up to 10 concurrent threads
    logger.info(f"Processing {len(uploaded_files)} files with {max_workers} concurrent workers")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all files for processing
        future_to_file = {executor.submit(process_single_file, file): file for file in uploaded_files}
        
        # Collect results as they complete
        for future in as_completed(future_to_file):
            result = future.result()
            if result['status'] == 'success':
                results['success'].append({
                    'input_file': result['input_file'],
                    'output_file': result['output_file'],
                    'output_path': result['output_path']
                })
                logger.info(f"Successfully processed: {result['input_file']}")
            else:
                results['errors'].append({
                    'file': result['file'],
                    'error': result['error']
                })
                logger.error(f"Failed to process: {result['file']} - {result['error']}")
    
    return results
