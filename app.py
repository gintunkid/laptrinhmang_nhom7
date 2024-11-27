from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import openai
import os
from dotenv import load_dotenv
from datetime import datetime

# Load API Key từ file .env (thư viện python-dotenv)
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = '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'
socketio = SocketIO(app)

# OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Tạo biến để lưu thông tin
user_location = None
user_date = None

# Route chính để render giao diện
@app.route("/")
def index():
    return render_template("index.html")

@socketio.on("send_message")
def handle_message(data):
    user_message = data.get("message", "").strip().lower()
    bot_message = ""
    
    # Danh sách các tỉnh thành phố của Việt Nam
    tinh_thanh = [
        "Hà Nội", "Hồ Chí Minh", "Đà Nẵng", "Cần Thơ", "Hải Phòng", "An Giang", "Bà Rịa - Vũng Tàu", "Bắc Giang", 
        "Bắc Kạn", "Bạc Liêu", "Bắc Ninh", "Bến Tre", "Bình Định", "Bình Dương", "Bình Phước", "Bình Thuận", 
        "Cao Bằng", "Cà Mau", "Cần Thơ", "Gia Lai", "Hà Giang", "Hà Nam", "Hà Tĩnh", "Hải Dương", "Hậu Giang", 
        "Hòa Bình", "Hồ Chí Minh", "Hưng Yên", "Khánh Hòa", "Kiên Giang", "Kon Tum", "Lai Châu", "Lâm Đồng", 
        "Lạng Sơn", "Lào Cai", "Long An", "Nam Định", "Nghệ An", "Ninh Bình", "Ninh Thuận", "Phú Thọ", "Phú Yên", 
        "Quảng Bình", "Quảng Nam", "Quảng Ngãi", "Quảng Ninh", "Quảng Trị", "Sóc Trăng", "Sơn La", "Tây Ninh", 
        "Thái Bình", "Thái Nguyên", "Thanh Hóa", "Thừa Thiên Huế", "Tiền Giang", "Trà Vinh", "Tuyên Quang", 
        "Vĩnh Long", "Vĩnh Phúc", "Yên Bái"
    ]
    # Kiểm tra các từ khóa trong kịch bản
    if "chào" in user_message or "hi" in user_message or "hello" in user_message:
        bot_message = "Xin chào! Tôi có thể giúp gì cho bạn hôm nay?"
    elif "đặt phòng" in user_message or "book phòng" in user_message:
        bot_message = "Bạn muốn đặt phòng cho ngày nào và ở đâu?"
        # Kiểm tra xem có tỉnh thành nào trong danh sách được nhắc đến trong câu hỏi không
        for tinh in tinh_thanh:
            if tinh.lower() in user_message.lower():
                bot_message = f"Bạn muốn đặt phòng tại {tinh}. Bạn muốn đặt phòng cho ngày nào?"
                break
        else:
            # Nếu không có tỉnh thành nào được tìm thấy
            bot_message = "Bạn muốn đặt phòng ở thành phố hoặc tỉnh nào?"
        # Kiểm tra các từ khóa trong câu hỏi
        if "đặt phòng" in user_message or "book phòng" in user_message:
            bot_message = "Bạn muốn đặt phòng cho ngày nào và ở đâu?"
        
        # Kiểm tra xem có tỉnh thành nào trong câu hỏi không
        for tinh in tinh_thanh:
            if tinh.lower() in user_message:
                user_location = tinh  # Lưu tỉnh thành
                bot_message = f"Bạn muốn đặt phòng tại {tinh}. Bạn muốn đặt phòng cho khoảng thời gian nào?"
                break
        else:
            bot_message = "Bạn muốn đặt phòng ở thành phố hoặc tỉnh nào?"
    elif "ngày" in user_message or "giờ" in user_message:
        # Tìm kiếm mốc thời gian trong câu
        try:
            # Giả sử người dùng nhập thời gian theo định dạng như "ngày 25 tháng 12"
            user_date = datetime.strptime(user_message, "%d %m %Y")
            bot_message = f"Đặt lịch cho bạn tại {user_location} vào ngày {user_date.strftime('%d-%m-%Y')}"
        except ValueError:
            bot_message = "Xin vui lòng cung cấp ngày tháng rõ ràng."
        else:
            if user_location and user_date:
                bot_message = f"Đặt lịch cho bạn tại {user_location} vào ngày {user_date.strftime('%d-%m-%Y')}"
            else:
                bot_message = "Xin lỗi, tôi không hiểu yêu cầu của bạn."
                
    elif "giá" in user_message:
        bot_message = "Giá phòng dao động từ [giá]. Bạn muốn biết chi tiết về loại phòng nào?"
    elif "khuyến mãi" in user_message:
        bot_message = "Chúng tôi có khuyến mãi đặc biệt cho các kỳ nghỉ dài. Bạn muốn tìm hiểu thêm?"
    elif "wifi" in user_message:
        bot_message = "Chúng tôi cung cấp wifi miễn phí cho tất cả khách hàng."
    elif "không hiểu" in user_message:
        bot_message = "Xin lỗi, tôi không hiểu những gì bạn đang nói."
    elif "phòng" in user_message:
        if "đơn" in user_message or "phòng đơn" in user_message:
            bot_message = "Chúng tôi có phòng đơn với các tiện nghi cơ bản như giường đơn, điều hòa, TV, và wifi miễn phí. Giá dao động từ [giá]. Bạn muốn đặt phòng này cho ngày nào?"
        elif "đôi" in user_message or "phòng đôi" in user_message:
            bot_message = "Phòng đôi có không gian rộng rãi với giường đôi và các tiện ích như TV, minibar và phòng tắm riêng. Giá từ [giá]. Bạn muốn đặt vào ngày nào?"
        elif "gia đình" in user_message or "phòng gia đình" in user_message:
            bot_message = "Chúng tôi cung cấp phòng gia đình rộng rãi, có thể chứa từ 4 đến 6 người. Phòng có giường cỡ lớn, sofa, và các tiện nghi khác. Giá từ [giá]. Bạn cần phòng cho bao nhiêu người?"
        elif "suite" in user_message:
            bot_message = "Chúng tôi có các phòng suite cao cấp với không gian rộng rãi, khu vực tiếp khách, và phòng tắm riêng biệt. Phòng suite có giá từ [giá]. Bạn muốn tìm hiểu thêm?"
        elif "view biển" in user_message or "view thành phố" in user_message:
            bot_message = "Chúng tôi có phòng với view biển tuyệt đẹp hoặc view thành phố. Tùy theo loại phòng, giá dao động từ [giá]. Bạn muốn phòng view nào?"
        else:
            bot_message = "Bạn có thể chọn giữa phòng đơn, đôi, gia đình, hay suite. Bạn muốn phòng nào?"
    elif "tiện ích" in user_message or "dịch vụ" in user_message:
        if "bữa sáng" in user_message:
            bot_message = "Chúng tôi phục vụ bữa sáng buffet miễn phí từ 6:30 đến 10:00 mỗi ngày. Bạn muốn biết thêm gì về thực đơn?"
        elif "spa" in user_message:
            bot_message = "Khách sạn có dịch vụ spa thư giãn. Bạn có muốn đặt lịch cho một buổi massage không?"
        elif "gym" in user_message:
            bot_message = "Chúng tôi có phòng tập gym với trang thiết bị hiện đại, mở cửa từ 6:00 đến 22:00 mỗi ngày. Bạn muốn sử dụng dịch vụ này?"
        elif "hồ bơi" in user_message:
            bot_message = "Khách sạn có hồ bơi ngoài trời, bạn có thể sử dụng từ 8:00 đến 20:00. Bạn có muốn biết thêm về các dịch vụ hồ bơi không?"
        elif "đưa đón sân bay" in user_message:
            bot_message = "Chúng tôi cung cấp dịch vụ đưa đón sân bay miễn phí. Bạn cần đặt lịch đưa đón từ sân bay về khách sạn không?"
        elif "giặt ủi" in user_message:
            bot_message = "Chúng tôi có dịch vụ giặt ủi. Bạn cần giúp đỡ về việc giặt đồ không?"
        elif "thú cưng" in user_message:
            bot_message = "Khách sạn của chúng tôi chào đón thú cưng nhỏ. Bạn muốn mang thú cưng theo khi đặt phòng?"
        else:
            bot_message = "Khách sạn cung cấp nhiều dịch vụ như giặt ủi, spa, gym, và bữa sáng miễn phí. Bạn có cần dịch vụ nào không?"
    elif "chính sách" in user_message or "quy định" in user_message:
        if "hủy phòng" in user_message:
            bot_message = "Chính sách hủy phòng của chúng tôi cho phép hủy miễn phí trước 24 giờ. Sau thời gian đó, sẽ có một khoản phí hủy phòng. Bạn cần hủy phòng nào?"
        elif "thanh toán" in user_message:
            bot_message = "Chúng tôi chấp nhận thanh toán qua thẻ tín dụng, thẻ ghi nợ và chuyển khoản ngân hàng. Bạn muốn thanh toán như thế nào?"
        elif "giờ check-in" in user_message:
            bot_message = "Giờ check-in của chúng tôi là từ 14:00. Nếu bạn muốn check-in sớm, vui lòng thông báo trước để chúng tôi chuẩn bị."
        elif "giờ check-out" in user_message:
            bot_message = "Giờ check-out là 12:00. Nếu bạn muốn check-out muộn, chúng tôi có thể hỗ trợ nếu có phòng trống."
        elif "chính sách bồi thường" in user_message:
            bot_message = "Nếu có sự cố trong suốt thời gian lưu trú, chúng tôi có chính sách bồi thường tùy theo tình huống. Bạn muốn biết thêm chi tiết?"
        else:
            bot_message = "Khách sạn có nhiều chính sách linh hoạt về hủy phòng, thanh toán và check-in/check-out. Bạn có câu hỏi nào về chính sách không?"
    elif "khuyến mãi" in user_message or "giảm giá" in user_message:
        if "mới" in user_message:
            bot_message = "Chúng tôi hiện đang có chương trình giảm giá đặc biệt cho khách hàng lần đầu. Bạn muốn biết thêm chi tiết?"
        elif "mùa" in user_message or "lễ" in user_message:
            bot_message = "Vào mùa lễ, chúng tôi có các gói khuyến mãi đặc biệt. Bạn muốn biết giá phòng trong kỳ nghỉ lễ này?"
        elif "cho nhóm" in user_message:
            bot_message = "Chúng tôi có chính sách giảm giá cho đoàn khách từ 5 người trở lên. Bạn muốn biết thêm chi tiết về giảm giá cho nhóm?"
        else:
            bot_message = "Chúng tôi có nhiều khuyến mãi hấp dẫn. Bạn muốn kiểm tra khuyến mãi cho ngày bạn đặt phòng?"
    elif "liên hệ" in user_message or "giới thiệu" in user_message:
        bot_message = "Nếu bạn cần liên hệ với nhân viên khách sạn, vui lòng gọi đến số điện thoại [0797268602] hoặc gửi email đến [nguyentuankiet1660804@gmail.com]. Chúng tôi luôn sẵn sàng hỗ trợ bạn."
    else:
        # Gửi câu hỏi tới API của ChatGPT nếu không nhận diện được
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Bạn là một trợ lý giúp người dùng đặt phòng khách sạn."},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=150,
                temperature=0.7
            )
            bot_message = response['choices'][0]['message']['content'].strip()
        except Exception as e:
            bot_message = "Xin lỗi, tôi không hiểu những gì bạn đang nói. Vui lòng thử lại."
 
    # Gửi thông điệp trả lời về cho người dùng
    emit("receive_message", {"message": bot_message})

# Chạy ứng dụng
if __name__ == "__main__":
    socketio.run(app, debug=True)
