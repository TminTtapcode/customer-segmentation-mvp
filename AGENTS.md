# Quy tắc làm việc — Customer Segmentation MVP

## Phạm vi và cách làm

- Trao đổi và tài liệu bằng tiếng Việt; thuật ngữ Anh đi kèm giải thích.
- Dự án độc lập, đơn giản cho nhóm hai sinh viên. Đọc `docs/PROJECT_PLAN.md`, `docs/PROGRESS.md`, hai tài liệu tích lũy và file liên quan trước khi sửa.
- Chỉ làm **một task mỗi lần**: mục tiêu → phương pháp/lý do → code → kết quả → giải thích → kiểm tra phù hợp → cập nhật ngắn → nghiệm thu. Đi thẳng vào kế hoạch đã chấp nhận, không lập lại nhiều vòng audit/kế hoạch. Dừng chờ sinh viên, không tự chuyển task/phase.
- Sau mỗi task: thực hiện → giải thích kiến thức → chạy kiểm tra phù hợp → cập nhật REPORT, LEARNING_GUIDE và PROGRESS khi có nội dung liên quan → dừng để sinh viên nghiệm thu. Không chạy lại phân tích chỉ vì sửa tài liệu.
- Trạng thái hiện hành nằm tại `docs/PROGRESS.md`. Không kế thừa phase hoặc PASS của dự án cũ.
- Không xóa, ghi đè hoặc sửa `customer-analytics-antigravity`, `CustomerSegmentation`, IVRE hay FashionStore. Nguồn cũ chỉ đọc; kết quả audit ghi trong repo MVP.
- Hai báo cáo văn xuôi tích lũy duy nhất: `docs/REPORT.md` và `docs/LEARNING_GUIDE.md`. Số liệu/log lưu CSV/JSON dưới `results/`.
- Notebook là nơi học chính: code dễ đọc, bảng/hình tổng hợp thật và nhận xét. Script chỉ tách logic cần chạy lại; hàm có một trách nhiệm, không lặp code hoặc thêm tầng xử lý không cần thiết. Không viết comment diễn giải lại từng dòng.
- Kết quả mới ưu tiên CSV nhỏ, PNG cần dùng và Parquet cho dữ liệu lớn ngoài GitHub. JSON chỉ khi cần cấu hình/manifest máy đọc. Không tạo verification/log riêng cho từng phép kiểm nhỏ; giữ đối chiếu số dòng, missing, duplicate, khóa và công thức quan trọng. Không xóa/chuyển lưu trữ bằng chứng cũ nếu nhóm chưa đồng ý.
- Dùng Matplotlib đơn giản, màu xám/xanh trung tính; chỉ nhấn màu khi có ý nghĩa. Mỗi hình trả lời một câu hỏi, có tiêu đề/trục/đơn vị và 1–3 câu nhận xét. Không mặc định phương án tốt nhất trước thực nghiệm; không thêm thuật toán/scaler/thí nghiệm chỉ vì chúng có trong danh sách biểu đồ gợi ý.
- Phân biệt kết quả đã kiểm tra, giả định, lựa chọn của nhóm, ví dụ minh họa và phần chưa kiểm tra xong. Dùng tiếng Việt tự nhiên để thể hiện sự khác nhau này; không bắt buộc gắn nhãn tiếng Anh vào từng đoạn.
- Không bịa số liệu, không lấy kết quả 7D làm kết quả 5D, không ghi PASS nếu chưa chạy và đọc log. Thiếu đầu vào thì báo rõ, không thay bằng dữ liệu giả.

## Hợp đồng nghiên cứu

- Chỉ dataset REES46 Cosmetics, sự kiện 2019–2020; nguồn ngoài chỉ tham khảo. Demo phải ghi `Research Demo / REES46`; không công khai raw user IDs.
- Observation `[2019-10-01T00:00:00Z, 2020-02-01T00:00:00Z)`. Engagement `[2020-01-02T00:00:00Z, 2020-02-01T00:00:00Z)`. Cắt theo timestamp từng event, kể cả session vắt cutoff.
- Chỉ buyers đủ RFM hợp lệ vào K-Means; non-buyers chỉ mô tả engagement. Không gán recency 0/999/∞ cho non-buyers.
- Frequency = distinct purchase sessions theo khóa `(user_id, session_id)`; không phải orders hay số purchase events. Monetary = tổng price của purchase hợp lệ, không phải net GMV; không tự xác nhận currency/quantity/refunds.
- Chính sách buyer, purchase hợp lệ, dedup và làm tròn phải được chốt tại P2 trước khi chấp nhận bảng feature cũ làm đầu vào nghiên cứu.
- February đã được xem trong dự án cũ: nếu sử dụng, gọi **retrospective analysis** (phân tích hồi cứu), không gọi untouched test set. Không dùng February để tạo features hay chọn mô hình.
- F0 = `recency_days, frequency, monetary`; F1 = F0 + `sessions_30d, views_30d`. Cùng buyers, scaler fit riêng từng feature set; thử K=2–6, ghi seed và cấu hình.
- K-Means là phân cụm, không phải supervised prediction. Silhouette/DBI/ARI không phải classification accuracy. So sánh chất lượng, profile nghiệp vụ, khả năng giải thích và tài nguyên; không tối ưu một số hay gán trọng số tùy ý.
- Khi benchmark: cùng input, phần cứng/config/threads/seed; `time.perf_counter`, sampled process RSS bằng psutil, ghi hạn chế lấy mẫu. DuckDB memory_limit không chặn cứng RSS.
- Gợi ý marketing chỉ là giả thuyết theo bằng chứng mô tả; không tuyên bố nhân quả hay hiệu quả chiến dịch đã xác minh.

