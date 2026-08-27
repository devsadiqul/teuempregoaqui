import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candidate', '0002_alter_candidateprofile_country_of_birth_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='candidatelanguage',
            name='level',
        ),
        migrations.AddField(
            model_name='candidatelanguage',
            name='listening',
            field=models.CharField(blank=True, choices=[('basic', 'Basic'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced'), ('fluent_native', 'Fluent / Native')], max_length=15),
        ),
        migrations.AddField(
            model_name='candidatelanguage',
            name='reading',
            field=models.CharField(blank=True, choices=[('basic', 'Basic'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced'), ('fluent_native', 'Fluent / Native')], max_length=15),
        ),
        migrations.AddField(
            model_name='candidatelanguage',
            name='source',
            field=models.CharField(choices=[('verified', 'Verified'), ('declared_unverified', 'Declared / Unverified'), ('missing', 'Missing'), ('not_compliant', 'Not Compliant')], default='declared_unverified', help_text='Set to VERIFIED automatically when a matching certificate is on file.', max_length=20),
        ),
        migrations.AddField(
            model_name='candidatelanguage',
            name='speaking',
            field=models.CharField(blank=True, choices=[('basic', 'Basic'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced'), ('fluent_native', 'Fluent / Native')], max_length=15),
        ),
        migrations.AddField(
            model_name='candidatelanguage',
            name='writing',
            field=models.CharField(blank=True, choices=[('basic', 'Basic'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced'), ('fluent_native', 'Fluent / Native')], max_length=15),
        ),
        migrations.AddField(
            model_name='candidateprofile',
            name='expected_salary_max',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='candidateprofile',
            name='expected_salary_min',
            field=models.PositiveIntegerField(blank=True, help_text='Optional. May later interact with Tuacasaaqui housing/cost-of-living data.', null=True),
        ),
        migrations.AddField(
            model_name='candidateprofile',
            name='marketing_consent',
            field=models.BooleanField(default=False, help_text='Optional marketing-communications consent, kept separate from the Privacy Notice / Terms acceptance (client feedback: do not combine everything into one generic acceptance).'),
        ),
        migrations.AddField(
            model_name='candidateprofile',
            name='max_commute_minutes',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='candidateprofile',
            name='preferred_location',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='candidateprofile',
            name='salary_currency',
            field=models.CharField(blank=True, default='EUR', max_length=3),
        ),
        migrations.AddField(
            model_name='candidateprofile',
            name='willing_to_change_occupation',
            field=models.CharField(blank=True, choices=[('yes', 'Yes'), ('no', 'No'), ('maybe', 'Maybe')], help_text="'Are you willing to work outside your current professional field?'", max_length=5),
        ),
        migrations.AddField(
            model_name='candidateskill',
            name='source',
            field=models.CharField(choices=[('verified', 'Verified'), ('declared_unverified', 'Declared / Unverified'), ('missing', 'Missing'), ('not_compliant', 'Not Compliant')], default='declared_unverified', max_length=20),
        ),
        migrations.AddField(
            model_name='practicecredential',
            name='competent_authority',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='practicecredential',
            name='official_source_url',
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name='practicecredential',
            name='recognition_requirement_status',
            field=models.CharField(blank=True, choices=[('required', 'Required'), ('not_identified_as_required', 'Not Identified as Required'), ('further_verification_required', 'Further Verification Required')], help_text='System-populated from official sources, not user input.', max_length=30),
        ),
        migrations.AlterField(
            model_name='candidateprofile',
            name='age',
            field=models.PositiveSmallIntegerField(blank=True, help_text='Optional - collect only if a specific feature requires it. Must never be used as an employment-ranking variable.', null=True),
        ),
        migrations.AlterField(
            model_name='candidateprofile',
            name='email',
            field=models.EmailField(blank=True, help_text='Can be linked to the OIT account.', max_length=254),
        ),
        migrations.AlterField(
            model_name='candidateprofile',
            name='full_name',
            field=models.CharField(blank=True, help_text='Optional here - primarily belongs to the OIT user account.', max_length=255),
        ),
        migrations.AlterField(
            model_name='candidateprofile',
            name='immigration_status',
            field=models.CharField(blank=True, choices=[('eu_citizen', 'EU Citizen'), ('dual_citizenship', 'Dual Citizenship'), ('permanent_resident', 'Permanent Resident'), ('work_visa', 'Work Visa Holder'), ('student_visa', 'Student Visa Holder'), ('job_seeker_visa', 'Job Seeker Visa'), ('family_reunification', 'Family Reunification'), ('no_legal_status', 'No Legal Status'), ('other', 'Other')], help_text='Optional, more detailed classification. The primary self-declared signal is `work_authorization` below - we avoid forcing users into immigration categories they may not fully understand.', max_length=30),
        ),
        migrations.AlterField(
            model_name='candidateprofile',
            name='phone_number',
            field=models.CharField(blank=True, help_text='Not mandatory unless a specific feature requires it.', max_length=40),
        ),
        migrations.AlterField(
            model_name='candidateprofile',
            name='work_authorization',
            field=models.CharField(blank=True, choices=[('yes', 'Yes'), ('no', 'No'), ('pending', 'Pending'), ('dont_know', "I don't know")], help_text="Self-declared answer to: 'Do you currently have authorization to work in the selected country?' TeuEmpregoAqui does not provide an individualized legal opinion or determine immigration status.", max_length=12),
        ),
        migrations.AlterField(
            model_name='education',
            name='degree_recognized',
            field=models.CharField(choices=[('yes', 'Yes'), ('no', 'No'), ('in_progress', 'In Progress'), ('dont_know', "I Don't Know")], default='dont_know', help_text='Self-declared and optional - a migrant cannot be expected to know whether their qualification is officially recognized abroad. Whether recognition is actually required is determined separately by the system from official sources (see PracticeCredential.recognition_requirement_status).', max_length=12),
        ),
        migrations.CreateModel(
            name='CandidateLanguageCertificate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('test_name', models.CharField(max_length=120)),
                ('provider', models.CharField(blank=True, max_length=120)),
                ('score', models.CharField(blank=True, max_length=30)),
                ('cefr_level', models.CharField(blank=True, choices=[('A1', 'A1'), ('A2', 'A2'), ('B1', 'B1'), ('B2', 'B2'), ('C1', 'C1'), ('C2', 'C2'), ('native', 'Native')], max_length=10)),
                ('test_date', models.DateField(blank=True, null=True)),
                ('candidate_language', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='certificates', to='candidate.candidatelanguage')),
            ],
            options={
                'db_table': 'candidate_language_certificate',
            },
        ),
    ]