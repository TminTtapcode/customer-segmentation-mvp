# Notebooks — sổ thực hành Colab/Jupyter

Notebook hiện có: [01_data_exploration.ipynb](01_data_exploration.ipynb). **Phần 1–6** giữ nguyên 20 ô của P0-T3 đã nghiệm thu; **phần 7** nối thêm P2-T2 với bảng tổng hợp, bốn hình và code đọc kết quả. Ba ô code mới đã chạy bằng Python local, không chạy lại raw trong notebook; chưa xác nhận lần P2-T2 trên Colab. Không có K-Means hoặc feature mới.

Dự kiến bốn notebook gọn: 01_data_exploration, 02_data_preparation, 03_feature_engineering, 04_clustering. Chỉ tạo khi đến task, đã tạo [02_data_preparation.ipynb](02_data_preparation.ipynb) khi đến P2-T3; chưa tạo 03/04. Mỗi phần có câu hỏi, lý do, code, output, giải thích, kiểm tra và giới hạn; hình đơn giản, màu trung tính, có nhận xét.

Phần P0-T3 chạy độc lập theo [README](../README.md#mở-và-chạy-notebook-p0-t3). Phần 7 cần bản repo có results/p2_t2, chạy từ root repo hoặc notebooks; không cần raw để đọc bảng/hình. Nếu muốn quét lại, chuẩn bị bốn CSV rồi chủ động bật RUN_FULL_ASSESSMENT và dùng output mới. Không lưu đường dẫn cá nhân, credentials hoặc user IDs; có thể giữ output tổng hợp an toàn. Khi nghiệm thu trên Colab, mỗi người dùng bản sao riêng, khởi động lại và chạy từ đầu; không biến kiểm tra local thành bằng chứng Colab.

Với notebook 01, người sửa chính là **Thành viên 1**, người kiểm tra là **Thành viên 2** theo [quy trình cộng tác](../README.md#hai-thành-viên-cùng-làm-việc). Mỗi người dùng một bản Drive riêng; chỉ bản đã được chấp nhận và đưa vào GitHub main mới là phiên bản chính thức. Không tạo thêm notebook trong repo chỉ để lưu các bản thực hành cá nhân.

## Notebook 02 — chính sách làm sạch P2-T3

Notebook mới đọc results/p2_t3 bằng thư viện chuẩn, hiển thị số dòng, ảnh hưởng và schema. Cần bản repo đầy đủ; chạy được từ root hoặc notebooks. Nếu chỉ upload notebook lên Colab, cần clone repo/đổi cwd vào repo trước. RUN_POLICY=False mặc định; chỉ bật khi muốn quét lại bốn raw ở REES46_DATA_ROOT và chọn output mới. Không xuất Parquet chính thức. Người sửa chính **Thành viên 2**, người kiểm tra **Thành viên 1**; mỗi người dùng bản Drive riêng. Bốn ô code được kiểm chứng bằng Python local, chưa có xác nhận Colab mới.
