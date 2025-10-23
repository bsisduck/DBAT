import streamlit as st
import os
from batch_processor import process_batch
from zip_utils import create_zip_from_directory, cleanup_directory


# Page configuration
st.set_page_config(
    page_title="Batch MP3 Transcription",
    page_icon="🎙️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("🎙️ Batch MP3 Transcription")
st.markdown("Upload your MP3 files. Files will be processed in batches of 10.")

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Settings")
    
    # API Key input
    st.subheader("🔑 API Configuration")
    api_key_input = st.text_input(
        "Deepgram API Key",
        type="password",
        help="Enter your Deepgram API key. Get one at https://console.deepgram.com"
    )
    if api_key_input:
        st.session_state.api_key = api_key_input
        st.success("✅ API key configured")
    elif 'api_key' not in st.session_state or not st.session_state.get('api_key'):
        st.warning("⚠️ Please enter your API key to continue")
    
    st.divider()
    
    # Language selection
    st.subheader("Language")
    languages = {
        "English": "en",
        "Polish": "pl",
        "Spanish": "es",
        "French": "fr",
        "German": "de",
        "Italian": "it",
        "Portuguese": "pt",
        "Dutch": "nl",
        "Russian": "ru",
        "Chinese": "zh",
        "Japanese": "ja",
        "Korean": "ko"
    }
    selected_language = st.selectbox(
        "Audio Language",
        options=list(languages.keys()),
        index=0,
        help="Select the language of your audio files"
    )
    language_code = languages[selected_language]
    
    st.divider()
    
    # Transcription parameters
    st.subheader("Transcription Options")
    smart_format = st.checkbox("Smart Format", value=True, help="Enable smart formatting for better readability")
    punctuate = st.checkbox("Punctuation", value=True, help="Add punctuation to transcription")
    
    st.divider()

# Initialize session state for managing app state
if 'smart_format' not in st.session_state:
    st.session_state.smart_format = True
if 'punctuate' not in st.session_state:
    st.session_state.punctuate = True
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'zip_path' not in st.session_state:
    st.session_state.zip_path = None
if 'results' not in st.session_state:
    st.session_state.results = None
if 'all_results' not in st.session_state:
    st.session_state.all_results = {'success': [], 'errors': []}

# File uploader
uploaded_files = st.file_uploader(
    "Choose MP3 files",
    type=["mp3"],
    accept_multiple_files=True,
    help="Upload any number of MP3 files - they will be processed in batches of 10"
)

# Display file count info
if uploaded_files:
    file_count = len(uploaded_files)
    num_batches = (file_count + 9) // 10  # Calculate number of batches needed
    st.info(f"✅ {file_count} file(s) ready to transcribe in {num_batches} batch(es) of up to 10 files each")

# Transcribe button
col1, col2 = st.columns([1, 1])
with col1:
    has_api_key = st.session_state.get('api_key')
    transcribe_button = st.button(
        "🚀 Transcribe All",
        disabled=not uploaded_files or not has_api_key,
        use_container_width=True
    )

with col2:
    if st.session_state.zip_path and os.path.exists(st.session_state.zip_path):
        with open(st.session_state.zip_path, "rb") as zip_file:
            st.download_button(
                label="⬇️ Download ZIP",
                data=zip_file,
                file_name=os.path.basename(st.session_state.zip_path),
                mime="application/zip",
                use_container_width=True
            )

# Process files when button is clicked
if transcribe_button:
    st.session_state.processing = True
    st.session_state.zip_path = None
    st.session_state.results = None
    st.session_state.all_results = {'success': [], 'errors': []}

# Handle transcription process
if st.session_state.processing:
    try:
        # Split files into batches of 10
        total_files = len(uploaded_files)
        batch_size = 10
        num_batches = (total_files + batch_size - 1) // batch_size
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Process each batch
        for batch_num in range(num_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, total_files)
            batch_files = uploaded_files[start_idx:end_idx]
            
            status_text.text(f"Processing batch {batch_num + 1}/{num_batches} ({len(batch_files)} files)...")
            
            # Process current batch with user settings
            results = process_batch(
                batch_files, 
                output_dir="outputs",
                api_key=st.session_state.get('api_key'),
                language=language_code,
                smart_format=smart_format,
                punctuate=punctuate
            )
            
            # Accumulate results
            st.session_state.all_results['success'].extend(results['success'])
            st.session_state.all_results['errors'].extend(results['errors'])
            
            # Update progress
            progress_bar.progress((batch_num + 1) / num_batches)
        
        # Create zip file from all transcriptions
        if st.session_state.all_results['success']:
            status_text.text("Creating zip file...")
            zip_path = create_zip_from_directory("outputs", ".", file_filter=".txt")
            st.session_state.zip_path = zip_path
            st.session_state.results = st.session_state.all_results
            st.session_state.processing = False
            status_text.empty()
            progress_bar.empty()
            st.rerun()
        else:
            st.error("No files were successfully transcribed.")
            st.session_state.processing = False
            status_text.empty()
            progress_bar.empty()
                
    except ValueError as e:
        st.error(f"❌ Input Error: {str(e)}")
        st.session_state.processing = False
    except Exception as e:
        st.error(f"❌ Error during transcription: {str(e)}")
        st.session_state.processing = False

# Display results
if st.session_state.results:
    results = st.session_state.results
    
    st.divider()
    st.markdown("### 📊 Transcription Results")
    
    # Success results
    if results['success']:
        st.success(f"✅ Successfully transcribed {len(results['success'])} file(s)")
        with st.expander("View successful transcriptions"):
            for item in results['success']:
                st.markdown(f"- **{item['input_file']}** → `{item['output_file']}`")
    
    # Error results
    if results['errors']:
        st.warning(f"⚠️ Failed to transcribe {len(results['errors'])} file(s)")
        with st.expander("View errors"):
            for error_item in results['errors']:
                st.markdown(f"- **{error_item['file']}**: {error_item['error']}")
    
    # Cleanup option
    if st.button("🧹 Clear Results", key="clear_results"):
        try:
            cleanup_directory("outputs")
            st.session_state.results = None
            st.session_state.zip_path = None
            st.success("Results cleared. You can upload new files.")
            st.rerun()
        except Exception as e:
            st.error(f"Error clearing results: {str(e)}")

# Footer
st.divider()
st.markdown(
    """
    <div style="text-align: center; color: gray; font-size: 0.8rem;">
    Powered by Deepgram Nova-3 | Processes files in batches of 10
    </div>
    """,
    unsafe_allow_html=True
)
