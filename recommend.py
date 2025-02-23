from sentence_transformers import SentenceTransformer
import time
# import sqlite3
import os
import numpy as np
import pyodbc

conn_str = (
    "Driver={ODBC Driver 17 for SQL Server};"  # Driver SQL Server phù hợp với hệ điều hành của bạn
    "Server=47.130.30.15;"  # Địa chỉ IP của server
    "Database=VFundFuture;"  # Tên database bạn muốn kết nối
    "UID=sa;"  # Tên người dùng (user)
    "PWD=qjeF68CTt3UdVkxA;"  # Mật khẩu người dùng
    "Encrypt=yes;"  # Mã hóa kết nối
    "TrustServerCertificate=yes;"  # Tin tưởng chứng chỉ của server
)

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()


#
cursor.execute("SELECT Story FROM dbo.Fund where FundID = 'B08E698E-3FB9-44AB-BDA4-1D80412DAD88'")
rows = cursor.fetchall()
print(rows)
print(type(rows[0]))
try:
    print(type(rows[0][0]))
except:
    print('--')
import json
with open('data.json', 'w') as f:
    json.dump(rows[0][0], f)
cursor.close()
conn.close()


#embedding part
model = SentenceTransformer("BAAI/bge-m3")
t1 = time.time()
stories = [
    'Quỹ xem concert Anh trai vượt ngàn chông gai được thành lập nhằm tạo cơ hội cho những người yêu nghệ thuật, đặc biệt là những cá nhân có hoàn cảnh khó khăn, được thưởng thức những tiết mục âm nhạc đầy cảm hứng. Với sự hỗ trợ tài chính từ các nhà hảo tâm và doanh nghiệp, quỹ đảm bảo việc mua vé, phương tiện di chuyển và các dịch vụ hỗ trợ khác cho khán giả. Buổi hòa nhạc với chủ đề “Vượt qua mọi thử thách” không chỉ đem đến những trải nghiệm âm nhạc đậm chất nghệ thuật mà còn lan tỏa thông điệp về lòng kiên trì, sức mạnh tinh thần vượt qua gian nan. Qua đó, quỹ góp phần gắn kết cộng đồng và khơi dậy niềm tin vào khả năng vươn lên của mỗi cá nhân.',
    'Quỹ xem buổi hòa nhạc Anh trai say hi được thành lập với mục tiêu mang nghệ thuật đến gần hơn với mọi người, đặc biệt là những tầng lớp có điều kiện kinh tế hạn chế. Thông qua việc hỗ trợ mua vé và các chi phí liên quan, quỹ giúp khán giả có cơ hội trải nghiệm một sự kiện âm nhạc sôi động, tràn đầy năng lượng và thông điệp “say hi” thân thiện, cởi mở. Sự kiện không chỉ là dịp thưởng thức các tiết mục đặc sắc mà còn là nơi kết nối, giao lưu giữa các thế hệ và cộng đồng yêu nhạc, góp phần xây dựng một không gian văn hóa đa dạng và gắn kết.',
    'Tech Club Championship là sự kiện giao lưu, thi đua dành cho các câu lạc bộ công nghệ, nơi các đội thi có cơ hội thể hiện tài năng, sáng tạo và chia sẻ kinh nghiệm trong lĩnh vực công nghệ. Chương trình bao gồm các cuộc thi, workshop và các phiên thảo luận chuyên sâu, tạo điều kiện cho các thành viên được học hỏi, trao đổi và khám phá những ý tưởng đột phá. Sự kiện còn là cầu nối giữa sinh viên, chuyên gia và các doanh nghiệp hàng đầu, mở ra cơ hội hợp tác và phát triển nghề nghiệp. Qua đó, Tech Club Championship góp phần thúc đẩy sự đổi mới sáng tạo và nâng cao trình độ kỹ thuật của cộng đồng công nghệ trẻ.',
    'Chương trình hỗ trợ giúp đỡ đội ngũ phát triển được khởi xướng nhằm tạo điều kiện tối ưu cho các nhóm nghiên cứu, phát triển sản phẩm và dự án công nghệ. Bằng cách cung cấp nguồn lực tài chính, các khóa đào tạo chuyên sâu và hỗ trợ kỹ thuật, chương trình giúp đội ngũ phát triển nhanh chóng khắc phục những khó khăn, nâng cao năng lực sáng tạo và thực thi ý tưởng. Qua đó, không chỉ góp phần đưa các dự án công nghệ tiên phong ra thị trường mà còn tạo ra một môi trường làm việc chuyên nghiệp, khuyến khích sự hợp tác và chia sẻ kiến thức giữa các thành viên. Sự hỗ trợ này được kỳ vọng sẽ thúc đẩy sự phát triển bền vững của ngành công nghệ trong nước.',
    'Quỹ hỗ trợ người vô gia cư được thành lập với mục tiêu cải thiện cuộc sống cho những người đang sống trong điều kiện thiếu thốn và rơi vào hoàn cảnh khó khăn. Thông qua việc cung cấp chỗ ở tạm thời, thực phẩm, quần áo và hỗ trợ y tế, quỹ giúp người vô gia cư có cơ hội khôi phục cuộc sống và hội nhập trở lại cộng đồng. Bên cạnh đó, các chương trình đào tạo nghề và hỗ trợ tâm lý được triển khai nhằm trang bị kỹ năng sống, tăng cường tự tin và khả năng tự lập cho người nhận hỗ trợ. Sự đóng góp từ các cá nhân, doanh nghiệp và tổ chức đã tạo nên một mạng lưới nhân văn rộng khắp, lan tỏa tinh thần sẻ chia và đồng cảm trong xã hội.',
    'Sự kiện giao lưu các câu lạc bộ sinh viên trên địa bàn Hà Nội được tổ chức nhằm tạo cơ hội kết nối, chia sẻ kinh nghiệm và khám phá những ý tưởng sáng tạo giữa các nhóm sinh viên đến từ nhiều trường đại học khác nhau. Chương trình bao gồm các hoạt động văn hóa, thể thao và học thuật, giúp các câu lạc bộ phát huy thế mạnh, học hỏi lẫn nhau và xây dựng mối quan hệ hợp tác bền vững. Qua đó, sự kiện không chỉ góp phần nâng cao kỹ năng mềm, tăng cường tinh thần đoàn kết mà còn khơi dậy niềm đam mê sáng tạo trong cộng đồng sinh viên, mở ra những hướng đi mới cho tương lai.',
    'Quỹ trao đổi sinh viên giữa các trường đại học được thiết lập nhằm thúc đẩy giao lưu học thuật và văn hóa, tạo điều kiện cho sinh viên trải nghiệm môi trường học tập mới và phương pháp giảng dạy tiên tiến. Thông qua hỗ trợ tài chính, học bổng và các chương trình trao đổi, sinh viên có cơ hội rèn luyện kỹ năng giao tiếp, làm việc nhóm và thích nghi với những thử thách đa dạng. Sự trao đổi không chỉ giúp nâng cao trình độ chuyên môn mà còn mở rộng tầm nhìn, góp phần xây dựng một cộng đồng học thuật đa dạng và gắn kết, hỗ trợ sự phát triển bền vững của nền giáo dục trong nước.',
    'Quỹ hỗ trợ trẻ em nghèo được thành lập với sứ mệnh tạo điều kiện cho các em vượt qua khó khăn về điều kiện sống và học tập. Thông qua việc cung cấp học bổng, đồ dùng học tập, và chăm sóc y tế, quỹ giúp trẻ em có cơ hội tiếp cận giáo dục chất lượng và phát triển toàn diện. Các chương trình của quỹ còn bao gồm các hoạt động ngoại khóa, tư vấn tâm lý và phát triển kỹ năng sống, góp phần xây dựng nền tảng vững chắc cho tương lai của các em. Qua đó, quỹ mong muốn mở ra một con đường mới đầy hy vọng cho những trẻ em có hoàn cảnh khó khăn.',
    'Quỹ trồng cây gây rừng hướng đến việc phục hồi hệ sinh thái và cải thiện chất lượng môi trường thông qua các dự án trồng cây quy mô lớn. Bằng cách huy động nguồn lực từ cộng đồng, doanh nghiệp và các tổ chức phi chính phủ, quỹ triển khai các chương trình trồng cây tại những khu vực bị xói mòn và suy thoái. Mỗi tán cây được trồng không chỉ góp phần tạo nên bức tường xanh bảo vệ đất đai mà còn giúp giảm thiểu tác động của biến đổi khí hậu, tạo nên một môi trường sống lành mạnh cho con người và động thực vật.',
    'Quỹ hỗ trợ cuộc thi hackathon được xây dựng nhằm khuyến khích sự sáng tạo và tinh thần đổi mới trong cộng đồng công nghệ. Quỹ tài trợ cung cấp nguồn lực về kinh phí, cơ sở hạ tầng và hỗ trợ kỹ thuật cho các đội thi, giúp họ có điều kiện tối ưu để phát huy ý tưởng đột phá. Ngoài ra, sự kiện hackathon còn tạo cơ hội giao lưu, học hỏi giữa các sinh viên, chuyên gia và doanh nghiệp, từ đó thúc đẩy mối liên kết chặt chẽ và tạo nên những giải pháp công nghệ tiên tiến cho các vấn đề thực tiễn.',
    'Quỹ hỗ trợ giúp đỡ hoàn cảnh khó khăn được thành lập nhằm mang lại sự hỗ trợ kịp thời cho những cá nhân, gia đình gặp khó khăn về kinh tế và xã hội. Qua các chương trình cấp cứu thực phẩm, hỗ trợ y tế, học tập và tạo việc làm, quỹ góp phần xóa tan bớt gánh nặng trong cuộc sống của người dân. Các hoạt động của quỹ được thực hiện thông qua sự hợp tác chặt chẽ giữa các tổ chức từ thiện, chính quyền địa phương và cộng đồng tình nguyện, tạo ra một mạng lưới hỗ trợ lan tỏa yêu thương và đồng cảm.',
    'Quỹ hỗ trợ trồng 1 triệu cây xanh đặt mục tiêu góp phần bảo vệ môi trường và cải thiện chất lượng không khí qua việc trồng cây trên diện rộng. Với sự chung tay của cộng đồng, doanh nghiệp và các tổ chức môi trường, dự án hướng đến việc tạo dựng những khu rừng xanh mát, duy trì đa dạng sinh học và giảm thiểu biến đổi khí hậu. Mỗi tán cây được trồng không chỉ là một bước tiến trong bảo vệ thiên nhiên mà còn mang lại cơ hội giáo dục về ý thức bảo vệ môi trường cho người dân địa phương.',
    'Quỹ cho cuộc thi lập trình quốc tế ICPC quốc gia được thành lập nhằm khuyến khích và phát triển tài năng lập trình trẻ. Thông qua việc hỗ trợ học bổng, trang thiết bị và tổ chức các khóa đào tạo chuyên sâu, quỹ tạo điều kiện cho các sinh viên thể hiện năng lực và tư duy sáng tạo trong lĩnh vực công nghệ thông tin. Các cuộc thi không chỉ là sân chơi cạnh tranh lành mạnh mà còn là nơi kết nối sinh viên với các chuyên gia, doanh nghiệp công nghệ hàng đầu, mở ra nhiều cơ hội hợp tác và phát triển sự nghiệp.',
    'Quỹ sách giáo khoa cho học sinh vùng núi được thành lập với mục tiêu xóa bỏ khoảng cách về cơ hội học tập giữa các vùng miền. Qua việc cung cấp sách giáo khoa và tài liệu học tập thiết yếu, quỹ góp phần nâng cao chất lượng giáo dục cho học sinh tại những khu vực khó khăn. Bên cạnh đó, quỹ còn tổ chức các chương trình bồi dưỡng kỹ năng cho giáo viên và học sinh, tạo ra môi trường học tập đầy đủ, khuyến khích sự sáng tạo và phát triển bền vững của thế hệ trẻ vùng núi.',
    'Quỹ trồng rừng phòng hộ hướng tới việc bảo vệ đất đai và giảm thiểu thiên tai như lũ lụt, xói mòn thông qua các dự án trồng rừng bảo vệ. Bằng cách kết hợp kiến thức khoa học với kinh nghiệm thực tiễn của cộng đồng địa phương, quỹ triển khai các chương trình trồng cây tại các khu vực dễ bị thiên tai. Mỗi khu rừng phòng hộ không chỉ giúp ổn định môi trường mà còn tạo ra một không gian sinh thái đa dạng, góp phần nâng cao ý thức bảo vệ thiên nhiên cho cộng đồng.',
    'Quỹ hỗ trợ phát triển Trí tuệ Nhân tạo được thành lập nhằm thúc đẩy nghiên cứu, đổi mới và ứng dụng công nghệ AI vào giải quyết các vấn đề thực tiễn. Thông qua việc tài trợ dự án, cấp học bổng và tổ chức hội thảo chuyên đề, quỹ góp phần xây dựng một cộng đồng chuyên gia AI vững mạnh và tiên phong. Các dự án được hỗ trợ không chỉ mang lại những giải pháp công nghệ hiện đại mà còn tạo ra những bước tiến vượt bậc trong việc cải thiện chất lượng cuộc sống, từ y tế, giáo dục cho đến an ninh mạng và phát triển kinh tế số.'
]
embeddings = model.encode(sentences)

similarities = model.similarity(embeddings, embeddings)
print(similarities.shape)
print('time needed: ', time.time() - t1)