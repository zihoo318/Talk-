#########사용코드##########
#오타처리 방식 바꿈

import re
from konlpy.tag import Okt
from collections import defaultdict

class User:
    def __init__(self, name):
        self.name = name
        self.typo_count = 0 #오타 횟수
        self.initial_message_count = 0  # 초성 사용 횟수
        self.message_count = 0  # 메시지 보낸 횟수
        self.emoji_count = 0  # 이모티콘 횟수(카톡 임티는 포함X)
        self.personal_file_path = f'/content/{self.name}_personal.txt'  # 개인 파일 경로 초기화

class ChatRoom:
    def __init__(self, file_path):
        self.file_path = file_path
        self.room_name = self.extract_room_name()
        self.members = {}  # 사용자 이름을 키로 하고 User 객체를 값으로 하는 딕셔너리
        self.user_chats = defaultdict(str)
        self.total_chats = []
        self.okt = Okt()  # Okt 객체 생성
        self.group_file_path = '/content/group.txt'
        self.excluded_jamo_set = {'ㅋ', 'ㅍ', 'ㅎ', 'ㅌ','ㅠ','ㅜ','큐','쿠','튜','투','퓨','푸','튵','큨','캬','컄','헝','엉','어'}  # 제외할 자모음 집합

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
        pattern = re.compile(r'\[(.+?)\] \[.+?\] (.+)')
        matches = pattern.findall(text)
        for match in matches:
            user_name = match[0].strip()  # 보낸이
            message = match[1].strip()  # 보낸 메세지

            # 사용자 객체 생성 또는 가져오기
            if user_name not in self.members:
                self.members[user_name] = User(user_name)

            user = self.members[user_name]

            # 오타 처리
            tokens = message.split()
            for token in tokens:
                if not self.is_jamo_only(token): #특수기호,이모티콘 제거
                    for char in token:
                      if self.is_emoji(char):
                        user.emoji_count += 1
                    token=self.remove_emojis(token)
                    token=self.remove_special_symbols(token)
                    
                result = self.classify_jamo_vowel(token)
                if result == 0: #자모음 둘다
                    check=self.okt.morphs(token)
                    i=0
                    for char in check:
                      if not self.is_excluded_jamo(char):
                        i+=1
                    if i >= 3:
                        user.typo_count += 1
                        continue #오타확정
                    else: 
                      self.user_chats[user_name] += token+' '
                      self.total_chats.append(token+' ')
                elif result == 1: #자음만
                    self.user_chats[user_name] += token+' '
                    self.total_chats.append(token+' ')
                    if not self.is_excluded_jamo(token):
                      user.initial_message_count += 1
                elif result == 2: #모음만
                    if not self.is_excluded_jamo(token):
                      user.typo_count += 1
                      continue #오타확정
                    else:
                      self.user_chats[user_name] += token+' '
                      self.total_chats.append(token+' ')
                else:
                  self.user_chats[user_name] += token+' '
                  self.total_chats.append(token+' ')

            user.message_count += 1  # 메시지 보낸 횟수 증가
            self.user_chats[user_name] += ';'
            self.total_chats.append(';')


        # 개인별 메시지 저장 (오타 거른 상태로 저장)
        for user_name, chat in self.user_chats.items():
            user = self.members[user_name]
            with open(user.personal_file_path, 'w', encoding='utf-8') as file:
                file.write(chat)

        # 전체 메시지 저장 (오타 거른 상태로 저장)
        chat_string = ''.join(self.total_chats)
        with open(self.group_file_path, 'w', encoding='utf-8') as file:
            file.write(chat_string)

        # 오타 카운트 결과 출력
        print("오타 카운트:")
        for user_name, user in self.members.items():
            print(f"{user_name}: {user.typo_count}개")

    def is_special_symbol(self, character):
        """입력된 문자가 특수 기호인지 여부를 반환하는 함수"""
        category = unicodedata.category(character)
        if category.startswith('S') and not category.startswith('So'):
            return True
        else:
            return False

    def remove_special_symbols(self, word):
        """특수 기호를 제거한 문자열을 반환하는 함수"""
        result = []
        for char in word:
            if not self.is_special_symbol(char):
                result.append(char)
        return ''.join(result)

    def is_emoji(self, character):
        """입력된 문자가 이모티콘인지 여부를 반환하는 함수"""
        category = unicodedata.category(character)
        if category.startswith('So'):
            return True
        else:
            return False

    def remove_emojis(self, word):
        """이모티콘을 제거한 문자열을 반환하는 함수"""
        result = []
        for char in word:
            if not self.is_emoji(char):
                result.append(char)
        return ''.join(result)

    def classify_jamo_vowel(self,word):
        jamo_pattern = re.compile("[ㄱ-ㅎ]+")  # 자음 패턴
        vowel_pattern = re.compile("[ㅏ-ㅣ]+")  # 모음 패턴
    
        has_jamo = bool(jamo_pattern.search(word))
        has_vowel = bool(vowel_pattern.search(word))
    
        if has_jamo and has_vowel:
            return 0  # 자음과 모음이 모두 있는 경우
        elif has_jamo:
            return 1  # 자음만 있는 경우
        elif has_vowel:
            return 2  # 모음만 있는 경우
        else:
            return -1  # 영어인 경우

    def is_jamo_only(self, word):
        # 한글 외의 문자가 있는지 체크
        jamo_pattern = re.compile("[ㄱ-ㅎㅏ-ㅣ]+")
        return bool(jamo_pattern.fullmatch(word))

    def is_excluded_jamo(self, word):
        # 제외할 자음 또는 모음으로만 구성된 단어인지 체크(ㅋ큐ㅠ)
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

    def rank_users_by_message_count(self):
        message_counts = [(user.name, user.message_count) for user in self.members.values()]
        message_counts.sort(key=lambda x: x[1], reverse=True)
        return message_counts

    def rank_users_by_typo_count(self):
        typo_counts = [(user.name, user.typo_count) for user in self.members.values()]
        typo_counts.sort(key=lambda x: x[1], reverse=True)
        return typo_counts

    def rank_users_by_initial_message_count(self):
        initial_message_counts = [(user.name, user.initial_message_count) for user in self.members.values()]
        initial_message_counts.sort(key=lambda x: x[1], reverse=True)
        return initial_message_counts
        
    def rank_users_by_emoji_count(self):
        """사용자의 이모티콘 개수에 따라 사용자들을 정렬하여 반환"""
        emoji_counts = [(user.name, user.emoji_count) for user in self.members.values()]
        emoji_counts.sort(key=lambda x: x[1], reverse=True)
        return emoji_counts

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
