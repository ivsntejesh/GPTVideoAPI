import google.generativeai as genai
import os
import time
import tempfile
import streamlit as st

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

#video_file_name = "big_buck_bunny_720p_20mb.mp4"
#video_file_name = "WhatsApp Video 2024-05-26 at 6.08.12 PM.mp4"

def process_video(video):
  with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
        temp_file.write(video.read())
        temp_file_path = temp_file.name
    
    # Use the temporary file path with genai.upload_file
  try:
      #print(f"Uploading file...")
      st.text("Uploading file to gemini....")
      video_file = genai.upload_file(path=temp_file_path)
      #print(f"Completed upload: {video_file.uri}")
      st.success(f"Video uploaded and submitted successfully! Uploaded at: {video_file.uri}")
      #st.write(f"Completed upload: {video_file.uri}")

      while video_file.state.name == "PROCESSING":
          #print('Waiting for video to be processed....')
          st.text("Waiting for video to be processed.")
          time.sleep(10)
          video_file = genai.get_file(video_file.name)

      if video_file.state.name == "FAILED":
        raise ValueError(video_file.state.name)
      
      #print(f'Video processing complete: ' + video_file.uri)
      st.success(f'Video processing complete: ' + video_file.uri)
      return video_file
  
  except Exception as e:
      return f"Upload Failed: {str(e)}"
  finally:
      os.remove(temp_file_path)

def ask_gpt(prompt, video):
  # Create the prompt.
  #prompt = "Describe this video and count the number of chacrecters in the video."

  # Set the model to Gemini 1.5 Pro.
  model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest")

  # Make the LLM request.
  #print("Making LLM inference request...")
  st.text("Making LLM inference request...")
  response = model.generate_content([prompt, video], request_options={"timeout": 600})
  #print(response.text)
  return response.text


def main():
  # File uploader for video
  user_text = st.text_input("Enter your prompt, be as precise as possible:")
  uploaded_video = st.file_uploader("Choose a video...", type=["mp4", "mov", "avi", "mkv"])

  # Submit button
  if st.button("Submit"):
      if uploaded_video is not None:
          # Display a message indicating successful upload
          st.success("Video uploaded and submitted successfully!")

          # Optionally, you can display the uploaded video
          #st.video(uploaded_video)

          video_file_vf = process_video(uploaded_video)
          responce_text_from_gpt = ask_gpt(user_text, video_file_vf)
          #print(responce_text_from_gpt)
          st.write("Output from gpt: ")
          st.write(responce_text_from_gpt)
      else:
          st.error("Please upload a video file before submitting.")

if __name__ == "__main__":
    main()
