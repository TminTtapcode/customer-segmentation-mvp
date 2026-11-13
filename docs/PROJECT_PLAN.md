# Kế hoạch MVP — RFM + Engagement

**Cập nhật:** 13/11/2026 (Asia/Bangkok). **Trạng thái thật:** xem `PROGRESS.md`.
**Trạng thái hiện tại:** P2-T1 PASS, PR #6 đã merge main; P2-T2 **READY FOR STUDENT REVIEW** sau khi quét đủ bốn CSV. Từ task này ưu tiên notebook, CSV tổng hợp và hình đơn giản, giữ kiểm tra quan trọng; chưa làm sạch hoặc triển khai P2-T3. RQ/F0/F1/H1–H3 và thiết kế cải tiến giữ nguyên.

## 1. Mục tiêu, câu hỏi và phạm vi

Đề tài: Phân khúc khách hàng thương mại điện tử bằng K-Means dựa trên mô hình RFM mở rộng với đặc trưng tương tác website. Dự án độc lập cho nhóm hai sinh viên, ưu tiên đơn giản, dễ giải thích và kiểm chứng theo CRISP-DM — quy trình hiểu nghiệp vụ, hiểu/chuẩn bị dữ liệu, mô hình hóa, đánh giá và trình diễn.

Mục tiêu là cải thiện khả năng phân khúc bằng lựa chọn đặc trưng, tiền xử lý phù hợp và bổ sung tương tác website để hỗ trợ marketing. Trình tự: F0 cơ sở → hạn chế có bằng chứng → đề xuất → thực nghiệm → đánh giá → hỗ trợ quyết định. So sánh F0/F1 là cách kiểm chứng, không mặc định F1 thắng. Giữ nguyên ba câu hỏi đã nghiệm thu:

- RQ1: Dữ liệu REES46 cho thấy những đặc điểm gì về hành vi mua hàng và tương tác website?
- RQ2: Bổ sung Engagement vào RFM có giúp phân biệt những hành vi khách hàng mà RFM truyền thống chưa thể hiện rõ không?
- RQ3: Các phân khúc khách hàng có đặc điểm gì và có thể gợi ý những định hướng marketing nào? Đây là gợi ý mô tả, chưa có bằng chứng hiệu quả chiến dịch hay quan hệ nhân quả.

P1-T1 xác định vấn đề, mục tiêu, phạm vi và phương pháp dự kiến tại REPORT mục 1; bảng kế hoạch ba câu hỏi ở mục 2. Sổ tay phần 13 giải thích thuật ngữ, hai ví dụ và ba câu hỏi tự kiểm tra. Chưa có kết quả thực nghiệm trả lời các RQ.

**Bắt buộc:** REES46; audit làm sạch, EDA; F0 gồm R/F/M và F1 thêm sessions_30d/views_30d; K-Means K=2–6; so sánh Silhouette, Davies–Bouldin, cluster profiles — hồ sơ cụm; bốn notebook Colab có giải thích/output; Streamlit nhỏ; hai tài liệu tích lũy; PowerPoint cuối kỳ 7 slide (trong khoảng 5–8).

**Ngoài phạm vi:** React, FastAPI, PostgreSQL, IVRE integration, decision engine, campaign execution, auth, streaming, Docker/Kubernetes, MLflow/Airflow/CI phức tạp, surrogate, clustering non-buyers, nhiều thuật toán, tự chọn hàng chục feature. Chưa thêm CVR/AOV/Category Breadth/Brand Diversity; không triển khai các thí nghiệm mở rộng trong MVP chính.

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
| P1-T3 | Đọc nghiên cứu RFM-B | P1-T2 PASS | PASS (Student Verified) theo yêu cầu P1-T4; PR #4 đã merge, nội dung nghiên cứu giữ nguyên |
| P1-T4 | Thiết kế cải tiến và lý do chọn biến | P1-T3 PASS | PASS (Student Verified); PR #5 đã merge, Phase 1 CLOSED; chưa chứng minh giả thuyết |
| P2-T1 | Schema | P1 đã đóng/bàn giao main | PASS (Student Verified): người dùng xác nhận sau review; header/mẫu đủ bốn tháng, 4.000 dòng, exit 0. Chưa kiểm tra chất lượng toàn bộ hoặc tính hash toàn raw tháng 12 |
| P2-T2 | Chất lượng dữ liệu | P2-T1 PASS | READY FOR STUDENT REVIEW: 16.536.158 event, missing theo cột/tháng/loại, so khóa 7/9, giá/ID/session/time và hash tháng 12; hai CSV/bốn hình/một manifest, chưa chọn policy |
| P2-T3 | Cleaning policies | P2-T2 | Chốt dedup 7/9 trường, buyer/price/session/rounding; chứng minh ảnh hưởng |
| P2-T4 | Observation Parquet | P2-T3 | Artifact có manifest/hash/schema; không future; bảo toàn grain/cohort |
| P3-T1 | EDA event/customer | P2 | Bảng/biểu đồ có câu hỏi và mẫu số rõ |
| P3-T2 | Phân phối hành vi | P3-T1 | Phân phối, outliers và mô tả buyers/non-buyers |
| P3-T3 | EDA findings | P3-T2 | Kết luận có nguồn và giới hạn, không nhân quả |
| P4-T1 | RFM | P3 | Công thức, bảng tính tay và đối soát nguồn |
| P4-T2 | Engagement | P4-T1 | sessions_30d/views_30d đúng recent window và khóa |
| P4-T3 | Customer feature table | P4-T2 | Cohort rõ, đủ năm cột, không NULL/inf sai quy tắc |
| P4-T4 | Transform / scale | P4-T3 | Chọn biến đổi có căn cứ phân phối, ghi trước cột/rule; scaler riêng F0/F1, cùng quy tắc cho RFM chung |
| P5-T1 | F0 baseline và hạn chế | P4 | K=2–6, cấu hình/seed/metrics/time/RSS thật; ghi hạn chế có bằng chứng và giả thuyết trước F1. Nếu cần, kiểm tra một thay đổi tiền xử lý trong cùng F0/cohort/K/seed, lưu trước/sau |
| P5-T2 | F1 kiểm chứng đề xuất | P5-T1 được nghiệm thu, quy trình đã ghi | Cùng buyers/cutoff/cleaning/K-Means, K=2–6 và seed/cấu hình chung; thêm đúng hai biến, fit scaler riêng, không tái dùng kết quả 7D |
| P5-T3 | Đánh giá cải tiến | P5-T2 | Bảng các mặt được/mất: Silhouette/DBI/ổn định/cỡ cụm/hồ sơ năm biến gốc/khác biệt hành vi/hỗ trợ marketing/tài nguyên; có thể giữ F0 |
| P5-T4 | Chọn/lưu model | P5-T3 | Lý do trước đánh giá hồi cứu; model + preprocessing có version |
| P6-T1 | Cluster profiles | P5 | Phân bố/cỡ nhóm và thống kê đơn vị gốc |
| P6-T2 | Marketing Decision Support | P6-T1 | Cụm → đặc điểm quan sát → mục tiêu marketing → hành động gợi ý → căn cứ → KPI → hạn chế; chỉ hỗ trợ quyết định, chưa chứng minh hiệu quả chiến dịch |
| P6-T3 | Streamlit | P6-T2 | Hiển thị hồ sơ và bảng bảy cột P6-T2, ghi Research Demo / REES46, không raw IDs; không gửi chiến dịch/decision engine |
| P6-T4 | Kiểm chứng app | P6-T3 | Đối soát hiển thị với artifact, chạy thật |
| P7-T1 | Báo cáo học thuật | P6 | REPORT đầy đủ từ evidence |
| P7-T2 | Sổ tay bảo vệ | P7-T1 | LEARNING_GUIDE và bài tập/câu hỏi |
| P7-T3 | PowerPoint 7 slide | P7-T2 | Nội dung trung thực, số liệu truy nguyên |
| P7-T4 | Tái lập/demo cuối | P7-T3 | Chạy lại trên môi trường sạch, checklist nghiệm thu |

