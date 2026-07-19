  ├── ingress/
  │   ├── __init__.py
  │   ├── design.md
  │   ├── adapter/
  │   │   ├── __init__.py
  │   │   ├── base_adapter.py      # BaseAdapter + BaseBatchAdapter
  │   │   ├── upload_adapter.py    # 浏览器上传
  │   │   ├── local_adapter.py     # 指定单文件
  │   │   └── folder_adapter.py    # 目录扫描
  │   ├── model/
  │   │   ├── __init__.py
  │   │   ├── input_file.py        # @dataclass(frozen=True) InputFile
  │   │   └── source_type.py       # SourceType enum (7 sources)
  │   └── service/
  │       ├── __init__.py
  │       ├── checksum.py          # SHA256 (calculate + calculate_bytes)
  │       ├── mime_detector.py     # filetype → python-magic fallback
  │       ├── metadata_reader.py   # size, extension, created_time
  │       └── input_file_factory.py # InputFile 唯一创建入口


             Ingress
                |
 ┌──────────────┼──────────────┐
 |              |              |
API            CLI          Watcher
 |
Service
 |
Adapter
 |
Factory
 |
InputFile
 |
DocumentDispatcher


启动方式：uvicorn main:app --reload