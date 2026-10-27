import csv
from decimal import Decimal, InvalidOperation

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify

from store.models import Categories, Products


TRUE_VALUES = ('1', 'true', 'yes', 'y')
FALSE_VALUES = ('0', 'false', 'no', 'n')


class Command(BaseCommand):
    help = (
        "Import categories and/or products from CSV files. "
        "Rows are matched by slug: existing rows are updated, new rows are created. "
        "See samples/categories.csv and samples/products.csv for the format."
    )

    def add_arguments(self, parser):
        parser.add_argument('--categories', help='Path to categories CSV')
        parser.add_argument('--products', help='Path to products CSV')
        parser.add_argument('--dry-run', action='store_true', help='Validate and show what would change without saving')

    def handle(self, *args, **options):
        if not options['categories'] and not options['products']:
            raise CommandError('Pass --categories and/or --products')

        with transaction.atomic():
            if options['categories']:
                self.import_categories(options['categories'])
            if options['products']:
                self.import_products(options['products'])

            if options['dry_run']:
                transaction.set_rollback(True)
                self.stdout.write(self.style.WARNING('Dry run: no changes saved'))

    def read_rows(self, path):
        try:
            with open(path, newline='', encoding='utf-8-sig') as f:
                return list(csv.DictReader(f))
        except FileNotFoundError:
            raise CommandError(f'File not found: {path}')

    def parse_bool(self, value, default, line):
        value = (value or '').strip().lower()
        if not value:
            return default
        if value in TRUE_VALUES:
            return True
        if value in FALSE_VALUES:
            return False
        raise CommandError(f'Line {line}: invalid true/false value "{value}"')

    def parse_decimal(self, value, line, field, required=False):
        value = (value or '').strip()
        if not value:
            if required:
                raise CommandError(f'Line {line}: {field} is required')
            return None
        try:
            return Decimal(value)
        except InvalidOperation:
            raise CommandError(f'Line {line}: invalid {field} "{value}"')

    def import_categories(self, path):
        rows = self.read_rows(path)
        created = updated = 0
        parents = {}

        # First pass: create/update categories, so parent order in the file doesn't matter
        for line, row in enumerate(rows, start=2):
            name = (row.get('name') or '').strip()
            if not name:
                raise CommandError(f'Line {line}: name is required')
            slug = (row.get('slug') or '').strip() or slugify(name)

            category, is_new = Categories.objects.update_or_create(
                slug=slug,
                defaults={
                    'name': name,
                    'description': (row.get('description') or '').strip() or None,
                    'active': self.parse_bool(row.get('active'), True, line),
                    'menu': self.parse_bool(row.get('menu'), False, line),
                },
            )
            parents[category] = ((row.get('parent_slug') or '').strip(), line)
            created += is_new
            updated += not is_new

        # Second pass: link parents
        for category, (parent_slug, line) in parents.items():
            parent = None
            if parent_slug:
                parent = Categories.objects.filter(slug=parent_slug).first()
                if not parent:
                    raise CommandError(f'Line {line}: parent category "{parent_slug}" not found')
            if category.parent_id != (parent.id if parent else None):
                category.parent = parent
                category.save(update_fields=['parent'])

        self.stdout.write(self.style.SUCCESS(f'Categories: {created} created, {updated} updated'))

    def import_products(self, path):
        rows = self.read_rows(path)
        created = updated = 0

        for line, row in enumerate(rows, start=2):
            name = (row.get('name') or '').strip()
            code = (row.get('code') or '').strip()
            if not name or not code:
                raise CommandError(f'Line {line}: code and name are required')
            slug = (row.get('slug') or '').strip() or slugify(name)

            category_slugs = [s.strip() for s in (row.get('categories') or '').split('|') if s.strip()]
            categories = list(Categories.objects.filter(slug__in=category_slugs))
            missing = set(category_slugs) - {c.slug for c in categories}
            if missing:
                raise CommandError(f'Line {line}: categories not found: {", ".join(sorted(missing))}')

            defaults = {
                'code': code,
                'name': name,
                'description': (row.get('description') or '').strip() or None,
                'price': self.parse_decimal(row.get('price'), line, 'price', required=True),
                'discount_price': self.parse_decimal(row.get('discount_price'), line, 'discount_price'),
                'order': int((row.get('order') or '0').strip() or 0),
                'featured': self.parse_bool(row.get('featured'), True, line),
                'active': self.parse_bool(row.get('active'), True, line),
            }
            # Image is a path inside media/ (e.g. products/lantern.jpg); blank keeps the current image
            image = (row.get('image') or '').strip()
            if image:
                defaults['image'] = image

            product, is_new = Products.objects.update_or_create(slug=slug, defaults=defaults)
            product.categories.set(categories)
            created += is_new
            updated += not is_new

        self.stdout.write(self.style.SUCCESS(f'Products: {created} created, {updated} updated'))