**Cách làm mỗi task:** mục tiêu → phương pháp/lý do → code → kết quả → giải thích → kiểm tra phù hợp → cập nhật ngắn → nghiệm thu. Ưu tiên notebook và bảng/hình chính; không lập lại nhiều vòng audit hoặc lưu file verification cho mọi phép kiểm. Giữ đối chiếu dòng/missing/duplicate/khóa/công thức cần thiết và mọi bằng chứng đã nghiệm thu.

Thiết kế P1-T4 nằm ở REPORT phần 5–11, mục A–G: lý do năm biến, H1–H3, kiểm soát tiền xử lý/F0/F1, tám nhóm tiêu chí và kế hoạch biểu đồ Phase 3–6. Cấu hình dự kiến chung: K=2–6, seed [0,21,42], n_init=10; các lựa chọn này chưa phải kết quả tối ưu. Chưa chốt cột log, cleaning policy hoặc K cuối. Thay đổi có lý do phải ghi trước khi chạy task tương ứng; không chọn tiêu chí sau khi xem F1.

## 4. Kiến trúc và tổ chức tối thiểu dự kiến

`REES46 observation → DuckDB → bảng khách hàng → F0/F1 + scikit-learn → profiles/metrics → Streamlit`.

- `notebooks/`: 01 hiện có phần P0-T3 và P2-T2. Hướng tới 01_data_exploration, 02_data_preparation, 03_feature_engineering, 04_clustering; không tạo trước file chưa cần. Hồ sơ/demo có thể học trong notebook hiện hữu khi đến phase.
- `data/`: chỉ hướng dẫn/manifest được Git theo dõi; dữ liệu lớn để cục bộ/Drive riêng.
- `results/`: audit, metrics, profiles, figures; bảng cá nhân không công khai.
- `model/` tạo khi cần lưu artifact ở P5; `app.py` chỉ tạo ở Phase 6. `tests/` hiện có kiểm tra helper đường dẫn bằng thư viện chuẩn.
- `scripts/` có hai script audit cũ, helper `data_paths.py` và `verify_colab_notebook.py` để kiểm tra notebook local; không phải framework ETL.
- `docs/PROJECT_PLAN.md`, `PROGRESS.md` là quản lý công việc; `REPORT.md`, `LEARNING_GUIDE.md` là hai báo cáo văn xuôi.
- REPORT có năm phần trình bày chính, hướng tới khoảng năm trang Word A4/3–5 hình ở P7; phần chi tiết đã nghiệm thu giữ trong mục thu gọn, không xóa. LEARNING_GUIDE giải thích sâu và không giới hạn năm trang. Word cuối dùng Times New Roman 12, giãn dòng 1,15, lề 2–2,5 cm; chưa xuất Word ở P2.

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

Nhóm đã nghiệm thu Phase 0/Phase 1/P2-T1; PR #1–#6 đã merge. P2-T2 chỉ đo chất lượng và đang chờ nghiệm thu, chưa giải quyết cleaning policy hoặc chứng minh cải tiến mô hình. Không làm lại task cũ, tự chuyển P2-T3 hoặc đóng Phase 2.
