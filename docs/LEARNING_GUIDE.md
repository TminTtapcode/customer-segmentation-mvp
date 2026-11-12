# Sổ tay học tập — MVP RFM + Engagement

**Cập nhật 13/11/2026.** Phần 1–9 về kiểm kê P0-T1, phần 10–12 về công cụ/cộng tác, phần 13 về câu hỏi nghiên cứu và phần 14 về RFM từ repository tham khảo. P1-T1 đã được người dùng xác nhận PASS; P1-T2 chờ nghiệm thu. Số liệu local cũ vẫn giữ riêng, không coi là số đo Colab mới.

## 1. Tệp dữ liệu, cấu trúc bảng và nguồn gốc xử lý là gì?

Khi đọc dự án, nhóm sẽ gặp CSV gốc, Parquet đã xử lý, bảng đặc trưng, notebook và model. Đó là các tệp đầu vào hoặc kết quả của từng bước. Một tệp có tên `clean` chưa đủ để kết luận nó đã được làm sạch đúng.

**Schema — cấu trúc bảng** gồm tên cột và kiểu dữ liệu. Header CSV chỉ cho biết tên cột; chưa kiểm tra được kiểu và giá trị của mọi dòng.

**Grain — đơn vị một dòng** cho biết mỗi dòng đại diện cho điều gì. Bảng event có một dòng cho một sự kiện; bảng khách hàng có một dòng cho một user. Một session — phiên truy cập — có thể chứa nhiều sự kiện, kể cả nhiều dòng purchase.

**Nguồn gốc và quá trình xử lý dữ liệu** cho biết tệp nào tạo ra tệp nào, bằng code và quy tắc nào, ở mốc thời gian nào. Nhờ đó nhóm có thể lần ngược từ kết quả về dữ liệu ban đầu.

**SHA256** là dấu vân tay của nội dung tệp. So sánh hash giúp kiểm tra hai bản sao có cùng nội dung hay không; không chứng minh công thức đúng, nguồn đáng tin hoặc được phép chia sẻ. Phần kỹ thuật này được giữ ở đây để tự kiểm tra khi chuyển dữ liệu.

## 2. Vì sao kiểm tra trước khi dùng lại?

Nhóm cần biết cửa sổ dữ liệu, điều kiện buyer — khách mua hợp lệ, cách tính phiên mua, cách xử lý giá và bản ghi trùng. Không nên huấn luyện mô hình chỉ vì có sẵn một bảng feature — bảng dữ liệu đặc trưng.

Kết quả P0-T1 cho thấy năm đặc trưng khớp khi tính lại từ observation — dữ liệu trước mốc chốt. Tuy nhiên, cách loại trùng theo 7/9 trường chưa thống nhất, điều kiện buyer chưa chốt và CSV tháng 12 chưa đọc được header/hash. Tính toán nhất quán chưa đủ để kết luận quy tắc xử lý là phù hợp nhất.

Model cũ dùng 7D — bảy đặc trưng — không phải kết quả F1 5D — năm đặc trưng — của MVP.

## 3. Các đặc trưng được tính như thế nào?

Quy trình kiểm tra gồm: lập danh sách tệp → đọc kích thước/cột/số dòng → tìm code và quy tắc đã dùng → kiểm tra thời gian/khóa → tính lại năm đặc trưng → đối chiếu bằng Python → ghi phần chưa kiểm tra xong.

RFM gồm Recency — thời gian từ lần mua gần nhất đến mốc chốt, Frequency — số phiên mua riêng biệt và Monetary — tổng giá trị mua hợp lệ. Engagement là mức tương tác website, ở đây gồm số phiên và số lượt xem trong 30 ngày.

Với cutoff — mốc chốt — `T = 2020-02-01 00:00:00 UTC`, tập purchase hợp lệ `P_u` của user u theo code cũ yêu cầu event_type=purchase, price>0 và user_id hợp lệ:

- `R_u = (T - max(event_time trong P_u)).total_seconds() / 86400`, lưu làm tròn 2 chữ số.
- `F_u = số session_id khác nhau, khác NULL trong P_u`, gom riêng từng user. Khóa toàn bảng là `(user_id, session_id)`.
- `M_u = sum(price trong P_u)`, lưu làm tròn 2 chữ số; không suy orders/quantity/refunds/net GMV.
- `sessions_30d = số session_id khác nhau, khác NULL của user trong [T-30d,T)`.
- `views_30d = số event_type=view của user trong [T-30d,T)`; không phải số sản phẩm khác nhau. Theo code hiện tại, view thiếu session vẫn được đếm khi có user/time hợp lệ.
- `MiB = bytes / 2^20`; tránh gọi MiB là MB khi ghi kích thước chính xác.

Theo code cũ, buyer đủ RFM cần F>0 và M>0. Nếu không có purchase hợp lệ thì recency là **NULL**, nghĩa là không xác định; không gán 0 hoặc 999. Quy tắc cuối của MVP cần chốt ở P2.

Event ở đúng T bị loại khỏi observation. Nếu một phiên kéo dài qua mốc chốt, chỉ lấy từng event trước T. Đưa dữ liệu tương lai vào đặc trưng có thể gây **Data Leakage — rò rỉ dữ liệu**, khiến kết quả đánh giá bị sai lệch.

Thời gian UTC hiện dựa trên quy ước nguồn vì cột TIMESTAMP không kèm múi giờ. Điều này vẫn cần kiểm tra khi đọc lại CSV gốc.

## 4. Ví dụ tính tay để hiểu công thức

Đây là ví dụ giảng dạy, không phải số liệu nghiên cứu hoặc dữ liệu thay thế.

User A có hai purchase events trong cùng session s1 vào 20/01/2020 12:00:00 UTC, giá 10 và 20; có một view ở s1 và một view ở s2 ngày 21/01. Giả sử không có event khác:

- R = 11,5 ngày, F = 1 purchase session, M = 30 đơn vị giá.
- sessions_30d = 2, views_30d = 2.
- Nếu user B cũng có token s1, session của B khác session của A do khóa gồm user.
- Thêm một purchase vào đúng 01/02/2020 00:00:00 không được làm thay đổi feature tại cutoff này.

## 5. Có thể chọn cách xử lý khác không?

