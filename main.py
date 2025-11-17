import streamlit as st
from googleapiclient.discovery import build
import pandas as pd

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="YouTube Top Comment Finder", layout="centered")
st.title("🔍 YouTube 영상에서 가장 좋아요 많은 댓글 찾기")

st.write("유튜브 영상 URL 또는 ID를 입력하면, 해당 영상의 **가장 좋아요를 많이 받은 댓글**을 알려주는 사이트입니다.")

api_key = st.text_input("YouTube Data API Key", type="password")
video_url = st.text_input("YouTube 영상 URL 또는 Video ID 입력")

run = st.button("가장 좋아요 많은 댓글 가져오기")

# -----------------------------
# Helper: Extract video ID
# -----------------------------
def extract_video_id(url):
    if "youtube.com/watch?v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    return url  # assume already ID

# -----------------------------
# YouTube API Call
# -----------------------------
def fetch_top_comment(video_id, key):
    youtube = build("youtube", "v3", developerKey=key)
    comments = []

    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=100,
        order="relevance"
    )
    response = request.execute()

    for item in response.get("items", []):
        top_comment = item["snippet"]["topLevelComment"]["snippet"]
        comments.append({
            "author": top_comment.get("authorDisplayName"),
            "text": top_comment.get("textDisplay"),
            "likes": top_comment.get("likeCount"),
            "published": top_comment.get("publishedAt"),
        })

    if not comments:
        return None

    df = pd.DataFrame(comments)
    df = df.sort_values("likes", ascending=False)
    return df

# -----------------------------
# Run
# -----------------------------
if run:
    if not api_key or not video_url:
        st.error("API Key와 영상 URL을 모두 입력해주세요.")
    else:
        vid = extract_video_id(video_url)
        st.write(f"**Video ID:** `{vid}`")

        df = fetch_top_comment(vid, api_key)
        if df is None or df.empty:
            st.error("댓글을 불러올 수 없습니다. 댓글이 없거나 API 제한일 수 있습니다.")
        else:
            top = df.iloc[0]
            st.success("가장 좋아요 많은 댓글을 찾았습니다!")

            st.markdown(f"""
            ### 🏆 Top Comment
            **작성자:** {top['author']}  
            **좋아요:** {top['likes']} 👍  
            **작성일:** {top['published']}  

            ---
            **댓글 내용:**  
            {top['text']}
            """)

            st.write("---")
            st.write("### 전체 상위 댓글 데이터")
            st.dataframe(df)
