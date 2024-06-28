# 랭킹


##전처리로 기록된 정보들
# 메시지 수 기준 랭킹 출력
#chat_room.rank_users_by_message_count()함수 호출 시 정렬된 리스트 반환
#(user_name, count) 형식의 튜플을 요소로 가진 리스트
message_count_ranking = chat_room.rank_users_by_message_count()
print("\n메시지 수 기준 랭킹:")
for rank, (user_name, count) in enumerate(message_count_ranking, 1):
    print(f"{rank}. {user_name}: {count} 개")

# 오타 수 기준 랭킹 출력
#chat_room.rank_users_by_typo_count()함수 호출 시 정렬된 리스트 반환
#(user_name, count) 형식의 튜플을 요소로 가진 리스트
typo_count_ranking = chat_room.rank_users_by_typo_count()
print("\n오타 수 기준 랭킹:")
for rank, (user_name, count) in enumerate(typo_count_ranking, 1):
    print(f"{rank}. {user_name}: {count} 개")

# initial_message_count 기준 랭킹 출력
#chat_room.rank_users_by_initial_message_count()함수 호출 시 정렬된 리스트 반환
#(user_name, count) 형식의 튜플을 요소로 가진 리스트
initial_message_count_ranking = chat_room.rank_users_by_initial_message_count()
print("\n초성 사용 횟수 기준 랭킹:")
for rank, (user_name, count) in enumerate(initial_message_count_ranking, 1):
    print(f"{rank}. {user_name}: {count} 번")


##파일에서 검색해 낼 정보들
#언급한 횟수, 언급된 횟수를 각각 담은 딕셔너리 3개 반환
def count_mentions(chat_room):
    # 멤버들 이름을 키로 하고, 값을 0으로 초기화한 딕셔너리 생성
    mention_counts = {user_name: 0 for user_name in chat_room.get_members()}
    mentioned_counts = {user_name: 0 for user_name in chat_room.get_members()}

    # 각 사용자의 개인 파일 경로 가져오기
    members = chat_room.get_members()
    for member in members:
        personal_file_path = chat_room.get_personal_file_path(member)

        # 개인 파일을 읽어서 언급한 횟수와 언급된 횟수 계산
        if personal_file_path:
            with open(personal_file_path, 'r', encoding='utf-8') as file:
                messages = file.read().split(';')
                for message in messages:
                    # 언급된 이름 찾기
                    mentions = re.findall(r'@(\w+)', message)
                    for mentioned_name in mentions:
                        mentioned_name = mentioned_name.strip()
                        if mentioned_name in mention_counts:
                            # 언급한 사람의 횟수 증가
                            mention_counts[member] += 1
                            # 언급된 사람의 횟수 증가
                            mentioned_counts[mentioned_name] += 1

    # 값에 따라 내림차순으로 정렬
    mention_counts = dict(sorted(mention_counts.items(), key=lambda item: item[1], reverse=True))
    mentioned_counts = dict(sorted(mentioned_counts.items(), key=lambda item: item[1], reverse=True))

    return mention_counts, mentioned_counts

mention, mentioned = count_mentions(chat_room)
print("\n언급한 횟수:", mention)
print("언급된 횟수:", mentioned)

#사진 보낸 갯수
def count_photos(chat_room):
    photo_count = {user_name: 0 for user_name in chat_room.get_members()}

    # 각 사용자의 개인 파일 경로 가져오기
    members = chat_room.get_members()
    for member in members:
        personal_file_path = chat_room.get_personal_file_path(member)

        # 개인 파일을 읽어서 사진 개수 계산
        if personal_file_path:
            with open(personal_file_path, 'r', encoding='utf-8') as file:
                messages = file.read().split(';')
                for message in messages:
                    message = message.strip()
                    # '사진' 또는 '사진 X장' 패턴 찾기
                    matches = re.findall(r'사진\s*(\d*)\s*장?', message)
                    for match in matches:
                        # '사진', 숫자, '장' 외 다른 문자가 포함되지 않은 경우
                        if re.fullmatch(r'사진\s*\d*\s*장?', message):
                            if match.isdigit():
                                photo_count[member] += int(match)
                            else:
                                photo_count[member] += 1
    # 값에 따라 내림차순으로 정렬하여 리스트로 반환
    photo_count = dict(sorted(photo_count.items(), key=lambda item: item[1], reverse=True))
    return photo_count