| Cách | Lợi ích | Đánh đổi |
|---|---|---|
| Đọc toàn CSV bằng pandas | Dễ quan sát với dữ liệu nhỏ | Không phù hợp khi materialize nhiều triệu event vào RAM; còn tệp bị khóa |
| DuckDB query Parquet | Đọc cột cần thiết, truy vấn event lớn mà không tạo pandas DataFrame toàn bảng | Vẫn cần xác minh lineage/cleaning; memory_limit không giới hạn cứng RSS |
| Tái dùng buyer_features | Nhỏ, dễ đưa lên Colab để học | Chỉ nhận sau khi chốt policy; phải bỏ biến ngoài F0/F1, không reuse scaler/model |
| Tái dựng từ raw | Kiểm soát policy rõ hơn | Tốn công/time/I/O, cần raw đầy đủ và log mới; thuộc P2, chưa làm ở đây |

Nhóm dùng DuckDB và thư viện chuẩn Python cho kiểm kê. PyArrow từng bị Windows Application Control chặn DLL, còn CSV tháng 12 bị tiến trình khác khóa một phần. Nhóm ghi lại giới hạn, không đổi chính sách bảo mật hoặc tự đóng tiến trình để vượt lỗi.

## 6. Đọc kết quả kiểm tra ra sao?

Ở P0-T1 có 15.667.350 event observation, 1.341.499 users và 92.652 buyers. Khi đối chiếu cả ba bảng customer/buyer/non-buyer, năm đặc trưng không lệch so với source theo quy tắc cũ. Có 191 token session được nhiều user dùng chung, nên khóa phiên phải gồm cả user và session.

Kiểm tra bổ sung dùng Python `set`, `datetime` và `Decimal` trên 30 users / 2.733 event thật, không có mismatch — sai lệch. Mẫu này được chọn theo tình trạng mua, mua lặp và hoạt động gần đây; không phải một cách tính độc lập cho mọi user.

Kết quả 5/5 + 4/4 checks và exit 0 cho biết các điều kiện đã kiểm tra đều đạt. Chưa thể dùng chúng để nói dữ liệu đã được nghiệm thu toàn bộ, mô hình tốt hoặc marketing hiệu quả.

## 7. Code và cách tự kiểm tra

Muốn chạy lại P0-T1 khi được giao, dùng Python có `duckdb==2.0.0`, mở terminal tại root repo rồi chạy:

```powershell
python -B scripts/audit_existing_artifacts.py --source 'DUONG_DAN_PROJECT_CU'
python -B scripts/verify_audit.py
```

Lần chạy ban đầu dùng Python sẵn có của dự án cũ. Lệnh và đường dẫn thực tế nằm trong `results/p0_t1/execution.json`. Không cần nạp model joblib hoặc import ETL cũ. Tùy chọn `-B` tránh ghi bytecode, còn script giới hạn nơi ghi kết quả trong repo MVP.

Trong `audit.json`, đọc `observation`, `cohorts`, `reconciliations`, `preservation` và `verification`. Trong `inventory.csv`, cột `reuse_decision` cho biết tệp có thể dùng vào mục đích nào. Các trường này giữ tên như trong code để nhóm dễ tìm.

Khi chuyển tệp, đối chiếu SHA256. Nếu file bị khóa và hash/schema là NULL thì phải ghi chưa kiểm tra được, không tự điền giá trị. Audit mất 19,691 giây trong lần chạy đã lưu; đó không phải benchmark — phép đo hiệu năng — của toàn pipeline và không có phép đo RSS mới. RSS là lượng bộ nhớ process đang dùng.

## 8. Những lỗi dễ mắc và giới hạn

- Đếm purchase rows thay cho số phiên mua; quên user trong khóa session.
- Đọc `clean_events.parquet` có cả February hoặc dùng wildcard — ký hiệu đọc gộp nhiều file — làm lẫn dữ liệu tương lai.
- Gán recency=0 cho non-buyers; gọi họ là khách chưa từng mua trong đời dù chỉ quan sát một khoảng thời gian.
- Dùng model/scaler 7D cho bảng 5D; gọi kết quả cũ là kết quả mô hình mới. Scaler là bộ biến đổi thang đo đã học từ dữ liệu.
- Nghĩ hash khớp chứng minh quy tắc xử lý đúng, hoặc cột TIMESTAMP tự chứng minh múi giờ UTC.
- Gọi RSS tại một thời điểm là bộ nhớ cao nhất đã lấy mẫu dù chưa đo như vậy.
- Gọi February là untouched test — tập kiểm chứng chưa từng được xem — chỉ vì tạo repository mới.
- Nghĩ không thấy notebook trong source tree đồng nghĩa không có notebook trên Drive hoặc máy khác.
- Kết luận hiệu quả marketing hoặc quan hệ nhân quả từ mô tả một cụm.

Ở P0-T1, nhóm chưa dựng lại raw→clean, chưa kiểm tra toàn bộ CSV, chưa giải quyết file lock hoặc xác minh xong license/currency. P0-T3 sau đó đã được sinh viên nghiệm thu trên Colab; mô hình MVP chưa chạy. Tính nhất quán của bảng hiện có không thay thế việc chốt quy tắc xử lý ở P2.

## 9. Câu hỏi tự kiểm tra

1. Một user có 5 purchase events trong một session thì Frequency là bao nhiêu? Vì sao không gọi là số orders? Nếu hai user dùng cùng session token thì khóa cần những cột nào?
2. Vì sao feature khớp với observation chưa đủ để nói cách loại trùng là đúng? Hash xác minh điều gì và không xác minh điều gì?
3. Tạo repo mới có biến February đã xem thành tập kiểm chứng độc lập chưa? Khi dùng dữ liệu này, nhóm phải mô tả ra sao?

Bài tập: tự tính lại ví dụ ở mục 4, chỉ ra event nào bị loại ở cutoff rồi mở JSON tìm bằng chứng cho các kết quả ở mục 6. Không đưa bảng có user IDs lên báo cáo public.

## 10. P0-T2 — Làm việc với repository, môi trường và đường dẫn

### Các khái niệm cần biết

**Repository — kho mã nguồn** là thư mục dự án cùng lịch sử thay đổi do Git quản lý; không nhất thiết chứa mọi dataset. Git giúp lưu phiên bản, so sánh và ghép code. GitHub là dịch vụ chia sẻ repo Git. Google Drive phù hợp để lưu/chia sẻ file và dữ liệu, nhưng đồng bộ Drive không thay thế commit, branch — nhánh phát triển — và việc xem xét thay đổi của Git.

**Virtual environment — môi trường ảo `.venv`** giữ các Python packages riêng cho project để giảm xung đột. Nó không phải máy ảo hoặc cách vượt chính sách Windows.

**Dependency — thư viện phụ thuộc** là thư viện chương trình cần dùng. `requirements.txt` cho pip biết cần cài gì. Một **lockfile — file khóa phiên bản** giúp cố định những phiên bản đã kiểm chứng. Requirements hiện tại chưa khóa đầy đủ, nên hai máy cài ở hai thời điểm chưa chắc có cùng bộ thư viện.

