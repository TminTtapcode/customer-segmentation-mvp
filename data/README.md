# Dữ liệu REES46 — chỉ lưu riêng

- Mặc định: `data/cleaned/observation_events.parquet` tính từ root repository.
- Có thể đặt biến môi trường `REES46_DATA_ROOT` trỏ tới thư mục chứa `cleaned/`; đường dẫn tương đối tính từ root repository.
- Kiểm tra đường dẫn: `python -B scripts/data_paths.py`. Lệnh không đọc hoặc tạo dataset.
- Windows local / Google Colab–Drive: xem [README](../README.md#đường-dẫn-dữ-liệu).
- Không chép raw CSV, Parquet, archive hoặc bảng chứa user IDs vào Git. Chỉ README này được cho phép theo dõi trong `data/`.
- Kiểm tra SHA256 với [inventory P0-T1](../results/p0_t1/inventory.csv) khi chuyển file. Chưa copy/upload dữ liệu trong P0-T2.
- Artifact cũ chỉ là ứng viên tái sử dụng; các policy chưa chốt vẫn còn mở ở [PROGRESS](../docs/PROGRESS.md).
