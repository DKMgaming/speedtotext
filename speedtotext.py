import os
import streamlit as st
import speech_recognition as sr
from docx import Document
import librosa
import soundfile as sf

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def convert_audio_to_text(audio_path):
    recognizer = sr.Recognizer()
    text = ""
    
    # Đọc file âm thanh và chia thành các đoạn nhỏ
    try:
        with sr.AudioFile(audio_path) as source:
            duration = source.DURATION
            
            # Chia thành các đoạn nhỏ (ví dụ: 10 giây)
            for start in range(0, int(duration), 10):
                end = min(start + 10, int(duration))
                source_audio = recognizer.record(source, duration=end - start)  # Ghi âm đoạn nhỏ
                
                try:
                    segment_text = recognizer.recognize_google(source_audio, language='vi-VN')
                    text += segment_text + " "
                except sr.UnknownValueError:
                    text += "[Không thể nhận diện] "
                except sr.RequestError as e:
                    return f"Lỗi khi yêu cầu dịch vụ nhận diện giọng nói: {e}"
                
    except Exception as e:
        return f"Đã xảy ra lỗi: {e}"

    return text.strip()

def create_word_document(text, output_path):
    doc = Document()
    doc.add_heading('Transcript', level=1)
    doc.add_paragraph(text)
    doc.save(output_path)

st.title("Chuyển đổi âm thanh thành văn bản")
st.write("Tải lên file âm thanh để nhận diện và tạo tài liệu Word.")

uploaded_file = st.file_uploader("Chọn file âm thanh", type=["wav", "mp3", "m4a"])

if uploaded_file is not None:
    audio_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
    with open(audio_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    if uploaded_file.type == "audio/mpeg":
        wav_audio_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name.replace(".mp3", ".wav"))
        audio_data, sr_rate = librosa.load(audio_path, sr=None)
        sf.write(wav_audio_path, audio_data, sr_rate)
        audio_path = wav_audio_path

    text = convert_audio_to_text(audio_path)

    output_path = os.path.join(UPLOAD_FOLDER, 'transcript.docx')
    create_word_document(text, output_path)

    with open(output_path, "rb") as f:
        st.download_button("Tải xuống tài liệu Word", f, file_name='transcript.docx')
