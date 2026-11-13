# Kế hoạch MVP — RFM + Engagement

**Cập nhật:** 13/11/2026 (Asia/Bangkok). **Trạng thái thật:** xem `PROGRESS.md`.
**Trạng thái hiện tại:** P1-T2 đã được hai sinh viên xác nhận PASS; chỉ thực hiện P1-T3, chờ nghiệm thu. Nền P0/P1-T1/P1-T2 đã có trên main. Chỉ đọc bài báo và cập nhật tài liệu, không thêm biến hay đổi F0/F1; vấn đề dữ liệu vẫn chờ Phase 2. P1-T4 chưa bắt đầu.

## 1. Mục tiêu, câu hỏi và phạm vi

Đề tài: Phân khúc khách hàng thương mại điện tử bằng K-Means dựa trên mô hình RFM mở rộng với đặc trưng tương tác website. Dự án độc lập cho nhóm hai sinh viên, ưu tiên đơn giản, dễ giải thích và kiểm chứng theo CRISP-DM — quy trình hiểu nghiệp vụ, hiểu/chuẩn bị dữ liệu, mô hình hóa, đánh giá và trình diễn.

- RQ1: Dữ liệu REES46 cho thấy những đặc điểm gì về hành vi mua hàng và tương tác website?
- RQ2: Bổ sung Engagement vào RFM có giúp phân biệt những hành vi khách hàng mà RFM truyền thống chưa thể hiện rõ không?
- RQ3: Các phân khúc khách hàng có đặc điểm gì và có thể gợi ý những định hướng marketing nào? Đây là gợi ý mô tả, chưa có bằng chứng hiệu quả chiến dịch hay quan hệ nhân quả.

P1-T1 xác định vấn đề, mục tiêu, phạm vi và phương pháp dự kiến tại REPORT mục 1; bảng kế hoạch ba câu hỏi ở mục 2. Sổ tay phần 13 giải thích thuật ngữ, hai ví dụ và ba câu hỏi tự kiểm tra. Chưa có kết quả thực nghiệm trả lời các RQ.

**Bắt buộc:** REES46; audit làm sạch, EDA; F0 gồm R/F/M và F1 thêm sessions_30d/views_30d; K-Means K=2–6; so sánh Silhouette, Davies–Bouldin, cluster profiles — hồ sơ cụm; bốn notebook Colab có giải thích/output; Streamlit nhỏ; hai tài liệu tích lũy; PowerPoint cuối kỳ 7 slide (trong khoảng 5–8).

**Ngoài phạm vi:** React, FastAPI, PostgreSQL, IVRE integration, decision engine, campaign execution, auth, streaming, Docker/Kubernetes, MLflow/Airflow/CI phức tạp, surrogate, clustering non-buyers, nhiều thuật toán, tự chọn hàng chục feature. AOV proxy/Purchase Session Rate chỉ là ablation — thí nghiệm thêm/bớt biến — tùy chọn sau MVP chính.

## 2. Hợp đồng dữ liệu và thực nghiệm

| Nội dung | Thiết kế / điều kiện |
|---|---|
| Dataset | REES46 Cosmetics 2019–2020; nguồn Kaggle được dự án cũ khai báo, điều khoản tải/chia sẻ phải kiểm tra ở P1/P2 |
| Observation | `[2019-10-01 00:00:00 UTC, 2020-02-01 00:00:00 UTC)` |
| Recent 30d | `[2020-01-02 00:00:00 UTC, 2020-02-01 00:00:00 UTC)` |
| Grain — đơn vị một dòng | Event ở nguồn; user ở feature table; session theo `(user_id, session_id)` |
| Frequency | Distinct purchase sessions theo policy hợp lệ; không suy order_id |
| Monetary | Tổng purchase-event price hợp lệ; không phải net GMV, currency chưa xác minh |
| Buyers | Chỉ tập đủ RFM; cần chốt policy price/session tại P2; không gán recency giả cho non-buyers |
| F0 / F1 | `[recency_days, frequency, monetary]` / F0 + `[sessions_30d, views_30d]` |
| Thực nghiệm | Cùng population buyers; fit scaler riêng; K=2–6; seed/cấu hình/preprocessing được ghi lại ở P5 |
| Chọn mô hình | Đúng cutoff/grain/cohort trước; sau đó trade-off matrix giữa chất lượng, business utility, giải thích, runtime, sampled RSS; không cộng điểm trọng số tùy ý |
| February | Đã được xem trong dự án cũ. Nếu dùng: phân tích hồi cứu, không phải untouched holdout, không dùng để chọn mô hình |
| Công khai | Demo ghi `Research Demo / REES46`; chỉ số tổng hợp, không xuất raw user IDs |

