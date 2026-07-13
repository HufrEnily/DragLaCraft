import hashlib
import json
from pathlib import Path


# Папка, в которой находится этот скрипт.
BASE_DIR = Path(__file__).resolve().parent

# Папка серверной сборки.
BUILD_DIR = BASE_DIR / "build"

# Манифест будет создан внутри build.
OUTPUT_FILE = BUILD_DIR / "manifest.json"

CHUNK_SIZE = 1024 * 256  # 256 КБ


def calculate_sha256(file_path: Path) -> str:
    digest = hashlib.sha256()

    with file_path.open("rb") as file:
        while True:
            chunk = file.read(CHUNK_SIZE)

            if not chunk:
                break

            digest.update(chunk)

    return digest.hexdigest()


def generate_manifest():
    if not BUILD_DIR.is_dir():
        raise FileNotFoundError(
            f"Не найдена папка сборки:\n{BUILD_DIR}"
        )

    manifest = {
        "format": 2,
        "hash_algorithm": "sha256",
        "files": {},
    }

    files = sorted(
        path
        for path in BUILD_DIR.rglob("*")
        if path.is_file() and path.resolve() != OUTPUT_FILE.resolve()
    )

    for file_path in files:
        relative_path = file_path.relative_to(
            BUILD_DIR
        ).as_posix()

        file_size = file_path.stat().st_size
        file_hash = calculate_sha256(file_path)

        manifest["files"][relative_path] = {
            "sha256": file_hash,
            "size": file_size,
        }

        print(
            f"Добавлен: {relative_path} "
            f"({file_size} байт)"
        )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
    ) as output:
        json.dump(
            manifest,
            output,
            ensure_ascii=False,
            indent=4,
            sort_keys=True,
        )

    print()
    print("Манифест успешно создан:")
    print(OUTPUT_FILE)
    print(f"Всего файлов: {len(manifest['files'])}")


if __name__ == "__main__":
    try:
        generate_manifest()
    except Exception as error:
        print()
        print("Ошибка создания манифеста:")
        print(f"{type(error).__name__}: {error}")

        input("\nНажмите Enter для выхода...")