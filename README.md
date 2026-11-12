# Simple RFM + Engagement Customer Segmentation MVP

Dự án nghiên cứu độc lập trên **REES46 Cosmetics**, cho nhóm hai sinh viên. So sánh K-Means F0 (RFM) với F1 (RFM + sessions_30d, views_30d), sau đó diễn giải và trình diễn Streamlit khi đến task tương ứng. Không có model hoặc dashboard MVP ở bước hiện tại.

**P0-T3: PASS (Student Verified)** theo xác nhận của người dùng ngày 13/11/2026: cả hai sinh viên đã trực tiếp nghiệm thu trên Colab/Drive. Các số liệu 11/11, 92.652 dòng và phiên bản thư viện trong logs vẫn là kết quả local của Codex, không phải chỉ số Colab mới được cung cấp. **Hiện chỉ làm P0-T4**, chờ nghiệm thu quy trình và bàn giao vào GitHub main; chưa chuyển Phase 1. Xem [tiến độ](docs/PROGRESS.md), [kế hoạch](docs/PROJECT_PLAN.md), [báo cáo](docs/REPORT.md) và [sổ tay](docs/LEARNING_GUIDE.md).

## Hai thành viên cùng làm việc

GitHub `main` là mã nguồn chính thức đã được chấp nhận. Drive giữ dữ liệu và bản notebook để thực hành; nhánh task/PR trên GitHub là bản đề nghị để hai bạn xem trước khi đưa vào main.

| Notebook hiện có | Người sửa chính | Người chạy kiểm tra |
|---|---|---|
| `01_data_exploration.ipynb` | Thành viên 1 | Thành viên 2; cả hai tự chạy từ đầu |

“Thành viên 1/2” là vai trò phân công, chưa phải tên cá nhân. Hai bạn thống nhất ai giữ mỗi vai trò trước khi làm; nếu đổi người, sửa dòng phân công này. Khi tạo notebook mới mới thêm một dòng cho notebook đó.

1. Lấy cùng phiên bản mới nhất từ GitHub; ghi commit gốc và người phụ trách trong phần task của PROGRESS. Nếu Git báo còn thay đổi chưa lưu, lưu lại trước khi đồng bộ; không reset hoặc force-push để bỏ qua.
2. Người sửa chính dùng bản Drive riêng, ví dụ `01_data_exploration_TV1_work.ipynb`. Người kiểm tra tạo bản sao riêng, ví dụ `01_data_exploration_TV2_check.ipynb`. Không cùng sửa một file Drive hoặc lưu bản của mình đè bản người kia.
3. Mỗi người khởi động lại runtime rồi chạy từ ô đầu tới ô cuối. Lưu bản có output phù hợp trên Drive; ghi task/ngày/người chạy và kết quả thực tế trong PROGRESS, kèm đường dẫn bản lưu nếu được nhóm cung cấp. Không tự tạo phiên bản hoặc số liệu còn thiếu.
4. Người kiểm tra gửi nhận xét cho người sửa chính; chỉ người sửa chính tổng hợp thay đổi. Giữ bản trước đó cho tới khi bản mới được kiểm tra xong.
5. Khi notebook được chấp nhận, người sửa chính tải bản cuối về; giữ code đã được duyệt, bỏ output và thông tin riêng trước khi đưa lên nhánh task. Lưu kết quả tổng hợp cần thiết dưới `results/`; giữ dataset và bản thực hành trên Drive. Xem diff và danh sách file trước commit, không thêm dữ liệu lớn, credentials hoặc user IDs. Người còn lại kiểm tra PR trước khi nhóm đưa vào `main`; không ghi đè thay đổi mới trên GitHub.
6. Sau mỗi task: thực hiện → giải thích kiến thức → kiểm tra → cập nhật REPORT/LEARNING_GUIDE/PROGRESS khi phù hợp → dừng nghiệm thu. Code hoặc dữ liệu thay đổi sau khi được duyệt thì kiểm tra lại.

