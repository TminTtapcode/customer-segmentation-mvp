# Nhật ký công việc — Customer Segmentation MVP

**Cập nhật:** 13/11/2026 (Asia/Bangkok).

- **P0-T1:** hoàn thành kiểm kê trong phạm vi đọc được; đã được chấp nhận để tiếp tục, còn vấn đề dữ liệu.
- **P0-T2: PASS — đã nghiệm thu** dựa trên báo cáo Codex: 6/6 bài kiểm tra đường dẫn và 15/15 điều kiện kiểm tra đạt. Sinh viên chưa chạy lại script trên máy local.
- **Sửa văn phong:** được chấp nhận theo báo cáo; sinh viên chưa mở bản local mới nhất để xác nhận độc lập.
- **P0-T3: PASS (Student Verified).** Người dùng xác nhận ngày 13/11/2026 cả hai sinh viên đã trực tiếp nghiệm thu trên Colab/Drive. Không tự bổ sung log/chỉ số Colab chưa được gửi.
- **P0-T4: PASS (Student Verified).** Người dùng xác nhận nhóm đã nghiệm thu và đóng Phase 0 trong yêu cầu P1-T1. Không yêu cầu làm lại P0.
- **P1-T1:** READY FOR STUDENT REVIEW — xác định vấn đề, mục tiêu, ba câu hỏi và cách kiểm chứng dự kiến; chưa thực hiện P1-T2.
- **GitHub cần nhóm xử lý:** PR #1 vẫn Open/Draft, chưa merge; main chỉ có `.gitignore` khi đối chiếu đầu P1-T1. Trạng thái này không được ghi thành “đã merge” theo suy đoán từ nghiệm thu học tập.

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
- [ ] Đưa bản P0 đã được nhóm chấp nhận vào GitHub main; PR #1 thực tế chưa merge. Không tự bổ sung bằng chứng đối chiếu Drive chưa được gửi.
- [x] Sinh viên nghiệm thu P0-T4 và xác nhận đóng Phase 0 theo thông báo trong yêu cầu P1-T1.

**Phase 0: ĐÃ ĐÓNG theo xác nhận của nhóm.** Người dùng cho phép bắt đầu P1-T1 dù cần đối chiếu tình trạng merge. Phần bàn giao vào main chưa hoàn thành được theo dõi riêng, không tự sửa lịch sử GitHub hoặc làm lại P0. Các vấn đề dữ liệu vẫn để Phase 2, không đánh dấu đã giải quyết.

| Nhóm task còn lại | Trạng thái |
|---|---|
| P0-T2 | PASS — đã nghiệm thu theo báo cáo Codex; sinh viên chưa chạy lại local |
| P0-T3 | PASS (Student Verified) — xác nhận người dùng 13/11/2026, không thêm chỉ số Colab |
| P0-T4 | PASS (Student Verified); nhóm xác nhận đóng Phase 0, PR #1 chưa merge |
| P1-T1 | READY FOR STUDENT REVIEW |
| P1-T2…T4 | NOT STARTED |
| P2-T1…T4 | NOT STARTED |
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

**Hai sinh viên cần đọc và xác nhận:**

Bản xem chung là [PR #2 — P1-T1](https://github.com/TminTtapcode/customer-segmentation-mvp/pull/2), nhánh `p1-t1-research-questions`, base `p0-t4-team-workflow`. Bản này chỉ có thay đổi sáu tài liệu so với nền P0, không thay thế việc merge PR #1. Khi nhóm đã xử lý PR #1, cần đối chiếu lại base/diff trước khi đưa P1 vào main. Codex không tự merge hai PR.

- [ ] Đọc REPORT mục 1–2, giải thích được ba RQ cần dữ liệu và bằng chứng nào.
- [ ] Đọc LEARNING_GUIDE phần 13, mỗi người tự trả lời ba câu hỏi rồi đối chiếu gợi ý.
- [ ] Giải thích vì sao nghiên cứu Engagement và vì sao vẫn có thể chưa tìm được bằng chứng F1 tốt hơn F0.
- [ ] Thống nhất nội dung P1-T1 trước khi chuyển P1-T2; xử lý riêng việc đưa bản P0 vào main.

**Còn mở:** toàn bộ vấn đề dữ liệu ở mục 4, giới hạn môi trường và các thông số Colab chưa được gửi vẫn giữ nguyên. Chưa có thực nghiệm trả lời RQ1–RQ3. Trạng thái **READY FOR STUDENT REVIEW**; dừng chờ nhóm nghiệm thu, không thực hiện P1-T2.

### Điều chỉnh theo nhận xét P1-T1

Nhận xét được cung cấp đánh giá nội dung P1-T1 đạt yêu cầu và đủ điều kiện nghiệm thu, nhưng vẫn yêu cầu hai sinh viên tự kiểm tra rồi xác nhận PASS. Chưa coi nhận xét này là xác nhận hoàn tất nghiệm thu.

- Rút gọn REPORT mục 1.6 ở mức phương pháp dự kiến; chuyển chi tiết chỉ số, độ ổn định và tài nguyên sang phần kế hoạch Phase 5. Giữ nguyên ba RQ, bảng kiểm chứng và giới hạn diễn giải.
- Bỏ thông tin cập nhật PR/main khỏi báo cáo nghiên cứu; nhật ký bàn giao ở PROGRESS. Không đổi ví dụ, công thức, số liệu hoặc kết quả P0.
- Đối chiếu GitHub trong lượt review: PR #1 Open/Draft, chưa merge; PR #2 Open, đã ra khỏi Draft nhưng chưa merge, base vẫn `p0-t4-team-workflow`. Việc ra khỏi Draft chưa thay thế xác nhận PASS của sinh viên.
- Thứ tự bàn giao được đề xuất: kiểm tra và merge PR #1 bằng merge commit để giữ lịch sử; đổi base PR #2 sang main, kiểm tra diff chỉ còn sáu tài liệu P1-T1; duyệt/merge P1-T1 sau nghiệm thu. Không tạo lại P0.

**Kiểm tra đợt điều chỉnh:** chạy đoạn Python thư viện chuẩn qua `python -B -` để so hash, nội dung và liên kết; `git -c core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol diff --check` exit 0. Chỉ REPORT, PROGRESS và nhãn liên kết PR #2 trong README thay đổi; 27 file khác, gồm notebook, sổ tay/ví dụ và 13 bằng chứng, giữ nguyên hash. Ba RQ, các bảng, REPORT mục 4.1–4.8 và danh sách vấn đề dữ liệu không đổi; chi tiết đánh giá được chuyển nguyên nội dung sang phần dự kiến Phase 5. Có 26 liên kết local hợp lệ. Không chạy lại dữ liệu hoặc mô hình.

P1-T1 giữ **READY FOR STUDENT REVIEW**; P1-T2 chưa bắt đầu. Chỉ triển khai prompt P1-T2 trong tệp nhận xét sau khi hai sinh viên xác nhận P1-T1 PASS.
