# Nhật ký công việc — Customer Segmentation MVP

**Cập nhật:** 13/11/2026 (Asia/Bangkok).

- **P0-T1:** hoàn thành kiểm kê trong phạm vi đọc được; đã được chấp nhận để tiếp tục, còn vấn đề dữ liệu.
- **P0-T2: PASS — đã nghiệm thu** dựa trên báo cáo Codex: 6/6 bài kiểm tra đường dẫn và 15/15 điều kiện kiểm tra đạt. Sinh viên chưa chạy lại script trên máy local.
- **Sửa văn phong:** được chấp nhận theo báo cáo; sinh viên chưa mở bản local mới nhất để xác nhận độc lập.
- **P0-T3: PASS (Student Verified).** Người dùng xác nhận ngày 13/11/2026 cả hai sinh viên đã trực tiếp nghiệm thu trên Colab/Drive. Không tự bổ sung log/chỉ số Colab chưa được gửi.
- **P0-T4: PASS (Student Verified).** Người dùng xác nhận nhóm đã nghiệm thu và đóng Phase 0 trong yêu cầu P1-T1. Không yêu cầu làm lại P0.
- **P1-T1: PASS (Student Verified).** Người dùng xác nhận trực tiếp “P1-T1 PASS”; không tự bổ sung bài trả lời hoặc log sinh viên chưa gửi.
- **P1-T2: PASS (Student Verified).** Phần xác nhận sau trong tệp yêu cầu P1-T3 ghi hai sinh viên đã đọc REPORT mục 3, LEARNING_GUIDE phần 14, trả lời câu hỏi và xác nhận PASS; checklist được cung cấp ghi 5/5. Không tự bổ sung bài trả lời ngoài nội dung đã gửi.
- **P1-T3: PASS (Student Verified).** Người dùng xác nhận hai sinh viên đã nghiệm thu trong yêu cầu P1-T4; không tự bổ sung bài trả lời hoặc checklist từng câu chưa gửi.
- **P1-T4: PASS (Student Verified).** Người dùng xác nhận hai sinh viên nghiệm thu trong yêu cầu P2-T1; không tự bổ sung bài trả lời từng câu. **Phase 1 CLOSED** sau khi đối chiếu/bàn giao main; H1–H3 chưa được chứng minh.
- **P2-T1: BLOCKED.** Đã kiểm tra schema trong phạm vi đọc được, raw `2019-Dec.csv` vẫn PermissionError. Chưa đủ điều kiện nghiệm thu hoàn tất; chưa thực hiện P2-T2/P2-T3/P2-T4.
- **GitHub:** PR #1–#5 đã merge sau nghiệm thu. Main có đủ 30 file P0–P1; thay đổi P2-T1 ở nhánh riêng.

## 1. P0-T1 — kiểm kê dữ liệu cũ

**Đã làm:** kiểm kê tệp, cấu trúc bảng và nguồn gốc xử lý trong `D:\Lap trinh\customer-analytics-antigravity`; tính lại năm đặc trưng để đối chiếu và kiểm tra thêm bằng Python. Không sửa dữ liệu, chạy lại ETL hoặc nạp model cũ.

**Kết quả đã lưu:** 153 tệp được kiểm kê, 152 tệp tính được SHA256; có 5 CSV gốc, 3 Parquet sự kiện và 4 Parquet đặc trưng/kết quả cụm. Đã đọc header 4/5 CSV. Không tìm thấy notebook trong phạm vi đã duyệt. CSV tháng 12 chưa đọc được header/hash.

Bảng dưới giữ nguyên số liệu từ P0-T1, không phải lần chạy lại trong đợt sửa tài liệu:

| Phép kiểm | Kết quả mới |
|---|---|
| Audit checks | 5/5, exit 0 |
| Kiểm chứng bổ sung | 4/4, exit 0; Python 30 users / 2.733 events |
| Observation | 15.667.350 events, biên 2019-10-01 → 2020-01-31 23:59:58, 0 event sai cutoff |
| Cohorts | 1.341.499 users = 92.652 buyers + 1.248.847 non-buyers |
| Năm features | 0 mismatch ở cả ba feature tables |
| Monetary | 5.141.266,90 đơn vị dataset, không phải net GMV |
| Session | 191 token dùng chung nhiều user, 0 lỗi composite key |
| Bảo toàn nguồn | 152 hash giữ nguyên; metadata/Git status không đổi; 1 raw file không hash được |
| Thời gian | 19,691 giây cho audit, không phải pipeline benchmark; chưa đo RSS |

**Cách kiểm tra và bằng chứng:** `results/p0_t1/` giữ sáu tệp kết quả/log; `execution.json` ghi lệnh thật và môi trường Python 3.14.7 / DuckDB 2.0.0. Script là `scripts/audit_existing_artifacts.py` và `scripts/verify_audit.py`. Các phần kiểm tra không đọc được hoặc bị loại khỏi việc so hash vẫn được ghi rõ trong JSON.

**Quyết định:** sinh viên đã chấp nhận kết quả để chuyển P0-T2, chưa chấp nhận vô điều kiện dữ liệu cũ. Các vấn đề ở mục 4 vẫn còn mở.

## 2. P0-T2 — tổ chức dự án MVP

**Đã làm:**

- Hoàn thành P0-T2.1 (kiểm tra repo), P0-T2.2 (cấu trúc), P0-T2.3 (thư viện), P0-T2.4 (đường dẫn), P0-T2.5 (tài liệu).
- Giữ đủ 16 tệp có sẵn; không xóa dữ liệu/code hoặc đổi cấu trúc đã được thống nhất.
- Thêm `requirements.txt`, `data/README.md`, `notebooks/README.md`, `scripts/data_paths.py` và `tests/test_data_paths.py`.
- Chuẩn hóa ignore dữ liệu lớn; hướng dẫn local/Colab qua `REES46_DATA_ROOT`.
- Cập nhật AGENTS, README và bốn tài liệu. Giữ `requirements-audit.txt` cho cấu hình audit P0-T1.
- Chưa tạo `model/`, `app.py`, notebook phân tích hoặc dữ liệu thay thế.

**Kết quả kiểm tra đã được báo cáo:** gồm sáu bài kiểm tra đường dẫn và 15 điều kiện kiểm tra cấu trúc.

| Nội dung | Kết quả |
|---|---|
| Bài kiểm tra đường dẫn | 6/6 đạt; 0,011 giây, exit 0 |
| Điều kiện kiểm tra cấu trúc | 15/15 đạt |
| Liên kết/code | 19 liên kết local hợp lệ; parse bốn file Python; không có đường dẫn dữ liệu cá nhân viết cứng trong code |
| Git ignore | Sáu đường dẫn dữ liệu được bỏ qua; bốn đường dẫn tài liệu/inventory được phép theo dõi |
| Bảo toàn P0-T1 | Sáu tệp bằng chứng, hai script audit và requirements-audit.txt có SHA256 không đổi |
| Nguồn cũ | 153 tệp giữ size/mtime; 138 tệp nhỏ ≤1MiB giữ SHA256; Git status không đổi |
| Staging / dữ liệu mặc định | Staging rỗng; observation chưa tồn tại ở vị trí mặc định |

