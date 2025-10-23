import os
import logging
from deepgram import DeepgramClient, PrerecordedOptions
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()


def get_api_key():
    """
    Retrieve Deepgram API key from environment variables.
    
    Returns:
        str: The Deepgram API key
        
    Raises:
        ValueError: If API key is not found in environment
    """
    api_key = os.getenv("DEEPGRAM_API_KEY")
    if not api_key:
        raise ValueError("DEEPGRAM_API_KEY not found in environment variables. Please set it in .env file.")
    return api_key


MAX_FILE_SIZE_MB = 2000  # Max file size for long MP3 files


def validate_mp3_file(file_path):
    """
    Validate that file is a valid MP3 with acceptable size.
    
    Args:
        file_path (str): Path to file to validate
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file is not valid MP3 or too large
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Check file extension
    if not file_path.lower().endswith('.mp3'):
        raise ValueError(f"Invalid file format. Only MP3 files are supported.")
    
    # Check file size
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        raise ValueError(f"File is too large ({file_size_mb:.2f}MB). Max size is {MAX_FILE_SIZE_MB}MB.")
    
    if file_size_mb < 0.1:
        raise ValueError(f"File is too small ({file_size_mb:.2f}MB). Minimum size is 0.1MB.")


def transcribe_mp3(file_path, api_key=None, language="en", smart_format=True, punctuate=True):
    """
    Transcribe a single MP3 file using Deepgram Nova-3 API.
    
    Args:
        file_path (str): Path to the MP3 file to transcribe
        api_key (str): Deepgram API key (optional, falls back to env)
        language (str): Language code for transcription
        smart_format (bool): Enable smart formatting
        punctuate (bool): Enable punctuation
        
    Returns:
        str: The transcribed text
        
    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If API key is missing or file is invalid
        Exception: If Deepgram API call fails
    """
    try:
        # Validate file
        validate_mp3_file(file_path)
        logger.info(f"Validating and transcribing: {file_path}")
        
        # Get API key (use provided or fallback to env)
        if not api_key:
            api_key = get_api_key()
        
        # Initialize Deepgram client
        deepgram = DeepgramClient(api_key)
        
        # Configure transcription options
        options = PrerecordedOptions(
            model="nova-3",
            language=language,
            smart_format=smart_format,
            punctuate=punctuate,
        )
        
        # Read file and transcribe
        with open(file_path, "rb") as audio_file:
            payload = {"buffer": audio_file}
            
            response = deepgram.listen.rest.v("1").transcribe_file(
                payload,
                options,
            )
        
        # Extract transcript from response
        if response.results and response.results.channels:
            transcript = response.results.channels[0].alternatives[0].transcript
            logger.info(f"Successfully transcribed: {os.path.basename(file_path)}")
            return transcript
        else:
            error_msg = "No transcription results returned from API"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
    except FileNotFoundError as e:
        logger.error(f"File error: {str(e)}")
        raise FileNotFoundError(f"File error: {str(e)}")
    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        raise ValueError(f"Configuration error: {str(e)}")
    except Exception as e:
        error_msg = f"Transcription failed for {file_path}: {str(e)}"
        logger.error(error_msg)
        if "401" in str(e) or "Unauthorized" in str(e):
            raise Exception("API authentication failed. Check your API key.")
        elif "429" in str(e) or "rate" in str(e).lower():
            raise Exception("Rate limit exceeded. Please try again later.")
        elif "timeout" in str(e).lower():
            raise Exception("Request timeout. File may be too large or API is busy.")
        else:
            raise Exception(error_msg)