photo = count_photos(chat_room)
print("\n사진 보낸 횟수:", photo)

#이모티콘 보낸 갯수
def count_emojis(chat_room):
    emoji_count = {user_name: 0 for user_name in chat_room.get_members()}

    # 각 사용자의 개인 파일 경로 가져오기
    members = chat_room.get_members()
    for member in members:
        personal_file_path = chat_room.get_personal_file_path(member)

        # 개인 파일을 읽어서 이모티콘 개수 계산
        if personal_file_path:
            with open(personal_file_path, 'r', encoding='utf-8') as file:
                messages = file.read().split(';')
                for message in messages:
                    message = message.strip()
                    # '이모티콘'만 있는 경우 찾기
                    if message == '이모티콘':
                        emoji_count[member] += 1

    # chat_room.rank_users_by_emoji_count()의 결과 가져오기
    basic_emoji_counts = chat_room.rank_users_by_emoji_count()

    # emoji_count와 sorted_emoji_counts를 같은 키 값끼리 더해주기
    for name, count in basic_emoji_counts:
        if name in emoji_count:
            emoji_count[name] += count
    # 값에 따라 내림차순으로 정렬하여 리스트로 반환
    emoji_count = dict(sorted(emoji_count.items(), key=lambda item: item[1], reverse=True))
    return emoji_count

emoji = count_emojis(chat_room)
print("\n이모티콘 보낸 횟수:", emoji)


#검색어 받아서 검색하는 함수 만들기
def search_keyword_in_personal_files(chat_room, keyword):
    members = chat_room.get_members()
    search_results = defaultdict(int)

    for user_name in members:
        personal_file_path = chat_room.get_personal_file_path(user_name)
        if not os.path.exists(personal_file_path):
            continue

        with open(personal_file_path, 'r', encoding='utf-8') as file:
            messages = file.read().split(';')
            for message in messages:
                if keyword.strip() in message:
                    search_results[user_name] += 1

    # 결과를 횟수 기준으로 내림차순 정렬하여 반환
    sorted_results = dict(sorted(search_results.items(), key=lambda item: item[1], reverse=True))
    return sorted_results

# 검색어 설정
keyword = '삭제된 메시지입니다'
# 검색 실행 및 결과 출력
results = search_keyword_in_personal_files(chat_room, keyword)
print("\n검색어 횟수 랭킹:")
rank=1
for user_name, count in results.items():
    print(f"{rank}. {user_name}: {count}회")
    rank += 1
print(type(results))


#메세지 평균 길이
def calculate_average_message_length(chat_room):
    user_average_lengths = {}
    members = chat_room.get_members()

    for user_name in members:
        personal_file_path = chat_room.get_personal_file_path(user_name)

        if os.path.exists(personal_file_path):
            with open(personal_file_path, 'r', encoding='utf-8') as file:
                content = file.read().split(';')

            total_length = 0
            num_messages = 0
            for message in content:
                message = message.strip()
                if message:  # 빈 문자열이 아닌 경우에만 처리
                    total_length += len(message)
                    num_messages += 1

            if num_messages > 0:
                average_length = total_length / num_messages
            else:
                average_length = 0
            #print(user_name,"전체 합:",total_length)
            #print(user_name,"메세지 개수:",num_messages)
            user_average_lengths[user_name] = average_length
    
    # 평균 길이 순으로 정렬
    sorted_results = {user_name: user_average_lengths[user_name] for user_name, _ in message_count_ranking if user_name in user_average_lengths}
    sorted_results = dict(sorted(sorted_results.items(), key=lambda item: item[1], reverse=True))
    return sorted_results

results=calculate_average_message_length(chat_room)
# 결과 출력
print("\n평균 메시지 길이 기준 랭킹:")
for rank, (user_name, avg_length) in enumerate(results.items(), 1):
    print(f"{rank}. {user_name}: {avg_length:.2f} 글자")