**Bàn giao P0-T4:** [PR nháp #1](https://github.com/TminTtapcode/customer-segmentation-mvp/pull/1) trên nhánh `p0-t4-team-workflow` đã có các file MVP để nhóm xem. Đầu lượt kiểm tra 13/11/2026, GitHub main chỉ có `.gitignore`, nên PR bàn giao cả các file đã có từ P0-T1/T2/T3. Notebook local P0-T3 được giữ nguyên; hai bạn so với bản đã nghiệm thu trên Drive trước khi chấp nhận PR và đưa vào main. Phase 0 còn chờ nghiệm thu P0-T4 và cập nhật bản chính thức.

## Mở và chạy notebook P0-T3

1. Dùng [notebooks/01_data_exploration.ipynb](notebooks/01_data_exploration.ipynb) của đúng phiên bản GitHub được nhóm chấp nhận. Mở [Google Colab](https://colab.research.google.com/), chọn **Upload / Tải lên** notebook hoặc mở từ GitHub; lưu bản thực hành riêng trên Drive theo quy trình ở trên. Nếu `main` chưa nhận bản bàn giao, dùng bản local/nhánh task được ghi trong PROGRESS, không tự coi đó là phiên bản chính thức.
2. Đọc phần giới thiệu, chạy ô kiểm tra Python/DuckDB. Chỉ DuckDB được cài nếu còn thiếu; chưa cần toàn bộ requirements của MVP.
3. Chạy ô kết nối Drive và tự cấp quyền qua giao diện Colab. Không dán mật khẩu/token vào ô code. Codex chưa mount hoặc thay quyền Drive trong lần thực hiện này.
4. Nếu nhóm đồng ý đưa dữ liệu lên Drive, chỉ chuẩn bị tệp ứng viên nhỏ `buyer_features.parquet` (~2,16 MiB). Nguồn local đã kiểm kê là `../customer-analytics-antigravity/data/features/buyer_features.parquet`, tính từ root repo MVP. Không cần upload toàn bộ events. Đặt file ở `MyDrive/datasets/rees46/features/buyer_features.parquet`, hoặc chỉnh một biến `DATA_ROOT` trong notebook cho đúng nơi nhóm chọn.
5. Chạy lần lượt các ô schema, số đếm và đối chiếu P0-T1. Đúng bản đã kiểm kê có **92.652 dòng, 23 cột, 2.266.870 bytes**; SHA256 phải khớp mốc trong notebook. Notebook không in user IDs. Thiếu file sẽ dừng rõ ràng, không tạo dữ liệu thay thế.
6. Mỗi thành viên **khởi động lại phiên rồi chạy toàn bộ từ đầu**, trả lời ba câu hỏi cuối bài và giải thích được đầu ra. P0-T3 đã được người dùng xác nhận nghiệm thu; tiếp tục dùng cách chạy này khi có phiên bản mới. Không thực hiện EDA hoặc K-Means ở bài thiết lập này.

Kết quả local đã lưu ở P0-T3: `nbformat` đọc/validate thành công; cả 9 ô code chạy theo thứ tự trong process Python mới; 8 điều kiện đối chiếu file đạt. Tổng 11 kiểm tra local đạt, gồm trường hợp thiếu dữ liệu. Xác nhận Colab của sinh viên được ghi riêng trong PROGRESS; không gán các số này cho Colab. Xem [verification.json](results/p0_t3/verification.json) và [log local](results/p0_t3/local_run.txt).

Notebook tự chạy, không cần clone repo trên Colab. Nếu muốn kiểm tra lại bằng công cụ local của dự án, dùng Python có DuckDB; `nbformat` chỉ là công cụ kiểm tra notebook và được cài riêng vào thư mục tạm đã ignore:

```text
python -B -m pip install --target .tmp/notebook-validation nbformat
python -B scripts/verify_colab_notebook.py --source ../customer-analytics-antigravity
```

Lệnh thứ hai mở notebook bằng `nbformat`, chạy các ô bằng Python local trong process mới cho từng trường hợp và lưu logs; không mở trình duyệt/Jupyter kernel hoặc kết nối Drive. Không cần cài nbformat để sinh viên chạy notebook trên Colab. Danh sách bảy dependency MVP chưa được cài/import/chốt phiên bản đầy đủ trong task này.

## Cấu trúc hiện tại

```text
customer-segmentation-mvp/
├── AGENTS.md
├── README.md
├── requirements.txt
├── requirements-audit.txt          # cấu hình audit P0-T1 được giữ lại
├── .gitignore
├── data/README.md                  # chỉ hướng dẫn, chưa có dataset
├── notebooks/
│   ├── README.md
│   └── 01_data_exploration.ipynb    # hiện chỉ có thiết lập và đọc thử dữ liệu
├── results/
│   ├── p0_t1/                      # bằng chứng audit giữ nguyên
│   ├── p0_t2/                      # baseline, logs và kiểm chứng cấu trúc
│   └── p0_t3/                      # kiểm tra notebook bằng Python local
├── docs/
│   ├── PROJECT_PLAN.md
│   ├── REPORT.md
│   ├── LEARNING_GUIDE.md
│   └── PROGRESS.md
├── scripts/
│   ├── audit_existing_artifacts.py
│   ├── verify_audit.py
│   ├── data_paths.py
│   └── verify_colab_notebook.py
└── tests/test_data_paths.py
```

`model/` tạo khi cần lưu model ở P5; `app.py` chỉ tạo ở Phase 6. Chưa tạo file/thư mục rỗng. Các README của data/notebooks là hướng dẫn sử dụng ngắn; hai báo cáo tích lũy vẫn nằm trong `docs/`.

## Cách bắt đầu

Mở terminal tại root repository — thư mục chứa `AGENTS.md` và `requirements.txt`. Các lệnh sau **là hướng dẫn tạo môi trường Windows**, chưa được thực hiện cài mới ở P0-T2:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -B scripts/data_paths.py
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
```

Dùng trực tiếp executable trong `.venv` nên không cần thay execution policy Windows để activate. Nếu Python đã có sẵn, hai lệnh kiểm tra không cần dependency bên ngoài:

```text
python -B scripts/data_paths.py
python -B -m unittest discover -s tests -v
```

P0-T2 đã chạy sáu tests đường dẫn bằng Python sẵn có, không cài thư viện. Lệnh/exit code/stdout thực tế nằm ở [commands.json](results/p0_t2/commands.json). `observation_exists=false` là kết quả dự kiến khi chưa đặt dữ liệu; helper chỉ tính đường dẫn, không chấp nhận dữ liệu về mặt nghiên cứu.

`requirements.txt` khai báo trực tiếp **duckdb, pandas, numpy, matplotlib, scikit-learn, streamlit, joblib**. Chưa pin toàn bộ phiên bản vì chưa kiểm chứng môi trường cài mới; đây chưa phải lockfile — file khóa phiên bản. `requirements-audit.txt` chỉ giữ pin DuckDB đã dùng trong P0-T1. Chưa khai báo PyArrow trực tiếp vì dự kiến đọc/ghi Parquet bằng DuckDB; điều này không bảo đảm các dependency bắc cầu sẽ không kéo PyArrow. P0-T3 chỉ cần DuckDB; việc cài/import và kiểm tra tương thích đủ bảy thư viện vẫn còn mở.

| Dependency | Mục đích khi đến task tương ứng |
|---|---|
| duckdb | Truy vấn event lớn, đọc/ghi Parquet |
| pandas | Xử lý bảng khách hàng sau tổng hợp |
| numpy | Tính toán số và mảng feature |
| matplotlib | Biểu đồ phục vụ EDA/diễn giải |
| scikit-learn | Preprocessing, K-Means và metrics phân cụm |
| streamlit | Web demo nhỏ ở Phase 6 |
| joblib | Lưu/nạp artifact mô hình MVP mới ở phase tương ứng |

## Đường dẫn dữ liệu

Helper [scripts/data_paths.py](scripts/data_paths.py) dùng quy tắc:

1. Không đặt `REES46_DATA_ROOT`: lấy `data/` tính từ root repository.
2. Đặt một đường dẫn tương đối: tính từ root repository, kể cả terminal đang ở thư mục khác.
3. Đặt đường dẫn tuyệt đối: dùng root dữ liệu riêng đó, rồi ghép `cleaned/observation_events.parquet`.

Ví dụ Windows local, không cần ghi đường dẫn ổ đĩa vào source:

```powershell
$env:REES46_DATA_ROOT = '../datasets/rees46'
python -B scripts/data_paths.py
```

Trong Python chạy từ root repository:

```python
from scripts.data_paths import observation_path
path = observation_path()
print(path.is_file())  # chỉ kiểm tra có file; chưa đọc hoặc xác nhận policy
```

**Colab / Drive:** notebook P0-T3 chạy độc lập và dùng `DATA_ROOT` hoặc biến môi trường `REES46_DATA_ROOT`; hiện chỉ đọc `features/buyer_features.parquet`. Không cần đặt working directory vào repo khi upload notebook lên Colab. Helper `scripts/data_paths.py` vẫn giữ thiết kế cho observation ở `cleaned/observation_events.parquet` khi đến bước tương ứng; không đổi đường dẫn helper chỉ để thử bảng buyer nhỏ. Xem [data/README.md](data/README.md).

`.gitignore` bỏ toàn bộ dữ liệu dưới `data/`, chỉ cho theo dõi README; bỏ Parquet/model artifacts và bảng CSV có nhãn user_level. Inventory CSV và metrics tổng hợp vẫn có thể được theo dõi. Trước khi commit, luôn xem `git diff --cached --name-only` / `git diff --cached --stat`; không dùng `git add -f` để vượt ignore dữ liệu. Kiểm tra staging không thay thế việc đọc nội dung bảng trước khi công khai.

## Kết quả P0-T1 — bằng chứng lịch sử, không chạy lại trong P0-T2

- 15.667.350 events observation, 1.341.499 users, 92.652 buyers.
- Năm features đối soát từ source: 0 mismatch; Python kiểm chứng 30 users / 2.733 events: 0 mismatch.
- 5/5 audit checks và 4/4 kiểm chứng bổ sung qua. Đây là kiểm chứng tính toán, chưa phải nghiệm thu policy làm sạch hay model.
- 153 tệp được kiểm kê, 152 tệp hash giữ nguyên trước/sau. Raw `2019-Dec.csv` bị tiến trình khác khóa: chưa đọc header/hash. Git status nguồn giữ nguyên.
- Có lệch policy dedup 7/9 trường, model cũ 7D và giới hạn February đã xem. Chi tiết và checklist nghiệm thu ở báo cáo.

Bằng chứng: [inventory](results/p0_t1/inventory.csv), [audit](results/p0_t1/audit.json), [Python verification](results/p0_t1/independent_verification.json), [execution/log record](results/p0_t1/execution.json). Không chứa bảng user-level hay raw user IDs.

## Chạy lại audit P0-T1 khi được giao

Mở terminal tại root MVP, dùng Python có dependency trong `requirements-audit.txt`; `--source` trỏ tới project cũ độc lập:

```powershell
python -B scripts/audit_existing_artifacts.py --source ../customer-analytics-antigravity
python -B scripts/verify_audit.py
```

Audit chỉ đọc project nguồn, ghi `results/p0_t1/` trong repo MVP. Không import scripts cũ, không load joblib, không train, không đọc outcome February. CSV tương lai chỉ đọc header/metadata và hash; Parquet mixed/future chỉ schema/footer/hash. Nếu tệp bị khóa, ghi rõ phần thiếu thay vì giả lập kết quả.

Hai script trả exit 0 nếu checks được định nghĩa đều đạt; vẫn phải xem `preservation.unhashed_paths`, các giới hạn và trạng thái nghiệm thu. Log đầu ra của lần chạy đã lưu trong `audit_stdout.txt` / `verification_stdout.txt`. Chạy lại cập nhật JSON/CSV; muốn giữ lịch sử hãy dùng `--output results/TEN_LAN_CHAY` và truyền `--audit results/TEN_LAN_CHAY/audit.json` khi verify.

## Chạy lại audit trên máy khác hoặc Colab — hướng dẫn chưa kiểm chứng

Clone repo MVP; chuẩn bị Python có DuckDB theo `requirements-audit.txt`. Nếu chưa có, có thể tạo môi trường riêng và chạy `python -m pip install -r requirements-audit.txt`; đây là hướng dẫn, lần thực hiện hiện tại không cài dependency. Với nguồn project cũ đầy đủ trên máy khác:

```text
python -B scripts/audit_existing_artifacts.py --source /path/to/legacy/project
python -B scripts/verify_audit.py
```

Không cần ổ D cố định; `--source` chỉ định đường dẫn và phải khác repo MVP. Chỉ muốn học tiếp từ dữ liệu đã duyệt thì mang observation Parquet kèm manifest/hash/schema và policy đã chốt; script inventory toàn nguồn cần cây project cũ đầy đủ.

Đề xuất `REES46_DATA_ROOT=/content/drive/MyDrive/datasets/rees46`, file ở `cleaned/observation_events.parquet`. Sau P2 chấp nhận policy, copy sang runtime `/content/rees46/cleaned/observation_events.parquet` khi cần và so SHA256 với inventory. P0-T3 đã được sinh viên nghiệm thu với notebook đọc thử bảng buyer nhỏ; chưa có xác nhận chạy toàn bộ audit hoặc observation trên Colab.

Dữ liệu lớn/model/bảng user-level không commit lên public GitHub. Tôn trọng điều khoản nguồn REES46; điều khoản/currency còn chờ xác minh. February đã được xem ở dự án cũ, không gọi là untouched test set.
