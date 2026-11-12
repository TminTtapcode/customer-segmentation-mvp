# Sổ tay học tập — MVP RFM + Engagement

**Cập nhật 13/11/2026.** Phần 1–9 về kiểm kê P0-T1, phần 10 về tổ chức dự án, phần 11 về notebook Colab và phần 12 về cộng tác nhóm. P0-T3 đã được người dùng xác nhận hai sinh viên nghiệm thu trên Colab/Drive; số liệu local cũ vẫn giữ riêng, không coi là số đo Colab mới.

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

Nhóm chưa dựng lại raw→clean, chưa kiểm tra toàn bộ CSV, chưa giải quyết file lock hoặc xác minh xong license/currency. Colab và mô hình MVP chưa chạy. Tính nhất quán của bảng hiện có không thay thế việc chốt quy tắc xử lý ở P2.

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
