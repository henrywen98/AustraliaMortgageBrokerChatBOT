import os
from dotenv import load_dotenv

load_dotenv()

# 基本路径
ROOT = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(ROOT, "data")
STORAGE_DIR = os.path.join(ROOT, "storage")

# 确保目录存在
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(STORAGE_DIR, exist_ok=True)

# 数据库和Chroma路径
DB_PATH = os.path.join(DATA_DIR, "archive.db")
CHROMA_DIR = os.path.join(DATA_DIR, "chroma")

# 库目录（文件索引的单一来源）
LIBRARY_DIR = os.getenv("LIBRARY_DIR", STORAGE_DIR)
os.makedirs(LIBRARY_DIR, exist_ok=True)

# 分块策略版本号
CHUNKING_VERSION = int(os.getenv("CHUNKING_VERSION", "1"))

# OpenAI配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-5-mini")

# 分块参数
CHUNK_CHARS = int(os.getenv("CHUNK_CHARS", "2500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))
SHORT_CHUNK_CHARS = int(os.getenv("SHORT_CHUNK_CHARS", "1000"))
SHORT_CHUNK_OVERLAP = int(os.getenv("SHORT_CHUNK_OVERLAP", "100"))
LONG_DOC_PAGE_THRESHOLD = int(os.getenv("LONG_DOC_PAGE_THRESHOLD", "15"))

# 批处理和向量数据库配置
EMBEDDING_BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE", "128"))
HNSW_M = int(os.getenv("HNSW_M", "16"))
HNSW_EF_CONSTRUCTION = int(os.getenv("HNSW_EF_CONSTRUCTION", "200"))
HNSW_EF_SEARCH = int(os.getenv("HNSW_EF_SEARCH", "80"))

# 检索参数
TOP_K = int(os.getenv("TOP_K", "6"))
MAX_CONTEXT_CHARS = int(os.getenv("MAX_CONTEXT_CHARS", "6000"))

# 管理员密码哈希
ADMIN_PWD_HASH = os.getenv('ADMIN_PWD_HASH', '')
