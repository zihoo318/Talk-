#########사용코드##########
#워드클라우드를 위해 personal.txt, group.txt가 형태소 분석으로 인해 형태가 변하지 않고 오타만 거른 상태로 저장되도록 하기 위한
#언급 카운트 추가

import re
from konlpy.tag import Okt
from collections import defaultdict

class User:
    def __init__(self, name):
        self.name = name
        self.typo_count = 0 #오타 횟수
        self.initial_message_count = 0  # 초성 사용 횟수
        self.message_count = 0  # 메시지 보낸 횟수
        self.emoji_count = 0  # 이모티콘 횟수
        self.personal_file_path = f'/content/{self.name}_personal.txt'  # 개인 파일 경로 초기화
        self.mentioned_count=0 #본인이 언급된 경우 카운트
        self.mentionAnother_count #다른 사람을 언급하는 경우 카운트

class ChatRoom:
    def __init__(self, file_path):
        self.file_path = file_path
        self.room_name = self.extract_room_name()
        self.members = {}  # 사용자 이름을 키로 하고 User 객체를 값으로 하는 딕셔너리
        self.user_chats = defaultdict(str)
        self.total_chats = []
        self.okt = Okt()  # Okt 객체 생성
        self.group_file_path = '/content/group.txt'
        self.excluded_jamo_set = {'ㅋ', 'ㅍ', 'ㅎ', 'ㅌ'}  # 제외할 자음 집합

    def extract_room_name(self):
        with open(self.file_path, 'r', encoding='utf-8') as file:
            first_line = file.readline()
            room_name = first_line.split(" 님과")[0]
            return room_name.strip()

    def preprocess_and_analyze(self):
        # 텍스트 파일 읽기
        with open(self.file_path, 'r', encoding='utf-8') as file:
            text = file.read()

        # 날짜 정보 제거
        text = re.sub(r'저장한 날짜 : \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', '', text)
        text = re.sub(r'--------------- \d{4}년 \d{1,2}월 \d{1,2}일 \w+ ---------------', '', text)

        # 정규 표현식을 사용하여 사용자별 메시지를 추출
        lines = text.split('\n')
        for line in lines:
            match = re.match(r'\[(.+?)\] \[.+?\] (.+)', line)
            if match:
                user_name = match.group(1).strip() #보낸이
                message = match.group(2).strip() #보낸 메세지

                # 사용자 객체 생성 또는 가져오기
                if user_name not in self.members:
                    self.members[user_name] = User(user_name)

                user = self.members[user_name]

                # 형태소 분석 후 처리
                tokens = self.okt.morphs(message)
                for token in tokens:
                    if self.is_jamo_only(token):
                        user.typo_count += 1
                    elif self.is_jamo(token):
                      if not self.is_excluded_jamo(token):
                            user.initial_message_count += 1

                user.message_count += 1  # 메시지 보낸 횟수 증가
                self.user_chats[user_name] += message + ' '
                self.total_chats.append(message)

                # 언급 처리
                mentions = re.findall(r'@(\w+)', message) #한 라인에서 추출된 언급이름 저장하는 리스트 mentions
                for mentioned_name in mentions:
                    mentioned_name = mentioned_name.strip() #공백 제거
                    if mentioned_name in self.members:
                        self.members[mentioned_name].mentioned_count += 1 #언급된 사람 카운트 증가
                        user.mentionAnother_count += 1 #언급한 사람 카운드 증가


        # 개인별 메시지 저장 (오타 거른 상태로 저장)
        for user_name, chat in self.user_chats.items():
            user = self.members[user_name]
            with open(user.personal_file_path, 'w', encoding='utf-8') as file:
                # 각 메시지를 공백을 기준으로 나누어 처리
                words = chat.split()
                for word in words:
                    word_without_spaces = word.replace(' ', '')
                    if self.is_jamo_only(word_without_spaces):
                      # 오타가 있는 경우 처리하지 않고 건너뜁니다.
                      continue
                    else:
                      # 파일에 저장
                      file.write(word + ' ')

        # 전체 메시지 저장 (오타 거른 상태로 저장)
        with open(self.group_file_path, 'w', encoding='utf-8') as file:
            for message in self.total_chats:
                words = message.split()
                for word in words:
                    word_without_spaces = word.replace(' ', '')
                    if self.is_jamo_only(word_without_spaces):
                      # 오타가 있는 경우 처리하지 않고 건너뜁니다.
                      continue
                    else:
                      # 파일에 저장
                      file.write(word + ' ')
                file.write('\n')  # 각 메시지를 줄 단위로 구분



        # 오타 카운트 결과 출력
        print("오타 카운트:")
        for user_name, user in self.members.items():
            print(f"{user_name}: {user.typo_count}개")

    def is_jamo_only(self, word):
        # 한글 자모음으로만 구성된 단어인지 체크
        jamo_pattern = re.compile("[ㄱ-ㅎㅏ-ㅣ]+")
        return bool(jamo_pattern.fullmatch(word))

    def is_jamo(self, word):
        # 한글 자음으로만 구성된 단어인지 체크
        jamo_pattern = re.compile("[ㄱ-ㅎ]+")
        return bool(jamo_pattern.fullmatch(word))

    def is_excluded_jamo(self, word):
        # 제외할 자음 또는 모음으로만 구성된 단어인지 체크
        return all(char in self.excluded_jamo_set for char in word)

    def get_member_count(self):
        return len(self.members)

    def get_members(self):
        return list(self.members.keys())

    def get_user_info(self, user_name):
        if user_name in self.members:
            user = self.members[user_name]
            return f"이름: {user.name}, 오타 개수: {user.typo_count}, 초성 사용 횟수: {user.initial_message_count}, 메시지 수: {user.message_count}"
        else:
            return f"{user_name} 사용자 정보 없음"

    def get_personal_file_path(self, user_name):
        if user_name in self.members:
            return self.members[user_name].personal_file_path
        else:
            return None

    def get_group_file_path(self):
        return self.group_file_path

# 파일 경로 설정
file_path = '/content/KakaoTalk.txt'

# ChatRoom 객체 생성 및 분석 수행
chat_room = ChatRoom(file_path)
chat_room.preprocess_and_analyze()

# 채팅방 정보 출력
print(f"채팅방 이름: {chat_room.room_name}")
print(f"채팅방 인원 수: {chat_room.get_member_count()}")
print(f"멤버들: {', '.join(chat_room.get_members())}")

# 개인별 파일 경로 출력
for user_name in chat_room.get_members():
    print(f"{user_name}의 개인 파일 경로: {chat_room.get_personal_file_path(user_name)}")

# 특정 사용자 정보 출력 예시
user_name = '강지후'
print(chat_room.get_user_info(user_name))
