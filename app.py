import streamlit as st
import os
import google.generativeai as genai
import requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

# --- Unsplash Image Function ---
def get_image_urls(prompt, count):
    access_key = os.getenv("UNSPLASH_ACCESS_KEY")
    url = f"https://api.unsplash.com/search/photos?query={prompt}&client_id={access_key}&per_page={count}"
    
    try:
        response = requests.get(url)
        data = response.json()
        if "results" in data and len(data["results"]) > 0:
            return [img["urls"]["regular"] for img in data["results"][:count]]
        else:
            st.warning("No Unsplash images found. Using placeholders.")
            return ["https://via.placeholder.com/600x400.png?text=Image+Not+Found"] * count
    except Exception as e:
        st.error(f"Unsplash fetch error: {e}")
        return ["https://via.placeholder.com/600x400.png?text=Image+Error"] * count

# --- Streamlit UI ---
st.set_page_config(page_title="WriteWise - AI Blog Assistant")
st.title("✍️ WriteWise: Your Personal AI Blog Assistant")
st.subheader("Craft engaging blog posts with AI support.")

# Sidebar Input
st.sidebar.title("🛠 Blog Options")
blog_title = st.sidebar.text_input("Blog Title")
keywords = st.sidebar.text_area("Keywords (comma-separated)")
tone = st.sidebar.selectbox("Select Blog Tone", ["Formal", "Casual", "Informative", "Friendly", "Funny"])
num_words = st.sidebar.slider("Number of words", min_value=250, max_value=2000, step=100)
num_images = st.sidebar.number_input("Number of images", min_value=1, max_value=3, step=1)

submit_button = st.sidebar.button("🚀 Generate Blog")

# --- Generate Blog on Submit ---
if submit_button:
    if not blog_title.strip():
        st.error("Please enter a blog title.")
    else:
        with st.spinner("Generating your blog post..."):

            # Gemini Prompt
            prompt = f"""
            Write a {tone.lower()} blog titled "{blog_title}" using the following keywords: {keywords}.
            The blog should be around {num_words} words.
            Make it engaging and well-structured.
            """
            try:
                # Generate blog
                response = model.generate_content(prompt)
                blog_content = response.text

                # Split content into paragraphs
                paragraphs = blog_content.split("\n\n")
                total_paragraphs = len(paragraphs)

                # Fetch images
                image_urls = get_image_urls(blog_title, num_images)

                st.subheader("🧠 AI-Generated Blog")

                # --- Insert Top Image ---
                if num_images >= 1:
                    st.image(image_urls[0], caption="📌 Cover Image")

                # --- Display Content with Images ---
                for i, para in enumerate(paragraphs):
                    st.markdown(para)

                    # --- Insert Middle Image ---
                    if num_images >= 2 and i == total_paragraphs // 2:
                        st.image(image_urls[1], caption="📸 Midpoint Image")

                    # --- Insert Bottom Image ---
                    if num_images >= 3 and i == total_paragraphs - 2:
                        st.image(image_urls[2], caption="🖼️ Closing Image")

            except Exception as e:
                st.error(f"An error occurred: {e}")
