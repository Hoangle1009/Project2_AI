Wumpus World Project
1. Cài đặt môi trường

Yêu cầu Python >= 3.9

Cài đặt thư viện cần thiết:

pip install -r requirements.txt

2. Chạy demo

Trong project hỗ trợ 2 loại tác tử (agent):

Hybrid Agent → sử dụng A* và BFS để tìm đường đi tối ưu.

Random Agent → chọn hành động ngẫu nhiên, không có chiến lược tối ưu.

=> Để chạy demo, dùng lệnh:

python main.py

3. Mô tả kết quả

Hybrid Agent: di chuyển có kế hoạch, tìm đường đi tối ưu bằng A*, kết hợp BFS khi cần, và tránh được nguy hiểm.

Random Agent: chọn bước đi ngẫu nhiên, dẫn đến đường đi vòng vèo hoặc có thể rơi vào hố.
