import streamlit as st
from googleapiclient.discovery import build
import pandas as pd

# --------------------------------------------------
# Streamlit: YouTube 댓글 좋아요 순 정렬 사이트
# --------------------------------------------------
st.set_page_config(page_title="YouTube 댓글 좋아요 순 정렬", layout="wide")
st.title("🔍 YouTube 댓글 좋아요 순으로 정렬하는 사이트")

st.write("유튜브 영상 링크를 입력하면 해당 영상의 댓글을 불러와 **좋아요 많은 순**으로 정렬해서 보여줍니다.")

# -----------------------------
# 입력값
# -----------------------------
api_key = st.text_input("YouTube Data API Key", type="password")
video_url = st.text_input("YouTube 영상 URL 또는 Video ID")
limit = st.slider("가져올 댓글 수 (최대 500개 권장)", 20, 500, 100)
run = st.button("댓글 불러오기")

# -----------------------------
# Helper: 영상 ID 추출
# -----------------------------
def extract_video_id(url):
    if "youtube.com/watch?v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    return url

# -----------------------------
# YouTube API 댓글 가져오기
# -----------------------------
def get_comments(video_id, key, max_comments=200):
    youtube = build("youtube", "v3", developerKey=key)
    comments = []
    next_page = None
    fetched = 0

    while True:
        req = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100,
            pageToken=next_page,
            order="relevance"
        )
        res = req.execute()

        for item in res.get("items", []):
            snip = item["snippet"]["topLevelComment"]["snippet"]
            comments.append({
                "author": snip.get("authorDisplayName"),
                "comment": snip.get("textDisplay"),
                "likes": snip.get("likeCount"),
                "published": snip.get("publishedAt"),
            })
            fetched += 1
            if fetched >= max_comments:
                return pd.DataFrame(comments)

        next_page = res.get("nextPageToken")
        if not next_page:
            break

    return pd.DataFrame(comments)

# -----------------------------
# Run
# -----------------------------
if run:
    if not api_key or not video_url:
        st.error("API 키와 영상 링크를 모두 입력해야 합니다.")
    else:
        vid = extract_video_id(video_url)
        st.write(f"### 🎬 Video ID: `{vid}`")

        df = get_comments(vid, api_key, limit)
        if df is None or df.empty:
            st.error("댓글을 불러올 수 없습니다. API 제한 또는 댓글 없음.")
        else:
            df_sorted = df.sort_values("likes", ascending=False).reset_index(drop=True)

            st.success("댓글 불러오기 완료! 좋아요 순으로 정렬했습니다.")

            # Top comment highlight
            top = df_sorted.iloc[0]
            st.markdown(f"""
            ## 🏆 가장 좋아요 많은 댓글
            **작성자:** {top['author']}  
            **좋아요:** {top['likes']} 👍  
            **작성일:** {top['published']}  

            ---
            {top['comment']}
            """)

            st.write("---")
            st.write("## 📄 전체 정렬된 댓글 목록")
            st.dataframe(df_sorted, use_container_width=True)

            # CSV Export
            st.download_button(
                label="📥 CSV로 다운로드",
                data=df_sorted.to_csv(index=False).encode('utf-8'),
                file_name="youtube_comments_sorted.csv",
                mime="text/csv"
            )