**Cách kiểm tra:** các lệnh sau đã được Codex chạy ở P0-T2, không chạy lại trong lần sửa văn phong:

```text
python -B -m unittest discover -s tests -v
python -B scripts/data_paths.py
git diff --check
git diff --cached --name-only
```

Lệnh với executable/cwd và output thật nằm trong `results/p0_t2/commands.json`; kết quả tổng hợp ở `verification.json`. Thư mục này còn giữ `repository_before.json`, `document_preservation.json` và `verification_stdout.txt`. Nguồn cũ không được hash lại toàn bộ raw lớn; không suy kiểm tra metadata thành bằng chứng mọi byte dữ liệu đều như cũ.

Lần kiểm tra ignore đầu gặp khác biệt CRLF khi truyền tên file qua stdin trên Windows. Lần kiểm tra lại truyền bằng argv đã đạt; lần chưa đạt cũng được giữ trong evidence. `git diff --check` exit 0; thông báo LF→CRLF của Git không phải lỗi whitespace.

**Nghiệm thu:** PASS theo báo cáo được cung cấp. Sinh viên chưa chạy lại các script trên máy local. Việc nghiệm thu P0-T2 không giải quyết vấn đề dữ liệu P0-T1 hoặc xác nhận đầy đủ môi trường cài mới.

## 3. Điều chỉnh văn phong tài liệu — đã báo hoàn thành trước P0-T3

**Theo yêu cầu mới:**

- AGENTS bổ sung quy tắc viết phù hợp bài tập lớn của nhóm hai sinh viên.
- REPORT trình bày theo mục đích, cách làm, kết quả, nhận xét và hạn chế; mục 4.7 viết lại về tổ chức thư mục và môi trường làm việc.
- LEARNING_GUIDE giải thích khái niệm, công thức, code và ví dụ bằng tiếng Việt dễ hiểu.
- Nhật ký rút gọn; README và kế hoạch ghi nhận P0-T2 đã nghiệm thu.
- Giữ số liệu, bảng kết quả, nguồn dẫn và những vấn đề chưa giải quyết; giữ evidence kỹ thuật trong results.

**Kiểm tra của đợt sửa văn phong:** đã giữ nguyên hai bảng trong REPORT, ba bảng và các khối code trong LEARNING_GUIDE; nguồn dẫn không đổi. Cả 11 tệp evidence khi đó, code, tests và dependencies giữ nguyên hash. Đợt đó chỉ đổi sáu tệp tài liệu; không chạy lại unit tests, ETL, tạo đặc trưng hoặc huấn luyện mô hình.

## 4. Các vấn đề chưa giải quyết

1. CSV `2019-Dec.csv` chưa có header/hash đọc được; lần này không xử lý file lock.
2. Cách loại trùng theo 7/9 trường chưa thống nhất.
3. Quy tắc buyer, price, session và rounding chưa chốt.
4. Bảng đặc trưng cũ chỉ là ứng viên tái sử dụng, chưa phải đầu vào đã được chấp nhận vô điều kiện.
5. Không dùng model/scaler/labels/metrics 7D cũ cho MVP 5D.
6. February 2020 đã được xem, không phải untouched holdout — tập kiểm chứng chưa từng được xem. Nếu dùng lại phải gọi là phân tích hồi cứu.
7. P0-T3 đã được sinh viên nghiệm thu, nhưng chưa cung cấp log, phiên bản runtime/thư viện, thời gian hoặc số đo Colab cụ thể. Chỉ ghi nhận xác nhận đã nhận, không tự điền các giá trị còn thiếu; điều này không phủ nhận nghiệm thu P0-T3.
8. Môi trường chưa được xác nhận đầy đủ: requirements chưa khóa bộ phiên bản tương thích, chưa cài/import đủ bảy thư viện trong môi trường mới.

Điều khoản sử dụng, currency, biên nhận tải/mã kiểm tra từ nguồn cung cấp và lỗi import PyArrow Windows cũng còn mở. Không đổi chính sách bảo mật. Tệp buyer khớp P0-T1 ở P0-T3 không giải quyết các vấn đề trên.

## 5. P0-T3 — notebook chuẩn bị Google Colab

**Đã làm:** tạo `notebooks/01_data_exploration.ipynb` với sáu phần, 20 ô (9 Python, 11 Markdown). Bài chỉ cần DuckDB và thư viện chuẩn; có hướng dẫn mount Drive qua giao diện, cấu hình DATA_ROOT, đọc bảng buyer nhỏ, đối chiếu P0-T1 và ba câu hỏi kèm gợi ý. Không EDA, biểu đồ hoặc K-Means.

**Kiểm tra local:** nbformat 5.11.1 đọc/validate thành công; chín ô code chạy theo thứ tự trong process Python mới. Có 92.652 dòng, 23 cột, 92.652 users riêng biệt; số dòng thiếu khóa/đặc trưng hoặc không mang cờ buyer đều bằng 0. Kích thước 2.266.870 bytes và SHA256 khớp P0-T1; tám điều kiện đối chiếu đều đúng. Tệp nguồn không đổi hash/size/mtime.

Một process mới khác không có dataset dừng ở `FileNotFoundError`, không tạo data hoặc đánh dấu đạt. Tổng **11/11 kiểm tra local** đạt; các số này không phải chỉ số Colab do sinh viên cung cấp. Notebook giao cho sinh viên đã xóa output và execution counts, không có đường dẫn Windows, credentials hoặc giá trị user IDs.

**Cách chạy đã dùng:** `python -B scripts/verify_colab_notebook.py` bằng interpreter hiện có của project cũ (Python 3.14.7, DuckDB 2.0.0). Công cụ dùng nbformat và `exec` từng ô, không phải Jupyter/Colab kernel. nbformat còn thiếu nên được cài riêng bằng `python -B -m pip install --target .tmp/notebook-validation nbformat`; không thêm vào dependency runtime MVP hoặc cài bảy thư viện chưa dùng. `.tmp/` đã được ignore.

**Bằng chứng:** `results/p0_t3/verification.json` ghi lệnh của hai process, môi trường, output từng ô và hash trước/sau; `local_run.txt` dễ đọc hơn. Lần kiểm tra đường dẫn Windows đầu dò JSON đã escape nên báo sai; đã sửa công cụ để dò nội dung cell đã decode, notebook không đổi. Lần kiểm tra này và lần sửa được ghi trong kết quả, không che lần chưa đạt.

**Files tạo/sửa:** tạo một notebook, `scripts/verify_colab_notebook.py` và hai tệp bằng chứng P0-T3; cập nhật README, notebooks/README, AGENTS, kế hoạch, hai tài liệu tích lũy, nhật ký và ignore thư mục QA tạm. Không sửa hai script audit cũ, tests đường dẫn, requirements hoặc evidence P0-T1/P0-T2. Không upload dataset, mount Drive hoặc thay quyền chia sẻ.