Silhouette/DBI thuộc đánh giá phân cụm, không phải classification accuracy. F0/F1 có không gian khoảng cách khác nhau nên không xếp hạng chỉ bằng một điểm Silhouette. Không kế thừa K=4 hay metrics/labels/scaler của mô hình 7D cũ.

## 3. Checklist task và dependencies

Tất cả dependency bao gồm nghiệm thu task trước. Lịch chi tiết chưa được ấn định; không kế thừa lịch/phase của dự án cũ.

| Task | Công việc | Phụ thuộc | Sản phẩm / gate |
|---|---|---|---|
| P0-T1 | Audit Existing Data Artifacts | Đọc nguồn cũ | Được sinh viên chấp nhận có điều kiện; inventory/log giữ nguyên, các vấn đề dữ liệu còn mở |
| P0-T2 | Khởi tạo cấu trúc tối thiểu | P0-T1 được nghiệm thu | Đã nghiệm thu PASS theo báo cáo Codex: 6/6 tests, 15/15 checks; sinh viên chưa chạy lại local |
| P0-T3 | Môi trường Colab | P0-T2 | PASS (Student Verified): người dùng xác nhận hai sinh viên đã trực tiếp nghiệm thu trên Colab/Drive; bằng chứng local của Codex giữ riêng |
| P0-T4 | Hoàn thiện quy trình cộng tác nhóm | P0-T3 | Nhóm đã xác nhận nghiệm thu/đóng Phase 0; PR #1 đã merge main |
| P1-T1 | Vấn đề, mục tiêu và câu hỏi nghiên cứu | P0 được nhóm nghiệm thu; nền có đủ file P0 | PASS theo xác nhận người dùng; PR #2 đã merge main |
| P1-T2 | RFM truyền thống tham khảo | P1-T1 PASS | PASS theo xác nhận hai sinh viên; PR #3 đã merge main |
| P1-T3 | Đọc nghiên cứu RFM-B | P1-T2 PASS | REPORT mục 3.5–3.9, LEARNING_GUIDE phần 15: định nghĩa, kết quả tác giả, giới hạn và liên hệ Cosmetics; READY FOR STUDENT REVIEW |
| P1-T4 | Feature rationale | P1-T3 | Lý do chọn năm biến, liên hệ RQ2, chưa tự thêm biến |
| P2-T1 | Schema | P1 | Kiểu dữ liệu/timezone/khóa được đọc và xác minh |
| P2-T2 | Chất lượng dữ liệu | P2-T1 | Missing, duplicates, giá, biên thời gian và ảnh hưởng metric |
| P2-T3 | Cleaning policies | P2-T2 | Chốt dedup 7/9 trường, buyer/price/session/rounding; chứng minh ảnh hưởng |
| P2-T4 | Observation Parquet | P2-T3 | Artifact có manifest/hash/schema; không future; bảo toàn grain/cohort |
| P3-T1 | EDA event/customer | P2 | Bảng/biểu đồ có câu hỏi và mẫu số rõ |
| P3-T2 | Phân phối hành vi | P3-T1 | Phân phối, outliers và mô tả buyers/non-buyers |
| P3-T3 | EDA findings | P3-T2 | Kết luận có nguồn và giới hạn, không nhân quả |
| P4-T1 | RFM | P3 | Công thức, bảng tính tay và đối soát nguồn |
| P4-T2 | Engagement | P4-T1 | sessions_30d/views_30d đúng recent window và khóa |
| P4-T3 | Customer feature table | P4-T2 | Cohort rõ, đủ năm cột, không NULL/inf sai quy tắc |
| P4-T4 | Transform / scale | P4-T3 | Ví dụ giải thích; preprocessing tái lập, tách F0/F1 |
| P5-T1 | F0 baseline | P4 | K=2–6, config/seed/metrics/time/RSS thực |
| P5-T2 | F1 experiment | P5-T1 | Cùng buyers và protocol, thêm đúng hai biến |
| P5-T3 | So sánh | P5-T2 | Trade-off matrix và profiles trên chỉ số chung |
| P5-T4 | Chọn/lưu model | P5-T3 | Lý do trước đánh giá hồi cứu; model + preprocessing có version |
| P6-T1 | Cluster profiles | P5 | Phân bố/cỡ nhóm và thống kê đơn vị gốc |
| P6-T2 | Diễn giải nghiệp vụ | P6-T1 | Gợi ý có bằng chứng, không hứa hiệu quả marketing |
| P6-T3 | Streamlit | P6-T2 | App nhỏ, nguồn/dataset rõ, không raw IDs |
| P6-T4 | Kiểm chứng app | P6-T3 | Đối soát hiển thị với artifact, chạy thật |
| P7-T1 | Báo cáo học thuật | P6 | REPORT đầy đủ từ evidence |
| P7-T2 | Sổ tay bảo vệ | P7-T1 | LEARNING_GUIDE và bài tập/câu hỏi |
| P7-T3 | PowerPoint 7 slide | P7-T2 | Nội dung trung thực, số liệu truy nguyên |
| P7-T4 | Tái lập/demo cuối | P7-T3 | Chạy lại trên môi trường sạch, checklist nghiệm thu |

