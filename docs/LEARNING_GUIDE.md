# Sổ tay học tập — MVP RFM + Engagement

**Cập nhật 13/11/2026.** Phần 1–17 giữ kiến thức/diễn biến đã nghiệm thu; phần 18 học P2-T2 theo cách gọn hơn: notebook, bảng chính và hình đơn giản. P2-T1 PASS; P2-T2 READY FOR STUDENT REVIEW. Kết quả mới là chạy local trên bốn CSV, chưa có xác nhận Colab mới.

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

## 15. P1-T3 — Học cách mở rộng RFM từ bài nghiên cứu RFM-B

### 15.1. Đọc bài báo khác với chấp nhận kết luận

Nguồn là [bài RFM-B, v1 ngày 13/04/2026](https://www.preprints.org/manuscript/202604.0852/v1), chưa qua bình duyệt. REPORT mục 3.5–3.9 ghi định nghĩa, kết quả tác giả công bố và nhận xét của nhóm. Ở bài học này chỉ đọc, tính ví dụ nhỏ và kiểm tra cách lập luận; không tái tạo mô hình hoặc thay đổi F0/F1.

Khi đọc một kết luận, tự hỏi: tác giả muốn giải quyết gì, đo bằng đại lượng nào, mẫu số là gì, so với phương án nào, và kết quả có đủ để khẳng định điều đó không? “Tác giả công bố” khác với “nhóm đã chạy và kiểm chứng”. Các ví dụ tiếp theo **đều do nhóm đặt để học, không phải số liệu bài báo hoặc REES46**.

### 15.2. CVR: tỷ số event không phải tỷ lệ phiên

Với một khách trong cùng cửa sổ, gọi P là số purchase events và V là số view events. Định nghĩa ở Bảng 2 dùng `CVR_event = P/V`, khi V>0. Nó mô tả mức đếm mua so với mức đếm xem, không trực tiếp cho biết bao nhiêu phiên hoặc người đã chuyển thành mua hàng.

| Phiên minh họa | View events | Purchase events |
|---|---:|---:|
| s1 | 5 | 3 |
| s2 | 5 | 0 |

Trong ví dụ này, P/V=3/10=0,3. Nếu định nghĩa tỷ lệ phiên có mua là số phiên có ít nhất một purchase chia tổng phiên hợp lệ, kết quả là 1/2=0,5. Ba purchase events nằm trong một phiên, nên không được đổi 0,3 thành “30% phiên có mua”. Đây là phản ví dụ tính tay, chưa phải định nghĩa KPI mới của MVP.

V=0 thì phép chia chưa xác định, không tự gán 0 hoặc cộng 1 cho mẫu số. Tỷ số event có thể lớn hơn 1, chẳng hạn P=4, V=1 cho 4; nó không mặc nhiên là xác suất. Khi áp dụng Cosmetics cần kiểm tra loại event, user, thời gian, chất lượng session và điều kiện hợp lệ; phần văn giải thích theo phiên không được thay công thức event của Bảng 2 mà không nói rõ.

### 15.3. AOV: gọi tên theo đúng mẫu số

Trong bài, `AOV_proxy = M/F`, với F là số phiên có mua riêng biệt. M=300, F=2 cho 150 đơn vị giá **mỗi phiên mua**. Đây là Average Spend per Purchase Session, không phải bình quân mỗi order thật khi REES46 không có order_id. Chỉ tính khi F>0; không gán giá trị tùy ý cho non-buyers.

| Khách minh họa | M | F — phiên có mua | M/F |
|---|---:|---:|---:|
| A | 300 | 2 | 150 |
| B | 300 | 10 | 30 |

A mua ít phiên hơn nhưng chi nhiều hơn mỗi phiên; B có nhiều phiên nhưng mức chi mỗi phiên thấp hơn. RFM đã phân biệt họ qua F; AOV giúp diễn đạt tỷ số M/F rõ hơn, không bảo đảm thuật toán sẽ cho hai cụm khác nhau. Vì M/F suy ra từ hai số đã có, không tự gọi nó là thông tin độc lập hoặc bằng chứng mô hình tốt hơn.

Để liên hệ Cosmetics, cần cùng tập purchase hợp lệ cho M và F, khóa user-session rõ và chính sách giá/làm tròn đã chốt. Đơn vị giá/currency còn mở; không mang nhãn USD của bài báo sang dữ liệu nhóm.

### 15.4. Category Breadth và Brand Diversity

**Category Breadth — độ rộng danh mục mua:** công thức là số nhóm danh mục cấp cao khác nhau mà khách đã mua. Giả sử ba category_id 10, 11, 20 được một bản đồ danh mục minh họa xác nhận lần lượt thuộc nhóm cấp cao Chăm sóc da, Chăm sóc da, Chăm sóc tóc. Số ID là 3 nhưng độ rộng cấp cao là 2. Nó cho biết phạm vi danh mục đã mua, chưa chứng minh khách gắn bó hơn.

Với Cosmetics, cần xác minh category_id đại diện cấp nào, có bản đồ phân cấp hay category_code đáng tin không, và phần bị thiếu ảnh hưởng ra sao. Không tự giả sử mỗi ID là một nhóm cấp cao, hoặc ép số nhóm tối đa theo nền tảng multi-category của bài báo.

**Brand Diversity — độ đa dạng thương hiệu mua:** công thức là số thương hiệu khác nhau trong các lần mua. Ví dụ A, A, B và một giá trị thiếu cho thấy **hai thương hiệu được quan sát**; phần thiếu vẫn chưa biết. Không biến missing thành thương hiệu “Unknown” rồi tính thêm một, cũng không suy một brand duy nhất là bằng chứng lòng trung thành.

Muốn áp dụng cần kiểm tra missing brand, chuỗi rỗng, cách viết hoa/thường và tên chuẩn nếu có. Chưa đọc các phân phối này ở P1-T3, không điền thương hiệu giả hoặc tự chốt quy tắc chuẩn hóa. Cả hai biến chỉ là ứng viên có điều kiện về dữ liệu, chưa được đưa vào MVP.

### 15.5. Hiểu bước Random Forest mà không triển khai

Luồng cần phân biệt là: bảy đặc trưng → K-Means → nhãn cụm; sau đó Random Forest học dự đoán **nhãn cụm đó**. Bảng kết quả công bố được giữ ở REPORT mục 3.7. Nhãn đích không phải “sẽ mua tháng tới”, và bộ phân loại không kiểm tra hiệu quả chiến dịch.

Ví dụ tính tay khác: nếu bộ phân loại khớp nhãn K-Means của 9 trong 10 khách kiểm tra, accuracy phục hồi nhãn là 9/10=90%. Điều đó không có nghĩa 90% khách sẽ mua, hoặc 90% gợi ý marketing có tác dụng. Đây chỉ là ví dụ về ý nghĩa mẫu số, không phải accuracy bài báo/MVP.

Feature importance trong bộ phân loại cho biết biến giúp phân biệt các nhãn đó; không tự chứng minh nguyên nhân mua hoặc lợi nhuận. Bài học có thể hiểu bằng luồng trên, không cần huấn luyện thêm Random Forest trong MVP.

### 15.6. Cần đối chứng gì và vì sao chưa dùng đủ bảy biến?

Trong các phần phương pháp/kết quả và bảng đã đọc, nhóm chưa tìm thấy đối chứng rõ RFM 3D với RFM-B 7D trên cùng tập khách và cùng quy trình. Không lấy một kết quả 7D, hình PCA hoặc accuracy chép nhãn cao làm bằng chứng phương án đó vượt RFM.

Một so sánh có ích cần giữ cùng khách, cutoff và điều kiện dữ liệu; ghi rõ cách chuẩn hóa/lựa chọn K; xem nhiều tiêu chí và đặc điểm cụm trên thang gốc. Các không gian có số chiều khác nhau không được xếp hạng bằng một điểm Silhouette đơn lẻ. Đây là cách đọc bằng chứng; P1-T3 không chạy thí nghiệm để sửa bài báo.

Nhóm dùng Cosmetics, còn bài dùng REES46 multi-category; không mặc định schema, cấp danh mục, missing, số khách hoặc cleaning giống nhau. Khoảng quan sát ngắn cũng không đủ để khẳng định một kiểu hành vi bền vững; tên “Lost” hoặc “Potential Loyalists” không phải nhãn tương lai đã xác minh.

MVP giữ F0=R/F/M và F1 thêm sessions_30d/views_30d. Hai phép đếm mô tả việc quay lại và xem gần cutoff, dễ nối với câu hỏi nghiên cứu và phạm vi học hiện tại. Chưa chứng minh chúng tốt nhất; cũng không cần thêm mọi biến đã đọc để gọi là vận dụng bài báo. P1-T4 sẽ tiếp tục phần lý do lựa chọn sau nghiệm thu, không làm trong task này.

### 15.7. Ba câu hỏi tự kiểm tra

Hai bạn tự trả lời trước khi đọc gợi ý:

1. CVR tính bằng purchase events / view events có giống tỷ lệ phiên có mua không? Vì sao?
2. Một khách có Monetary=300 và Frequency=2 thì AOV proxy bằng bao nhiêu? Tại sao không gọi đó là giá trị đơn hàng trung bình thực tế?
3. Bài báo có bảy đặc trưng, vậy tại sao nhóm không bắt buộc dùng đủ bảy? Muốn biết đặc trưng bổ sung có ích thì cần thực nghiệm như thế nào?

**Gợi ý đối chiếu:** (1) Không: event và session khác đơn vị đếm; ví dụ 3/10=0,3 nhưng chỉ 1/2 phiên có mua. (2) 150 đơn vị giá/phiên mua; không có order_id để gọi là giá trị mỗi đơn. (3) Cần phù hợp dữ liệu, câu hỏi và phạm vi; giữ F0/F1 như kế hoạch. Muốn đánh giá phần thêm vào cần đối chứng cùng khách/cutoff, quy trình minh bạch và nhiều tiêu chí, không mặc định nhiều biến hơn là tốt hơn. P1-T3 chưa thực hiện đối chứng đó.

Lỗi dễ mắc: gọi event ratio là xác suất phiên mua; coi purchase session là đơn hàng; đếm category_id thành danh mục cấp cao; đếm missing brand thành thương hiệu; gọi accuracy phục hồi nhãn là độ chính xác mua hàng; mang K=5/metrics hoặc model 7D cũ vào kết quả MVP.

## 16. P1-T4 — Thiết kế cải tiến có kiểm chứng

### 16.1. Baseline, cải tiến và giả thuyết

Baseline là phương án cơ sở để biết trước khi thay đổi ta đang có gì. Trong dự án, F0 dùng R/F/M và K-Means. Cải tiến mô hình không nhất thiết đổi thuật toán; có thể sửa cách biểu diễn dữ liệu hoặc bổ sung thông tin có lý do. F1 vẫn K-Means, thêm sessions_30d và views_30d. Chưa chạy thì chỉ gọi F1 là **đề xuất cải tiến**.

Giả thuyết là nhận định cần bằng chứng để kiểm tra. H1 nói Engagement có thể bổ sung khác biệt hành vi; H2 nói tiền xử lý phù hợp có thể giúp phân cụm trong cùng bộ biến; H3 nói hồ sơ rõ có thể giúp viết gợi ý marketing có căn cứ. Chúng không phải ba kết luận đã đạt.

Cách làm: chạy F0 ở Phase 5 → ghi hạn chế thực sự thấy và bằng chứng → nêu thay đổi nào có thể giúp → giữ điều kiện so sánh → chạy và đọc cả kết quả thuận lợi lẫn bất lợi. Không viết trước rằng dữ liệu lệch hoặc F0 chia cụm xấu khi chưa quan sát. Làm sạch đúng giúp đầu vào đáng tin, nhưng chưa chứng minh mô hình tốt hơn.

### 16.2. Vì sao F0/F1 khác nhau? Ví dụ minh họa

Ví dụ sau do nhóm đặt để học, **không phải khách REES46 hoặc kết quả mô hình**. Cùng mốc T=01/02/2020, A và B đều có R=40 ngày, F=2 phiên mua, M=50 đơn vị giá; A có 0 phiên/0 lượt xem trong 30 ngày, B có 8 phiên/25 lượt xem và chưa mua thêm. Lần mua gần nhất trước cửa sổ 30 ngày nên tình huống này không mâu thuẫn với số phiên gần đây của A.

F0 thấy hai vector giống nhau `[40,2,50]`. F1 thấy `[40,2,50,0,0]` và `[40,2,50,8,25]`. Hai biến mới cho biết B vẫn quay lại và xem. Điều đó không bảo đảm K-Means tách A/B thành hai cụm, không nói B sắp mua và không chứng minh gợi ý gửi cho B sẽ hiệu quả.

F đếm hai **phiên có mua**, dù mỗi phiên có nhiều purchase events; M cộng price hợp lệ, chưa phải doanh thu ròng. Công thức đầy đủ năm biến, cửa sổ, dữ liệu cần và các quy tắc chờ Phase 2 ở REPORT phần thiết kế mục B. Không tự điền recency cho non-buyers.

CVR cần rõ mẫu số event/phiên và xử lý mẫu số 0. AOV proxy M/F suy từ RFM, không phải giá trị mỗi order thật. Category Breadth cần biết cấp danh mục, Brand Diversity cần kiểm tra missing/chuẩn hóa brand. Hai phép đếm hiện tại đơn giản và sát RQ2; chưa có bằng chứng chúng tối ưu hoặc cần thêm tất cả biến trong bài báo.

### 16.3. Log khác scaling; kiểm tra từng thay đổi

Log1p là `ln(1+x)`, thường dùng để nén chênh lệch mức lớn khi miền dữ liệu phù hợp. Ví dụ x=0,9,99 cho khoảng 0; 2,3026; 4,6052. Đây là phép tính minh họa, chưa phải quyết định lấy log cột nào. Không thay giá âm/thiếu thành 0 chỉ để log chạy được.

StandardScaler chuẩn hóa từng cột theo `z=(x−mean)/std`, học mean/std từ tập dùng để fit rồi dùng lại khi transform. Ví dụ cột [1,3] có mean=2, std=1 theo cách tính của scaler, trở thành [−1,1]. Nó đổi thang đo, không tự làm phân phối hết lệch hoặc loại ảnh hưởng outliers; xem [tài liệu StandardScaler](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html). Không chuẩn hóa chung các đơn vị ngày/giá/lượt bằng một mean/std duy nhất.

Nếu vừa thêm hai biến vừa thêm log rồi thấy điểm đổi, chưa biết phần nào gây ra. Vì vậy H2 cần giữ F0, cùng buyers, K, seed và cấu hình; ví dụ so **StandardScaler** với **log1p trên các cột đã chọn rồi StandardScaler** để kiểm tra riêng bước log. Chỉ làm nếu dữ liệu gợi ý cần, không cố tạo một baseline xử lý sai để chứng minh thắng. Cột/rule được ghi trước ở Phase 4; P1-T4 không chạy biến đổi hoặc mô hình.

Log/scaling cũng đổi hình học khoảng cách. Điểm Silhouette tăng sau biến đổi chưa đủ để nói tốt hơn về nghiệp vụ; phải xem hồ sơ gốc, cỡ cụm và ổn định. Khi so F0/F1, ba cột RFM chung dùng cùng quy tắc biến đổi, nhưng fit hai scaler riêng theo đúng ba/năm cột. Không nạp scaler/model 7D cũ.

### 16.4. So sánh thế nào để có ích?

Giữ cùng buyers, thời gian, cleaning policy đã chốt và K-Means. Kế hoạch thử K=2–6 với ba seed [0,21,42], n_init=10 cho cả F0/F1; đây là lựa chọn thiết kế, chưa có lần fit. `random_state` điều khiển ngẫu nhiên khởi tạo; `n_init` là số khởi tạo trong một lần fit, không phải số cụm. Cấu hình đầy đủ và quy trình lưu hạn chế F0 trước F1 ở REPORT mục D.

So Silhouette, DBI, cỡ/tỷ lệ cụm, hồ sơ cùng năm biến gốc và chi phí. ARI so sự giống nhau giữa các cách chia qua seed: nếu chỉ đổi tên cụm 0↔1 thì cách chia vẫn như cũ; đây không phải accuracy so với nhãn mua hàng. Ba seed chỉ kiểm tra khởi tạo, không chứng minh ổn định theo mùa. Đọc các trường hợp cùng K để xem ảnh hưởng thêm biến; khi chọn mô hình cuối có thể chọn K khác nhau, nhưng phải nói rõ phần thay đổi đó.

F0 chỉ fit ba biến nhưng vẫn dùng đủ năm biến để **mô tả cụm sau khi fit**. Quy tắc chọn nhóm RFM tương tự phải ghi từ F0 trước khi xem F1, dùng lại cho cả hai. Nếu F1 tách theo lượt xem, đó cũng là hệ quả trực tiếp của đầu vào; cần xem có đặc điểm rõ, đủ khách và lặp lại qua seed không. Không chọn vài khách thuận lợi làm bằng chứng cho toàn bộ dữ liệu.

Nếu F1 khó giải thích, không ổn định hoặc không thêm thông tin đáng kể, có thể giữ F0 và báo cáo giới hạn H1. Nếu chỉ một mặt hữu ích còn mặt khác kém, trình bày các mặt được/mất, không đặt trọng số tùy ý hoặc chỉ lấy seed/điểm đẹp nhất.

### 16.5. Từ phân khúc đến hỗ trợ marketing

Luồng đọc là **cụm → đặc điểm quan sát → mục tiêu → hành động gợi ý → căn cứ → KPI → hạn chế**. KPI là chỉ số để theo dõi, cần nêu rõ đếm gì, trên ai và trong khoảng nào. Ví dụ có điều kiện: nếu quan sát được nhóm lâu chưa mua nhưng còn xem, có thể gợi ý thử nội dung hỗ trợ lựa chọn; chưa biết vì sao họ chưa mua hoặc thông điệp nào hiệu quả.

Số phiên/lượt xem hiện tại là mô tả. Tỷ lệ phản hồi hoặc doanh thu tăng nhờ chiến dịch cần dữ liệu tiếp cận và thử nghiệm đối chứng riêng; không suy được từ cụm. Phase 6 chỉ trình bày hồ sơ/bảng gợi ý, không gửi chiến dịch hay xây decision engine.

### 16.6. Ba câu hỏi tự kiểm tra

Mỗi người trả lời trước khi đọc gợi ý:

1. Hai khách có cùng RFM nhưng khác sessions_30d/views_30d thì F1 bổ sung điều gì? Có bảo đảm họ khác cụm hoặc sắp mua không?
2. Muốn kiểm tra tác động riêng của log, cần giữ gì cố định? Vì sao vừa thêm Engagement vừa thêm log rồi so Silhouette chưa đủ?
3. Nếu F1 có Silhouette cao hơn, đã kết luận cải tiến thành công và marketing tăng doanh thu được chưa? Trước khi chạy F1 phải ghi gì từ F0?

**Gợi ý trả lời:**

1. Bổ sung mức quay lại và xem gần cutoff, chưa có bảo đảm về nhãn cụm hay hành vi tương lai. Cần dữ liệu và thực nghiệm để kiểm tra H1.
2. Cùng bộ cột, buyers, cửa sổ, cleaning policy, K, seed và cấu hình; giữ scaling, chỉ thay bước log trên cột đã ghi. Hai thay đổi đồng thời gây lẫn tác động; điểm cũng được tính trong hình học đã đổi.
3. Chưa: cần ổn định, cỡ cụm, hồ sơ năm biến gốc, khác biệt hành vi, khả năng giải thích và chi phí; hiệu quả chiến dịch cần thử nghiệm riêng. Trước F1 phải lưu cấu hình/kết quả F0, hạn chế thực sự quan sát, bằng chứng, giả thuyết cải tiến và cách kiểm tra. Chấp nhận cả kết quả chưa ủng hộ giả thuyết.

## 17. P2-T1 — Hiểu cấu trúc dữ liệu trước khi làm sạch

### 17.1. Schema và data type là gì?

Schema là danh sách cột và cách dữ liệu được tổ chức; data type là kiểu giá trị, như văn bản, số nguyên, số thực hoặc thời gian. Ví dụ `price DOUBLE` cho biết cách máy đọc số, chưa nói mọi giá đều hợp lệ để tính tiền mua.

Cần tách ba điều: **kiểu lưu trong tệp**, **kiểu công cụ suy luận/đọc**, và **kiểu muốn dùng sau này**. CSV chứa văn bản, nên chuỗi `2019-10-01 00:00:00 UTC` chưa phải cột TIMESTAMP được lưu sẵn. Parquet có schema; INT64 là kiểu vật lý, còn TIMESTAMP_MICROS là cách diễn giải số thành thời gian. Script lưu cả kiểu vật lý/logical và kiểu DuckDB đọc, không gọi mọi kiểu là “kiểu gốc”.

Trong mẫu thực tế, user_id ép được BIGINT, nhưng về ý nghĩa nó là **định danh**, không phải độ lớn khách hàng. Không đưa ID vào khoảng cách K-Means. Tương tự product_id không phải số sản phẩm đã mua; category_id chưa chắc là danh mục cấp cao. Kiểu mong muốn ở bước xử lý phải giữ đúng định danh, giá trị và timezone; P2-T1 chưa chuyển đổi tệp hoặc chốt chính sách.

Một lỗi công cụ đã được kiểm thử phát hiện: DuckDB có thể ép `1.25` thành BIGINT bằng làm tròn. Nếu chỉ thấy ép kiểu thành công thì sẽ suy sai kiểu giá. Vì vậy script còn kiểm tra chuỗi có đúng dạng số nguyên trước khi chọn BIGINT. Một cột toàn ô trống trong mẫu phải ghi chưa suy luận được, không tự đoán kiểu từ tên.

### 17.2. Event, session, customer và khóa

Event là một hành động; session là một phiên có nhiều hành động; customer là khách có nhiều phiên. Ví dụ **giả định để học**: user_A xem ba lần rồi có hai purchase events trong session_X. Có năm dòng event, một phiên và một khách; Frequency dự kiến tăng một khi phiên mua hợp lệ. Không có order_id nên không kết luận hai purchase rows là hai đơn hàng.

Primary key là khóa nhận diện duy nhất mỗi dòng. user_id không là khóa duy nhất cho bảng event vì một người có nhiều event. Composite key là khóa ghép từ nhiều trường; `(user_id, user_session)` nhận diện nhóm phiên theo người dùng, vẫn lặp trên nhiều dòng event. Không gọi khóa nhóm phiên là primary key của bảng event hoặc tự xóa các dòng cùng khóa.

Header không có event_id, nên chưa biết một khóa event duy nhất chỉ bằng nhìn tên cột. UUID là dạng biểu diễn token phiên, không tự chứng minh phiên không thiếu hoặc không được dùng lại. Kiểm tra kiểu/định dạng là bước đầu; tính đầy đủ, uniqueness và dedup cần kiểm tra đúng grain ở task sau.

### 17.3. Vì sao phải kiểm tra datetime và timezone?

Datetime biểu diễn ngày giờ; timezone cho biết cách quy đổi thời điểm. Ví dụ minh họa `2020-02-01 00:30:00+07:00` tương ứng `2020-01-31 17:30:00 UTC`. Nếu chỉ nhìn ngày địa phương “tháng 2” rồi loại, có thể loại sai một event còn trước cutoff UTC.

Bốn mẫu thật có 4.000/4.000 thời gian parse được và chứa hậu tố UTC, gồm cả tháng 12 trong lần chạy lại. Điều này xác nhận cách biểu diễn trong mẫu, không xác nhận toàn bộ bốn tháng. Parquet đang lưu TIMESTAMP không kèm timezone và isAdjustedToUTC=0, nên không tự lấy việc parse thành công hoặc cấu hình UTC của công cụ làm bằng chứng nguồn luôn là UTC. Giải thích kiểu tại [tài liệu DuckDB](https://duckdb.org/docs/2.0/sql/data_types/timestamp.html).

Giữ cửa sổ observation `[01/10/2019, 01/02/2020)` và 30 ngày `[02/01/2020, 01/02/2020)` theo UTC: lấy đầu, không lấy cuối. Xét thời gian từng event, kể cả session qua cutoff. P2-T1 chỉ kiểm tra cách đọc, chưa lọc/tạo observation.

### 17.4. Các bước thực hành đã dùng

1. Đọc inventory/audit P0-T1 và cấu hình, code ETL cũ dưới dạng văn bản để tìm nguồn. Sau đó kiểm tra file thật có tồn tại/đọc được; danh sách cũ không thay thế kiểm tra mới.
2. Đọc header và tối đa 1.000 dòng đầu mỗi raw observation; chỉ giữ mẫu trong RAM. Không đọc CSV February ngoài header. Suy luận kiểu trên mẫu, ghi parse/định dạng và các ô trống liên quan; không sửa giá trị.
3. Với sáu Parquet ứng viên, dùng `parquet_schema`, `parquet_file_metadata` và DESCRIBE. Không tải toàn bảng, không tính lại feature hoặc đọc outcome February. [Metadata Parquet](https://duckdb.org/docs/2.0/data/parquet/metadata.html) cho biết schema/số dòng footer, không chứng minh nội dung đã làm sạch đúng.
4. So tên/thứ tự cột giữa những tệp đọc được, nối với nhu cầu năm biến, rồi tách phần quan sát được khỏi phần cần kiểm tra ở P2-T2/P2-T3.
5. Lưu JSON/CSV metadata nhỏ, không lưu raw user/session IDs. Tên user_A/session_X trong bài học chỉ là minh họa; không dùng dữ liệu kiểm thử làm số liệu nghiên cứu.

Script được tạo là `scripts/inspect_schema.py`, không thêm notebook thứ hai hoặc sửa notebook Colab đã nghiệm thu. Lệnh thật đã chạy từ root MVP bằng Python/DuckDB sẵn có:

```powershell
& '..\customer-analytics-antigravity\.venv\Scripts\python.exe' -B scripts/inspect_schema.py --data-root ../customer-analytics-antigravity/data --sample-rows 1000 --output results/p2_t1/recheck_01
```

Input là root có raw/, cleaned/, features/. Output mới có [inspection.json](../results/p2_t1/recheck_01/inspection.json), [schema.csv](../results/p2_t1/recheck_01/schema.csv); [execution.json](../results/p2_t1/recheck_01/execution.json) ghi lần chạy/lệnh/exit code. Bằng chứng lần trước bị chặn giữ nguyên trong thư mục cha. Đây là kiểm tra local, chưa chạy script mới trên Colab.

Để chạy lại, chọn thư mục output mới, ví dụ `results/p2_t1_recheck`, vì script từ chối ghi đè bằng chứng đã có. Có thể dùng `python -B scripts/inspect_schema.py ...` trong môi trường đã có DuckDB. `--data-root` hoặc `REES46_DATA_ROOT` đổi nơi dữ liệu; đường dẫn tương đối tính từ root MVP. Trên Colab, khi đến lần thực hành được nhóm thống nhất, trỏ tới root dữ liệu trên Drive và chạy script từ bản repo đã chấp nhận; task này chưa mount/copy dữ liệu hoặc xác nhận chạy Colab.

### 17.5. Đọc kết quả và giới hạn

Lần chạy lại đã đọc header năm CSV gồm bốn tháng observation và February; chỉ bốn CSV observation có mẫu, tổng 4.000 dòng. Tháng 12 đã đọc được trực tiếp sau khi người dùng gỡ chặn; không lấy schema Parquet hoặc các tháng khác để điền thay. Header của bốn raw observation giống nhau về chín tên cột và thứ tự; các kiểu suy luận trên mẫu cũng giống nhau.

Trong cả bốn mẫu có bốn event_type: view, cart, purchase, remove_from_cart. Điều đó bác bỏ việc mặc định chỉ có view/cart/purchase, nhưng chưa chứng minh không còn loại khác. Có ô trống brand/category_code; chưa biết tỷ lệ toàn bộ. Min/max được ghi là min/max mẫu đầu tệp, không phải cả tháng.

Các cột cần cho năm biến có trong header bốn tháng, nhưng còn phải kiểm tra buyer/giá/session/dedup/rounding và thời gian toàn dữ liệu. Kiểm tra schema trước giúp biết sẽ kiểm tra gì và tránh nhầm kiểu/đơn vị; không thay thế cleaning. Lần mới trả **exit 0** và được bàn giao ở trạng thái READY FOR STUDENT REVIEW; sau review, người dùng đã xác nhận **PASS (Student Verified)**. Lần cũ exit 2 vẫn được giữ như lịch sử; chưa tính SHA256 toàn raw tháng 12 và chưa xác nhận chất lượng toàn bộ chỉ từ mẫu.

Kiểm thử công cụ dùng các tệp nhỏ tạm thời, tách khỏi nghiên cứu: giới hạn dòng đọc, không sửa nguồn, không xuất ID, phân biệt thời gian không timezone, chỉ đọc header future, đọc footer và từ chối ghi đè. Lệnh đã chạy:

```powershell
& '..\customer-analytics-antigravity\.venv\Scripts\python.exe' -B -m unittest discover -s tests -p test_inspect_schema.py -v
```

### 17.6. Ba câu hỏi tự kiểm tra

1. Trong CSV, user_id đọc được BIGINT thì có nên đưa nó vào tính khoảng cách K-Means không? Có header đủ chín cột thì đã chứng minh năm feature hợp lệ chưa?
2. Một phiên có ba view và hai purchase events cho bao nhiêu event/phiên? Vì sao không gọi `(user_id, user_session)` là khóa duy nhất của từng event hoặc kết luận có hai đơn?
3. Header đủ bốn tháng giống nhau và parse được 4.000 timestamp có UTC thì đã xác nhận toàn dữ liệu sạch chưa? Vì sao P2-T1 mới READY FOR STUDENT REVIEW, chưa phải PASS?

**Gợi ý:** (1) Không: ID là định danh; có cột/kiểu mới chỉ đủ điều kiện kỹ thuật ban đầu, chính sách nghiệp vụ chưa chốt. (2) Năm event, một phiên, Frequency dự kiến tăng một nếu hợp lệ; khóa phiên lặp giữa event, không có order_id. (3) Chưa: chỉ đọc header/mẫu giới hạn; missing, duplicates, giá, khóa và thời gian toàn bộ chưa kiểm tra đầy đủ. READY ghi nhận công việc chờ hai sinh viên xem và nghiệm thu; không tự thay bằng PASS hoặc triển khai P2-T2.

## 18. P2-T2 — Đánh giá chất lượng trên toàn bộ bốn CSV

### 18.1. Học từ notebook và bảng chính

Từ task này, nhóm đi theo mục tiêu → phương pháp → code → kết quả → giải thích → kiểm tra → nghiệm thu. Mở phần 7 của notebook 01 để xem bảng tổng hợp và bốn biểu đồ; REPORT trình bày ngắn phương pháp/kết quả, phần này giải thích sâu hơn. Không cần đọc nhiều JSON để hiểu phát hiện chính. Bản Word khoảng năm trang và 3–5 hình được hoàn thiện ở Phase 7; hiện chưa xuất Word hoặc làm các phase sau.

P2-T1 chỉ kiểm tra 4.000 dòng mẫu. P2-T2 đọc **mọi dòng của bốn CSV tháng 10/11/12/2019 và 01/2020**, chưa đọc sự kiện February hoặc lấy Parquet đã làm sạch làm đầu vào. Mỗi dòng vẫn là một event, không phải một đơn hàng.

### 18.2. Missing và mẫu số

Nhóm định nghĩa ô thiếu cho phép đo là NULL hoặc chuỗi chỉ có khoảng trắng: `x IS NULL OR trim(x)=''`. Hàm trim chỉ dùng để nhận diện, không ghi giá trị mới vào nguồn. Khi đọc CSV, trường rỗng được DuckDB biểu diễn là NULL; xem [tham số CSV](https://duckdb.org/docs/2.0/data/csv/overview.html). Một chuỗi chữ “NULL” không tự được coi là thiếu theo định nghĩa này.

`Tỷ lệ thiếu = số event thiếu cột / số event trong nhóm × 100%`. “Nhóm” có thể là tất cả dữ liệu, một tháng, một loại event hoặc giao tháng–loại event. Ví dụ minh họa: 2 ô thiếu session trên 10 event cho 20%; đây không phải tỷ lệ khách thiếu hoặc kết quả REES46. Bảng quality_details có scope, month, event_type và denominator để kiểm tra mẫu số.

Missing brand/category_code có thể cản trở diễn giải danh mục/thương hiệu, nhưng không trực tiếp làm thiếu năm biến đã chọn. Missing user_id ảnh hưởng việc gom theo khách; thiếu session ảnh hưởng Frequency/Sessions 30d. Không vì thiếu session mà tự bỏ view hợp lệ; quyết định ở P2-T3.

Trong lần chạy thật, 3.543 event thiếu session nhưng không có purchase thiếu session. Vì vậy cần xem ảnh hưởng tới Sessions 30d và các event tương tác, không nói 3.543 lượt mua hoặc khách bị mất. Brand thiếu 41,9155% và category_code thiếu 98,3285% dùng mẫu số 16.536.158 event.

### 18.3. Hai định nghĩa trùng 7 và 9 trường

Chín trường là toàn bộ cột raw. Bảy trường bỏ brand và category_code, còn event_time, event_type, product_id, category_id, user_id, user_session, price. So sánh hiện tại dùng **giá trị văn bản đã đọc từ CSV**, NULL gom cùng NULL; không trim, đổi hoa/thường, chuẩn hóa số hoặc timestamp trước khi nhóm. Vì vậy, `1.0` và `1.00` chưa tự bằng nhau. Đây là đối chiếu hai bộ khóa trên cùng dữ liệu, chưa khẳng định tương đương việc ETL cũ suy kiểu rồi loại trùng.

Với một khóa xuất hiện n lần: số dòng trong nhóm là n; số dòng dư nếu chỉ giữ một là `n−1`. Ví dụ minh họa một khóa xuất hiện ba lần: có ba dòng trong nhóm nhưng chỉ hai dòng dư. Trong test tính tay, thêm thay đổi brand làm số dòng dư theo 7 trường lớn hơn 9 trường. Tổng tần số các nhóm phải bằng tổng event đã đọc; số dòng dư 7 trường không được nhỏ hơn 9 trường.

Không có event_id nên giá trị trùng chưa chứng minh đó là lỗi kỹ thuật. Việc lặp purchase có thể tăng tổng price, view lặp có thể tăng Views; còn Frequency đếm phiên riêng biệt không tự tăng theo số purchase rows. Bảng chi tiết có số dòng view/purchase dư và tổng price dương tương ứng **nếu chỉ giữ một dòng/khóa**. Đây là phân tích giả định để xem ảnh hưởng, chưa thực hiện xóa hoặc chọn quy tắc.

### 18.4. Giá, định danh và thời gian

Price được kiểm tra thành sáu nhóm không giao nhau: thiếu, không parse được, không hữu hạn (NaN/Infinity), âm, bằng 0, dương. Tổng sáu nhóm phải bằng tổng event. Purchase có giá thiếu/lỗi/không dương được đọc với mẫu số là số purchase events, không phải số đơn. Chưa xác nhận currency/refunds/quantity nên không gọi tổng price là doanh thu ròng.

Giá cao được gắn cờ tham khảo bằng `Q3 + 3×IQR`, với `IQR=Q3−Q1`, tính trên purchase có giá dương hữu hạn. Đây là lựa chọn để xem đuôi phân phối, chưa phải ngưỡng lỗi hoặc điều kiện xóa. Biểu đồ price dùng cùng 60 khoảng cho tất cả giá hữu hạn và nhóm giá dương, trục số lượng dùng log; “nhóm giá dương” chỉ là đối chiếu, không phải file đã làm sạch.

Kết quả thật: 91 purchase giá âm và 1 giá 0 trên 1.045.014 purchase events; chưa tự loại. Trên 1.044.922 purchase dương, Q1=1,59, Q3=5,40 nên ngưỡng xem xét là 16,83; 36.107 event vượt ngưỡng. Không được gọi 36.107 event này là dữ liệu sai khi chưa hiểu bối cảnh.

user_id được kiểm tra dạng chữ số và khả năng đọc BIGINT, session kiểm tra hình thức UUID. Dạng hợp lệ không chứng minh danh tính thật hoặc order_id. Nếu một token được dùng bởi nhiều user, phải xem khóa ghép user-session; nhiều event cùng khóa phiên là bình thường.

Timestamp được parse trên toàn bộ dòng, kiểm tra hậu tố UTC/thông tin timezone, tháng nguồn và observation `[2019-10-01,2020-02-01)` theo UTC. Giá trị thiếu, không parse được, không hữu hạn, ngoài cửa sổ và trong cửa sổ được đếm riêng, không âm thầm bỏ hàng lỗi khỏi mẫu số. Cấu hình UTC của công cụ không thay cho bằng chứng timezone trong chuỗi.

### 18.5. Chạy lại và kiểm tra kết quả quan trọng

Chạy từ root repo trong Python có DuckDB và Matplotlib:

```text
python -B scripts/assess_quality.py --data-root ../customer-analytics-antigravity/data --output results/p2_t2
```

Hoặc đặt REES46_DATA_ROOT rồi bỏ --data-root. Mỗi lần chạy lại chọn output mới, ví dụ results/p2_t2_recheck, để giữ kết quả cũ. Dữ liệu lớn ở local/Drive; bảng tạm để đếm nằm trong thư mục riêng đã ignore và được dọn sau khi chạy, không phải observation sạch. Không cần chuyển Parquet thành CSV cho mô hình tương lai.

Mở [quality_summary.csv](../results/p2_t2/quality_summary.csv) trước; [quality_details.csv](../results/p2_t2/quality_details.csv) lưu chi tiết theo tháng/loại và mẫu số. Một [run_manifest.json](../results/p2_t2/run_manifest.json) giữ cấu hình, input, hash code, hash tháng 12 và giới hạn để tái lập, không tạo log riêng cho từng phép kiểm.

Script kiểm tra tổng số dòng theo tháng và loại, tổng tần số khóa trùng, các nhóm giá/thời gian và tổng histogram. Test phần mềm dùng ví dụ nhỏ riêng để đối chiếu n−1, missing, giá, timezone/cutoff và toàn luồng xuất bảng/hình; không lấy ví dụ test làm dữ liệu nghiên cứu.

SHA256 là dấu vân tay bytes. Hash tháng 12 giống nhau trước/sau cho biết bản local ổn định trong lần kiểm tra; chưa có hash từ nhà cung cấp hoặc biên nhận tải thì không chứng minh nguồn gốc. Điều này khác với việc chỉ đọc được header ở P2-T1.

### 18.6. Đọc biểu đồ và dừng ở đâu?

- Missing: so tỷ lệ theo cột trên cùng tổng event; cột đậm chỉ để nhấn phần thiếu nhiều, không phải tiêu chí loại cột.
- Event type: đọc số sự kiện, không diễn giải thành funnel chuyển đổi hoặc số đơn.
- Price: so hai phạm vi được ghi rõ, cùng khoảng giá và thang log số lượng; không gọi ảnh sau là đã làm sạch.
- Duplicate: so dòng dư theo hai định nghĩa, kết hợp thông tin bị bỏ khỏi khóa; không mặc định cột thấp hơn là chính sách đúng.

P2-T3 mới quyết định điều kiện buyer/purchase, giá, session thiếu, loại trùng và rounding. P2-T2 chưa tạo feature hoặc chứng minh Engagement giúp mô hình tốt hơn. Không tự bổ sung RobustScaler/MiniBatchKMeans hoặc chạy các phase khác theo danh sách biểu đồ gợi ý.

**Ba câu tự kiểm tra:**

1. Vì sao số event thiếu session không bằng số khách thiếu session? Mẫu số của tỷ lệ purchase có giá không dương là gì?
2. Một khóa xuất hiện ba lần có bao nhiêu dòng dư? Vì sao trùng theo 7 trường có thể nhiều hơn 9 trường nhưng vẫn chưa được tự xóa?
3. Hash tháng 12 trước/sau giống nhau chứng minh điều gì và chưa chứng minh điều gì? Tại sao cờ giá cao chưa phải lỗi?

**Gợi ý:** (1) Một khách có nhiều event; tỷ lệ purchase dùng số purchase events, không dùng số đơn. (2) Hai dòng dư; bỏ brand/category_code có thể gộp khác biệt, và thiếu event_id nên chưa phân biệt lỗi kỹ thuật với hành vi lặp. (3) Xác nhận ổn định bytes local trong lần chạy, chưa xác thực nguồn; giá cao có thể là mua hợp lệ, cần xem bối cảnh ở P2-T3.

## 19. P2-T3 — làm sạch theo mục đích RFM + Engagement

### 19.1. Giữ cột vì cần tính gì?

P2-T2 đã được người dùng nghiệm thu PASS. P2-T3 đề nghị chính sách dưới đây và chạy thử trên toàn bộ bốn CSV; vẫn chờ sinh viên duyệt trước khi tạo observation Parquet chính thức ở P2-T4. Raw được giữ nguyên. “Chạy thử” ở đây dùng dữ liệu thật trong database tạm, không phải lấy mẫu hoặc tạo dữ liệu thay thế.

Năm đặc trưng chỉ cần biết ai, lúc nào, hành động gì, phiên nào và giá mua. Vì vậy output đề nghị có:

| Cột | Kiểu DuckDB dự kiến trong Parquet | Dùng cho |
|---|---|---|
| event_time | TIMESTAMP WITH TIME ZONE, UTC | R và giới hạn observation/30 ngày |
| event_type | VARCHAR | Phân biệt purchase/view; mọi loại event đều có thể xác nhận phiên |
| user_id | BIGINT | Gom theo khách, không dùng ID làm biến khoảng cách |
| user_session | VARCHAR, có thể NULL | F và Sessions; ghép với user_id |
| price | DECIMAL(18,2), có thể NULL | M của purchase hợp lệ |

Brand và category_code không phục vụ năm biến nên bỏ khỏi output; không điền thiếu và **không xóa event vì thiếu chúng**. Product_id/category_id vẫn cần để phân biệt hai event khác sản phẩm/danh mục khi loại trùng; chỉ bỏ ở projection cuối. Raw vẫn cho phép nghiên cứu lại sản phẩm về sau, không cần giữ mọi cột trong bảng làm việc của MVP.

### 19.2. Thứ tự xử lý và chính sách đề nghị

1. Đọc đúng bốn CSV observation, chín cột dạng văn bản, strict_mode; lỗi cấu trúc CSV phải dừng. Không đọc events February. Không chạy pipeline cũ.
2. Loại bản dư theo **đủ chín giá trị gốc**, trước trim/ép kiểu/làm tròn. Một nhóm n dòng giữ một, loại n−1; NULL gom cùng NULL. Không đưa tên file/tháng vào khóa. P2-T2 cho khóa 7/9 cùng số dòng dư, nhưng chín trường giữ thông tin đầy đủ và tránh gộp khác biệt brand/category khi dữ liệu đổi. Không có event_id nên đây là giả định nghiên cứu, không phải chứng minh mọi dòng trùng đều là lỗi kỹ thuật.
3. Kiểm tra timestamp: phải parse được, hữu hạn, có timezone rõ; quy về UTC và giữ `[2019-10-01,2020-02-01)`. Không tự gắn UTC cho chuỗi thiếu múi giờ, không cắt về ngày trước khi lọc. Lọc theo thời điểm event, kể cả phiên vắt cutoff.
4. User phải là chuỗi chữ số đọc được BIGINT dương. Không tạo ID thay thế hoặc nối khách theo session. Event thiếu/sai user không dùng cho cả năm biến.
5. Giữ bốn loại view/cart/remove_from_cart/purchase; loại khác cần xem lại nguồn. Bảng lý do loại ưu tiên: timestamp sai → ngoài observation → user sai → loại event lạ. Mỗi event sau dedup chỉ thuộc một lý do; price/session được kiểm tra riêng, không cộng thành số hàng xóa.
6. Session thiếu/trống hoặc sai hình thức UUID chuyển NULL trong bản làm việc; giữ event. Token hợp lệ giữ nguyên chữ hoa/thường, không tự sửa/điền session. Khóa phiên là `(user_id,user_session)` vì P2-T2 thấy 191 token dùng chung nhiều user. UUID chỉ là kiểm tra hình thức trong dữ liệu này, không chứng minh danh tính/đơn hàng. Nếu nguồn tương lai dùng định dạng khác, phải xem lại chính sách; không suy token sai dạng chắc chắn là event giả.
7. Price thiếu/không parse được/không hữu hạn thành NULL; âm và 0 giữ nguyên để truy nguyên ý nghĩa. Không biến âm thành trị tuyệt đối, không điền median, không winsorize/cắt đuôi giá cao. Tất cả vẫn là event tương tác nếu user/time hợp lệ. Dữ liệu hiện tại không có giá thiếu/parse lỗi/không hữu hạn. Guard dừng nếu giá hữu hạn không vừa DECIMAL(18,2) hoặc có biểu diễn cần thêm chính sách độ chính xác; không âm thầm làm tròn.
8. Purchase hợp lệ cho **cả R/F/M** là `event_type='purchase' AND price>0 AND user_session IS NOT NULL`, sau các kiểm tra trên. Buyer có ít nhất một purchase hợp lệ. Purchase giá âm/0/NULL hoặc không có phiên không đóng góp R/F/M, nhưng event vẫn có thể xác nhận một phiên tương tác. “Không có purchase hợp lệ” không chứng minh khách chưa từng mua thật; nhóm này tách khỏi mô hình RFM.
9. Cuối cùng chỉ chọn năm cột; **không DISTINCT thêm trên năm cột**. Hai dòng cùng lúc, user, session, price nhưng khác product_id có thể là hai sản phẩm mua hợp lệ. Sau projection chúng giống nhau nhưng vẫn phải được giữ để M/Views không mất.

Ví dụ minh họa: cùng user/phiên có hai purchase giá 10 cho hai sản phẩm khác nhau. Kết quả đúng theo chính sách là F=1, M=20. Nếu bỏ product_id trước loại trùng, có thể còn M=10. Nếu một purchase giá −2 xảy ra sau đó, không lấy thời điểm này làm lần mua hợp lệ cuối và không trừ −2 như hoàn tiền vì chưa biết ý nghĩa refunds.

### 19.3. Tác động đến từng biến

| Chính sách | R | F | M | Sessions 30d | Views 30d |
|---|---|---|---|---|---|
| Bỏ brand/category_code, rồi product/category sau dedup | Không đổi | Không đổi | Không đổi | Không đổi | Không đổi |
| Giữ một/chín trường gốc | Không đổi max thời điểm của cùng bản trùng | Không đổi số phiên riêng biệt | Giảm tổng price dương bị lặp | Không đổi phiên riêng biệt | Giảm view lặp trong cửa sổ |
| Purchase hợp lệ có giá dương và phiên | Có thể lùi lần mua cuối; không gán R cho người mất toàn bộ purchase hợp lệ | Bỏ phiên chỉ có purchase không hợp lệ; phiên còn mua hợp lệ vẫn tính | Chỉ cộng giá mua dương hợp lệ; giữ giá cao | Event mua không hợp lệ vẫn có thể xác nhận phiên tương tác | Không loại view vì giá |
| Session NULL/sai dạng | Purchase đó không xác định R | Không tạo phiên giả | Không cộng purchase đó | Không đếm NULL thành một phiên | Vẫn đếm view có user/time hợp lệ |
| User sai | Không tính cho khách chưa xác định | Không tính | Không tính | Không tính | Không tính |
| Time sai/ngoài observation | Không lấy làm lần mua cuối | Không tính mua ngoài kỳ | Không cộng ngoài kỳ | Kiểm tra cửa sổ riêng | Kiểm tra cửa sổ riêng |
| Rounding | Giữ độ phân giải thời gian khi tính R | Số nguyên | Cộng DECIMAL chính xác; không cắt giá cao | Số nguyên | Số nguyên |

Đây là tác động theo định nghĩa, không có nghĩa mọi trường hợp đều xuất hiện. Kết quả thật nằm trong hai CSV P2-T3. Bảng stage_summary đếm trên **toàn bộ users** để kiểm tra chính sách, chưa phải bảng feature theo từng buyer hoặc kết quả phân khúc. Khi đến Phase 4, F0/F1 vẫn phải cùng tập buyers.

### 19.4. Rounding — làm tròn lúc nào?

R dự kiến là `(T − last_valid_purchase_timestamp) / 86.400 giây`, giữ phần lẻ và độ phân giải nguồn; không floor sang ngày, không round trước fit. Ví dụ lần mua cuối cách T 36 giờ thì R=1,5 ngày. Khi hiển thị có thể dùng hai chữ số sau dấu phẩy. F/Sessions/Views là số đếm nguyên. M cộng price bằng DECIMAL(18,2), không cộng DOUBLE rồi làm tròn từng nhóm; display hai chữ số không đổi giá trị gốc đã kiểm tra. Rounding không phải log transform hoặc scaling; chưa quyết định tiền xử lý mô hình ở task này.

DuckDB DECIMAL lưu số thập phân cố định, phép cộng chính xác trong giới hạn kiểu; scale thấp hơn nguồn có thể làm tròn. Vì vậy script kiểm tra **toàn bộ giá hữu hạn trước khi cast**: chỉ chấp nhận biểu diễn số thông thường tối đa hai chữ số thập phân và vừa kiểu; gặp `0.005` thì dừng, không đổi thành `0.01`. Phép chia tính R sẽ dùng số thực; display và tính toán tách nhau. Xem [kiểu số DuckDB](https://duckdb.org/docs/2.0/sql/data_types/numeric.html).

### 19.5. Column projection và output Parquet dự kiến

Projection nghĩa là chỉ chọn những cột cần đọc. Khi tới P2-T4 mới xuất observation năm cột; không chạy lệnh xuất chính thức trong task này. Sau đó, bước chỉ kiểm tra view có thể dùng:

```python
# Ví dụ cho bước sau, chưa chạy với observation chính thức.
con.execute("""SELECT count(*) FROM read_parquet(?)
               WHERE event_type='view' AND event_time>=TIMESTAMPTZ '2020-01-02 00:00:00+00'
                 AND event_time<TIMESTAMPTZ '2020-02-01 00:00:00+00'""", [parquet_path])
```

DuckDB hỗ trợ projection/filter pushdown cho Parquet; không cần load toàn bộ bằng pandas hoặc `SELECT *`. Đọc CSV vẫn phải xử lý dòng văn bản; không tuyên bố bỏ cột có cùng lợi ích I/O như Parquet. Kiểm thử riêng ghi/đọc một Parquet nhỏ trong thư mục tạm để đối chiếu kiểu năm cột, UTC, số dòng và kế hoạch chỉ đọc hai cột; đó là fixture phần mềm, không phải observation nghiên cứu. Xem [đọc/ghi Parquet bằng DuckDB](https://duckdb.org/docs/2.0/data/parquet/overview.html).

### 19.6. Chạy lại, giới hạn và câu hỏi nghiệm thu

Mở notebook 02 ở bản repo đầy đủ. Mặc định chỉ đọc bảng tổng hợp công khai, không cần raw. Chạy lại toàn dữ liệu bằng lệnh README với output mới; một database riêng dưới .tmp được dọn khi kết thúc. Bảng counts phải bảo toàn:

`raw = duplicate_extras + invalid_time + outside_window + invalid_user + unknown_event + retained`.

Các số price/session/cohort là lý do loại khỏi **phép tính tương ứng**, không phải hàng xóa khỏi retained. Hai CSV và một manifest là đủ cho lần chạy; không thêm hình vì biểu đồ trùng P2-T2 đã giải thích thay đổi lớn. So metadata cả bốn raw và SHA256 tháng 12 trước/sau; hash local ổn định chưa xác thực nguồn tải. Không khẳng định mọi bytes của ba tệp khác đã được hash. Không đọc events February hoặc Parquet cũ; không xuất features, K-Means hoặc official Parquet. Colab mới và môi trường cài mới chưa được xác nhận, không thay bảo mật Windows.

Ba câu tự kiểm tra:

1. Vì sao phải giữ product/category tới sau dedup, dù output không cần chúng? Nếu DISTINCT lần nữa trên năm cột, M có thể sai thế nào?
2. Một purchase giá âm có session hợp lệ đóng góp vào R/F/M và Sessions ra sao? Một view thiếu session có còn đóng góp Views không?
3. Vì sao giữ price cao và R phần lẻ? Nếu dữ liệu xuất hiện giá `0.005`, script phải làm gì thay vì tự làm tròn?

Gợi ý: (1) Phân biệt event khác sản phẩm; có thể làm mất giá mua/lượt xem hợp lệ. (2) Không vào RFM, vẫn xác nhận phiên tương tác; view vẫn tính nếu user/time hợp lệ. (3) Chưa có bằng chứng giá cao sai, làm tròn sớm mất thông tin; dừng và xem lại độ chính xác/chính sách.

### 19.7. Kết quả kiểm chứng trên dữ liệu thật

Lần hoàn tất dùng Python 3.14.7, DuckDB 2.0.0, hai threads, memory_limit=768MB. Guard độ chính xác giá đạt trên toàn nguồn; không cần làm tròn price hoặc thêm PyArrow. Đây là kiểm tra chính sách, không phải benchmark mô hình; chưa đo sampled RSS hoặc chạy Colab mới.

| Chỉ tiêu | Trước dedup, cùng điều kiện hợp lệ | Sau chính sách |
|---|---:|---:|
| Event | 16.536.158 | 15.667.350 |
| View toàn observation | 7.704.235 | 7.703.765 |
| Purchase events | 1.045.014 | 1.044.221 |
| Purchase đủ điều kiện RFM | 1.044.922 | 1.044.133 |
| Purchase giá không dương, giữ trong event | 92 | 88 |
| Event thiếu session, giữ trong event | 3.543 | 3.179 |
| Buyers đủ điều kiện | 92.652 | 92.652 |
| Phiên mua hợp lệ | 126.503 | 126.503 |
| Tổng price mua hợp lệ, đơn vị dataset | 5.144.461,71 | 5.141.266,90 |
| Sessions 30d, toàn users | 947.209 | 947.209 |
| Views 30d, toàn users | 1.997.977 | 1.997.872 |

Loại đúng 868.808 bản dư; bốn lý do user/time/ngoài cửa sổ/event lạ đều 0. Không bỏ hàng vì brand/category_code, price hoặc session. Còn 363.403 dòng khác nhau trên khóa nguồn nhưng trùng giá trị năm cột sau projection, vẫn giữ. Bốn raw không đổi metadata; SHA256 tháng 12 trước/sau cùng ebf98f504e238109efa406d26a26a90e0d467faa938bf96b68e3fea663d2008e, khớp P2-T2 nhưng chưa xác thực nhà cung cấp.

Sau dedup, tổng price của mọi purchase là 5.138.624,02. Chỉ cộng purchase hợp lệ cho M được 5.141.266,90, cao hơn 2.642,88 do không trừ giá âm; không gọi chênh lệch này là doanh thu tăng hay tiền hoàn. Mọi phiên có purchase trong dữ liệu này đều còn ít nhất một purchase hợp lệ, nên F không giảm bởi điều kiện giá. Không user mất toàn bộ purchase hợp lệ hoặc đổi thời điểm mua cuối: tác động thực tế lên R/cohort bằng 0. Tám view 30d thiếu phiên vẫn được giữ, không tạo phiên NULL.

Đọc [stage_summary.csv](../results/p2_t3/stage_summary.csv), [policy_counts.csv](../results/p2_t3/policy_counts.csv) và [manifest](../results/p2_t3/run_manifest.json). `nullable` trong manifest là metadata của view DuckDB (có thể ghi YES cho cả cột đã được lọc); không phải DDL ràng buộc NOT NULL của artifact P2-T4. Theo chính sách, event_time/event_type/user_id bắt buộc hợp lệ; session/price có thể NULL. Dừng READY FOR STUDENT REVIEW.
