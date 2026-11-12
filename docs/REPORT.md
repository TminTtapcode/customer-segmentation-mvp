# Báo cáo bài tập lớn — Phân khúc khách hàng bằng RFM và Engagement

**Cập nhật:** 13/11/2026. Báo cáo trình bày vấn đề, mục tiêu và kế hoạch kiểm chứng; chưa có thí nghiệm F0/F1. Nhật ký thực hiện và nghiệm thu được ghi riêng trong `PROGRESS.md`.

## 1. Giới thiệu và thiết kế nghiên cứu — P1-T1

### 1.1. Giới thiệu đề tài

Khách hàng của một website mỹ phẩm có thể khác nhau về thời điểm mua, số lần mua, mức chi tiêu và việc quay lại xem sản phẩm. Nếu chỉ nhìn tổng doanh thu hoặc coi mọi người giống nhau, doanh nghiệp có thể bỏ qua những nhu cầu khác nhau và khó giải thích vì sao cần một hướng chăm sóc khách hàng cụ thể.

Phân khúc khách hàng là chia khách thành các nhóm có đặc điểm tương đồng theo tiêu chí đã chọn. Nhóm nghiên cứu cách phân khúc từ REES46 Cosmetics bằng K-Means — phương pháp gom các điểm dữ liệu gần nhau. Đây là nghiên cứu mô tả hành vi, chưa phải mô hình dự đoán một người sẽ mua hàng hay đánh giá hiệu quả chiến dịch.

### 1.2. Lý do chọn đề tài

Nhóm lựa chọn đề tài này vì dữ liệu mua hàng và dữ liệu tương tác phản ánh những khía cạnh khác nhau. Trong tình huống minh họa, khách A mua thường xuyên và chi tiêu nhiều; khách B từng mua nhưng đã lâu không quay lại; khách C mua ít nhưng vẫn truy cập và xem sản phẩm. Một thông điệp chung cho cả ba có thể chưa phù hợp với nhu cầu của từng người. Phân khúc giúp mô tả các khác biệt trước khi đặt giả thuyết về cách tiếp cận; không chứng minh thông điệp nào đã hiệu quả.