**Đường dẫn tuyệt đối** xác định vị trí từ ổ đĩa hoặc root filesystem. **Đường dẫn tương đối** cần một thư mục gốc để diễn giải. Với dữ liệu của dự án này, helper luôn lấy root repository làm gốc nếu cấu hình là đường dẫn tương đối.

### Vì sao chia thư mục?

| Thư mục | Vai trò | Ví dụ / trạng thái P0-T2 |
|---|---|---|
| `notebooks/` | Sổ thực hành gồm câu hỏi, lý thuyết, code, output và diễn giải | Hiện chỉ có hướng dẫn, chưa có notebook phân tích |
| `data/` | Vị trí mặc định cho dữ liệu riêng | Chỉ README vào Git; dataset chưa copy |
| `results/` | Bằng chứng chạy, metrics/figures khi được tạo | P0-T1 audit giữ nguyên, thêm logs cấu trúc P0-T2 |
| `docs/` | Kế hoạch, tiến độ và hai tài liệu tích lũy | Không giấu kết luận trong notebook không có nguồn |
| `scripts/` | Lệnh nhỏ dùng lại khi thật sự cần | Hai script audit và helper đường dẫn |
| `tests/` | Kiểm tra hành vi cần bảo vệ | Đường dẫn phải đúng khi đổi working directory |

`model/` chỉ tạo khi cần lưu mô hình mới ở P5, còn `app.py` chỉ tạo ở Phase 6. Git không theo dõi thư mục rỗng, nên README ngắn trong data/notebooks vừa hướng dẫn vừa giữ vị trí thư mục, không cần `.gitkeep`.

Không commit khoảng 20 triệu events gốc: CSV chiếm hàng GB theo inventory P0-T1, làm nặng clone/lịch sử Git và có định danh người dùng. Nhóm lưu code, hướng dẫn nguồn và manifest — bảng mô tả tệp — trong Git; dataset giữ riêng theo điều khoản nguồn. Xóa file ở commit sau cũng chưa tự xóa nó khỏi lịch sử trước.

### Đường dẫn được tìm như thế nào?

Gọi `R` là root repo, `E` là `REES46_DATA_ROOT`:

- E không có hoặc chỉ là khoảng trắng: `data_root = R / 'data'`.
- E tương đối: `data_root = resolve(R / E)`.
- E tuyệt đối: `data_root = resolve(E)`.
- `observation_path = data_root / 'cleaned' / 'observation_events.parquet'`.

`scripts/data_paths.py` chỉ tính đường dẫn; khi chạy CLI — dòng lệnh — còn kiểm tra file có tồn tại. Nó không tạo, đọc hoặc chấp nhận dataset về mặt nghiên cứu, cũng không mount Drive. Notebook sau này import helper từ root repo, không chép đường dẫn ổ đĩa riêng vào từng file.

### Ví dụ và cách thực hiện

Ví dụ để học: bạn A và bạn B clone repo ở hai nơi khác nhau. Cả hai đặt file tại `data/cleaned/observation_events.parquet` trong repo thì không cần sửa source. Nếu dataset nằm cạnh repo trong `datasets/rees46`, đặt `REES46_DATA_ROOT=../datasets/rees46`.

Sau khi thiết lập Colab ở P0-T3, nhóm có thể đặt root `/content/drive/MyDrive/datasets/rees46`. Đây mới là phương án cấu hình; P0-T2 chưa mount Drive hoặc kiểm tra nó trên Colab.

| Cách làm | Lợi ích | Giới hạn |
|---|---|---|
| Chỉ `Path('data/...')` | Ngắn | Phụ thuộc working directory hiện tại, dễ sai từ notebook |
| Root repo + biến môi trường | Một helper nhỏ, đổi máy không sửa code | Cần đặt env đúng và giữ hợp đồng thư mục `cleaned/` |
| Config framework / path manager nhiều lớp | Nhiều tùy chọn | Chưa có nhu cầu, tăng việc học và bảo trì nên không thêm |
| Requirements chưa pin | Khai báo phạm vi thư viện đơn giản | Chưa tái lập phiên bản đầy đủ; phải kiểm chứng/chốt ở P0-T3 |

`requirements-audit.txt` giữ pin — phiên bản cố định — của DuckDB đã dùng ở P0-T1; nó không thay `requirements.txt` cho toàn MVP. Không khai báo trực tiếp PyArrow không bảo đảm thư viện khác sẽ không kéo nó như một dependency bắc cầu. Lỗi import cũ vẫn còn mở.

### Chạy và đọc kết quả

Tại root repo, dùng Python sẵn có:

```text
python -B -m unittest discover -s tests -v
python -B scripts/data_paths.py
git diff --cached --name-only
git diff --check
```

Kết quả Codex ghi ở P0-T2 cho thấy sáu tests đường dẫn đã qua, gồm đổi working directory — thư mục làm việc — và không tạo file khi dữ liệu thiếu. Observation mặc định chưa tồn tại; không cần lấp chỗ trống này bằng dữ liệu giả. Lệnh, exit code và output nằm trong `results/p0_t2/commands.json`.

Sinh viên đã nghiệm thu P0-T2 dựa trên báo cáo 6/6 tests và 15/15 checks; chưa chạy lại local. Việc nghiệm thu không chứng minh cả bảy dependency đã tương thích hoặc môi trường mới chạy được toàn pipeline.

README có hướng dẫn tạo `.venv` và cài requirements, nhưng P0-T2 chưa cài mới. Có thể gọi trực tiếp `.venv/Scripts/python.exe` trên Windows mà không đổi execution policy. Mount Drive và chạy Colab là công việc của P0-T3.

### Lỗi dễ mắc và câu hỏi ôn tập

- Có tên thư viện trong requirements không có nghĩa thư viện đã được cài hoặc tương thích.
- `.gitignore` không tự bỏ file đã tracked/staged — được Git theo dõi/đưa vào vùng chuẩn bị commit. Luôn xem staging và không dùng `git add -f` với data.
- Helper in đường dẫn tuyệt đối sau khi resolve không có nghĩa source chứa đường dẫn cá nhân viết cứng.
- File tồn tại/hash khớp không giải quyết được cách loại trùng, điều kiện buyer hoặc quyền sử dụng.
- Chấp nhận P0-T1 có điều kiện không cho phép dùng model/scaler/labels/metrics 7D hoặc gọi February là untouched holdout.

