import streamlit as st
import random

st.title("26명 4~5인 조 편성기")

st.write("""
26명을 4명씩 기본 조로 나누고,
남는 인원(2명)을 각 조에 1명씩 넣어 5명인 조도 만들어주는 프로그램입니다.
또한 **7번은 27번으로 자동 치환**됩니다.
""")

# 고정된 학생 번호 생성 (1~26) + 7→27 변환
def get_students():
    students = list(range(1, 27))
    # 7을 27로 치환
    students = [27 if s == 7 else s for s in students]
    return students

if st.button("조 편성 시작!"):
    students = get_students()
    random.shuffle(students)

    # 기본 4명이 들어가는 조 6개
    groups = [students[i:i+4] for i in range(0, 24, 4)]

    # 남는 인원 2명
    leftovers = students[24:]

    # 앞의 두 조에 1명씩 추가
    for i in range(len(leftovers)):
        groups[i].append(leftovers[i])

    st.subheader("📌 조 편성 결과")
    for idx, g in enumerate(groups, start=1):
        st.write(f"### {idx}조 ({len(g)}명)")
        st.write(g)

st.write("""
---
### GitHub 업로드 방법
1. 이 파일을 `app.py`로 저장
2. 같은 폴더에 `requirements.txt` 생성 (아래 내용 입력)
```
streamlit
```
3. GitHub에 업로드
4. Streamlit Cloud에서 Deploy
""")