## Công cụ và sản phẩm

- Python, DuckDB + Parquet cho event lớn; pandas sau tổng hợp. Chỉ thêm dependency có lý do. MVP dùng notebook Colab/Jupyter, scikit-learn, Matplotlib, Streamlit, joblib khi đến task tương ứng; không cần GPU.
- Không làm React/FastAPI/PostgreSQL/IVRE integration, decision engine, gửi chiến dịch, auth, streaming, Docker/Kubernetes, MLflow/Airflow, surrogate, non-buyer clustering hay nhiều thuật toán.
- Không tạo thư mục/file rỗng. Không load joblib cũ trong audit. Không chạy pipeline cũ vì có thể ghi đè nguồn.
- Notebook phải có Research Question / Theory / Why / Code / Output / Interpretation / Verification / Limitations. Giải thích kỹ thuật mới bằng ví dụ nhỏ trước dữ liệu thật.
- Sau mỗi phase, khởi động lại phiên chạy và chạy notebook từ ô đầu tới ô cuối để phát hiện biến còn sót từ phiên trước. Chỉ ghi đã chạy Colab khi có lần chạy thật trên Colab; kiểm tra local không thay thế xác nhận của hai sinh viên.
- Sổ tay giải thích khái niệm, lý do sử dụng, cách hoạt động/công thức, ví dụ tính tay, code, cách đọc/kiểm tra kết quả và lỗi thường gặp. Nêu lựa chọn khác và giới hạn khi cần; có 2–3 câu hỏi tự kiểm tra.
- Sau mỗi task, tóm tắt việc đã làm, kết quả thực tế, tài liệu đã sửa và vấn đề còn lại. Dùng mẫu chi tiết khi người dùng yêu cầu; không áp một mẫu dài cho mọi chỉnh sửa nhỏ.
- Người dùng đã xác nhận P0-T3 PASS (Student Verified), nghiệm thu P0-T4/đóng Phase 0, P1-T1…P1-T4, P2-T1 và P2-T2 PASS; PR #7 đã merge main tại b282e490. Phase 1 CLOSED về nghiên cứu/thiết kế, không có nghĩa H1–H3 đã được chứng minh. Không biến số liệu local thành chỉ số Colab hoặc tự điền câu trả lời sinh viên chưa gửi. Lịch sử bàn giao nằm trong PROGRESS.
- Lượt hiện tại **chỉ làm P2-T3 — Cleaning policies** sau xác nhận P2-T2 PASS của người dùng. Giữ bốn CSV raw chỉ đọc. Dùng đủ chín trường văn bản để loại trùng trước ép kiểu; product_id/category_id còn trong khóa, chỉ bỏ cùng brand/category_code ở projection cuối. Đề nghị output năm cột event_time/event_type/user_id/user_session/price; không DISTINCT lại sau projection. Kiểm chứng chính sách trên toàn observation trong database tạm, chỉ xuất bảng tổng hợp và một manifest; chưa tạo observation Parquet chính thức (P2-T4), bảng features/model hoặc đọc event February. Tài liệu và notebook 02 giải thích ảnh hưởng R/F/M/Sessions/Views. Không thêm dependency. Tạo PR nháp, READY FOR STUDENT REVIEW rồi dừng. `app.py` chỉ tạo tại Phase 6.

## Cộng tác giữa hai thành viên