**Gate mỗi task:** input thật → implement đúng phạm vi → lệnh/log thật → kiểm chứng độc lập → giải thích → cập nhật hai tài liệu/progress → nghiệm thu. P0-T1 thành công không đồng nghĩa P0 hoặc P2 đã PASS.

## 4. Kiến trúc và tổ chức tối thiểu dự kiến

`REES46 observation → DuckDB → bảng khách hàng → F0/F1 + scikit-learn → profiles/metrics → Streamlit`.

- `notebooks/`: hiện có `01_data_exploration.ipynb`, ở P0-T3 chỉ thiết lập môi trường/đọc thử bảng buyer; chưa EDA. Các phần phân tích, features/preprocessing, F0/F1 và profiles/demo chỉ làm khi đến task.
- `data/`: chỉ hướng dẫn/manifest được Git theo dõi; dữ liệu lớn để cục bộ/Drive riêng.
- `results/`: audit, metrics, profiles, figures; bảng cá nhân không công khai.
- `model/` tạo khi cần lưu artifact ở P5; `app.py` chỉ tạo ở Phase 6. `tests/` hiện có kiểm tra helper đường dẫn bằng thư viện chuẩn.
- `scripts/` có hai script audit cũ, helper `data_paths.py` và `verify_colab_notebook.py` để kiểm tra notebook local; không phải framework ETL.
- `docs/PROJECT_PLAN.md`, `PROGRESS.md` là quản lý công việc; `REPORT.md`, `LEARNING_GUIDE.md` là hai báo cáo văn xuôi.

## 5. Hướng dữ liệu cho máy khác / Colab — Design choice

Chưa copy dữ liệu, chưa cấu hình hoặc chạy Colab ở P0-T1. Đề xuất biến môi trường `REES46_DATA_ROOT` trỏ tới một thư mục riêng chứa `cleaned/observation_events.parquet`, tùy chọn `features/buyer_features.parquet`, và `raw/` để tái dựng sau này. Không đưa các file này lên GitHub public.