1. Terminal đang ở `notebooks/` thì vì sao `Path('data/...')` có thể trỏ sai? Helper dùng root nào?
2. GitHub và Drive nên giữ những loại tệp nào? Vì sao không commit toàn bộ events rồi xóa sau?
3. Sáu tests đường dẫn PASS chứng minh được gì? Đã đủ để nói Colab, dependencies và pipeline chạy lại đầy đủ chưa?

## 11. P0-T3 — Bắt đầu với Google Colab và một tệp Parquet

### Colab, Drive và môi trường Python là gì?

Google Colab cho phép chạy notebook Python qua trình duyệt. Runtime — phiên chạy — giữ các biến và thư viện đang dùng; Google Drive giữ tệp lâu dài hơn phiên chạy. Jupyter local cũng chạy notebook nhưng dùng Python và tài nguyên trên máy của bạn. Vì môi trường khác nhau, một lần chạy local không chứng minh Colab đã hoạt động.

Notebook gồm ô Markdown để giải thích và ô Python để thực hiện. Chạy các ô theo thứ tự giúp hiểu biến được tạo ở đâu. Sau khi hoàn thành, khởi động lại runtime và chạy toàn bộ từ đầu để tránh trường hợp một ô chỉ chạy được vì còn biến từ lần trước.

Bài P0-T3 chỉ cần DuckDB ngoài thư viện chuẩn Python. Ô môi trường hiển thị phiên bản Python/DuckDB và chỉ cài DuckDB nếu chưa tìm thấy. Không cần cài pandas, scikit-learn, Streamlit hoặc PyArrow để làm những kiểm tra này. Điều này chưa xác nhận cả bảy dependency MVP hoặc một bộ phiên bản tương thích đầy đủ.

### Vì sao chọn Parquet và bảng buyer nhỏ?

