import os
import time
from groq import Groq
from credentials import groq_token, gemini_token
client = Groq(
    api_key= groq_token#get tokenn from groq
)
import google as genai
import os
import time
genai.configure(api_key=gemini_token) #get token from google

model = genai.GenerativeModel('gemini-1.5-flash')
chat_session = None
config = genai.GenerationConfig(
    max_output_tokens=2048, temperature=0, top_p=1, top_k=32
)
def generate_answer_groq(prompt):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="llama3-70b-8192",
        temperature=1,
        max_tokens=2048,
    )

    return chat_completion.choices[0].message.content

def get_answer(string):
    return generate_answer_groq(string)

def start_chat():
    global chat_session
    # chat_session = client.chat.sessions.create(
    #     model="llama3-70b-8192",
    #     temperature=1,
    #     max_tokens=2048,
    # )
    chat_session = model.start_chat()
def chat(prompt):
    global chat_session
    
    response = chat_session.send_message(prompt, generation_config=config).text
    return response
def create_email(receiver, caption, body):
    prompt = "Dựa theo thông tin về email gửi đến, tiêu đề và một phần nội dung (nếu có) email sau, hãy hoàn thiện email một cách phù hợp bằng tiếng Việt\n"
    receiver = f"Người nhận: {receiver}"
    caption = f"Tiêu đề: {caption}"
    if body:
        body = f"Nội dung: {body}"
    else:
        print('No body\n')
        body = "Nội dung: Chưa có"
    email = f"{receiver}\n{caption}\n{body}\n"
    # return generate_answer_groq(prompt + email)
    return model.generate_content(prompt + email, generation_config= config).text
from PIL import Image

def create_campaign(name, description,  image_url):
    prompt = "Hãy hoàn thiện thông tin mô tả chi tiết về chiến dịch một cách phù hợp bằng tiếng Việt dựa trên tên chiến dịch và ảnh minh họa chiến dịch như sau\n"
    name = f"Tên chiến dịch: {name}"
    prompt = f"{prompt}\n{name}"
    # goal = f"Mục tiêu: {goal}"
    # start_date = f"Ngày bắt đầu: {start_date}"
    # end_date = f"Ngày kết thúc: {end_date}"
    image  = Image.open(image_url)
    # campaign = f"{name}\n{description}\n{goal}\n{start_date}\n{end_date}\n{image_url}\n"
    description = f"Mô tả: {description}"
    # return generate_answer_groq(prompt + campaign)
    return model.generate_content([prompt , image], generation_config= config).text




if __name__ == "__main__":
    choice = input('Nhập chức năng theo số: ')
    if choice == '1':
        start_chat()
        while True:
            question = input("User: ")
            print('Agent: ', chat(question))
    elif choice == '2': 
        while True:
            question = input("Enter your question: ")
            print(get_answer(question))
    elif choice == '3':
        print(create_email("FPT Software", "Hỗ trợ gây quỹ dự án từ thiện Tết Sẻ Chia 2025", "Kính gửi các bên liên quan. Tôi tên là Nguyễn Văn A, đại diện cho Ban tổ chức chương trình từ thiện Tết Sẻ Chia 2025. Chúng tôi đang tìm kiếm các nhà tài trợ để hỗ trợ cho chương trình của chúng tôi. Chúng tôi rất mong nhận được sự hỗ trợ từ các bạn. Xin cảm ơn."))
    elif choice == '4':
        print(create_campaign("Mùa Hè Xanh 2025", "Mùa Hè Xanh 2025 là một chiến dịch của Hội Đoàn thanh niên PTIT với mục đích lan tỏa tinh thần trồng cây, yêu thương thiên nhiên cho mọi người. Thông tin chi tiết như sau: ", "image\example_campaign.jpg"))
    else:
        print('Invalid choice')
