from urllib.parse import urlparse
from django.contrib import admin, messages
import csv
from django.http import HttpResponse
from .models import Website, EmailAddress, ParserStatus
from django import forms
from django.urls import path
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.db.models import Min

from django.utils.html import format_html
from scrapers import generator_functions
from utils import run


class EmailInline(admin.TabularInline):
    model = EmailAddress
    extra = 1

class HasEmailFilter(admin.SimpleListFilter):
    title = 'Email checked'
    parameter_name = 'checked_email'

    def lookups(self, request, model_admin):
        """Определяем значения фильтра"""
        return (
            ('only', 'Companies with emails'),
            ('any', 'Companies that has no emails'),
            ('yes', 'Email checked or no domain'),
            ('no', 'Not checked (Need to check with Snovio API)')
        )

    def queryset(self, request, queryset):
        """Фильтрация queryset на основе выбранного значения"""
        if self.value() == 'yes':
            return queryset.exclude(emails_checked=False, domain__isnull=False)
        elif self.value() == 'no':
            unique_emails = (
                queryset.filter(emails_checked=False, domain__isnull=False)
                .values('domain')  # Группируем по email
                .annotate(min_id=Min('id'))  # Берём минимальный id для уникального email
                .values_list('min_id', flat=True)  # Получаем только id записей
            )
            return queryset.filter(id__in=unique_emails)
        
        elif self.value() == 'only':
            return queryset.exclude(email_addresses__isnull=True)
        
        elif self.value() == 'any':
            return queryset.filter(email_addresses__isnull=True)

        return queryset


class AllDataFilter(admin.SimpleListFilter):
    title = 'All emails'
    parameter_name = 'all'

    def lookups(self, request, model_admin):
        """Определяем значения фильтра"""
        return (
            ('all', 'All emails'),
            ('uniq', 'Unique emails'),
        )

    def queryset(self, request, queryset):
        """Фильтрация queryset на основе выбранного значения"""
        if self.value() == 'all':
            return queryset
        elif self.value() == 'uniq':
            # Группируем пользователей по email, выбирая только одного для каждого email
            unique_emails = (
                queryset.values('email')  # Группируем по email
                .annotate(min_id=Min('id'))  # Берём минимальный id для уникального email
                .values_list('min_id', flat=True)  # Получаем только id записей
            )
            return queryset.filter(id__in=unique_emails)
        return queryset


class CSVImportForm(forms.Form):
    csv_file = forms.FileField()


@admin.register(Website)
class WebsiteAdmin(admin.ModelAdmin):
    # Поля, которые будут отображаться в списке записей
    list_display = ('company', 'url', 'token_page', 'source', 'get_emails')
    list_filter = ('source', HasEmailFilter)
    inlines = [EmailInline]


    def get_emails(self, obj):
        return ", ".join(email.email for email in obj.email_addresses.all())

    get_emails.short_description = 'Emails'