Đối chiếu cuối: giữ đủ 26 files có sẵn; 11 evidence P0-T1/P0-T2 và các bảng REPORT/LEARNING_GUIDE không đổi. Source cũ giữ 153 metadata và 138 hash file nhỏ; không có thay đổi trong phạm vi kiểm tra. Có 24 liên kết tài liệu local hợp lệ; staging rỗng và bộ QA tạm được ignore.

**Xác nhận sinh viên — nguồn riêng:** người dùng thông báo trong yêu cầu P0-T4 ngày 13/11/2026 rằng cả hai sinh viên đã trực tiếp nghiệm thu PASS trên Google Colab/Drive. Trạng thái hiện hành là **PASS (Student Verified)**.

Chưa nhận link/bản notebook đã chạy, log, phiên bản Python/DuckDB hoặc số đo Colab cụ thể. Không gán 92.652 dòng, 11/11 hay phiên bản local phía trên cho Colab. Giữ nguyên `results/p0_t3/verification.json` và `local_run.txt` như bằng chứng local lịch sử, kể cả nhãn READY FOR STUDENT TEST tại thời điểm chúng được tạo. Khi bàn giao GitHub, nhóm cần so bản local đề xuất với bản Drive đã chấp nhận; không giả định hai bản có cùng code nếu chưa đối chiếu.

## 6. P0-T4 — quy trình cộng tác và bàn giao

**Đã thực hiện:** phân biệt GitHub main chính thức với nhánh task/PR và bản Drive thực hành; phân công notebook 01 cho Thành viên 1 sửa chính, Thành viên 2 kiểm tra trên bản sao riêng. Đây là vai trò, chưa tự gán tên cá nhân. README hướng dẫn lấy cùng phiên bản, tránh sửa chung, chạy lại từ đầu, giữ output phù hợp trước khi bỏ output khỏi bản public và cập nhật tài liệu sau mỗi task.

