from django.core.management.base import BaseCommand
from django.apps import apps
from django.conf import settings
from django.core.files import File
from django.db import models as djmodels
import os


class Command(BaseCommand):
    help = 'Upload existing MEDIA files to Cloudinary and update FileField/ImageField values.'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Do not actually upload; just report what would be done.')

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        # Require Cloudinary to be enabled
        use_cloudinary = getattr(settings, 'USE_CLOUDINARY', False)
        if not use_cloudinary:
            self.stdout.write(self.style.ERROR('Cloudinary is not enabled (USE_CLOUDINARY is False or credentials missing).'))
            self.stdout.write('Set CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET in env and redeploy/run with those set.')
            return

        total_uploaded = 0
        # Iterate all installed models
        for model in apps.get_models():
            model_name = f"{model._meta.app_label}.{model.__name__}"
            file_fields = [f for f in model._meta.get_fields() if isinstance(f, (djmodels.FileField, djmodels.ImageField))]
            if not file_fields:
                continue

            # Informational message
            self.stdout.write(f'Checking model {model_name}')

            # Query instances that have any of these fields set
            qs = model.objects.all()
            for field in file_fields:
                field_name = field.name
                # Filter only objects where field is not empty
                qs_field = qs.exclude(**{f"{field_name}": ''}).exclude(**{f"{field_name}__isnull": True})
                for obj in qs_field.iterator():
                    f = getattr(obj, field_name)
                    if not f:
                        continue

                    # If URL already points to Cloudinary, skip
                    try:
                        url = f.url
                    except Exception:
                        url = ''
                    if 'res.cloudinary.com' in url:
                        continue

                    local_path = os.path.join(settings.MEDIA_ROOT, f.name)
                    if not os.path.exists(local_path):
                        self.stdout.write(self.style.WARNING(f'Local file not found: {local_path} (model={model_name} id={obj.pk} field={field_name})'))
                        continue

                    # Upload using the field's storage (which will be Cloudinary storage)
                    try:
                        if dry_run:
                            self.stdout.write(f'[dry-run] Would upload: {local_path} (model={model_name} id={obj.pk} field={field_name})')
                        else:
                            with open(local_path, 'rb') as fh:
                                django_file = File(fh)
                                # keep the same filename when saving to storage
                                basename = os.path.basename(f.name)
                                f.save(basename, django_file, save=True)
                            total_uploaded += 1
                            self.stdout.write(self.style.SUCCESS(f'Uploaded: {local_path} -> {getattr(obj, field_name).url}'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error uploading {local_path}: {e}'))

        self.stdout.write(self.style.SUCCESS(f'Done. Total files uploaded/updated: {total_uploaded}'))
