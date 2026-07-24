"""SourceType enum — defines all supported data sources.

V1: UPLOAD, LOCAL, FOLDER
V2: GITHUB, CONFLUENCE, OSS, S3
"""

from enum import Enum, auto


class SourceType(Enum):
    UPLOAD = auto()
    LOCAL = auto()
    FOLDER = auto()
    # --- V2 ---
    GITHUB = auto()
    CONFLUENCE = auto()
    OSS = auto()
    S3 = auto()
