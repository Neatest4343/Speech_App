import streamlit as st
import speech_recognition as sr
from threading import Thread
import time

# Global variables to control recognition state
recognizer = None
paused = False

# Function to perform speech recognition using the selected API and language
def recognize_speech(audio_file, api, language):
    global recognizer
    global paused

    recognizer = sr.Recognizer()

    try:
        # Load audio file
        with sr.AudioFile(audio_file) as source:
            audio = recognizer.record(source)
        
        # Configure language for Google Speech Recognition API
        if api == 'Google Speech Recognition':
            if language == 'English':
                text = recognizer.recognize_google(audio, language='en-US')
            elif language == 'Spanish':
                text = recognizer.recognize_google(audio, language='es-ES')
            # Add more languages as needed
            else:
                st.error("Selected language not supported for Google Speech Recognition.")
                return None
        
        # Configure language for CMU Sphinx API
        elif api == 'CMU Sphinx':
            if language == 'English':
                text = recognizer.recognize_sphinx(audio, language='en-US')
            elif language == 'Spanish':
                text = recognizer.recognize_sphinx(audio, language='es-ES')
            # Add more languages as needed
            else:
                st.error("Selected language not supported for CMU Sphinx.")
                return None
        
        # Add more conditions for other APIs if needed (e.g., Azure, IBM)
        else:
            st.error("Selected API not supported.")
            return None
        
        return text
    
    except sr.UnknownValueError:
        st.error("Speech recognition could not understand audio.")
        return None
    
    except sr.RequestError as e:
        st.error(f"Could not request results from {api} service; {e}")
        return None

# Function to asynchronously perform speech recognition
def perform_recognition(audio_file, api, language):
    global paused

    while not paused:
        # Perform speech recognition
        text_result = recognize_speech(audio_file, api, language)

        if text_result:
            # Display result
            st.write("Recognized Text:")
            st.write(text_result)

            # Option to save the result to a file
            if st.button("Save to File"):
                save_to_file(text_result)

            break
        else:
            time.sleep(0.5)  # Adjust sleep time as needed

# Streamlit app
def main():
    st.title("Ifon Speech Recognition App")
    st.write("Select a speech recognition API, language, and upload an audio file.")

    # Select speech recognition API
    selected_api = st.selectbox("Select Speech Recognition API", ['Google Speech Recognition', 'CMU Sphinx'])

    # Select language
    selected_language = st.selectbox("Select Language", ['English', 'Spanish'])

    # Upload audio file
    audio_file = st.file_uploader("Upload an audio file (.wav, .mp3)", type=['wav', 'mp3'])

    if audio_file is not None:
        st.audio(audio_file, format='audio/wav', start_time=0)

        # Control buttons for speech recognition
        if not st.session_state.get('is_recognizing', False):
            st.session_state.is_recognizing = False

        if not st.session_state.is_recognizing:
            if st.button("Start Recognition"):
                st.session_state.is_recognizing = True
                Thread(target=perform_recognition, args=(audio_file, selected_api, selected_language)).start()
        else:
            if st.button("Pause"):
                global paused
                paused = True
            if st.button("Resume"):
                paused = False
                Thread(target=perform_recognition, args=(audio_file, selected_api, selected_language)).start()

def save_to_file(text):
    # Allow user to specify filename and location for saving
    file_name = st.text_input("Enter a filename:", value="transcribed_text.txt")
    
    if st.button("Save"):
        try:
            # Write text to file
            with open(file_name, 'w', encoding='utf-8') as file:
                file.write(text)
            st.success(f"Text saved successfully as {file_name}")
        except Exception as e:
            st.error(f"Error saving file: {e}")

if __name__ == "__main__":
    main()