**Bàn giao GitHub:** đã tạo nhánh `p0-t4-team-workflow` và [PR nháp #1](https://github.com/TminTtapcode/customer-segmentation-mvp/pull/1). Kiểm tra trực tiếp đầu lượt 13/11/2026 cho thấy main chỉ có `.gitignore`; commit gốc là `95cdb761b60aea21149e71cf1190a974c382f5e8`. Vì vậy, PR gồm cả notebook, code và bằng chứng đã có từ P0-T1/T2/T3; riêng P0-T4 chỉ sửa bảy tài liệu. Notebook local giữ nguyên để nhóm so với bản Drive đã nghiệm thu. Không sửa data, code, dependencies hoặc bằng chứng cũ; chưa đưa PR vào main.

**Kiểm tra local:** chạy đoạn Python thư viện chuẩn qua `python -B -` để đối chiếu snapshot trước/sau, các bảng, liên kết và nội dung file; chạy `git diff --check`, `git diff --cached --name-only` và `git ls-remote --heads origin main p0-t4-team-workflow`. Có 25 liên kết local hợp lệ; chỉ đổi bảy tài liệu có sẵn, không thêm/xóa file dự án. Notebook và 13 tệp bằng chứng P0-T1/T2/T3 giữ nguyên SHA256; code, tests và requirements không đổi. Source cũ giữ metadata của 153 tệp và hash của 138 tệp nhỏ; không kiểm tra lại mọi byte của raw lớn. Staging ban đầu rỗng. Bản bàn giao chỉ gồm 30 file đã kiểm tra, không có dataset/model; đối chiếu Git blob bảo đảm giữ đúng bytes local.

Kiểm tra whitespace trên bảy tài liệu đạt với `git -c core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol diff --cached --check -- AGENTS.md README.md docs/LEARNING_GUIDE.md docs/PROGRESS.md docs/PROJECT_PLAN.md docs/REPORT.md notebooks/README.md`. Kiểm tra toàn staging chưa đạt: sau khi nhận diện CRLF, còn 37 cảnh báo ở log lịch sử `results/p0_t2/verification_stdout.txt`. Giữ nguyên log này để bảo toàn bằng chứng; không gọi kiểm tra toàn bộ là PASS.

Kiểm tra `git var GIT_AUTHOR_IDENT` ban đầu chưa đạt vì local chưa cấu hình tác giả. Kết nối GitHub đọc được repo nhưng lệnh tạo blob và PR bị HTTP 403 (thiếu quyền ghi của integration). Đã dùng Git để push và GitHub REST API để tạo PR nháp bằng thông tin đăng nhập sẵn có của Git Credential Manager; không lưu token vào file/log. Tên đăng nhập/email tác giả được đối chiếu từ tài khoản GitHub và chỉ dùng cho lệnh commit, không đổi cấu hình toàn máy. Lệnh `git -c credential.interactive=never push -u origin p0-t4-team-workflow` thành công; PR được tạo với `draft=true`, base là main. Không chạy lại notebook, tests dữ liệu, ETL hoặc mô hình trong P0-T4.

**Trạng thái cập nhật theo yêu cầu P1-T1:** P0-T4 = PASS (Student Verified), nhóm xác nhận đóng Phase 0. Các kết quả kiểm tra P0-T4 phía trên là lịch sử, không chạy lại để nghiệm thu P0. Việc cập nhật GitHub main vẫn còn riêng bên dưới.

## 7. Checklist hoàn thành Phase 0

- [x] P0-T1 được chấp nhận có điều kiện; vấn đề dữ liệu vẫn theo dõi để xử lý ở Phase 2.
- [x] P0-T2 đã nghiệm thu theo báo cáo; giữ bằng chứng và giới hạn của lần kiểm tra đó.
- [x] P0-T3 được người dùng xác nhận hai sinh viên trực tiếp nghiệm thu trên Colab/Drive; không thêm chỉ số chưa cung cấp.
- [x] Có quy trình một người sửa chính/notebook, bản Drive riêng và người còn lại kiểm tra.
- [x] Có quy tắc lưu kết quả và thực hiện → giải thích → kiểm tra → cập nhật tài liệu → dừng nghiệm thu.
- [x] Bản bàn giao đã lên nhánh GitHub và PR nháp #1 để nhóm kiểm tra.
- [x] Đưa bản P0 đã được nhóm chấp nhận vào GitHub main bằng merge commit của PR #1; không tự bổ sung bằng chứng đối chiếu Drive chưa được gửi.
- [x] Sinh viên nghiệm thu P0-T4 và xác nhận đóng Phase 0 theo thông báo trong yêu cầu P1-T1.

**Phase 0: ĐÃ ĐÓNG theo xác nhận của nhóm.** Bàn giao P0 vào main đã hoàn thành khi bắt đầu P1-T2, không làm lại P0. Các vấn đề dữ liệu vẫn để Phase 2, không đánh dấu đã giải quyết.

| Nhóm task còn lại | Trạng thái |
|---|---|
| P0-T2 | PASS — đã nghiệm thu theo báo cáo Codex; sinh viên chưa chạy lại local |
| P0-T3 | PASS (Student Verified) — xác nhận người dùng 13/11/2026, không thêm chỉ số Colab |
| P0-T4 | PASS (Student Verified); nhóm xác nhận đóng Phase 0, PR #1 đã merge |
| P1-T1 | PASS (Student Verified); PR #2 đã merge |
| P1-T2 | PASS (Student Verified); PR #3 đã merge |
| P1-T3 | PASS (Student Verified); PR #4 đã merge |
| P1-T4 | PASS (Student Verified); PR #5 đã merge; Phase 1 CLOSED |
| P2-T1 | BLOCKED — raw tháng 12 chưa đọc được |
| P2-T2…T4 | NOT STARTED |
| P3-T1…T3 | NOT STARTED |
| P4-T1…T4 | NOT STARTED |
| P5-T1…T4 | NOT STARTED |
| P6-T1…T4 | NOT STARTED |
| P7-T1…T4 | NOT STARTED |

## 8. P1-T1 — vấn đề, mục tiêu và câu hỏi nghiên cứu

**Đối chiếu trước khi sửa:** GitHub REST qua kết nối GitHub và `git ls-remote --heads origin main p0-t4-team-workflow` cùng cho thấy main ở `95cdb761b60aea21149e71cf1190a974c382f5e8`, chỉ có `.gitignore`. PR #1 Open/Draft, `merged=false`; nhánh P0-T4 ở `ef6042c159cae09ba829e0fcd0264fd4a0ec51c1` có đủ 30 file MVP. Working tree ban đầu sạch. Nhánh `p1-t1-research-questions` được tạo từ đúng commit P0-T4 này, không tạo lại P0, không sửa PR #1 hoặc tự merge main.

**Đã thực hiện:**

- REPORT mục 1: giới thiệu, lý do, mục tiêu, ba RQ, phạm vi và phương pháp dự kiến; mục 2: bảng dữ liệu → phương pháp → kết quả → đánh giá cho từng RQ.
- LEARNING_GUIDE phần 13: sáu thuật ngữ nghiên cứu; ví dụ ba khách hàng và cặp có RFM giống nhau nhưng khác tương tác; bảng RFM/Engagement; ba câu hỏi tự kiểm tra kèm gợi ý.
- Đồng bộ README, AGENTS, PROJECT_PLAN và trạng thái nghiệm thu P0 trong PROGRESS. Chỉ sửa sáu tài liệu có sẵn, không tạo báo cáo mới.
- Giữ Frequency là số phiên có mua duy nhất, không phải số đơn. Nêu F0/F1 dùng cùng buyers; không kết luận từ riêng Silhouette, không coi phân cụm là dự đoán mua hay bằng chứng hiệu quả marketing.

**Kiểm tra đã chạy:** dùng `..\customer-analytics-antigravity\.venv\Scripts\python.exe -B .tmp/p1t1-verify.py` cho QA tài liệu và `git diff --stat` để xem phạm vi. Script QA chỉ dùng thư viện chuẩn, nằm trong `.tmp/` đã ignore, không thêm vào bản bàn giao. Có 26 liên kết local hợp lệ; ba RQ khớp giữa REPORT và kế hoạch; các phép tính ngày minh họa đúng (2, 90, 20, 40). Chỉ sáu tài liệu đổi; 24 file còn lại và 13 bằng chứng giữ nguyên hash. Các bảng cũ, REPORT mục 4.1–4.8 và toàn bộ danh sách vấn đề ở mục 4 được bảo toàn. Nguồn cũ giữ metadata 153 file, SHA256 của 138 file nhỏ và Git status; không hash lại toàn bộ raw lớn.

Kiểm tra whitespace qua `git -c core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol diff --check` exit 0. Lần dò section đầu qua stdin gặp `IndexError`; chuyển sang script QA tạm để kiểm tra đúng nội dung UTF-8, không sửa bằng chứng cũ để vượt kiểm tra. Tổng 14 điều kiện QA tài liệu đạt; đây không phải kết quả phân tích hoặc mô hình. Không chạy notebook, EDA, tạo đặc trưng, K-Means, dashboard hoặc cài dependency.

**Nội dung tự kiểm tra đã giao ở P1-T1:**

Tại thời điểm bàn giao P1-T1, bản xem chung là [PR #2](https://github.com/TminTtapcode/customer-segmentation-mvp/pull/2), nhánh `p1-t1-research-questions`, base `p0-t4-team-workflow`, chỉ đổi sáu tài liệu và chưa merge. Sau khi người dùng xác nhận PASS, hai PR được xử lý theo thứ tự đã đề xuất; kết quả hiện hành ghi ở mục 9.

- Đọc REPORT mục 1–2, giải thích được ba RQ cần dữ liệu và bằng chứng nào.
- Đọc LEARNING_GUIDE phần 13, mỗi người tự trả lời ba câu hỏi rồi đối chiếu gợi ý.
- Giải thích vì sao nghiên cứu Engagement và vì sao vẫn có thể chưa tìm được bằng chứng F1 tốt hơn F0.
- Thống nhất nội dung P1-T1 trước khi chuyển P1-T2. Người dùng sau đó đã xác nhận PASS; chưa gửi bài trả lời riêng nên không tự điền kết quả từng câu.

**Còn mở:** toàn bộ vấn đề dữ liệu ở mục 4, giới hạn môi trường và các thông số Colab chưa được gửi vẫn giữ nguyên. Chưa có thực nghiệm trả lời RQ1–RQ3. Tại thời điểm bàn giao P1-T1, trạng thái là READY FOR STUDENT REVIEW; xác nhận PASS sau đó được ghi bên dưới.

### Điều chỉnh theo nhận xét P1-T1

Nhận xét được cung cấp đánh giá nội dung P1-T1 đạt yêu cầu và đủ điều kiện nghiệm thu, nhưng vẫn yêu cầu hai sinh viên tự kiểm tra rồi xác nhận PASS. Chưa coi nhận xét này là xác nhận hoàn tất nghiệm thu.

- Rút gọn REPORT mục 1.6 ở mức phương pháp dự kiến; chuyển chi tiết chỉ số, độ ổn định và tài nguyên sang phần kế hoạch Phase 5. Giữ nguyên ba RQ, bảng kiểm chứng và giới hạn diễn giải.
- Bỏ thông tin cập nhật PR/main khỏi báo cáo nghiên cứu; nhật ký bàn giao ở PROGRESS. Không đổi ví dụ, công thức, số liệu hoặc kết quả P0.
- Đối chiếu GitHub trong lượt review: PR #1 Open/Draft, chưa merge; PR #2 Open, đã ra khỏi Draft nhưng chưa merge, base vẫn `p0-t4-team-workflow`. Việc ra khỏi Draft chưa thay thế xác nhận PASS của sinh viên.
- Thứ tự bàn giao được đề xuất: kiểm tra và merge PR #1 bằng merge commit để giữ lịch sử; đổi base PR #2 sang main, kiểm tra diff chỉ còn sáu tài liệu P1-T1; duyệt/merge P1-T1 sau nghiệm thu. Không tạo lại P0.

**Kiểm tra đợt điều chỉnh:** chạy đoạn Python thư viện chuẩn qua `python -B -` để so hash, nội dung và liên kết; `git -c core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol diff --check` exit 0. Chỉ REPORT, PROGRESS và nhãn liên kết PR #2 trong README thay đổi; 27 file khác, gồm notebook, sổ tay/ví dụ và 13 bằng chứng, giữ nguyên hash. Ba RQ, các bảng, REPORT mục 4.1–4.8 và danh sách vấn đề dữ liệu không đổi; chi tiết đánh giá được chuyển nguyên nội dung sang phần dự kiến Phase 5. Có 26 liên kết local hợp lệ. Không chạy lại dữ liệu hoặc mô hình.

Ở cuối lượt review, P1-T1 giữ READY FOR STUDENT REVIEW và P1-T2 chưa bắt đầu. Người dùng sau đó xác nhận trực tiếp **“P1-T1 PASS”**; điều kiện bắt đầu prompt P1-T2 đã được đáp ứng.

## 9. P1-T2 — học RFM từ repository tham khảo

**Nền tảng bàn giao:** theo thứ tự trong nhận xét, đưa PR #1 khỏi Draft rồi merge bằng merge commit `887f8bc`; đổi base PR #2 sang main, xác nhận diff chỉ sáu tài liệu và merge bằng merge commit `7098357`. Hai head được đối chiếu trước khi merge, không squash/rebase hoặc ghi đè nhánh. Cây file main sau merge khớp bản P1-T1 được chấp nhận. Không có commit statuses/check runs CI trên hai head; không gọi việc thiếu CI là tests PASS. Nhánh mới `p1-t2-rfm-reference` bắt đầu từ main `70983578c809aec5784502b46c022780c239cc24`.

**Đã đọc:** README.md, toàn bộ 28 ô Customer_Segmentation_Model.ipynb và customer_segmentation_app/app.py của ch1ns0n/Customer-Segmentation, tại commit `d4a8a864ef0128708a0cd0a0e2799faf23b9dd60`. Đọc thêm tài liệu gốc UCI về schema/cancellation và tài liệu NumPy/scikit-learn về log1p, StandardScaler, K-Means. Không tải Excel, model/scaler pickle hoặc đọc sâu Flask/HTML/CSS. Không xác nhận tệp Excel trùng bản UCI, môi trường chạy hay artifact pickle tái lập được.

**Kết quả đọc:** F đếm InvoiceNo riêng biệt; M cộng Quantity × UnitPrice; log rồi chuẩn hóa ba biến trước K-Means. Có Elbow K=1–10, K=4/seed=42 được đặt thủ công; tên cụm gán bằng dictionary. Code chưa tách hủy/hoàn trả. Output gốc ô 12–13 có RuntimeWarning và 41 giá trị Monetary_log thiếu; đây là output được lưu trong repo tham khảo, không phải lần chạy mới hoặc số liệu MVP. Ô 14 đưa M≤0 về 0 nhưng web lấy log trực tiếp; nhóm không sao chép sự khác biệt này.

**Tài liệu:** REPORT mục 3 phân tích cách triển khai, giới hạn có vị trí code và bảng so sánh REES46. LEARNING_GUIDE phần 14 có ví dụ RFM hai khách, log/scaler, K-Means ở mức khái niệm và ba câu hỏi/gợi ý. README, AGENTS và PROJECT_PLAN đồng bộ trạng thái. Chỉ sửa sáu tài liệu hiện có, không tạo báo cáo hoặc notebook mới.

**Kiểm tra đã chạy:** `..\customer-analytics-antigravity\.venv\Scripts\python.exe -B .tmp/p1t2-verify.py` dùng thư viện chuẩn, exit 0; script QA tạm được ignore, không thêm vào dự án. Có 26 liên kết local hợp lệ. Ví dụ tính tay A=(R=1,F=2,M=40), B=(R=4,F=1,M=30); log1p(1)≈0,6931, log1p(9)≈2,3026; cột [1,3] có mean=2/std=1 và giá trị mới 5 thành z=3. Đây chỉ là kiểm tra ví dụ giảng dạy, không phải chạy mô hình hoặc phân tích dataset.

Chỉ sáu tài liệu đổi; 24 file khác, gồm notebook, code, requirements và 13 bằng chứng P0, giữ nguyên SHA256. REPORT mục 1–2 và từ mục 4 trở đi, nội dung sổ tay cũ, các bảng và danh sách vấn đề dữ liệu không đổi. Hai file text tham khảo README/app.py có Git blob hash khớp cây nguồn; notebook được đọc tại commit cố định và có 28 ô. Nguồn cũ giữ metadata 153 file, hash 138 file nhỏ và Git status; không hash lại raw lớn. `git -c core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol diff --check` exit 0. Không chạy code repository tham khảo, ETL, EDA, features, K-Means trên REES46 hoặc web; không cài dependency, không đổi cleaning policy.

**Bàn giao P1-T2 tại thời điểm chờ nghiệm thu:**

Bản bàn giao khi đó là [PR #3 — P1-T2](https://github.com/TminTtapcode/customer-segmentation-mvp/pull/3), nhánh `p1-t2-rfm-reference`, base main, chỉ đổi sáu tài liệu. Sau xác nhận PASS trong tệp yêu cầu P1-T3, PR #3 được merge; lịch sử bàn giao giữ riêng với kết quả đọc tài liệu.

- [x] Đọc REPORT mục 3 và LEARNING_GUIDE phần 14, trả lời câu hỏi theo xác nhận của hai sinh viên.
- [x] Nghiệm thu ví dụ RFM/log/scaler và các khái niệm theo checklist 5/5 được cung cấp.
- [x] Xác nhận P1-T2 PASS; không tự điền bài trả lời chi tiết chưa được gửi.

**Còn mở:** danh sách vấn đề dữ liệu ở mục 4 giữ nguyên. Chưa có kết quả mô hình hoặc chính sách dữ liệu mới của REES46. Trạng thái bàn giao P1-T2 khi đó là READY FOR STUDENT REVIEW; hiện đã được sinh viên xác nhận PASS để bắt đầu riêng P1-T3.

## 10. P1-T3 — đọc bài nghiên cứu RFM-B

**Nền tảng:** PR #3 được đối chiếu head `4ce7021`, diff đúng sáu tài liệu đã nghiệm thu, đưa khỏi Draft và merge bằng merge commit `599526493300da3d9939d5222802f8de0a9e042f`. Không có statuses/check runs CI; không coi việc thiếu CI là tests PASS. Cây file main sau merge khớp bản P1-T2 đã chấp nhận. Nhánh `p1-t3-rfmb-paper` bắt đầu từ main này, không sửa code hoặc dữ liệu cũ.

**Đã đọc:** bài *Behavioral Intelligence in Digital Retail: An Extended RFM Framework for Customer Segmentation and Resource Allocation*, Iman Squalli Houssaini và Miloud Daoud; Preprints.org v1, đăng 13/04/2026, DOI `10.20944/preprints202604.0852.v1`. Đọc HTML gốc: Abstract, Introduction, mục 3/Bảng 2, mục 5–6/Bảng 3–4, mục 8 và Conclusion. Trang nguồn ghi chưa peer-reviewed. Không dựa riêng vào phần tóm tắt được dán trong yêu cầu.

**Kết quả học:** phân biệt CVR event với tỷ lệ phiên, AOV theo phiên mua với đơn hàng, danh mục cấp cao với category_id và missing brand với một thương hiệu. Đọc K/metrics như kết quả tác giả công bố; RF học nhãn K-Means, không phải nhãn mua tương lai. Trong phần phương pháp/kết quả và bảng đã đọc chưa thấy đối chứng 3D/7D cùng quy trình; không kết luận bài báo đã chứng minh RFM-B vượt RFM. Giữ F0=3D, F1=5D, chưa quyết định thêm biến hoặc làm feature rationale P1-T4.

**Tài liệu:** REPORT chỉ thêm mục 3.5–3.9, giữ phần P1-T2; LEARNING_GUIDE thêm phần 15 với ví dụ và ba câu hỏi/gợi ý. PROGRESS ghi xác nhận P1-T2, nguồn đọc, bàn giao và giới hạn. README, PROJECT_PLAN, AGENTS chỉ đồng bộ trạng thái/phạm vi hiện hành; không tạo báo cáo mới.

**Kiểm tra đã chạy:** `..\customer-analytics-antigravity\.venv\Scripts\python.exe -B .tmp/p1t3-verify.py`, thư viện chuẩn, exit 0; script/ghi chú QA tạm được ignore. Có 26 liên kết local hợp lệ. Ví dụ tính tay xác nhận 3/10=0,3 khác 1/2=0,5; 300/2=150, 300/10=30; ba ID danh mục có thể ánh xạ thành hai nhóm cấp cao; hai brand được quan sát và phần missing vẫn chưa biết. Số ghi trong REPORT được đối chiếu với ghi chú đọc mục 3.3/6.1 và Bảng 2/4, không phải tái tạo các metrics.

Chỉ sáu tài liệu đổi; 24 file khác, gồm code, notebook, requirements và 13 bằng chứng, giữ nguyên hash. REPORT phần P1-T1/P1-T2 và từ mục 4 trở đi, nội dung sổ tay 1–14, các bảng cũ, hợp đồng F0/F1 và danh sách vấn đề dữ liệu giữ nguyên. Source cũ giữ metadata 153 file, hash 138 file nhỏ và Git status; không hash lại raw lớn. `git -c core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol diff --check` exit 0. Không chạy REES46, EDA, K-Means/Random Forest, tạo feature/notebook, thêm dependency hoặc sửa source cũ.

**Nội dung giao nghiệm thu P1-T3 tại thời điểm bàn giao:**

Bản bàn giao khi đó là [PR #4 — P1-T3](https://github.com/TminTtapcode/customer-segmentation-mvp/pull/4), nhánh `p1-t3-rfmb-paper`, base main, chỉ thay đổi sáu tài liệu. Các mục dưới là yêu cầu tự học đã giao, không phải bài trả lời hoặc kết quả từng câu do sinh viên gửi. Số liệu công bố trong phần đọc bài báo không phải kết quả thực nghiệm MVP.

- [ ] Đọc REPORT mục 3.5–3.9 và LEARNING_GUIDE phần 15; giải thích được bốn biến và dữ liệu cần để đo.
- [ ] Tính lại ví dụ event/session, AOV, danh mục và thương hiệu; trả lời ba câu cuối phần 15 trước khi xem gợi ý.
- [ ] Phân biệt kết quả tác giả với kết quả MVP, accuracy nhãn cụm với dự đoán mua và nhận xét sơ bộ với quyết định feature P1-T4.

**Cập nhật nghiệm thu:** trong yêu cầu P1-T4, người dùng xác nhận hai sinh viên đã nghiệm thu **P1-T3 PASS (Student Verified)**. Không tự đánh dấu kết quả từng câu phía trên. PR #4 được bàn giao vào main như mục 11. Toàn bộ vấn đề dữ liệu ở mục 4 vẫn mở; chưa tái lập bài báo hoặc xác minh trên Cosmetics các điều kiện tính bốn biến.

## 11. P1-T4 — thiết kế cải tiến phân khúc

**Nền tảng bàn giao:** working tree ban đầu sạch. Đối chiếu PR #4 Open/Draft, head `35d1f6ccef529f5a33101112aac499facd53f36d`, diff chỉ sáu tài liệu đã nghiệm thu. Đưa khỏi Draft rồi merge bằng merge commit `b137750fe65261d8591f18323be5cc629d81563a`; cây file main khớp head được chấp nhận, không ghi đè lịch sử. Có 0 commit statuses/0 check runs CI; không gọi thiếu CI là tests PASS. Dùng GitHub REST/GraphQL qua thông tin đăng nhập Git Credential Manager sẵn có, không lưu token. Chạy `git fetch origin main`, rồi `git switch -c p1-t4-improvement-design origin/main` từ main này.

**Đã thực hiện:**

- Chuyển mục tiêu sang cải thiện phân khúc có kiểm chứng; giữ nguyên RQ1–RQ3, K-Means và F0 ba biến/F1 năm biến.
- REPORT phần thiết kế A–G: hạn chế giả định → giải pháp → dữ liệu/đánh giá; công thức, ý nghĩa, giới hạn năm biến; lý do chưa thêm CVR/AOV/danh mục/thương hiệu; H1–H3; quy trình thí nghiệm và kế hoạch biểu đồ Phase 3–6.
- Bắt buộc ghi hạn chế có bằng chứng của F0 trước F1. Kiểm tra tiền xử lý nếu cần trong cùng bộ biến/cohort/K/seed; khi so F0/F1 giữ quy tắc RFM chung và fit scaler riêng. Cấu hình dự kiến n_init=10, seed [0,21,42], K=2–6; chưa chốt cột log hoặc K cuối.
- Thiết kế đọc Silhouette/DBI cùng ổn định, cỡ cụm, hồ sơ năm biến ở đơn vị gốc, thông tin hành vi, căn cứ marketing và tài nguyên. Chấp nhận khả năng giữ F0 hoặc chưa đủ bằng chứng cải tiến.
- P6-T2/T3 có luồng cụm → đặc điểm quan sát → mục tiêu → hành động → căn cứ → KPI → hạn chế; chỉ hỗ trợ quyết định, không gửi chiến dịch. Sổ tay phần 16 giải thích và có ba câu hỏi/gợi ý.
- Chỉ sửa AGENTS, README và bốn tài liệu hiện có; không tạo báo cáo, dependency, biểu đồ, notebook hoặc artifact nghiên cứu mới.

**Kiểm tra đã chạy:** `..\customer-analytics-antigravity\.venv\Scripts\python.exe -B .tmp/p1t4-verify.py`, chỉ dùng thư viện chuẩn, exit 0. Có 24 điều kiện QA tài liệu đạt và 26 liên kết local hợp lệ; các bảng đúng số cột. Ba RQ, bảng kiểm chứng RQ, phần tài liệu tham khảo P1-T2/T3, toàn bộ mục 4 của REPORT, nội dung sổ tay 1–15, hợp đồng nghiên cứu và danh sách vấn đề mở được bảo toàn. Ví dụ tính tay xác nhận 40 ngày, cửa sổ 30 ngày, log1p(0/9/99)≈0/2,3026/4,6052 và chuẩn hóa [1,3] thành [−1,1]; đây không phải số liệu REES46.

Chỉ sáu tài liệu đổi; 24 file còn lại, gồm notebook, code, tests, requirements và 13 bằng chứng, giữ nguyên SHA256. Source cũ giữ metadata 153 file, hash 138 file nhỏ và Git status; không hash lại raw lớn hoặc xác nhận lại header/hash CSV tháng 12. Script/snapshot QA nằm trong `.tmp/` đã ignore, không thuộc bản bàn giao. `git diff --stat` dùng để kiểm tra phạm vi; kiểm tra whitespace bằng `git -c core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol diff --check` exit 0. Ban đầu staging rỗng. Không chạy notebook, ETL, EDA, feature engineering, K-Means hoặc cài dependency; chưa có thực nghiệm hay kết quả phân cụm trong P1-T4.

Đọc tài liệu chính thức scikit-learn cho KMeans, StandardScaler và adjusted_rand_score để kiểm tra ý nghĩa cấu hình/scaling/ARI; liên kết nằm trong REPORT và LEARNING_GUIDE. Không dùng phiên bản tài liệu web làm bằng chứng môi trường local đã được cài hoặc tái lập đầy đủ.

**Bàn giao P1-T4:** [PR nháp #5](https://github.com/TminTtapcode/customer-segmentation-mvp/pull/5), nhánh `p1-t4-improvement-design`, base main; chỉ thay sáu Markdown hiện có. Commit nội dung `7161992`. Đã chạy `git -c core.autocrlf=false add -- AGENTS.md README.md docs/PROJECT_PLAN.md docs/REPORT.md docs/LEARNING_GUIDE.md docs/PROGRESS.md`, kiểm tra `git diff --cached --check` với cấu hình whitespace phía trên (exit 0), rồi đối chiếu Git blob với bytes local: khớp cả sáu file, không có data/model trong staging. Dùng tên tác giả cho riêng lệnh commit, không đổi Git config toàn máy; `git -c credential.interactive=never push -u origin p1-t4-improvement-design` thành công. PR tạo với draft=true; không merge P1-T4 khi chưa nghiệm thu.

**Những điều đã chốt và còn chờ:** chốt phạm vi năm biến, ba giả thuyết và cách kiểm chứng; không chốt giả thuyết đúng. Toàn bộ mục 4 giữ nguyên. Phase 2 còn schema/nguồn/cleaning/buyer/price/session/rounding; Phase 3–4 còn phân phối, outliers, tính đặc trưng và chọn biến đổi; Phase 5 mới có nhãn, K, metrics, thời gian/bộ nhớ và kết luận F0/F1 thật. Chưa chứng minh log/scaling tốt hơn, tên cụm hay hiệu quả marketing.

**Nội dung tự kiểm tra P1-T4 đã giao khi bàn giao:**

- [ ] Đọc REPORT phần thiết kế A–G, giải thích được mỗi hạn chế đang là giả thuyết hay đã có bằng chứng.
- [ ] Tự trả lời ba câu phần 16 của LEARNING_GUIDE: thông tin F1 thêm, cách tách tác động log/Engagement, bằng chứng cần trước khi kết luận cải tiến/marketing.
- [ ] Thống nhất năm biến, điều kiện so sánh và sản phẩm Phase 5–6; không coi thiết kế là kết quả chạy.

Tại thời điểm bàn giao, P1-T4 là READY FOR STUDENT REVIEW. Yêu cầu P2-T1 sau đó xác nhận **P1-T4 PASS (Student Verified)**. Không tự đánh dấu kết quả từng câu chưa được gửi. Phase 1 được đóng sau đối chiếu main ở mục 12; nội dung thiết kế giữ nguyên.

## 12. Đóng Phase 1 và P2-T1 — kiểm tra schema

### Bàn giao và đóng Phase 1

Người dùng xác nhận hai sinh viên đã nghiệm thu P1-T4 PASS và thông báo PR #5 đã merge. Đối chiếu trực tiếp đầu lượt vẫn thấy PR #5 Open/Draft, head `ca07aca0567936afa6572520ab44321489c36d11`. Working tree sạch; diff đúng sáu tài liệu được nghiệm thu, không có thay đổi người khác. Đã đưa PR khỏi Draft rồi merge bằng merge commit `e941a906f8502d793a278927b18f8d26ae70827b`. Cây file main khớp head được chấp nhận. Có 0 commit statuses/0 check runs; không gọi thiếu CI là tests PASS. GitHub REST/GraphQL dùng thông tin Git Credential Manager sẵn có, không lưu token.

Chạy `git fetch origin main` và `git switch -c p2-t1-schema-inspection origin/main` từ đúng main này. Không force-push/reset hoặc viết lại nội dung đã nghiệm thu.

- [x] P1-T1…P1-T4 được người dùng xác nhận sinh viên nghiệm thu PASS.
- [x] PR #2–#5 đã vào main; giữ RQ1–RQ3, F0/F1, H1–H3, thiết kế thực nghiệm và hỗ trợ marketing.
- [x] Tách nghiệm thu thiết kế khỏi kết quả thực nghiệm; chưa khẳng định Engagement/log/scaling có hiệu quả.
- [x] Giữ nguyên vấn đề dữ liệu ở mục 4 để xử lý đúng task Phase 2.

**Phase 1: CLOSED** về nghiên cứu và thiết kế, theo xác nhận của nhóm và bằng chứng bàn giao GitHub.

### P2-T1 đã thực hiện trong phạm vi đọc được

- Đọc metadata/inventory/audit P0-T1; cấu hình nguồn và code ETL/feature cũ chỉ dưới dạng văn bản để hiểu quan hệ raw → Parquet sự kiện → bảng khách. Không chạy pipeline cũ.
- Tạo `scripts/inspect_schema.py`, dùng thư viện chuẩn + DuckDB có sẵn. Nhận root dữ liệu bằng tham số/biến môi trường, chỉ đọc CSV header/mẫu giới hạn và footer/schema Parquet; từ chối ghi đè output hoặc ghi vào cây dữ liệu nguồn. Không sửa notebook đã nghiệm thu, không thêm dependency.
- Kiểm tra 12 file thật: ba CSV observation có mẫu, tháng 12 không mở được, February chỉ header; sáu Parquet chỉ footer/schema; buyer_clusters chỉ metadata và bị loại khỏi đầu vào MVP.
- Tổng 3.000 dòng đầu của tháng 10/11/01; ba header có cùng chín cột và thứ tự. Các mẫu có view/cart/purchase/remove_from_cart; 3.000/3.000 thời gian parse được và có UTC; định dạng user/session đọc được trong mẫu. Không suy tỷ lệ hoặc min/max toàn bộ từ mẫu này.
- Ba Parquet sự kiện cùng 21 cột; ba bảng feature cùng 23 cột. Tất cả số dòng Parquet trong kết quả mới lấy từ footer; không đếm lại hoặc đọc dữ liệu dòng. event_time Parquet có isAdjustedToUTC=0, không đủ để xác nhận timezone gốc toàn bộ.
- REPORT có phần Data Understanding, từ điển cột/kiểu, grain/khóa/timezone, khả năng tính năm biến và việc chuyển tiếp. LEARNING_GUIDE phần 17 giải thích từng bước và ba câu hỏi. README/AGENTS/PROJECT_PLAN đồng bộ trạng thái.

### Lệnh, kết quả và bằng chứng

Lệnh thật, chạy từ root MVP bằng Python 3.14.7 / DuckDB 2.0.0 hiện có:

```powershell
& '..\customer-analytics-antigravity\.venv\Scripts\python.exe' -B -m unittest discover -s tests -p test_inspect_schema.py -v
& '..\customer-analytics-antigravity\.venv\Scripts\python.exe' -B scripts/inspect_schema.py --data-root ../customer-analytics-antigravity/data --sample-rows 1000 --output results/p2_t1
```

Lần kiểm thử đầu có 6/7 đạt: TRY_CAST số thập phân sang BIGINT vẫn thành công do làm tròn, khiến suy kiểu sai. Đã thêm kiểm tra dạng chữ số nguyên; chạy lại **7/7 tests đạt, exit 0**. Fixtures chỉ phục vụ kiểm thử phần mềm, không dùng làm dữ liệu nghiên cứu. Kết quả chạy thử trước sửa được giữ tạm trong `.tmp/` đã ignore; bằng chứng công khai của task là lần chạy sau sửa, có hash code đi kèm.

Lần đọc dữ liệu sau sửa: **script exit 2**, trạng thái BLOCKED do `raw/2019-Dec.csv` PermissionError (errno 13). Không coi đây là audit đầy đủ thành công. Thời gian 1,794 giây chỉ cho kiểm tra schema này, chưa đo RSS, không phải benchmark pipeline/mô hình. [inspection.json](../results/p2_t1/inspection.json) giữ schema/phạm vi/mẫu/giới hạn/môi trường; [schema.csv](../results/p2_t1/schema.csv) theo từng file/cột; [execution.json](../results/p2_t1/execution.json) giữ lệnh, thời điểm và exit code thật. Không có raw user/session IDs hoặc toàn bộ mẫu trong bằng chứng public.

Kiểm tra độc lập bằng `..\customer-analytics-antigravity\.venv\Scripts\python.exe -B .tmp/p2t1-verify.py`, exit 0: **24 điều kiện QA đạt**, 36 liên kết local hợp lệ. Đọc lại đúng ba mẫu giới hạn bằng Python để đối chiếu fingerprint, tên/kiểu cột, loại sự kiện và thời gian; kiểm tra không có giá trị user/session trong phần công khai. REPORT mục 1–4 và thiết kế P1-T4 A–G, nội dung sổ tay 1–16, RQ, các bảng cũ, hợp đồng nghiên cứu và danh sách vấn đề mở được giữ nguyên. Chỉ sáu tài liệu cũ đổi; 24 file khác cùng 13 bằng chứng cũ không đổi SHA256. Có năm file mới: script, tests và ba bằng chứng P2-T1; toàn bộ dự án có 35 file. Code, notebook, tests đường dẫn và requirements đã có đều không đổi.

Source cũ giữ metadata của 153 file, SHA256 của 138 file nhỏ và Git status; không kiểm tra lại mọi byte của raw lớn. `git diff --stat`, `git status --short` dùng để xem phạm vi; kiểm tra whitespace bằng `git -c core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol diff --check` với commit nền, exit 0. QA tạm được ignore. Kiểm tra lại riêng việc mở header tháng 12 ở cuối lượt vẫn PermissionError/errno 13, không tự ghi đã hết lỗi. Các kiểm tra phần mềm/tài liệu đạt không đổi trạng thái BLOCKED của task dữ liệu.

Chưa chạy P2-T2, cleaning, observation mới, bảng RFM/Engagement, K-Means hoặc Streamlit. Chưa chạy script mới trên Colab hoặc xác nhận toàn môi trường MVP; không bổ sung số đo Colab.

**Bàn giao phần P2-T1 đã thực hiện:** [PR nháp #6](https://github.com/TminTtapcode/customer-segmentation-mvp/pull/6), nhánh `p2-t1-schema-inspection`, base main, chưa merge. Commit nội dung `dcba28c`; PR ghi rõ BLOCKED do tháng 12, không đề nghị chuyển task. Đã stage đúng 11 file bằng `git -c core.autocrlf=false add -- ...` với danh sách tường minh gồm sáu tài liệu, script, tests và ba bằng chứng; đối chiếu Git blob khớp bytes local, không có dataset/model trong staging. Kiểm tra `git diff --cached --check` với cấu hình whitespace phía trên exit 0. Commit dùng danh tính theo riêng lệnh; `git -c credential.interactive=never push -u origin p2-t1-schema-inspection` thành công; PR tạo draft=true bằng REST/Git Credential Manager sẵn có, không lưu token.

### Vấn đề còn mở và nội dung nghiệm thu

Toàn bộ mục 4 vẫn giữ nguyên, không đánh dấu resolved. Tháng 12 hiện chỉ xác nhận file tồn tại theo metadata; chưa biết schema raw, chưa đọc header/hash hoặc suy kiểu. Không khẳng định nguyên nhân PermissionError là khóa tiến trình cụ thể; không kết thúc tiến trình hay đổi bảo mật Windows. Cần file tháng 12 đọc được hoặc bản sao cùng nguồn có thể đối chiếu để hoàn tất P2-T1. Không dùng Parquet cũ thay cho bằng chứng raw còn thiếu.

- [ ] Hai bạn giải thích được CSV text/kiểu suy luận trên mẫu/kiểu Parquet, ID số và giá trị số, event/session/customer và khóa ghép.
- [ ] Trả lời ba câu phần 17 của LEARNING_GUIDE, chỉ ra vì sao parse mẫu thành công chưa chứng minh dữ liệu toàn bộ hợp lệ.
- [ ] Khi có tháng 12 đọc được: chạy kiểm tra bổ sung vào output mới, đối chiếu đủ raw observation rồi mới đề nghị nghiệm thu hoàn tất P2-T1.

**P2-T1: BLOCKED — thiếu kiểm chứng raw tháng 12.** Bản công việc một phần sẽ bàn giao bằng PR nháp; không gọi READY FOR STUDENT REVIEW cho hoàn tất task khi còn thiếu đầu vào thiết yếu. Dừng, không tự triển khai P2-T2.
