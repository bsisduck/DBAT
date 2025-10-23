# TranscribeX 🎙️

Fast batch audio transcription powered by Deepgram Nova-3. Upload multiple MP3 files and get accurate transcriptions with concurrent processing.

## Features

- ✅ **Batch Processing** - Upload unlimited files, processed in batches of 10
- ✅ **Concurrent Transcription** - 10 files transcribed simultaneously for 10x speed
- ✅ **Multi-Language Support** - English, Polish, Spanish, French, German, Italian, Portuguese, Dutch, Russian, Chinese, Japanese, Korean
- ✅ **Customizable Options** - Toggle smart formatting and punctuation
- ✅ **Download as ZIP** - Get all transcriptions in one convenient file
- ✅ **Simple Web UI** - Clean Streamlit interface, no coding required

## Quick Start

### Prerequisites

- Python 3.8 or higher
- Deepgram API key ([Get one free](https://console.deepgram.com))

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/TranscribeX.git
cd TranscribeX
```

2. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Usage

1. Start the application:
```bash
streamlit run app.py
```

2. Open your browser at `http://localhost:8501`

3. Enter your Deepgram API key in the sidebar

4. Select your language and options

5. Upload MP3 files and click "Transcribe All"

6. Download the ZIP file with all transcriptions

## Configuration

### Transcription Options

- **Smart Format**: Improves readability with proper formatting
- **Punctuation**: Adds punctuation marks to transcriptions
- **Language**: Select the language of your audio files

### API Key

You can provide your API key in two ways:
1. Enter it in the sidebar UI (recommended)
2. Set `DEEPGRAM_API_KEY` in `.env` file

## How It Works

1. Files are split into batches of 10
2. Each batch processes 10 files concurrently using threading
3. Deepgram Nova-3 API transcribes the audio
4. Transcriptions are saved as `.txt` files
5. All files are packaged into a timestamped ZIP

## Performance

- **Sequential**: 28 files × 1 min = ~28 minutes
- **Concurrent (10 at once)**: 3 batches × 1 min = **~3 minutes**

Processing time depends on audio length and API response time.

## Requirements

```
streamlit==1.28.1
deepgram-sdk==3.5.0
python-dotenv==1.0.0
```

## Project Structure

```
TranscribeX/
├── app.py                    # Main Streamlit application
├── transcription_service.py  # Deepgram API wrapper
├── batch_processor.py        # Concurrent batch processing
├── zip_utils.py             # ZIP file creation
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
├── LICENSE                 # MIT License
└── README.md               # This file
```

## Supported Languages

English, Polish, Spanish, French, German, Italian, Portuguese, Dutch, Russian, Chinese, Japanese, Korean

More languages available - check [Deepgram docs](https://developers.deepgram.com/docs/languages-overview)

## Troubleshooting

**API key not working?**
- Verify key is valid at https://console.deepgram.com
- Check for typos when entering the key

**Files not uploading?**
- Only MP3 files are supported
- Max file size: 2000 MB per file
- Ensure stable internet connection

**Slow processing?**
- Processing time depends on audio length
- Check your Deepgram plan limits
- Longer files take proportionally longer

## License

MIT License - see [LICENSE](LICENSE) file for details

## Credits

- Built with [Streamlit](https://streamlit.io/)
- Powered by [Deepgram Nova-3](https://deepgram.com/)
- Concurrent processing with Python ThreadPoolExecutor

## Contributing

Contributions welcome! Please open an issue or submit a pull request.

## Support

- [Deepgram API Docs](https://developers.deepgram.com/docs)
- [Streamlit Docs](https://docs.streamlit.io/)
- For bugs, open an issue on GitHub
