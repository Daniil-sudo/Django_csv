import csv
from django.core.management.base import BaseCommand
from .models import Phone
from django.core.validators import URLValidator
from django.utils.text import slugify
from django.core.exceptions import ValidationError  # Для проверки валидности данных
import datetime


class Command(BaseCommand):
    help = 'Import phone data from a CSV file into the Phone model'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all existing phone data before importing',
        )

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']  # Получаем путь к файлу из аргументов команды

        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing phone data...'))
            Phone.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Existing phone data cleared.'))

        try:
            with open(csv_file_path, mode='r', encoding='utf-8') as file:
                # Используем DictReader, т.к. он более читаем и гибок
                reader = csv.DictReader(file)

                # Проверка наличия необходимых колонок
                required_fields = ['name', 'price', 'image', 'release_date', 'lte_exists']
                if not all(field in reader.fieldnames for field in required_fields):
                    missing = [f for f in required_fields if f not in reader.fieldnames]
                    self.stderr.write(self.style.ERROR(
                        f"CSV file is missing required fields: {', '.join(missing)}. "
                        f"Found fields: {', '.join(reader.fieldnames)}"
                    ))
                    return

                phones_created = 0
                phones_updated = 0
                skipped_rows = 0

                for i, row in enumerate(reader):
                    row_number = i + 1  # Номер строки в CSV (начиная с 1, после заголовка)
                    try:
                        # --- Извлечение и валидация данных ---
                        name = row.get('name')
                        price_str = row.get('price')
                        image_url = row.get('image')
                        release_date_str = row.get('release_date')
                        lte_exists_str = row.get('lte_exists')

                        # Базовая проверка на пустоту обязательных полей
                        if not all([name, price_str, image_url, release_date_str, lte_exists_str]):
                            self.stderr.write(self.style.WARNING(
                                f"Row {row_number}: Skipping due to missing essential data. Row: {row}"
                            ))
                            skipped_rows += 1
                            continue

                        # Валидация цены
                        try:
                            price = float(price_str)
                        except (ValueError, TypeError):
                            self.stderr.write(self.style.WARNING(
                                f"Row {row_number}: Skipping due to invalid price format: '{price_str}'. Expected a number."
                            ))
                            skipped_rows += 1
                            continue

                        # Валидация даты выпуска (предполагаемый формат YYYY-MM-DD)
                        try:
                            release_date = datetime.datetime.strptime(release_date_str, '%Y-%m-%d').date()
                        except (ValueError, TypeError):
                            self.stderr.write(self.style.WARNING(
                                f"Row {row_number}: Skipping due to invalid release_date format: '{release_date_str}'. Expected YYYY-MM-DD."
                            ))
                            skipped_rows += 1
                            continue

                        # Валидация URL изображения
                        try:
                            URLValidator()(image_url)
                        except ValidationError:
                            self.stderr.write(self.style.WARNING(
                                f"Row {row_number}: Skipping due to invalid image URL: '{image_url}'."
                            ))
                            skipped_rows += 1
                            continue

                        # Валидация поля lte_exists (True/False)
                        # Приводим к нижнему регистру и проверяем на распространенные значения True
                        lte_exists = lte_exists_str.lower() in ('true', '1', 'yes', 'да', 'истина')

                        # Генерация slug
                        slug = slugify(name)

                        # Создание или обновление объекта Phone
                        # Используем update_or_create для предотвращения дубликатов и обновления
                        # Если есть уникальный ID в CSV, его можно использовать для поиска
                        # Здесь мы ищем по name, но это может привести к проблемам, если есть одинаковые названия.
                        # Лучше использовать уникальный внешний ID из CSV, если он есть.
                        # Предполагая, что name + release_date могут быть уникальны, или просто name

                        phone, created = Phone.objects.update_or_create(
                            name=name,  # По этому полю ищется или создается объект
                            defaults={
                                'price': price,
                                'image': image_url,
                                'release_date': release_date,
                                'lte_exists': lte_exists,
                                'slug': slug,  # Slug будет сгенерирован, но мы его явно передаем
                            }
                        )

                        if created:
                            phones_created += 1
                            self.stdout.write(self.style.SUCCESS(f"Created: {name} (Slug: {slug})"))
                        else:
                            phones_updated += 1
                            self.stdout.write(self.style.SUCCESS(f"Updated: {name} (Slug: {slug})"))

                    except Exception as e:
                        self.stderr.write(
                            self.style.ERROR(f"Row {row_number}: Error processing row {row}. Exception: {e}"))
                        skipped_rows += 1
                        continue  # Продолжаем импорт остальных строк

            self.stdout.write(self.style.SUCCESS(f'\n--- Import Summary ---'))
            self.stdout.write(self.style.SUCCESS(f'Successfully created: {phones_created} phones'))
            self.stdout.write(self.style.SUCCESS(f'Successfully updated: {phones_updated} phones'))
            if skipped_rows > 0:
                self.stdout.write(self.style.WARNING(f'Skipped rows due to errors: {skipped_rows}'))
            self.stdout.write(self.style.SUCCESS('--- Import completed ---'))

        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f'Error: The file "{csv_file_path}" was not found.'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'An unexpected error occurred: {e}'))
