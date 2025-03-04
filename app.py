import os
import streamlit as st
import openai
import yt_dlp

# Make sure your OpenAI API key is set as an environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    st.error("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
    st.stop()

def download_audio(url):
    """
    Downloads the best available audio from the YouTube URL,
    extracts it as an MP3 using ffmpeg, and returns the filename.
    """
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloaded_audio.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        # The postprocessor forces an MP3 output regardless of the original extension.
        return "downloaded_audio.mp3"

def transcribe_audio(file_path):
    """
    Transcribes the audio using OpenAI Whisper API and returns the verbose JSON response.
    """
    with open(file_path, "rb") as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file, response_format="verbose_json")
    return transcript

def translate_audio(file_path):
    """
    Translates the audio (assumed to be Hindi) to English using the Whisper translation API.
    """
    with open(file_path, "rb") as audio_file:
        transcript = openai.Audio.translate("whisper-1", audio_file, response_format="verbose_json")
    return transcript

st.title("YouTube Video Transcription and Translation App")

video_url = st.text_input("Enter the YouTube video URL:")

if st.button("Transcribe"):
    if video_url:
        st.info("Downloading audio from YouTube...")
        try:
            audio_file_path = download_audio(video_url)
            st.success("Audio downloaded successfully!")
            
            st.info("Transcribing audio using OpenAI Whisper API...")
            transcript_data = transcribe_audio(audio_file_path)
            language = transcript_data.get("language", None)
            st.write(f"Detected language: {language}")
            
            # If the detected language is Hindi ("hi"), translate to English
            if language == "hi":
                st.info("Hindi detected. Translating to English...")
                transcript_data = translate_audio(audio_file_path)
            
            transcript_text = transcript_data.get("text", "")
            st.subheader("Transcript:")
            st.write(transcript_text)
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.error("Please enter a valid YouTube URL")