RFM tóm tắt lịch sử mua qua Recency — thời gian từ lần mua gần nhất, Frequency — tần suất mua và Monetary — tổng giá trị mua. Các thành phần này được giới thiệu trong [tài liệu RFM của IBM](https://www.ibm.com/docs/en/watsonx/w-and-w/2.4.x?topic=properties-rfmanalysisnode). Trong REES46 không có order_id, nên nhóm đo Frequency bằng số phiên có mua duy nhất theo khóa `(user_id, session_id)`, không gọi đó là số đơn hàng. Monetary là tổng giá purchase hợp lệ, chưa phải doanh thu ròng.

RFM chưa mô tả trực tiếp việc quay lại website mà chưa mua. Hai người có lịch sử mua giống nhau vẫn có thể khác số phiên truy cập và lượt xem gần đây. Vì vậy, nhóm đề xuất nghiên cứu thêm `sessions_30d` và `views_30d`, gọi chung là Engagement — mức độ tương tác website. Đây là lý do để kiểm tra, chưa phải kết luận hai biến chắc chắn làm phân cụm tốt hơn.

### 1.3. Mục tiêu nghiên cứu

Mục tiêu của nhóm là xem việc kết hợp RFM với Engagement có bổ sung cách mô tả khách hàng hữu ích hay không. Cụ thể:

- Mô tả hành vi mua hàng và tương tác trong khoảng thời gian nghiên cứu.
- So sánh F0 gồm R, F, M với F1 gồm R, F, M, sessions_30d, views_30d trên cùng tập buyers — khách mua đủ điều kiện.
- Diễn giải đặc điểm các phân khúc và đề xuất hướng marketing có căn cứ mô tả, kèm giới hạn và nhu cầu thử nghiệm tiếp.

### 1.4. Câu hỏi nghiên cứu

Để tìm hiểu vấn đề trên, nhóm đặt ra:

- **RQ1:** Dữ liệu REES46 cho thấy những đặc điểm gì về hành vi mua hàng và tương tác website?
- **RQ2:** Bổ sung Engagement vào RFM có giúp phân biệt những hành vi khách hàng mà RFM truyền thống chưa thể hiện rõ không?
- **RQ3:** Các phân khúc khách hàng có đặc điểm gì và có thể gợi ý những định hướng marketing nào?

### 1.5. Phạm vi nghiên cứu

Nhóm chỉ dùng REES46 Cosmetics. Khoảng quan sát dự kiến là `[2019-10-01, 2020-02-01)`; cửa sổ tương tác gần đây là `[2020-01-02, 2020-02-01)`, theo quy ước UTC đang chờ kiểm tra lại ở Phase 2. Mỗi bảng đặc trưng có một dòng/khách hàng; dữ liệu sự kiện được tổng hợp trước mốc chốt, kể cả khi session kéo dài qua mốc này.

Chỉ buyers có RFM hợp lệ được đưa vào so sánh F0/F1. Non-buyers được mô tả riêng về tương tác, không gán Recency giả. Cách loại trùng, buyer, price, session và rounding vẫn chờ chốt ở Phase 2; các bảng cũ chỉ là ứng viên. Không dùng model/scaler/labels/metrics 7D cũ cho nghiên cứu 5D này. February đã được xem nên không phải untouched holdout; không dùng February tạo đặc trưng hoặc chọn mô hình.

P1-T1 chỉ xác định bài toán và cách kiểm chứng. Chưa EDA, xử lý dữ liệu, tạo đặc trưng, chạy K-Means hoặc làm dashboard. Phạm vi toàn dự án nằm trong `PROJECT_PLAN.md`; các vấn đề dữ liệu giữ ở mục 4.5.

### 1.6. Phương pháp nghiên cứu dự kiến

Nhóm dự kiến kiểm tra chất lượng và chốt quy tắc dữ liệu ở Phase 2, mô tả hành vi ở Phase 3, tính năm đặc trưng ở Phase 4, so sánh F0/F1 ở Phase 5 rồi diễn giải ở Phase 6.

Nhóm sẽ dùng K-Means để so sánh hai bộ đặc trưng trên cùng buyers và cửa sổ dữ liệu. F0 là baseline — phương án cơ sở để đối chiếu. Kết quả được xem xét bằng các tiêu chí phù hợp, kết hợp chất lượng phân cụm, đặc điểm khách hàng và khả năng giải thích; không mặc định F1 tốt hơn F0. Chi tiết thực nghiệm và cách đánh giá sẽ học ở Phase 5, theo kế hoạch bên dưới.

## 2. Kế hoạch kiểm chứng ba câu hỏi

Đọc bảng từ trái sang phải: câu hỏi cần biết điều gì → phải có dữ liệu nào → dự kiến làm gì → phải lưu kết quả nào → dựa vào đâu để nhận xét. Đây là kế hoạch, chưa phải kết quả phân tích.

| Câu hỏi | Dữ liệu cần dùng | Cách phân tích dự kiến | Kết quả cần có | Cách đánh giá |
|---|---|---|---|---|
| RQ1 — hành vi mua và tương tác | Events trước cutoff: thời gian, loại event, user, session, price; quy tắc hợp lệ đã chốt | Phase 3: thống kê sự kiện, phiên và khách; mô tả phân phối mua/tương tác; tách buyers và non-buyers | Bảng/biểu đồ có đơn vị một dòng, mẫu số và cửa sổ thời gian rõ | Đối chiếu số đếm với nguồn đã chấp nhận; không coi purchase rows là số đơn; giải thích missing/outliers và giới hạn quan sát |
| RQ2 — thông tin bổ sung từ Engagement | Cùng buyers với năm biến hợp lệ; F0 dùng ba biến, F1 dùng năm biến | Phase 5: so sánh F0/F1; xem chỉ số và đặc điểm cụm trên cùng năm biến ở đơn vị gốc | Bảng so sánh cấu hình, Silhouette, Davies–Bouldin, cỡ cụm, đặc điểm cụm, ổn định và tài nguyên | Đúng cohort/cutoff trước; cân nhắc chất lượng, thông tin bổ sung và khả năng giải thích; không xếp hạng chỉ bằng Silhouette; chấp nhận kết quả chưa có bằng chứng F1 tốt hơn |
| RQ3 — diễn giải và gợi ý | Nhãn cụm mới cùng bảng đặc trưng đã chấp nhận; không lấy nhãn 7D cũ | Phase 6: mô tả mỗi nhóm và nối đặc điểm quan sát với hướng tiếp cận dự kiến | Bảng đặc điểm → diễn giải → gợi ý marketing → giới hạn | Mỗi gợi ý phải chỉ được bằng chứng mô tả; không gán xác suất mua, không khẳng định nhân quả hoặc hiệu quả chiến dịch khi chưa thử nghiệm |

## 3. Tài liệu tham khảo liên quan

### 3.1. Dự án RFM truyền thống được tham khảo — P1-T2

Nhóm đọc repository ch1ns0n/Customer-Segmentation tại commit `d4a8a864ef0128708a0cd0a0e2799faf23b9dd60`, gồm [README](https://github.com/ch1ns0n/Customer-Segmentation/blob/d4a8a864ef0128708a0cd0a0e2799faf23b9dd60/README.md), [Customer_Segmentation_Model.ipynb](https://github.com/ch1ns0n/Customer-Segmentation/blob/d4a8a864ef0128708a0cd0a0e2799faf23b9dd60/Customer_Segmentation_Model.ipynb) và [customer_segmentation_app/app.py](https://github.com/ch1ns0n/Customer-Segmentation/blob/d4a8a864ef0128708a0cd0a0e2799faf23b9dd60/customer_segmentation_app/app.py). Mục đích là hiểu cách nối dữ liệu giao dịch với RFM, biến đổi và phân cụm, không sao chép hoặc chạy lại mô hình. Số ô notebook dưới đây đếm từ 1, gồm cả ô Markdown, không phải execution count.

README ghi nguồn Online Retail từ UCI. Theo [mô tả UCI](https://archive.ics.uci.edu/dataset/352/online+retail), đây là giao dịch bán lẻ trực tuyến tại Anh giai đoạn 2010–2011. Tám cột gồm InvoiceNo — mã hóa đơn, StockCode — mã sản phẩm, Description — mô tả, Quantity — số lượng, InvoiceDate — thời điểm, UnitPrice — đơn giá, CustomerID — mã khách và Country — quốc gia. Một dòng thể hiện một mặt hàng trong giao dịch; một hóa đơn có thể có nhiều dòng. UCI mô tả mã InvoiceNo bắt đầu bằng C/c là giao dịch hủy và UnitPrice dùng bảng Anh. Nhóm chỉ đối chiếu mô tả và code, chưa tải/kiểm tra tệp Excel để xác nhận nó trùng bản UCI.

### 3.2. Cách repository tính RFM và phân cụm

| Bước và vị trí | Cách làm trong repository | Điều nhóm cần hiểu |
|---|---|---|
| Chuẩn bị, ô 3–7 | Đọc Excel, bỏ dòng thiếu CustomerID, tạo TotalPrice bằng Quantity × UnitPrice | Thiếu mã khách thì không gom RFM cho đúng người. Phân tích sau khi bỏ dòng chỉ đại diện các khách có ID; tổng giá một dòng khác đơn giá |
| RFM, ô 8 | Mốc tham chiếu là InvoiceDate lớn nhất sau bước bỏ ID thiếu cộng một ngày. Gom theo CustomerID: R lấy chênh lệch với ngày cuối bằng `.days`; F đếm InvoiceNo riêng biệt; M cộng TotalPrice | Một hóa đơn nhiều sản phẩm vẫn chỉ làm F tăng một. Code lấy ngày cuối của các dòng còn lại, chưa tách riêng mua hợp lệ với hủy/hoàn trả |
| Biến đổi, ô 12–15 | Lấy log1p của F và M; sau đó ghi đè Monetary_log: M dương thì lấy log1p, còn lại bằng 0. StandardScaler học trên R, Frequency_log, Monetary_log theo đúng thứ tự này | Log giảm chênh lệch lớn; scaler đưa các biến về thang đo so sánh được. Hai bước có vai trò khác nhau và chưa tự bảo đảm phân cụm tốt |
| Chọn K và phân cụm, ô 16–18 | Vẽ Elbow từ inertia cho K=1–10; sau đó đặt K=4, random_state=42 | Inertia là tổng khoảng cách bình phương tới tâm cụm. README nói K=4 được chọn thủ công theo khả năng diễn giải; không có lệnh tự tìm điểm gãy và không có chứng minh 4 là lựa chọn duy nhất |
| Diễn giải, ô 19–26 | Xem trung bình RFM, boxplot/biểu đồ; vẽ PCA hai chiều; gán tên bằng dictionary theo nhãn 0–3 | PCA được dùng sau khi fit để vẽ, không phải ba biến đầu vào mô hình. Tên cụm do tác giả đặt, không phải thuật toán tự hiểu nghiệp vụ |
| Demo, ô 28 và app.py | Lưu model/scaler; web nhận R/F/M, biến đổi log F/M, dùng scaler đã lưu rồi gán cụm bằng model | `predict` ở đây là gán vào cụm đã học, không phải dự đoán xác suất mua. Nhóm chỉ đọc luồng này, không mở web hoặc nạp pickle |

Tên được gán là Occasional Buyers, Loyal High-Spenders, Dormant Customers và Potential Loyalists. Bảng trung bình đã lưu ở ô 19 phù hợp với cách mô tả tương đối: cụm 1 có F/M cao hơn, cụm 2 có R cao hơn các cụm còn lại. Tuy nhiên, tên “tiềm năng trung thành” chưa xác minh hành vi tương lai. Khi tự nghiên cứu, nhóm cần đọc đặc điểm ở đơn vị gốc trước khi đặt tên; không mang nguyên tên hay số cụm sang REES46.

### 3.3. Những điểm cần thận trọng khi học theo

Các nhận xét dưới đây chỉ dựa trên ba file đã đọc và output được lưu trong notebook gốc, không phải kết quả chạy mới:

- **Hủy/hoàn trả:** trước khi tính RFM, code chỉ bỏ ID thiếu; chưa có bước lọc InvoiceNo dạng C/c hoặc kiểm tra Quantity/UnitPrice. Vì vậy hóa đơn hủy có thể được tính vào F, ngày hủy có thể ảnh hưởng R và giá trị âm có thể đi vào M. Cần xác định ý nghĩa giao dịch trước khi gọi chúng là hành vi mua.
- **Monetary không dương:** ô 12–13 lưu cảnh báo log không hợp lệ và giá trị Monetary_log thiếu. Ô 14 thay toàn bộ M≤0 bằng 0 trên thang log, làm mất phân biệt giữa các mức âm và 0; đây chưa phải chính sách xử lý hoàn trả đã được giải thích. Không chuyển quy tắc này sang MVP khi cleaning policy còn chờ Phase 2.
- **Đánh giá K:** ba file có inertia/Elbow và mô tả cụm, nhưng không có code tính Silhouette, Davies–Bouldin hoặc kiểm tra ổn định qua nhiều seed. Elbow và biểu đồ hai chiều chưa đủ để khẳng định K=4 tốt nhất; không suy ra độ chính xác phân loại hoặc hiệu quả marketing.
- **Nhất quán khi đưa lên web:** notebook dùng quy tắc M dương mới lấy log, còn app.py lấy log1p(M) trực tiếp. M âm có thể cho giá trị khác bước huấn luyện, hoặc không hữu hạn khi M≤−1. Chỉ riêng việc nạp cùng scaler không sửa được khác biệt này. App cũng chưa có kiểm tra miền giá trị nghiệp vụ trước bước log.
- **Giới hạn kiểm chứng:** không chạy notebook, không tải Excel, không nạp model/scaler pickle nên chưa xác nhận các artifact lưu sẵn khớp đúng notebook này. Đường dẫn xuất file Windows riêng ở ô 28 không phù hợp để sao chép sang Colab hoặc máy của nhóm.

### 3.4. So sánh với nghiên cứu REES46 của nhóm

| Nội dung | Repository Online Retail | MVP REES46 |
|---|---|---|
| Nguồn dữ liệu | UCI theo README, bán lẻ trực tuyến 2010–2011; chưa xác minh bản Excel | Cosmetics events 2019–2020; nguồn/điều khoản còn các mục cần xác minh ở Phase 2 |
| Đơn vị một dòng | Dòng mặt hàng trong giao dịch/hóa đơn | Sự kiện website: view, cart, purchase… |
| Mã hóa đơn/đơn hàng | Có InvoiceNo, một hóa đơn có thể nhiều dòng | Không có order_id; không suy mã đơn từ session |
| Frequency | Code đếm InvoiceNo riêng biệt, chưa loại hóa đơn hủy | Số phiên có mua duy nhất theo `(user_id, session_id)`; chính sách hợp lệ vẫn cần chốt |
| Monetary | Cộng Quantity × UnitPrice; code chưa tách hủy/hoàn trả | Cộng price của purchase hợp lệ; không có quantity để tự nhân, không gọi là net GMV |
| Đầu vào K-Means | Ba biến R, log F, log M sau StandardScaler, với quy tắc M≤0 nêu trên | Dự kiến F0: R/F/M; F1 thêm sessions_30d/views_30d; biến đổi cụ thể chờ Phase 4 |
| Đánh giá/trình bày | Inertia/Elbow, thống kê/biểu đồ, tên cụm thủ công và Flask demo | Dự kiến so sánh nhiều tiêu chí ở Phase 5 và giải thích kết quả ở Phase 6; chưa có model/metrics MVP |

Nhóm có thể học cách gom từ dòng giao dịch lên một khách hàng, xem phân phối trước khi biến đổi và đọc đặc điểm cụm trước khi đặt tên. Nhóm không sao chép K=4, quy tắc xử lý giá âm, dictionary tên cụm, đường dẫn xuất model hay Flask. Không so trực tiếp điểm Silhouette hoặc tên cụm giữa hai dự án có dữ liệu, định nghĩa và không gian đặc trưng khác nhau. P1-T2 chỉ giúp hiểu phương pháp; không thay đổi chính sách dữ liệu hoặc hoàn thành thí nghiệm REES46.

## 4. Tìm hiểu dữ liệu và chuẩn bị dự án

### 4.1. Mục đích kiểm kê dữ liệu cũ

Trước khi phân tích, nhóm cần biết những tệp nào đã có, chúng được tạo ra như thế nào và có phù hợp với MVP hay không. Nguồn kiểm kê là dự án cũ `D:\Lap trinh\customer-analytics-antigravity`. Dự án cũ đang ở P8 và còn việc cần sửa; trạng thái đó không phải tiến độ của MVP.

Ở P0-T1, Codex đọc tài liệu, cấu hình và code xử lý dữ liệu cũ; kiểm tra cấu trúc Parquet, tên cột CSV khi đọc được và tính lại năm đặc trưng để so sánh với bảng đã lưu. Phần kiểm tra không sửa nguồn cũ, không tạo lại bảng đặc trưng và không huấn luyện mô hình.

Số liệu trong mục 4.1–4.6 lấy từ lần kiểm tra P0-T1. Nhóm giữ nguyên chúng khi sửa văn phong, không coi đây là số liệu được tính lại trong lần cập nhật tài liệu này. Có thể xem [kết quả kiểm tra](../results/p0_t1/audit.json), [danh sách tệp](../results/p0_t1/inventory.csv), [kiểm tra bổ sung bằng Python](../results/p0_t1/independent_verification.json) và [script đã sử dụng](../scripts/audit_existing_artifacts.py).

### 4.2. Những tệp dữ liệu hiện có

Bảng dưới giữ nguyên kết quả kiểm kê. Đơn vị kích thước là **MiB = bytes / 1.048.576**. Cột “Artifact” chỉ tệp đầu vào hoặc kết quả đã được lưu; không có nghĩa tệp đó đã được chấp nhận sử dụng cho nghiên cứu mới.

| Artifact tương đối trong nguồn cũ | MiB | Số dòng | Khả năng sử dụng |
|---|---:|---:|---|
| `data/raw/2019-Oct.csv` | 460,19 | Chưa đếm lại | Nguồn tái dựng; header 9 cột đọc được |
| `data/raw/2019-Nov.csv` | 520,55 | Chưa đếm lại | Nguồn tái dựng; header 9 cột đọc được |
| `data/raw/2019-Dec.csv` | 396,06 | Chưa đếm lại | Đang bị tiến trình khác khóa; chưa đọc header/hash |
| `data/raw/2020-Jan.csv` | 478,55 | Chưa đếm lại | Nguồn tái dựng; header 9 cột đọc được |
| `data/raw/2020-Feb.csv` | 466,16 | Chưa đếm lại | Chỉ metadata/header/hash; không đọc event để đánh giá outcome |
| `data/cleaned/clean_events.parquet` | 474,71 | 19.583.742 | Có cả future; không dùng trực tiếp làm feature input |
| `data/cleaned/observation_events.parquet` | 379,06 | 15.667.350 | Ứng viên nguồn chính; chờ chốt cleaning policy ở P2 |
| `data/cleaned/holdout_events.parquet` | 95,63 | 3.916.392 | Metadata/footer/hash; không phân tích outcome |
| `data/features/customer_features.parquet` | 13,35 | 1.341.499 | Đối soát năm cột được; có cả non-buyers |
| `data/features/buyer_features.parquet` | 2,16 | 92.652 | Ứng viên bảng nhỏ cho MVP, chưa được chấp nhận vô điều kiện |
| `data/features/non_buyer_features.parquet` | 9,58 | 1.248.847 | Chỉ mô tả engagement; không clustering |
| `data/features/buyer_clusters.parquet` | 2,89 | 92.652 | Loại khỏi input/kết quả MVP: labels/PCA của thí nghiệm 7D |
| `outputs/models/kmeans_best_model.joblib` | 0,04 | Không áp dụng | Chỉ hash/metadata; không load hoặc tái sử dụng model/scaler |

Trong phạm vi cây thư mục đã kiểm tra, chưa tìm thấy notebook `.ipynb`. Các tệp `scratch/*.py` là script Python, không phải notebook đã chạy. Kết quả tìm kiếm này không cho biết liệu notebook có tồn tại ở Drive hoặc máy khác hay không. Những kết quả mô hình và giao diện cũ chỉ dùng để tìm hiểu nguồn gốc, không được coi là kết quả của MVP.

### 4.3. Cấu trúc bảng và ý nghĩa của một dòng

Cấu trúc bảng, thường gọi là schema, cho biết tên cột và kiểu dữ liệu. Grain là đơn vị mà một dòng đại diện: một sự kiện trong bảng event, hoặc một khách hàng trong bảng đặc trưng. Phân biệt hai mức này giúp tránh nhầm số dòng purchase với số phiên mua.

- CSV đọc được có 9 tên cột: `event_time, event_type, product_id, category_id, category_code, brand, price, user_id, user_session`. Đọc được tên cột chưa chứng minh kiểu dữ liệu của toàn bộ CSV. Cấu trúc CSV tháng 12 vẫn chưa kiểm tra được.
- Parquet sự kiện có **21 cột**. Các cột cần cho MVP gồm `event_time TIMESTAMP`, `event_type VARCHAR`, `user_id BIGINT`, `session_id VARCHAR`, `user_session_id VARCHAR`, `price DOUBLE`, `split_partition VARCHAR`, `is_valid_for_monetary BOOLEAN`, `is_valid_for_engagement BOOLEAN`, `is_valid_session BOOLEAN`. Những cột còn lại về sản phẩm, danh mục và chất lượng dữ liệu được ghi trong tệp kết quả kiểm tra.
- Parquet đặc trưng có **23 cột**, một dòng cho mỗi user. Năm cột cần dùng là `recency_days DOUBLE`, `frequency BIGINT`, `monetary DOUBLE`, `sessions_30d BIGINT`, `views_30d BIGINT`; khóa là `user_id BIGINT`. Mã user chỉ dùng để nối và đối chiếu bảng, không đưa vào tính khoảng cách của K-Means.
- Cột `TIMESTAMP` không kèm thông tin múi giờ. Việc hiểu thời gian là UTC hiện dựa trên quy ước và code cũ, chưa được kiểm tra lại từ toàn bộ CSV gốc.

### 4.4. Kết quả đối chiếu dữ liệu ở P0-T1

Observation là dữ liệu trước mốc chốt; buyers là những khách đủ điều kiện mua hợp lệ theo code cũ; non-buyers là phần còn lại trong thời gian quan sát. Bảng dưới giữ nguyên các kết quả đã lưu.

| Kiểm tra | Kết quả |
|---|---|
| Observation min/max | 2019-10-01 00:00:00 → 2020-01-31 23:59:58 |
| Timestamp NULL/ngoài `[2019-10-01, 2020-02-01)` | 0 event |
| Sai nhãn partition / thiếu user | 0 / 0 |
| Thiếu session | 3.179 event; không tự loại toàn bộ khỏi views |
| Session token được dùng bởi nhiều user | 191 token trong clean observation; phải dùng khóa user-session |
| Composite key lệch `(user_id, session_id)` | 0 event |
| Purchase events / price không dương hoặc thiếu | 1.044.221 / 88 |
| Monetary eligibility flag lệch công thức code cũ | 0 event |
| Tổng monetary hợp lệ | 5.141.266,90 đơn vị giá dataset; không gọi là net GMV |
| Users / buyers / non-buyers | 1.341.499 / 92.652 / 1.248.847 |
| Sai giá trị năm feature so với source | 0 user ở cả customer/buyer/non-buyer tables |
| Thiếu/thừa/trùng hoặc NULL user ID khi đối soát | 0 ở cả ba bảng |
| Recency non-buyer khác NULL / buyer không hợp lệ | 0 / 0 |
| Kiểm chứng Python độc lập | 30 users, 2.733 events, 0 lệch ở cả năm feature |

Kết quả cho thấy năm đặc trưng trong các bảng cũ khớp với cách tính từ observation theo cùng quy tắc xử lý. Phép kiểm tra Python trên một mẫu chỉ giúp đối chiếu thêm công thức; không thay thế một cách tính độc lập cho toàn bộ 1,34 triệu users.

Việc tính toán khớp chưa đủ để kết luận mọi quy tắc làm sạch đều phù hợp. Nhóm vẫn cần kiểm tra ảnh hưởng của việc loại trùng, điều kiện mua hợp lệ và cách làm tròn trước khi sử dụng bảng cũ làm đầu vào chính thức. Số lượng bài kiểm tra phần mềm, thời gian chạy và chi tiết đối chiếu tệp được giữ trong [nhật ký công việc](PROGRESS.md) và thư mục `results/`.

### 4.5. Nguồn gốc, quá trình xử lý và vấn đề còn lại

Dữ liệu cũ đi qua các bước: REES46 CSV → `scripts/phase2_etl.py` → Parquet sạch/observation → `scripts/phase3_feature_engineering.py` → bảng đặc trưng khách hàng.

Code cũ loại trùng theo 7 trường `event_time,event_type,product_id,category_id,user_id,user_session,price`, không dùng `brand/category_code` trong khóa. Các sự kiện có giá không dương vẫn được giữ cho việc phân tích tương tác. Monetary chỉ nhận purchase có price>0 và user hợp lệ; R/F/M cùng dựa trên điều kiện mua này. Recency và Monetary được lưu sau khi làm tròn 2 chữ số. Đây là quy tắc của hệ thống cũ, chưa phải lựa chọn cuối cùng của MVP.

Nhóm lựa chọn xem xét observation Parquet trước vì đã có thể đọc và đối chiếu được. Bảng buyer_features nhỏ hơn cũng có thể hữu ích, nhưng hiện chỉ là ứng viên tái sử dụng. Các vấn đề cần tiếp tục kiểm tra gồm:

1. **CSV tháng 12/2019:** ở P0-T1, tệp bị tiến trình khác khóa nên chưa đọc được header/hash. Cần kiểm tra lại khi tệp được nhả khóa; không tự kết thúc tiến trình hoặc đổi quyền máy.
2. **Loại bản ghi trùng:** code dùng 7 trường trong khi tài liệu mô tả 9 trường. Chưa chứng minh hai cách tương đương cho mọi sự kiện. Không có event_id nên việc coi dòng trùng là lỗi kỹ thuật vẫn là giả định; cần xem xét ở P2-T3.
3. **Điều kiện buyer và RFM:** code dùng purchase price>0, còn định nghĩa KPI cũ rộng hơn. Các quy tắc buyer, price, session và rounding chưa chốt; không tự đổi tập khách theo kết quả mô hình.
4. **Mô hình cũ:** cấu hình còn ghi phase=P2 và F1 tương ứng 5D, nhưng bảng kết quả có thêm cart_sessions_30d và log_activity_ratio, tức 7D. Không dùng model, scaler, labels, PCA hoặc metrics 7D làm kết quả MVP 5D.
5. **February 2020:** dữ liệu đã được xem trong dự án cũ. Nếu sử dụng lại thì gọi là phân tích hồi cứu, không phải untouched holdout — tập kiểm chứng chưa từng được xem. Không dùng dữ liệu tương lai để tạo đặc trưng hoặc chọn mô hình.
6. **Giao diện cũ:** bảng dữ liệu hiển thị và dashboard có sai lệch được ghi trong báo cáo cũ mục 12.3. Không lấy chúng làm nguồn số liệu chuẩn của MVP, cũng không tái sử dụng recommendations cũ như kết quả nghiên cứu mới.
7. **Nguồn và đơn vị giá:** URL lấy từ cấu hình cũ; chưa có biên nhận tải hoặc mã kiểm tra do bên cung cấp công bố. Dấu vân tay tệp local không chứng minh nguồn gốc hoặc quyền chia sẻ. Điều khoản sử dụng, currency và đơn vị giá vẫn chưa xác minh xong.
8. **Môi trường chạy:** PyArrow từng bị Windows Application Control chặn tải DLL. P0-T3 đã được sinh viên nghiệm thu cho notebook đọc thử trên Colab/Drive; việc này chưa xác nhận toàn bộ thư viện, pipeline hoặc cách làm sạch dữ liệu. Lỗi PyArrow local và khả năng chạy đầy đủ trên môi trường mới vẫn cần kiểm tra khi có công việc liên quan.

### 4.6. Chuẩn bị sử dụng dữ liệu trên máy khác

Nhóm dùng biến môi trường `REES46_DATA_ROOT` để thay đổi nơi lưu dữ liệu mà không sửa source. Ví dụ thiết kế cho Drive là `/content/drive/MyDrive/datasets/rees46`, trong đó observation nằm tại `cleaned/observation_events.parquet`.

Khi chuyển tệp cần đối chiếu với danh sách kiểm kê và quy tắc xử lý đã thống nhất. Không dùng cách đọc gộp vô tình đưa February vào đặc trưng. Việc đọc thử trên Colab/Drive đã được người dùng xác nhận nghiệm thu P0-T3; chưa có đầu ra Colab mới để đưa số liệu vào báo cáo.

P0-T1 đã được chấp nhận có điều kiện để tiếp tục tổ chức dự án. Điều này không đồng nghĩa toàn bộ dữ liệu đã được nghiệm thu hoặc được phép sử dụng model cũ.

### 4.7. Tổ chức thư mục và chuẩn bị môi trường làm việc

**Mục đích.** Nhóm sắp xếp thư mục để hai thành viên dễ tìm code, dữ liệu và kết quả. Cấu trúc được giữ đơn giản, phù hợp với việc học và viết báo cáo môn Phân tích Dữ liệu.

**Cách thực hiện.** Dự án có `data/` cho hướng dẫn/lưu dữ liệu riêng, `notebooks/` cho bài thực hành, `results/` cho bảng kết quả/biểu đồ, `scripts/` cho code hỗ trợ, `docs/` cho tài liệu và `tests/` cho bài kiểm tra chương trình. Nhóm chọn GitHub để quản lý mã nguồn; Google Drive dự kiến dùng để chia sẻ dữ liệu khi thiết lập Colab.

Nhóm khai báo DuckDB, pandas, NumPy, Matplotlib và scikit-learn để xử lý dữ liệu, tính toán, vẽ biểu đồ và phân cụm. Streamlit và joblib được chuẩn bị cho bước trình diễn/lưu mô hình sau này. Danh sách thư viện chưa phải bộ phiên bản đã xác nhận tương thích trên môi trường mới.

**Kết quả.** P0-T2 đã được nghiệm thu PASS dựa trên kết quả Codex báo cáo: 6/6 bài kiểm tra đường dẫn và 15/15 điều kiện kiểm tra đạt. Sinh viên chưa chạy lại các script trên máy local. Các tệp và bằng chứng P0-T1 được giữ lại; chưa có notebook phân tích, model hoặc giao diện web MVP.

**Nhận xét.** Cách chia thư mục giúp nhóm biết mỗi phần nằm ở đâu và dễ đối chiếu kết quả khi viết báo cáo cuối kỳ. Việc đổi nơi lưu dữ liệu được thực hiện qua cấu hình môi trường, không phải sửa đường dẫn ở từng notebook.

**Hạn chế.** Các kiểm tra P0-T2 chỉ xác nhận cấu trúc và đường dẫn trong phạm vi đã thử, chưa đánh giá chất lượng phân cụm hoặc toàn bộ môi trường. P0-T3 được trình bày riêng bên dưới; các vấn đề dữ liệu ở mục 4.5 vẫn còn mở.

### 4.8. Chuẩn bị notebook Google Colab — P0-T3

Nhóm chuẩn bị một notebook có hướng dẫn kiểm tra Python/DuckDB, kết nối Drive, chọn thư mục dữ liệu, đọc cấu trúc bảng và đối chiếu tệp với P0-T1. Bài thực hành dùng bảng ứng viên buyer_features.parquet nhỏ, chưa cần chuyển toàn bộ dữ liệu sự kiện. Notebook không hiển thị user IDs, chưa phân tích khám phá hoặc xây dựng mô hình.

Codex đã đọc và xác nhận định dạng notebook bằng nbformat, rồi chạy các ô theo thứ tự bằng Python local trong process mới. Tệp thật có 92.652 dòng, 23 cột và khớp mốc kiểm kê; trường hợp thiếu tệp dừng rõ ràng. Đây là số liệu của lần kiểm tra local đã lưu, không phải kết quả Colab được bổ sung ở P0-T4.

Ngày 13/11/2026, người dùng xác nhận cả hai sinh viên đã trực tiếp nghiệm thu P0-T3 trên Google Colab/Drive: **PASS (Student Verified)**. Nhóm ghi nhận xác nhận này riêng với bằng chứng local của Codex. Chưa có log, phiên bản thư viện, thời gian chạy hoặc số đo Colab mới được gửi nên không tự bổ sung. Các vấn đề dữ liệu ở mục 4.5 vẫn giữ nguyên.

### 4.9. Cách nhóm hai người cùng làm việc — P0-T4

Nhóm quy định GitHub main giữ mã nguồn chính thức, còn Drive giữ dữ liệu và các bản thực hành. Mỗi notebook có một người sửa chính và một người kiểm tra trên bản sao riêng; sau khi chạy lại và được chấp nhận, bản code được bàn giao để xem thay đổi trước khi đưa vào main. Kết quả phù hợp được giữ trên Drive và trong results để không mất khi bỏ output khỏi bản mã nguồn public.

Sau mỗi task, nhóm thực hiện, giải thích kiến thức, kiểm tra và cập nhật báo cáo/sổ tay/nhật ký khi có nội dung liên quan, rồi dừng nghiệm thu. Quy trình và phân công nằm trong README. Việc thống nhất cách làm việc không thay thế bước kiểm tra và chốt các vấn đề dữ liệu ở Phase 2.

## 5–11. Chuẩn bị dữ liệu, EDA, đặc trưng, mô hình, đánh giá và trình diễn

Những phần này chưa được thực hiện trong MVP. EDA là phân tích khám phá dữ liệu; Feature Engineering là tạo đặc trưng phục vụ mô hình. Nhóm sẽ giải thích cách làm, lý do chọn và giới hạn khi đến từng bước.

Hiện chưa có model F0/F1, chỉ số phân cụm, chiến dịch hoặc Streamlit mới. Các kết quả kiểm kê ở mục 4 không thay thế kết quả của P2–P6.

### Kế hoạch đánh giá ở Phase 5 — chưa thực hiện

Hai phương án dùng cùng buyers và cửa sổ dữ liệu, cùng dải K=2–6 và cách ghi seed/cấu hình; bộ chuẩn hóa thang đo được học riêng cho mỗi bộ biến. Chi tiết thực nghiệm chỉ hoàn thiện khi đến task tương ứng.

Ở Phase 5, nhóm dự kiến dùng Silhouette để xem mức gần nhau trong cụm so với cụm lân cận và Davies–Bouldin để xem độ phân tán so với khoảng cách giữa cụm. Trong cùng điều kiện đánh giá, Silhouette cao hơn và Davies–Bouldin thấp hơn thường được ưu tiên về mặt hình học. Hai chỉ số không phải độ chính xác dự đoán hay hiệu quả kinh doanh. Xem định nghĩa tại [Silhouette](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.silhouette_score.html) và [Davies–Bouldin](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.davies_bouldin_score.html).

F0 và F1 có số chiều và không gian khoảng cách khác nhau, nên không kết luận F1 tốt hơn chỉ vì một điểm số cao hơn. Nhóm sẽ đối chiếu cả hai cách chia trên cùng năm biến ở đơn vị gốc: kích thước cụm, trung vị và độ phân tán, khác biệt tương tác giữa các nhóm có RFM tương tự, mức ổn định qua seed, khả năng giải thích, thời gian và bộ nhớ. Việc F1 chia nhóm theo chính hai biến được thêm vào cũng chưa tự chứng minh lợi ích. Nếu nhóm không ổn định, chỉ tách vài điểm cực đoan hoặc không bổ sung cách diễn giải rõ ràng, nhóm cần báo cáo giới hạn thay vì mặc định đề xuất đã thành công.

## 12. Kết luận hiện tại và hạn chế

Đã có observation Parquet và năm đặc trưng cũ nhất quán về cách tính để nhóm xem xét sử dụng lại. Tuy nhiên, nguồn gốc, cách làm sạch, điều kiện mua hợp lệ, tư cách dữ liệu February và môi trường chạy vẫn cần kiểm tra theo kế hoạch.

Nhóm chưa có cơ sở nói việc thêm Engagement tạo ra mô hình tốt hơn. Khi đánh giá ở bước sau, cần nói rõ tiêu chí so sánh và giới hạn; không suy từ một nhóm khách hàng sang hiệu quả marketing thực tế.

## 13. Nguồn tham chiếu

- [REES46 Cosmetics trên Kaggle](https://www.kaggle.com/datasets/mkechinov/ecommerce-events-history-in-cosmetics-shop): URL do config nguồn khai báo; điều khoản/cách thu thập còn chờ kiểm tra.
- [`TminTtapcode/customer-segmentation-mvp`](https://github.com/TminTtapcode/customer-segmentation-mvp): nơi lưu mã nguồn, tài liệu và bằng chứng kiểm tra của MVP.
- Nguồn local cũ: `PROJECT_STATUS.md`; `configs/project.yaml`; `configs/kpi_dictionary.yaml`; `scripts/phase2_etl.py`; `scripts/phase3_feature_engineering.py`; `reports/DATA_ANALYTICS_REPORT.md` mục 12.3; `reports/TECHNICAL_LEARNING_NOTES.md` phần X. Hash/version nguồn trong `audit.json`.
- Bằng chứng mới: `results/p0_t1/{audit.json,inventory.csv,independent_verification.json,audit_stdout.txt,verification_stdout.txt,execution.json}`.
