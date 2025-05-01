from openai import OpenAI 
import os
from dotenv import load_dotenv


def summarizer(text):
    load_dotenv()

    # api 키 입력
    client = OpenAI()

    # GPT 호출
    response = client.chat.completions.create(
        model = "gpt-3.5-turbo",
        messages = [
                    # role는 무조건 필요, system, user, assistant
                    {"role": "system", "content": "당신은 전문 뉴스 요약가입니다. 사용자가 제공한 기사 내용을 간결하고 명확한 문장을 한국어로 3 ~ 4줄로 요약하되, 구체적인 수치는 포함하고, 불필요한 감탄사나 반복은 피하세요."},
                    {"role" : "user", "content" : text}    
        ],
        temperature=0.5
    )

    # 결과 출력
    print(response.choices[0].message.content)

    return {"요약" : response.choices[0].message.content}


