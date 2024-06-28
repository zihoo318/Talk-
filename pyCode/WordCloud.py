#워드클라우드 생성
#필터링 하지 않고 전처리과정에서 오타만 거른 파일로 그대로 워드클라운드 생성
# 최소 빈도수 이상인 단어들만 필터링 현재 min_frequency=25

from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os

def generate_wordcloud_from_file(personal_file_path):
    if not os.path.exists(personal_file_path):
        print(f"파일이 존재하지 않습니다: {personal_file_path}")
        return

    # 제외할 단어 목록
    excluded_words = {'안', '아'}

    # 개인 파일에서 형태소 분석 결과 읽기
    with open(personal_file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        
    # ' ;'를 제거하고 형태소 분석 결과를 분리
    morphs = content.replace(' ;', ' ').replace(';', '').split()

    # 제외할 단어를 걸러낸 형태소 리스트
    morphs = [word for word in morphs if word not in excluded_words and word.strip() != '']

    # 형태소 빈도 계산
    word_counts = Counter(morphs)
    
    # 최소 빈도수 이상인 단어들만 필터링
    min_frequency = 20
    filtered_word_counts = {word: count for word, count in word_counts.items() if count >= min_frequency}

    # 워드 클라우드 생성
    wordcloud = WordCloud(font_path='/usr/share/fonts/truetype/nanum/NanumGothic.ttf',
                          background_color='white', width=400, height=300).generate_from_frequencies(filtered_word_counts)

    # 워드 클라우드 출력
    plt.figure(figsize=(10, 8))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title("워드 클라우드")
    plt.show()

# ChatRoom 클래스의 필요한 부분을 이곳에 가져와서 사용 가능합니다
# 파일 경로 설정
file_path = '/content/KakaoTalk.txt'

# ChatRoom 객체 생성
#chat_room = ChatRoom(file_path)

# ChatRoom 객체를 사용하여 분석 수행
#chat_room.preprocess_and_analyze()

# 워드클라우드 생성 및 출력 예시
user_name = '강지후'
personal_file_path = chat_room.get_personal_file_path(user_name)
generate_wordcloud_from_file(personal_file_path)
# 워드클라우드 group 출력
# generate_wordcloud_from_file('/content/group.txt')