@admin.register(EmailAddress)
class EmailAddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'website', 'name', 'email', 'position')
    actions = ['export_to_csv']
    change_list_template = "admin/change_list.html"
    list_filter = (AllDataFilter,)

    def export_to_csv(self, request, queryset):
        """
        Действие для экспорта данных в CSV.
        """
        # Создаем HTTP-ответ с заголовками для скачивания файла
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="email_addresses.csv"'

        # Пишем данные в CSV
        writer = csv.writer(response)
        writer.writerow(['ID', 'User Name', 'Email', 'Position', 'Company', 'Website'])  # Заголовки
        for obj in queryset:
            writer.writerow([obj.id, obj.name, obj.email, obj.position, obj.website.company, obj.website.url])

        return response

    export_to_csv.short_description = "Download email-addresses in CSV"

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('import-csv/', self.import_csv, name='import_csv'),
        ]
        return custom_urls + urls

    def import_csv(self, request):
        if request.method == "POST":
            form = CSVImportForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = form.cleaned_data['csv_file']
                decoded_file = csv_file.read().decode('utf-8').splitlines()
                reader = csv.reader(decoded_file)
                header = next(reader)  # Пропустить заголовок
                must_have = ['website', 'Position', 'Email', 'First Name', 'companyName']

                if not all([x in header for x in must_have]):
                    self.message_user(request, "One or more headers missing: "+", ".join([x for x  in must_have if x not in header]))
                    return redirect("..")
                
                url = header.index(must_have[0])
                pos = header.index(must_have[1])
                email = header.index(must_have[2])
                name = header.index(must_have[3])
                company = header.index(must_have[4])
                total = 0

                for row in reader:
                    try:
                        has_company = False

                        if not str(url).startswith('http'):
                            row[url] = 'https://' + row[url]
                        
                        domain = urlparse(row[url]).netloc
                        if not domain:
                            row[url] = 'https://' + row[email].split('@')[1]
                            domain = urlparse(row[url]).netloc

                        if not row[company].strip():
                            row[company] = domain.upper()

                        if not row[url].strip() or not row[email].strip() or not row[company].strip():
                            self.message_user(
                                request, f"Import has been ignored for: Email {row[email]}, URL: {row[url]} and Company: {row[company]}",
                                level=messages.ERROR
                            )
                            continue
                        
                        for web in Website.objects.filter(domain=domain):
                            for emails in web.email_addresses.all():
                                if emails.email == row[email]:
                                    has_company = True
                                    break
                            
                            else:
                                EmailAddress.objects.create(
                                    website=web,
                                    name=row[name],
                                    email=row[email],
                                    position=row[pos]
                                )
                                web.emails_checked = True
                                web.save()
                            has_company = True

                        if not has_company:
                            web = Website.objects.create(
                                company=row[company],
                                domain=domain,
                                source='CSV Import',
                                url=row[url],
                                emails_checked=True
                            )
                            EmailAddress.objects.create(
                                website=web,
                                name=row[name],
                                email=row[email],
                                position=row[pos]
                            )
                        total += 1
                    except Exception as e:
                        self.message_user(
                            request, f"Error while loading {row}: {e}", level=messages.ERROR
                        )
                self.message_user(request, f"Data imported successfully! Total {total} emails been imported.", level=messages.SUCCESS)
                return redirect("..")
        else:
            form = CSVImportForm()

        context = {
            "form": form,
            "title": "Import CSV",
        }
        return TemplateResponse(request, "admin/import_csv.html", context)


@admin.register(ParserStatus)
class ParserStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'progress_bar', 'enabled', 'toggle_parser', 'last_scraped')
    list_filter = ('status', 'enabled')
    readonly_fields = ('progress_bar',)

    def progress_bar(self, obj):
        return format_html(
            f'<div style="width: 100%; background-color: #f3f3f3; border: 1px solid #ccc; border-radius: 4px;">'
            f'<div style="width: {obj.progress()}%; background-color: #4caf50; height: 20px; border-radius: 4px;">'
            f'</div></div>'
        )
    progress_bar.short_description = 'Progress'

    def toggle_parser(self, obj):
        """Добавляем кнопку ВКЛ/ВЫКЛ в список объектов"""
        if obj.enabled:
            return format_html(
                '<a class="button" href="toggle/{}/">OFF</a>', obj.id
            )
        else:
            return format_html(
                '<a class="button" href="toggle/{}/">ON</a>', obj.id
            )
    toggle_parser.short_description = "ON|OFF"

    def last_scraped(self, obj: ParserStatus):
        # return f'For last {(datetime.now(timezone.utc) - obj.last_run).seconds//60} minutes scraped {obj.processed_items} websites.'
        return f'For last hour scraped {len(obj.last_parsed.all())} websites.'
    
    last_scraped.short_description = 'Scraped for the last 1 hour time'

    def get_urls(self):
        """Добавляем новый маршрут для включения/выключения"""
        urls = super().get_urls()
        custom_urls = [
            path('toggle/<int:pk>/', self.toggle_status, name='toggle_parser'),
        ]
        return custom_urls + urls

    def toggle_status(self, request, pk):
        """Функция изменения состояния парсера"""
        parser = ParserStatus.objects.get(pk=pk)
        parser.enabled = not parser.enabled
        parser.save()

        if parser.enabled:
            messages.success(request, f"Scraper {parser.name} is ON!")
            # Здесь можно запустить парсер в отдельном потоке
            import threading
            threads = threading.Thread(target=run, args=[parser.name, generator_functions[parser.name]])
            threads.start()
        else:
            messages.warning(request, f"Scraper {parser.name} is OFF!")

        return redirect(request.META.get('HTTP_REFERER', 'admin:app_parserstatus_changelist'))
