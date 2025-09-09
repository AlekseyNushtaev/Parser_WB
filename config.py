from dotenv import load_dotenv
import os
from typing import Set, Optional

# Загрузка переменных окружения из .env файла
load_dotenv()

# Токен бота Telegram
TG_TOKEN: Optional[str] = os.environ.get("TG_TOKEN")

# Множество ID администраторов бота
ADMIN_IDS: Set[int] = {int(x) for x in os.environ.get("ADMIN_IDS", "").split()} if os.environ.get("ADMIN_IDS") else set()
VERSION: int = int(os.environ.get("VERSION"))
