"""
Management command to verify and fix media file references.
Usage: python manage.py check_media_files
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from accounts.models import UserProfile
from bids.models import TenderApplication
from tenders.models import Tenderss
import os


class Command(BaseCommand):
    help = 'Check and verify media files are properly stored and accessible'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            dest='fix',
            help='Attempt to fix broken media references',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            dest='verbose',
            help='Show detailed information',
        )

    def handle(self, *args, **options):
        verbose = options.get('verbose', False)
        fix_issues = options.get('fix', False)

        self.stdout.write(self.style.SUCCESS('\n=== Media File Checker ===\n'))
        
        # Check if using Cloudinary or filesystem
        using_cloudinary = getattr(settings, 'USE_CLOUDINARY', False)
        self.stdout.write(f"Storage Backend: {'Cloudinary' if using_cloudinary else 'Filesystem'}")
        self.stdout.write(f"Media Root: {settings.MEDIA_ROOT}")
        self.stdout.write(f"Media URL: {settings.MEDIA_URL}\n")

        # Check profile pictures
        self.stdout.write(self.style.WARNING('Checking Profile Pictures...'))
        profile_count = 0
        missing_count = 0

        for profile in UserProfile.objects.filter(profile_pic__isnull=False).exclude(profile_pic=''):
            profile_count += 1
            if using_cloudinary:
                if verbose:
                    self.stdout.write(f"  ✓ {profile.user.username}: {profile.profile_pic.url}")
            else:
                file_path = os.path.join(settings.MEDIA_ROOT, str(profile.profile_pic))
                if os.path.exists(file_path):
                    if verbose:
                        self.stdout.write(f"  ✓ {profile.user.username}: {file_path}")
                else:
                    missing_count += 1
                    self.stdout.write(
                        self.style.ERROR(f"  ✗ MISSING: {profile.user.username}")
                    )
                    if verbose:
                        self.stdout.write(f"    Path: {file_path}")

        self.stdout.write(f"Profile Pictures: {profile_count} found, {missing_count} missing\n")

        # Check tender documents
        self.stdout.write(self.style.WARNING('Checking Tender Documents...'))
        tender_count = 0
        tender_missing = 0

        for tender in Tenderss.objects.filter(document__isnull=False).exclude(document=''):
            tender_count += 1
            if using_cloudinary:
                if verbose:
                    self.stdout.write(f"  ✓ {tender.tender_id}: {tender.document.url}")
            else:
                file_path = os.path.join(settings.MEDIA_ROOT, str(tender.document))
                if os.path.exists(file_path):
                    if verbose:
                        self.stdout.write(f"  ✓ {tender.tender_id}: {file_path}")
                else:
                    tender_missing += 1
                    self.stdout.write(
                        self.style.ERROR(f"  ✗ MISSING: {tender.tender_id}")
                    )
                    if verbose:
                        self.stdout.write(f"    Path: {file_path}")

        self.stdout.write(f"Tender Documents: {tender_count} found, {tender_missing} missing\n")

        # Check bid application documents
        self.stdout.write(self.style.WARNING('Checking Bid Application Documents...'))
        bid_count = 0
        bid_missing = 0

        for bid in TenderApplication.objects.all():
            doc_fields = [
                bid.gst_document,
                bid.financial_statement,
                bid.technical_document,
                bid.financial_document,
                bid.other_document
            ]
            
            for doc in doc_fields:
                if doc:
                    bid_count += 1
                    if using_cloudinary:
                        if verbose:
                            self.stdout.write(f"  ✓ Bid {bid.id}: {doc.url}")
                    else:
                        file_path = os.path.join(settings.MEDIA_ROOT, str(doc))
                        if os.path.exists(file_path):
                            if verbose:
                                self.stdout.write(f"  ✓ Bid {bid.id}: {file_path}")
                        else:
                            bid_missing += 1
                            self.stdout.write(
                                self.style.ERROR(f"  ✗ MISSING: Bid {bid.id}")
                            )
                            if verbose:
                                self.stdout.write(f"    Path: {file_path}")

        self.stdout.write(f"Bid Documents: {bid_count} found, {bid_missing} missing\n")

        # Summary
        total_files = profile_count + tender_count + bid_count
        total_missing = missing_count + tender_missing + bid_missing

        if total_missing == 0:
            self.stdout.write(self.style.SUCCESS(f'✓ All {total_files} media files are accessible!\n'))
        else:
            self.stdout.write(
                self.style.ERROR(f'✗ Found {total_missing} missing files out of {total_files}\n')
            )

        if fix_issues and total_missing > 0 and not using_cloudinary:
            self.stdout.write(self.style.WARNING('Note: Manual intervention may be needed to restore missing files.\n'))
