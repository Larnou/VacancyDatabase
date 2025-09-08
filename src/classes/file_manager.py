import json
from pathlib import Path

import pandas as pd


class FileManager:

    @staticmethod
    def save_to_json(sql_data: pd.DataFrame, filename: str) -> None:
        """
        Сохранение результата после запроса в БД в json-файл.
        Args:
            sql_data: Результат запроса.
            filename: Название файла.
        """

        current_file = Path(__file__).resolve()
        BASE_DIR = current_file.parent.parent.parent
        DATA_PATH = BASE_DIR / "data/requests" / filename

        data = sql_data.to_dict("records")
        json_data = {"found": len(sql_data), "items": data}
        # Создаем директорию, если её нет
        DATA_PATH.parent.mkdir(parents=True, exist_ok=True)

        # Сохраняем в файл с форматированием
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=4)