- GitHub nhánh `main` giữ phiên bản mã nguồn chính thức sau nghiệm thu; nhánh task/PR là bản đề nghị bàn giao, chưa phải bản chính thức. Drive giữ dữ liệu riêng và các bản notebook thực hành.
- Mỗi notebook chỉ có một người sửa chính. Phân công notebook đang có nằm trong README; chỉ đổi vai trò sau khi hai bạn thống nhất và cập nhật dòng đó. Người kiểm tra chạy trên bản sao riêng, không sửa đè bản làm việc của người phụ trách.
- Bắt đầu từ cùng một phiên bản GitHub, ghi commit gốc và người đang phụ trách trong nhật ký task. Trước đồng bộ, xem Git status; không reset/force-push hoặc xóa bản chưa lưu để vượt xung đột.
- Sau khi chạy lại từ đầu, lưu bản thực hành có output an toàn trên Drive trước. Giữ kết quả tổng hợp cần đối chiếu trong results; không đưa user IDs, đường dẫn cá nhân hoặc credentials vào bản public.
- Sau khi sinh viên chấp nhận, người phụ trách tải notebook về, giữ nguyên code đã duyệt; có thể giữ bảng/hình tổng hợp an toàn, phải bỏ output chứa IDs, credentials hoặc thông tin riêng trước khi đưa lên nhánh GitHub. Người còn lại xem diff và kiểm tra trước main. Code hoặc input đổi sau nghiệm thu phải kiểm tra và nghiệm thu lại.
- Ghi nhận xác nhận của sinh viên riêng với bằng chứng Codex. Không tự điền tên người, link Drive, phiên bản runtime, thời gian chạy hoặc chỉ số chưa được cung cấp.

## Văn phong báo cáo phù hợp với nhóm sinh viên

- Viết tiếng Việt tự nhiên, câu ngắn, rõ ý và dựa trên kết quả thực tế. Báo cáo cần thể hiện nhóm hiểu cách làm và giới hạn của nghiên cứu, không viết như báo cáo kiểm toán doanh nghiệp.
- Có thể dùng “Nhóm sử dụng…”, “Mục đích của bước này là…”, “Kết quả cho thấy…”, “Nhóm nhận thấy…” khi đúng với bằng chứng. Việc mới dự kiến phải viết là dự kiến, không biến thành việc đã làm.
- Ưu tiên “Kết quả kiểm tra”, “Nhóm lựa chọn”, “Chưa kiểm tra xong”, “Nguồn gốc và quá trình xử lý dữ liệu”, “Bảng dữ liệu đặc trưng”, “Điều kiện hoàn thành bước”, “Khả năng chạy lại và nhận được kết quả tương ứng”. Hạn chế nhãn như Observed, Design choice, Pending validation, artifact lineage, verification gate, research-grade, production-ready hoặc sign-off approved.
- Giữ thuật ngữ cần học như RFM, Feature Engineering, EDA, StandardScaler, K-Means, Silhouette, Davies–Bouldin và Data Leakage; giải thích bằng tiếng Việt khi xuất hiện lần đầu. Không bỏ kiến thức chuyên môn chỉ để viết ngắn hơn.
- Không dùng “hoàn hảo”, “chính xác tuyệt đối”, “tối ưu nhất” hoặc “100% thành công” nếu chưa có bằng chứng. Không bịa số liệu; ví dụ minh họa phải được phân biệt với kết quả từ dữ liệu thật.
- **REPORT.md:** viết theo mục đích → dữ liệu sử dụng → cách thực hiện và lý do → kết quả → nhận xét → hạn chế. Chỉ giữ nội dung có ích cho báo cáo môn học. SHA256, danh sách file sửa, lệnh/log và kiểm tra phần mềm chi tiết đặt ở PROGRESS/results, trừ khi trực tiếp hỗ trợ kết luận nghiên cứu.
- Bản trình bày chính REPORT hướng tới năm phần/khoảng 5 trang Word A4 ở Phase 7, 3–5 hình quan trọng; Times New Roman 12, giãn dòng 1,15, lề 2–2,5 cm khi xuất Word. Không xuất Word ngay hoặc xóa nội dung đã nghiệm thu để ép số trang. Phần giải thích sâu để LEARNING_GUIDE; chi tiết nghiên cứu cũ có thể giữ trong mục thu gọn để không mất nội dung. Chưa có kết quả thì ghi đang thực hiện, không tạo chỉ số giả.
- **LEARNING_GUIDE.md:** giải thích gần gũi theo khái niệm → vì sao cần → cách hoạt động → ví dụ tính tay → code → đọc/kiểm tra kết quả → lỗi dễ mắc. Lý thuyết vừa đủ cho task, tránh lặp lại.
- **PROGRESS.md:** nhật ký ngắn gồm đã làm gì, kết quả, cách kiểm tra, vấn đề còn lại và bước tiếp theo; dẫn tới bằng chứng kỹ thuật khi cần.
- Khi sửa văn phong, giữ nguyên số liệu, bảng, nguồn dẫn, công thức, kết luận khoa học và vấn đề chưa giải quyết. Không sửa evidence trong results hoặc chạy lại ETL/features/model chỉ để đổi cách diễn đạt.