- Local ví dụ: thư mục dữ liệu ngoài repo, không phụ thuộc ổ D.
- Drive ví dụ: `/content/drive/MyDrive/datasets/rees46`.
- Runtime Colab đề xuất: copy observation đã được chấp nhận sang `/content/rees46/cleaned/observation_events.parquet` để query; phải kiểm tra SHA256 sau copy. Chưa benchmark tốc độ Drive/local.
- Gói tối thiểu mang sang máy khác: code commit/version + observation Parquet + dòng manifest tương ứng (hash/schema/rows) + policy đã chốt. Tái dựng raw→clean còn chờ P2; artifact cũ chỉ giúp audit hiện tại, chưa chứng minh rebuild đầy đủ.
- Không tạo hoặc fit lại model 7D cũ để khởi động MVP. Không đem February vào input feature.

## 6. Quyết định tổ chức ở P0-T2 — Design choice

- Giữ toàn bộ 16 tệp đã có trước P0-T2, bao gồm sáu tệp bằng chứng P0-T1. Sửa trạng thái trong tài liệu; không ghi đè số liệu audit lịch sử.
- `requirements.txt` là danh sách bảy dependency trực tiếp của MVP, chưa khóa phiên bản vì chưa xác minh một môi trường cài mới. `requirements-audit.txt` giữ riêng pin DuckDB đã dùng ở P0-T1, không phải danh sách chuẩn cho toàn MVP.
- Không khai báo PyArrow trực tiếp ở bước này; đọc/ghi Parquet dự kiến đi qua DuckDB. Lỗi import Windows cũ vẫn là giới hạn, không sửa chính sách máy.
- Tạo `data/README.md`, `notebooks/README.md`, `scripts/data_paths.py`, `tests/test_data_paths.py` vì có hướng dẫn/kiểm tra thực tế; không tạo `.gitkeep`, notebook rỗng, model hoặc app giả.
- Helper tính đường dẫn tương đối từ root repository ngay cả khi terminal chạy ở thư mục khác. Nếu `REES46_DATA_ROOT` tuyệt đối thì giữ root bên ngoài; không tự tạo/mount/copy dữ liệu.
- P0-T2 chỉ xác minh cấu trúc, đường dẫn, Git ignore/staging và bảo toàn nguồn/tài liệu. Cài đặt/chốt phiên bản, mount Drive và thực thi Colab còn thuộc P0-T3.

## 7. Điều kiện hoàn thành P0-T3

- Một notebook, sáu phần có giải thích và ba câu hỏi tự kiểm tra; chỉ cài DuckDB nếu thiếu, không cài toàn bộ thư viện chưa dùng.
- Dùng `buyer_features.parquet` nhỏ đã kiểm kê, không yêu cầu upload toàn bộ events; bảng vẫn là ứng viên dữ liệu.
- Local phải đọc/validate notebook và chạy được các ô không phụ thuộc Drive; thiếu dữ liệu phải dừng rõ ràng.
- Không in user IDs, lưu credentials, upload dữ liệu hoặc đổi quyền chia sẻ tự động. Không EDA, tạo đặc trưng hoặc huấn luyện mô hình.
- Kiểm tra local không đủ để PASS. P0-T3 đã được người dùng xác nhận hai sinh viên nghiệm thu trên Colab/Drive ngày 13/11/2026; không bổ sung phiên bản, thời gian chạy hay kết quả Colab chưa được gửi. Quy tắc khởi động lại/chạy từ đầu tiếp tục áp dụng cho các phiên bản sau.

## 8. Hoàn thành Phase 0

Nhóm đã nghiệm thu P0-T4/đóng Phase 0, P1-T1 và P1-T2 PASS. PR #1/#2/#3 đã merge; kết quả kiểm tra và commit bàn giao nằm trong PROGRESS. Không làm lại P0 hoặc đổi kết quả cũ. Vấn đề dữ liệu tiếp tục xử lý ở Phase 2, không tự ghi đã giải quyết. Lượt hiện tại chỉ làm P1-T3 rồi dừng chờ nghiệm thu; không tự chuyển P1-T4.