Parquet lưu dữ liệu theo cột, thuận tiện khi chỉ đọc các cột cần thiết. DuckDB đọc được Parquet trực tiếp và tính số đếm bằng SQL; chưa cần đưa toàn bộ events vào pandas. Xem [hướng dẫn DuckDB](https://duckdb.org/docs/stable/data/parquet/overview).

Tệp `buyer_features.parquet` đã kiểm kê có 2.266.870 bytes, khoảng 2,16 MiB. Nó đủ để thực hành môi trường, đường dẫn và kiểm tra tệp; không cần upload hàng GB events. Tệp này vẫn là ứng viên, chưa được nghiệm thu làm đầu vào nghiên cứu.

### Mở notebook và kết nối Drive

1. Mở `notebooks/01_data_exploration.ipynb` bằng chức năng Upload notebook của Colab. Notebook chạy độc lập, không cần clone repo.
2. Chạy ô môi trường rồi ô mount Drive. Tự xác nhận quyền qua giao diện Google; không viết mật khẩu/token trong code hoặc output.
3. Nếu nhóm đồng ý đưa tệp lên Drive, chỉ chuyển bản buyer nhỏ vào `MyDrive/datasets/rees46/features/buyer_features.parquet`. Codex chưa upload dữ liệu hoặc đổi quyền chia sẻ.
4. Giữ mặc định hoặc sửa biến `DATA_ROOT` thành thư mục chứa `features/`. Chạy các ô còn lại theo thứ tự.

Ví dụ đường dẫn để học: với `DATA_ROOT` là `/content/drive/MyDrive/datasets/rees46`, file được ghép bằng:

```python
DATA_FILE = DATA_ROOT / "features" / "buyer_features.parquet"
```

Nếu chạy local, có thể đặt `REES46_DATA_ROOT` trong môi trường. Notebook không chứa đường dẫn Windows cố định và không tự copy dataset. Thiếu file thì đọc thông báo, kiểm tra Drive/root/thư mục, không tạo dữ liệu giả để bỏ qua lỗi. Tài liệu chính thức: [Colab FAQ](https://research.google.com/colaboratory/faq.html) và [Colab: tệp/Drive](https://colab.research.google.com/notebooks/io.ipynb).

### Đọc và tự giải thích kết quả

- **Schema:** tên và kiểu cột. Notebook chỉ in cấu trúc, không in dòng khách hàng. Tên cột user_id có thể xuất hiện trong schema, nhưng không có giá trị mã khách hàng.
- **Row count:** số dòng. Đúng bản P0-T1 có 92.652 dòng; ở bảng này một dòng/user, không phải một dòng/event hay một đơn hàng.
- **Feature table:** bảng dữ liệu đặc trưng. File có 23 cột bao gồm khóa/thông tin hỗ trợ; không có nghĩa đưa cả 23 cột vào K-Means. MVP vẫn chỉ chọn năm đặc trưng đã thống nhất.
- **Các số đếm kiểm tra:** số users riêng biệt bằng số dòng, số dòng thiếu khóa/đặc trưng hoặc không mang cờ buyer bằng 0. Đây là kiểm tra đọc file, chưa phân tích hành vi hay đánh giá mô hình.
- **SHA256:** so với mốc P0-T1 để biết bản chuyển lên Drive có cùng nội dung. Hash khác thì dừng tìm nguyên nhân, không thay mốc cho khớp file mới. Hash khớp chưa giải quyết cách làm sạch, buyer, session hoặc rounding.

Notebook lưu sẵn mốc schema/số dòng/bytes/hash chép từ `results/p0_t1/audit.json`; nhờ vậy không cần tải thêm manifest. Tám điều kiện đối chiếu đều phải đúng với đúng bản đã kiểm kê. Nếu dữ liệu thay đổi, phải có lần kiểm kê mới được ghi nhận, không tự sửa điều kiện để đánh dấu đạt.

### Đã kiểm tra gì và còn cần sinh viên làm gì?

Local đã mở/validate notebook bằng [nbformat](https://nbformat.readthedocs.io/en/latest/api.html), chạy 9 ô code theo thứ tự trong process Python mới và đọc tệp thật khớp P0-T1. Một lần chạy khác không có dataset đã dừng ở lỗi FileNotFoundError. Đó là kiểm tra bằng Python, không phải chạy qua Jupyter kernel hoặc tài khoản Colab.

nbformat chỉ dùng cho công cụ kiểm tra local; Codex cài nó vào `.tmp/notebook-validation`, không sửa môi trường của dự án cũ hoặc danh sách dependency chạy notebook. Kết quả/log nằm tại `results/p0_t3/`; script để kiểm tra lại là `scripts/verify_colab_notebook.py`.

Người dùng đã xác nhận hai bạn trực tiếp nghiệm thu P0-T3 trên Colab/Drive ngày 13/11/2026: **PASS (Student Verified)**. Chưa có log hoặc thông số runtime được gửi nên sổ tay không thêm chỉ số Colab. Khi notebook đổi, mỗi người vẫn khởi động lại runtime, chạy từ đầu và giải thích kết quả trước khi nghiệm thu phiên bản mới.

Những lỗi dễ mắc: chỉnh DATA_ROOT thành đường dẫn cả file thay vì thư mục gốc; quên thư mục features; chạy ô sau trước ô khai báo biến; nhìn thấy file mà cho rằng dữ liệu đã được nghiệm thu; gọi kết quả local là Colab thành công. Bảng đặc trưng không chứa event_time để tự kiểm tra lại cutoff từ từng event. Không dùng bước này để giải quyết vấn đề 7/9 trường, model 7D hoặc February đã được xem.

## 12. P0-T4 — Cộng tác mà không ghi đè bài của nhau

### GitHub và Drive giữ những gì?

GitHub main là bản code chính thức sau khi nhóm chấp nhận. Drive là nơi học, chạy notebook và lưu dữ liệu riêng. Một bản trên nhánh task chưa tự trở thành bản chính thức: cần người còn lại xem thay đổi trước khi đưa vào main.

**Commit** là một mốc phiên bản có thể quay lại xem; **branch — nhánh** giữ thay đổi của task riêng; **pull request (PR)** là chỗ đề nghị và xem thay đổi trước khi ghép. Đây là cách dùng GitHub đã có, không thêm công cụ quản lý mới. Khi bắt đầu task, ghi commit gốc và ai sửa chính trong PROGRESS để biết hai bạn có đang dùng cùng bản hay không.

### Ví dụ một lần bàn giao

Với notebook 01, README phân công Thành viên 1 sửa chính, Thành viên 2 kiểm tra. Hai bạn tự thống nhất ai giữ vai trò nào; tài liệu chưa tự đặt tên cá nhân. Thành viên 1 lưu bản Drive có tên TV1_work; Thành viên 2 chạy bản sao TV2_check và gửi nhận xét, không sửa đè TV1_work.

Sau khi chỉnh xong, khởi động lại runtime và chạy toàn bộ. Lưu bản có output phù hợp trên Drive trước khi bỏ output khỏi bản đưa lên GitHub. Ghi ngày, người chạy và kết quả thật trong nhật ký; giữ bảng kết quả tổng hợp cần đối chiếu dưới results. Không đưa user IDs, token hoặc đường dẫn cá nhân lên repo public. Bỏ output khỏi bản code không có nghĩa xóa bằng chứng; bằng chứng đã được giữ riêng.

Người sửa chính tổng hợp góp ý và tải bản cuối về, so với đúng code đã nghiệm thu. Chỉ bỏ output/thông tin riêng, không âm thầm sửa code sau nghiệm thu. Đưa lên nhánh task, xem diff — phần thay đổi — và nhờ người còn lại kiểm tra. Nếu GitHub có thay đổi mới hoặc Git báo xung đột thì đối chiếu từng phần, giữ bản đang làm; không force-push hoặc reset để ghi đè.

Sau khi nhóm chấp nhận bản bàn giao, đưa vào main và lần sau bắt đầu từ commit đó. Nếu cần đổi người sửa chính, ghi lại ở dòng phân công trong README trước khi tiếp tục. Các bản Drive cá nhân không cần biến thành nhiều notebook trùng lặp trong repo.

### Sau mỗi task và cách đọc kết quả nghiệm thu

Thực hiện → giải thích kiến thức → kiểm tra → cập nhật REPORT/LEARNING_GUIDE/PROGRESS khi phù hợp → dừng để sinh viên nghiệm thu. Ví dụ, task chỉ sửa quy trình thì kiểm tra tài liệu và việc bảo toàn file, không cần chạy lại ETL hoặc K-Means.

P0-T3 có hai nguồn thông tin khác nhau: logs local do Codex tạo và xác nhận Colab/Drive do sinh viên cung cấp qua người dùng ngày 13/11/2026. Có thể ghi PASS (Student Verified) theo xác nhận đó, nhưng không tự ghi Python/DuckDB version, thời gian hoặc số đo Colab chưa được gửi. Notebook gốc và logs local vẫn giữ nguyên để đối chiếu.

Tự kiểm tra: Ai được sửa bản chính của notebook đang làm? Khi bỏ output để đưa lên GitHub, bằng chứng đã được giữ ở đâu? Một PR đã tạo nhưng chưa đưa vào main đã đủ để gọi là bản chính thức chưa?

## 13. P1-T1 — Từ vấn đề kinh doanh đến câu hỏi nghiên cứu

### Vì sao website mỹ phẩm cần hiểu các nhóm khách?

Giả sử A mua thường xuyên, B từng mua nhưng lâu không quay lại, còn C mua ít nhưng hay xem sản phẩm. Nếu nhìn cả ba như nhau, doanh nghiệp khó biết ai đang mua đều, ai ít hoạt động và ai vẫn đang tìm hiểu. Phân khúc giúp mô tả các kiểu hành vi để đặt câu hỏi phù hợp: cần tìm hiểu lý do B ít hoạt động hay nội dung nào có thể hữu ích cho C?

Đó mới là hướng nghiên cứu. Chưa thể nói gửi ưu đãi cho B sẽ khiến B quay lại, hoặc C xem nhiều nên chắc chắn sắp mua. Khách có thể xem để so sánh, chưa tìm được sản phẩm hoặc vì nhiều lý do khác mà dữ liệu chưa giải thích được.

### Sáu khái niệm để lập luận rõ ràng

| Khái niệm | Là gì và vì sao cần? | Ví dụ của đề tài | Tự kiểm tra cách hiểu |
|---|---|---|---|
| Business Problem — vấn đề kinh doanh | Khó khăn thực tế cần hiểu; giúp đề tài có lý do bắt đầu | Chỉ nhìn tổng doanh thu chưa thấy các kiểu mua và quay lại website khác nhau | Nêu được khó khăn mà không mở đầu bằng tên thuật toán chưa? |
| Research Objective — mục tiêu nghiên cứu | Điều nhóm muốn tìm hiểu; giúp giới hạn công việc | So sánh cách mô tả buyers khi dùng RFM và khi thêm Engagement | Mục tiêu có gắn với vấn đề, hay chỉ ghi “chạy K-Means”? |
| Research Question — câu hỏi nghiên cứu | Câu hỏi cụ thể cần dữ liệu trả lời; giúp chọn phân tích | RQ2 hỏi hai biến tương tác có bổ sung sự phân biệt hành vi không | Chỉ được dữ liệu và kết quả nào sẽ giúp trả lời chưa? |
| Hypothesis — giả thuyết | Nhận định tạm thời có thể không được bằng chứng ủng hộ; tránh coi mong muốn là kết quả | F1 có thể phân biệt mức tương tác giữa buyers có RFM tương tự theo cách ổn định và dễ giải thích | Nếu cụm không ổn định hoặc không có cách diễn giải bổ sung, có chấp nhận chưa đủ bằng chứng không? |
| Evidence — bằng chứng | Kết quả có nguồn và cách kiểm tra; giúp nhận xét không dựa vào cảm giác | Bảng đặc điểm cụm, chỉ số và cấu hình/lần chạy thực ở Phase 5; hiện chưa có | Kết quả đã tạo thật chưa, lấy từ đâu, có khớp đối tượng so sánh không? |
| Baseline — phương án cơ sở | Mốc so sánh để biết phần thêm vào có giá trị gì | F0 dùng R, F, M trên cùng buyers với F1 | Bỏ hai biến tương tác thì còn đúng F0 không? Có vô tình dùng model 7D cũ làm mốc không? |

Các RQ và bảng dữ liệu → phương pháp → kết quả → đánh giá nằm ở mục 1–2 của [REPORT](REPORT.md). Không cần học sâu thuật toán K-Means ở P1-T1.

### Ví dụ 1 — Đọc RFM của ba khách hàng

**Các số dưới đây chỉ để tính tay, không lấy từ REES46 và không dùng làm dữ liệu nghiên cứu.** Giả sử mốc chốt `T = 01/02/2020 00:00 UTC`, chỉ xét các lần mua hợp lệ từ 01/10/2019 đến trước T. Mỗi ngày trong ví dụ có 24 giờ; giá dùng đơn vị minh họa, không khẳng định tiền tệ REES46.

| Khách | Lần mua gần nhất, lúc 00:00 UTC | R — ngày | F — phiên có mua duy nhất | M — tổng giá mua | Cách đọc |
|---|---|---:|---:|---:|---|
| A | 30/01/2020 | 2 | 6 | 120 | Mua gần đây, nhiều phiên mua và chi tiêu cao hơn hai người còn lại |
| B | 03/11/2019 | 90 | 2 | 40 | Lần mua cuối cách xa mốc chốt; riêng RFM chưa cho biết có quay lại xem hay không |
| C | 12/01/2020 | 20 | 1 | 20 | Mới có một phiên mua; muốn biết có hay xem sản phẩm phải xem thêm tương tác |

Recency là số ngày từ lần mua cuối đến T; R nhỏ nghĩa là mua gần hơn. Frequency đếm các phiên có mua riêng biệt theo từng user; Monetary cộng giá purchase hợp lệ. Công thức và giới hạn quy tắc cũ đã có ở mục 3, không thay đổi ở bài này.

Ví dụ một người có hai purchase events giá 10 và 20 trong cùng phiên s1: F tăng 1, M tăng 30. Không biết đó là một hay nhiều đơn hàng vì dataset không có order_id. Khi dữ liệu có mã đơn đáng tin cậy, doanh nghiệp có thể đếm các order_id khác nhau; nhóm hiện chỉ có chỉ báo thay thế bằng phiên có mua. Cùng token s1 ở hai user là hai khóa khác nhau: `(user_id, session_id)`.

### Ví dụ 2 — RFM giống nhau nhưng tương tác khác nhau

Tiếp tục dùng mốc T trên. Hai buyers D và E đều có lần mua cuối ngày 23/12/2019, R=40 ngày, F=2 phiên mua và M=50 đơn vị minh họa. Cửa sổ 30 ngày là `[02/01/2020, 01/02/2020)`, nên các lần mua của họ nằm trước cửa sổ này. Đây cũng chỉ là ví dụ học tập.

| Khách | R | F | M | sessions_30d | views_30d |
|---|---:|---:|---:|---:|---:|
| D | 40 | 2 | 50 | 0 | 0 |
| E | 40 | 2 | 50 | 8 | 25 |

F0 nhìn D và E qua cùng ba giá trị mua hàng. F1 thêm thông tin E vẫn tương tác trong 30 ngày, còn D không có hoạt động được ghi nhận trong cửa sổ đó. Hai hàng khác nhau không bảo đảm K-Means sẽ đưa họ vào hai cụm khác nhau, vì kết quả còn phụ thuộc các khách khác, thang đo và K.

`sessions_30d` đếm các phiên riêng biệt của user trong cửa sổ gần đây; một phiên có nhiều events vẫn chỉ tính một lần. `views_30d` đếm events xem sản phẩm, không phải số sản phẩm khác nhau. Hai biến mô tả việc quay lại và mức xem gần đây; không phải xác suất mua. Một phiên cũng có thể có purchase, nên Engagement không có nghĩa chỉ tính người chưa mua.

### RFM và Engagement khác nhau ở đâu?

| Nội dung | RFM trong đề tài | Engagement trong đề tài |
|---|---|---|
| Câu hỏi chính | Mua gần đây không, mua qua bao nhiêu phiên, tổng giá bao nhiêu? | Gần đây có bao nhiêu phiên và bao nhiêu lượt xem? |
| Dữ liệu cần | Purchase hợp lệ, thời gian, user, session, price | Events hợp lệ cho từng phép đếm, thời gian, user, session và loại view |
| Khoảng thời gian | Observation trước cutoff; R đo từ lần mua cuối | 30 ngày trước cùng cutoff |
| Điều chưa thể kết luận | R lớn không tự chứng minh đã ngừng truy cập hoặc rời bỏ | Xem nhiều không tự chứng minh ý định mua hoặc hiệu quả marketing |

Trong so sánh chính, F0 và F1 đều dùng cùng buyers có RFM hợp lệ. Non-buyers được mô tả riêng, không gán Recency bằng 0/999 để đưa vào K-Means.

### Kiểm chứng đề xuất bằng cách nào?

Nhóm sẽ đối chiếu F0 (R, F, M) với F1 (R, F, M, sessions_30d, views_30d). Mục 2 của REPORT chỉ rõ dữ liệu và đầu ra dự kiến cho mỗi RQ. Ở Phase 5, nhóm xem đồng thời chỉ số, cỡ cụm, đặc điểm trên cùng năm biến ở đơn vị gốc, mức ổn định và khả năng giải thích; chưa chạy bất kỳ phép so sánh nào ở P1-T1.

Silhouette và Davies–Bouldin phản ánh quan hệ khoảng cách của các cụm, không đo tỷ lệ dự đoán đúng. Vì thêm biến làm thay đổi không gian khoảng cách, một điểm Silhouette cao hơn chưa đủ kết luận F1 tốt hơn. Định nghĩa chính thức nằm tại [Silhouette](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.silhouette_score.html) và [Davies–Bouldin](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.davies_bouldin_score.html); công thức chi tiết sẽ học ở Phase 5.

Lựa chọn đơn giản hơn là chỉ giữ F0 nếu phần bổ sung chưa cho thấy giá trị rõ. Giả thuyết không được ủng hộ vẫn là kết quả cần báo cáo. Nếu đề xuất một hướng marketing từ đặc điểm cụm, muốn kết luận hiệu quả cần một thử nghiệm riêng; trong bài này chưa thực hiện chiến dịch.

### Ba câu hỏi tự kiểm tra và gợi ý trả lời

Hai bạn trả lời riêng trước khi xem gợi ý, rồi giải thích cho nhau; không cần chạy notebook cho task này.

1. Một user có ba purchase events trong cùng một phiên hợp lệ thì F tăng bao nhiêu? Vì sao chưa được gọi là ba đơn hàng?
2. D và E trong ví dụ 2 giống nhau ở đâu, khác nhau ở đâu? Việc E có 25 views có chứng minh E sắp mua không?
3. Nếu F1 có Silhouette cao hơn F0, nhóm đã trả lời xong RQ2 và chứng minh marketing hiệu quả chưa? Cần kiểm tra thêm gì?

**Gợi ý đối chiếu:** (1) F tăng 1; events không phải order_id và phải gộp theo user-session. (2) Cùng R/F/M nhưng khác tương tác gần đây; chưa có bằng chứng về lần mua tương lai. (3) Chưa: cần cùng buyers/cutoff, xem cỡ và đặc điểm cụm trên đơn vị gốc, sự ổn định, khả năng giải thích và tài nguyên. Khác không gian khoảng cách nên không chỉ so một điểm; hiệu quả chiến dịch cần thử nghiệm riêng.

## 14. P1-T2 — Học RFM từ repository Online Retail

### 14.1. Đọc code theo luồng dữ liệu

Nguồn đọc và bảng so sánh với REES46 nằm ở REPORT mục 3. Nhóm dùng commit `d4a8a864ef0128708a0cd0a0e2799faf23b9dd60`; số ô dưới đây gồm cả Markdown, đếm từ 1. Không cần học Flask/HTML/CSS hoặc chạy model ở bài này.

Luồng chính là: dòng mặt hàng → bỏ dòng thiếu mã khách → tính giá dòng → gom thành RFM mỗi khách → biến đổi log → chuẩn hóa → K-Means → xem đặc điểm và đặt tên. Bỏ CustomerID thiếu vì không biết dòng thuộc người nào để gom RFM; không có nghĩa những giao dịch đó không có giá trị với mọi bài toán khác.

Trong [ô 8 của notebook](https://github.com/ch1ns0n/Customer-Segmentation/blob/d4a8a864ef0128708a0cd0a0e2799faf23b9dd60/Customer_Segmentation_Model.ipynb), `InvoiceNo` được gom bằng `nunique`, nghĩa là đếm mã khác nhau; `TotalPrice` được cộng bằng `sum`. Mốc tính R là thời điểm InvoiceDate lớn nhất còn lại cộng một ngày. Chênh lệch được lấy bằng `.days`, tức số ngày nguyên; đừng tự coi đó là ngày UTC hoặc công thức làm tròn hai chữ số của REES46.

### 14.2. Ví dụ tính RFM bằng tay cho hai khách

**Đây là số minh họa để học, không lấy từ Excel hoặc REES46 và không thay thế dữ liệu nghiên cứu.** Giả sử các thời điểm đều lúc 00:00 và không có hủy/hoàn trả:

| Khách | InvoiceNo minh họa | Ngày | Quantity | UnitPrice minh họa | Giá dòng |
|---|---|---|---:|---:|---:|
| A | 1001 | 01/12/2011 | 2 | 10 | 20 |
| A | 1001 | 01/12/2011 | 1 | 5 | 5 |
| A | 1002 | 08/12/2011 | 1 | 15 | 15 |
| B | 2001 | 05/12/2011 | 3 | 10 | 30 |

Ngày cuối trong ví dụ là 08/12, nên theo cách đặt mốc của repo, ngày tham chiếu là **09/12/2011**. Kết quả tính tay:

| Khách | R — ngày | F — hóa đơn riêng biệt | M — tổng giá dòng |
|---|---:|---:|---:|
| A | 1 | 2 | 40 |
| B | 4 | 1 | 30 |

A có ba dòng nhưng chỉ hai hóa đơn. Hóa đơn 1001 gồm hai sản phẩm, giá cộng là 20+5=25; M của A là 25+15=40. B mua ba đơn vị giá 10 nên M=30, không phải 10. Vì vậy cần TotalPrice = Quantity × UnitPrice trước khi cộng theo khách.

Với REES46, mỗi dòng là event và không có Quantity/InvoiceNo như trên. Nhóm không tự nhân price với số lượng hoặc đếm purchase rows làm Frequency. Vẫn dùng số phiên có mua riêng biệt; công thức REES46 ở mục 3 không thay đổi.

### 14.3. Log transformation — biến đổi log

Ô 12 dùng log1p, tức `ln(1+x)` — log tự nhiên của 1+x theo [NumPy](https://numpy.org/doc/stable/reference/generated/numpy.log1p.html). Ví dụ F=1 và F=9 biến thành khoảng 0,6931 và 2,3026. Chênh lệch từ 8 trên thang gốc còn khoảng 1,6094 trên thang log. Mục đích là giảm sự chênh lệch quá lớn, không làm mọi phân phối tự động thành chuẩn hoặc bảo đảm K-Means tốt hơn.

Khi đọc ô 12–14 cần chú ý thứ tự: Monetary được log trước, rồi ở ô 14 được tính lại theo quy tắc M>0 mới lấy log; M≤0 được đưa về 0. Tên cột giữ nguyên nhưng cách tính đã đổi. Với M=−5, log1p trực tiếp không cho kết quả thực hữu hạn; việc đổi nó thành 0 còn làm mất thông tin về giá trị âm. Đây là lựa chọn của repo cần nhận xét, chưa phải cách xử lý hoàn trả của nhóm.

Lựa chọn khác là giữ thang gốc hoặc xem xét biến đổi khác sau khi hiểu dữ liệu. Trong MVP, nhóm chưa quyết định biến đổi ở P1-T2; cleaning policy chờ Phase 2 và lựa chọn biến đổi chờ Phase 4.

### 14.4. StandardScaler — chuẩn hóa thang đo

Nếu một biến đo bằng ngày và một biến có giá trị tiền lớn, khoảng cách có thể bị biến có thang đo lớn chi phối. StandardScaler lấy từng giá trị trừ trung bình rồi chia độ lệch chuẩn đã học: `z = (x − mean) / std`. Nó không đưa mọi giá trị vào [0,1], không tự sửa giá trị âm, không loại outliers và không chọn K. Xem [tài liệu scikit-learn](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html).

Ví dụ một cột có hai giá trị minh họa [1,3]: mean=2, std=1 khi chia phương sai cho n như StandardScaler mặc định. Hai giá trị chuẩn hóa là [−1,1]. Với giá trị mới 5, dùng lại mean/std cũ được z=3; không học lại scaler chỉ trên một người mới.

Ô 15 học scaler trên ba cột theo thứ tự R, Frequency_log, Monetary_log. Log thay đổi quan hệ giữa các mức giá trị; scaler điều chỉnh thang đo từng cột. Hai thao tác này khác nhau. Khi giải thích cụm, quay lại R/F/M gốc để nói về ngày, hóa đơn và giá, thay vì gọi z=1 là “một đơn vị tiền”.

### 14.5. K-Means ở mức khái niệm và cách chọn K

Hãy xem mỗi khách là một điểm có ba tọa độ RFM đã biến đổi/chuẩn hóa. Với K tâm cụm, thuật toán gán điểm về tâm gần, cập nhật tâm bằng trung bình các điểm trong cụm rồi lặp lại. K là số nhóm phải chọn; thuật toán không biết trước ai là khách trung thành. Đây là cách hiểu khái niệm từ [hướng dẫn K-Means](https://scikit-learn.org/stable/modules/clustering.html#k-means), chưa cần học công thức tối ưu.

Ô 16 thử K từ 1 đến 10 và vẽ inertia — tổng khoảng cách bình phương từ các điểm đến tâm được gán. Elbow — phương pháp khuỷu tay — tìm chỗ đường giảm bắt đầu bớt rõ; tăng K có thể giảm inertia mà chưa tạo nhóm hữu ích hơn. Ô 18 đặt K=4, seed=42 để cố định nguồn ngẫu nhiên khi khởi tạo; README nói chọn K thủ công theo khả năng diễn giải. Không có lệnh tự chọn điểm gãy hoặc đánh giá nhiều seed trong các file đã đọc. Vì vậy không chép K=4 sang REES46.

Các biểu đồ và bảng trung bình ô 19–26 giúp nhìn đặc điểm cụm. PCA — phân tích thành phần chính — ở ô 23 chỉ phục vụ hình hai chiều sau khi mô hình đã fit trên ba biến; hình đẹp không chứng minh phân cụm đúng nghiệp vụ. Cách so sánh nhiều tiêu chí của MVP sẽ thực hiện ở Phase 5.

### 14.6. Tên cụm và tính nhất quán với web demo

Ô 24 tự ánh xạ nhãn 0–3 sang bốn tên. Ví dụ tên Loyal High-Spenders gắn với cụm có mua nhiều/chi tiêu cao trong bảng trung bình được lưu. Số 0,1,2,3 chỉ là định danh, không phải xếp hạng và không giữ cùng ý nghĩa khi đổi dataset/lần fit. Tên Potential Loyalists là diễn giải, chưa chứng minh khách sẽ trung thành trong tương lai.

Trong [app.py](https://github.com/ch1ns0n/Customer-Segmentation/blob/d4a8a864ef0128708a0cd0a0e2799faf23b9dd60/customer_segmentation_app/app.py), luồng là R/F/M nhập vào → log F/M → scaler đã học → model đã học → dictionary tên. Không fit lại scaler trên form, không đổi thứ tự cột. Gán cụm bằng `predict` không trả xác suất mua.

Điểm chưa thống nhất là ô 14 đưa M≤0 về 0 còn web gọi log1p(M) trực tiếp. Với M=−0,5, hai cách cho 0 và khoảng −0,6931; với M=−5, cách web không cho giá trị thực hữu hạn. Vì vậy cần cùng định nghĩa, miền đầu vào và chuỗi biến đổi, không chỉ cùng tên file model/scaler. Nhóm chưa nạp pickle nên chưa xác nhận các file lưu sẵn khớp code này.

### 14.7. Những lỗi dễ mắc

- Đếm dòng sản phẩm thành số hóa đơn, hoặc coi hóa đơn hủy cũng là một lần mua mà không giải thích.
- Lấy ngày hủy/hoàn trả làm lần mua cuối vì chưa chốt điều kiện giao dịch hợp lệ.
- Chép quy tắc giá âm bằng 0 chỉ để log chạy được; đổi cách biến đổi giữa notebook và web.
- Chép K=4, tên cụm hoặc đường dẫn Windows ở ô xuất model sang MVP.
- So điểm phân cụm giữa hai dataset/không gian khác nhau như cùng một thước đo, hoặc coi inertia/PCA là độ chính xác dự đoán.

### 14.8. Ba câu hỏi và gợi ý tự kiểm tra

Hai bạn trả lời riêng rồi đối chiếu code/công thức; không cần chạy notebook tham khảo:

1. Trong ví dụ, vì sao A có ba dòng nhưng F=2, M=40? Nếu là REES46, vì sao không dùng InvoiceNo để tính F?
2. Log và StandardScaler có cùng mục đích không? Với cột [1,3], mean=2, std=1, giá trị mới 5 được biến đổi thế nào và vì sao không fit lại scaler?
3. Repo chọn K=4 và đặt tên cụm dựa trên đâu? Vì sao chưa thể chép K/tên cụm sang REES46 hoặc dùng trực tiếp cách log M của web cho mọi giá trị?

**Gợi ý:** (1) Hai InvoiceNo khác nhau, M=2×10+1×5+1×15=40. REES46 không có InvoiceNo/order_id nên dùng phiên có mua. (2) Log nén chênh lệch mức giá trị; scaler đưa về thang đo dựa trên mean/std đã học. Giá trị 5 thành z=3; fit lại sẽ đổi hệ tọa độ so với model. (3) Có Elbow và lý do diễn giải, nhưng K được đặt thủ công; tên được gán bằng dictionary sau khi xem đặc điểm cụm. Dữ liệu và định nghĩa khác nên phải kiểm tra lại. Quy tắc M≤0 của notebook khác web; chưa có chính sách giá âm chung để sao chép.
