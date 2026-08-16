import io
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.contents.models import (
    NewsCategory, News, ArticleCategory, Article,
    Feedback,
)

DEMO_AUTHOR_ID = "00000000-0000-0000-0000-000000000001"
DEMO_USER_ID = "00000000-0000-0000-0000-000000000002"

_PNG_1PX = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4"
    "890000000a49444154789c6360000002000100ffff03000006000557bfabd400"
    "00000049454e44ae426082"
)


def _img(name):
    return ContentFile(_PNG_1PX, name=name)


NEWS_CATEGORIES = ["Immigration", "Jobs", "Recognition", "Living in the EU", "Guides"]
ARTICLE_CATEGORIES = ["Guides", "Legal", "Career"]

NEWS = [
    {
        "title": "Europe Wants You: The 2026 Skilled Labor Strategy",
        "title_es": "Europa Te Quiere: La Estrategia de Mano de Obra Calificada para 2026",
        "title_pt": "A Europa Quer Você: Estratégia de Mão de Obra Qualificada de 2026",
        "category": "Jobs",
        "location": "Brussels",
        "content": (
            "Faced with an aging population and critical skill shortages, European "
            "Union governments are aggressively competing for specialized international "
            "talent. The primary vehicle for this is the updated EU Blue Card, which "
            "has seen significant threshold adjustments for 2026:\n\n"
            "Portugal: To fill critical gaps, Portugal has set its 2026 EU Blue Card "
            "minimum annual gross salary threshold at €21,030. For designated "
            "\"shortage occupations\" (primarily in management, IT, and specialized "
            "professional roles), this threshold drops to 1.2 times the national "
            "average salary.\n\n"
            "Germany (The Benchmark): As the EU's largest economy, Germany requires "
            "a standard minimum gross salary of €50,700 in 2026. However, for "
            "bottleneck professions—such as academic STEM professionals, doctors, "
            "veterinarians, and IT specialists—the threshold is lowered to "
            "€45,934.20.\n\n"
            "Exigencies & Requirements: Candidates universally require a recognized "
            "higher education degree (or, in specific IT cases, 3 years of equivalent "
            "professional experience), a clean criminal record, and a binding "
            "employment contract of at least 6 months."
        ),
        "content_es": (
            "Ante el envejecimiento de la población y la escasez crítica de "
            "habilidades, los gobiernos de la Unión Europea compiten agresivamente "
            "por talento internacional especializado. El principal vehículo para "
            "esto es la Tarjeta Azul de la UE actualizada, que ha registrado "
            "ajustes significativos en sus umbrales para 2026:\n\n"
            "Portugal: Para cubrir vacíos críticos, Portugal ha fijado su umbral "
            "mínimo de salario bruto anual para la Tarjeta Azul de la UE en €21.030 "
            "para 2026. Para las \"ocupaciones con escasez\" designadas "
            "(principalmente en gestión, TI y funciones profesionales "
            "especializadas), este umbral baja a 1,2 veces el salario medio "
            "nacional.\n\n"
            "Alemania (La Referencia): Como la mayor economía de la UE, Alemania "
            "exige un salario bruto mínimo estándar de €50.700 en 2026. Sin "
            "embargo, para profesiones con cuellos de botella —como profesionales "
            "académicos STEM, médicos, veterinarios y especialistas en TI— el "
            "umbral se reduce a €45.934,20.\n\n"
            "Exigencias y Requisitos: Los candidatos requieren universalmente un "
            "título de educación superior reconocido (o, en casos específicos de "
            "TI, 3 años de experiencia profesional equivalente), antecedentes "
            "penales limpios y un contrato de trabajo vinculante de al menos 6 "
            "meses."
        ),
        "content_pt": (
            "Confrontados com o envelhecimento da população e a escassez crítica "
            "de habilidades, os governos da União Europeia estão competindo "
            "agressivamente por talentos internacionais especializados. O "
            "principal veículo para isso é o Cartão Azul da UE atualizado, que "
            "viu ajustes significativos em seus limites para 2026:\n\n"
            "Portugal: Para preencher lacunas críticas, Portugal definiu seu "
            "limite mínimo de salário bruto anual para o Cartão Azul em €21.030 "
            "para 2026. Para \"profissões escassas\" designadas (principalmente "
            "em gestão, TI e funções profissionais especializadas), este limite "
            "cai para 1,2 vezes o salário médio nacional.\n\n"
            "Alemanha (A Referência): Como a maior economia da UE, a Alemanha "
            "exige um salário bruto mínimo padrão de €50.700 em 2026. No "
            "entanto, para profissões com gargalos — como profissionais "
            "acadêmicos de STEM, médicos, veterinários e especialistas em TI — o "
            "limite é reduzido para €45.934,20.\n\n"
            "Exigências e Requisitos: Os candidatos universalmente exigem um "
            "diploma de ensino superior reconhecido (ou, em casos específicos de "
            "TI, 3 anos de experiência profissional equivalente), ficha criminal "
            "limpa e um contrato de trabalho vinculativo de pelo menos 6 meses."
        ),
    },
    {
        "title": "Iberia Job Application Guide",
        "title_es": "Visados, Diplomas y las Realidades de 2026 en la Península Ibérica",
        "title_pt": "Vistos, Diplomas e as Realidades de 2026 na Península Ibérica",
        "category": "Guides",
        "location": "Lisbon",
        "content": (
            "Applying for jobs in Portugal and Spain requires navigating complex, "
            "and recently updated, bureaucratic landscapes. Immigrants must be "
            "hyper-aware of legal changes to avoid jeopardizing their status.\n\n"
            "The Portuguese Reality Check: The landscape changed drastically "
            "recently. Portugal enacted Law No. 61/2025, which abolished the "
            "standard job-seeker visa. Furthermore, the popular Manifestação de "
            "Interesse (which allowed tourists to find work and regularize their "
            "status) was permanently discontinued at the end of 2025. Currently, "
            "immigration is heavily restricted to highly skilled professionals "
            "with specialized technical competencies and pre-arranged "
            "contracts.\n\n"
            "Spain's Job-Seeking Visa: Spain still offers a 12-month Job-Seeking "
            "Visa, but it is highly restrictive. It is generally available only "
            "to descendants of Spanish nationals by origin or highly qualified "
            "workers in the SEPE's \"Hard-to-Fill Occupations\" catalog. "
            "Applicants must prove they have between €8,000 to €10,000 in "
            "savings to support themselves without working initially.\n\n"
            "Diplomas & Documentation: Simply translating a diploma is not "
            "enough. Degrees must be legally recognized. For Spain, documents "
            "must bear the Hague Apostille and be translated by a certified "
            "sworn translator (traductor jurado).\n\n"
            "Avoiding Employment Scams: Be deeply skeptical of agencies that "
            "charge you \"processing fees\" to find you a job or guarantee a "
            "work visa. Legitimate employers cover their own recruitment and "
            "legal costs. Never travel on a tourist visa with the promise of "
            "\"sorting the paperwork out later,\" especially in Portugal, where "
            "this loophole is now firmly closed."
        ),
        "content_es": (
            "Solicitar empleo en Portugal y España requiere navegar paisajes "
            "burocráticos complejos y recientemente actualizados. Los "
            "inmigrantes deben estar hiperconscientes de los cambios legales "
            "para evitar poner en riesgo su estatus.\n\n"
            "La Realidad Portuguesa: El panorama cambió drásticamente "
            "recientemente. Portugal promulgó la Ley n.º 61/2025, que abolió el "
            "visado estándar de búsqueda de empleo. Además, la popular "
            "Manifestação de Interesse (que permitía a los turistas encontrar "
            "trabajo y regularizar su estatus) fue descontinuada de forma "
            "permanente a finales de 2025. Actualmente, la inmigración está muy "
            "restringida a profesionales altamente cualificados con "
            "competencias técnicas especializadas y contratos preestablecidos.\n\n"
            "El Visado de Búsqueda de Empleo de España: España todavía ofrece un "
            "Visado de Búsqueda de Empleo de 12 meses, pero es muy restrictivo. "
            "Generalmente solo está disponible para descendientes de nacionales "
            "españoles de origen o trabajadores altamente cualificados en el "
            "catálogo de \"Ocupaciones de Difícil Cobertura\" del SEPE. Los "
            "solicitantes deben demostrar que cuentan con entre 8.000 y 10.000 "
            "euros en ahorros para mantenerse sin trabajar inicialmente.\n\n"
            "Diplomas y Documentación: Simplemente traducir un diploma no es "
            "suficiente. Los títulos deben estar legalmente reconocidos. Para "
            "España, los documentos deben llevar la Apostilla de La Haya y ser "
            "traducidos por un traductor jurado certificado.\n\n"
            "Cómo Evitar Estafas de Empleo: Desconfíe profundamente de las "
            "agencias que le cobran \"tarifas de tramitación\" por encontrarle "
            "un empleo o garantizarle un visado de trabajo. Los empleadores "
            "legítimos cubren sus propios costos de reclutamiento y legales. "
            "Nunca viaje con un visado de turista con la promesa de \"arreglar "
            "el papeleo después\", especialmente en Portugal, donde este vacío "
            "legal ahora está firmemente cerrado."
        ),
        "content_pt": (
            "Candidatar-se a empregos em Portugal e na Espanha exige navegar "
            "por cenários burocráticos complexos e recentemente atualizados. Os "
            "imigrantes devem estar hiperconscientes das mudanças legais para "
            "evitar comprometer seu status.\n\n"
            "O Choque de Realidade Português: O cenário mudou drasticamente há "
            "pouco tempo. Portugal promulgou a Lei nº 61/2025, que aboliu o "
            "visto padrão de procura de trabalho. Além disso, a popular "
            "Manifestação de Interesse (que permitia aos turistas encontrar "
            "trabalho e regularizar seu status) foi permanentemente "
            "descontinuada no final de 2025. Atualmente, a imigração é "
            "fortemente restrita a profissionais altamente qualificados com "
            "competências técnicas especializadas e contratos "
            "pré-arranjados.\n\n"
            "O Visto de Procura de Emprego na Espanha: A Espanha ainda oferece "
            "um Visto de Procura de Emprego de 12 meses, mas é altamente "
            "restritivo. Geralmente está disponível apenas para descendentes de "
            "cidadãos espanhóis de origem ou trabalhadores altamente "
            "qualificados no catálogo de \"Ocupações de Difícil Preenchimento\" "
            "do SEPE. Os candidatos devem provar que possuem entre 8.000 e "
            "10.000 euros em economias para se sustentarem sem trabalhar "
            "inicialmente.\n\n"
            "Diplomas e Documentação: Simplesmente traduzir um diploma não é "
            "suficiente. Os diplomas devem ser legalmente reconhecidos. Para a "
            "Espanha, os documentos devem ter a Apostila de Haia e ser "
            "traduzidos por um tradutor juramentado oficial (traductor "
            "jurado).\n\n"
            "Evitando Golpes de Emprego: Seja profundamente cético em relação a "
            "agências que cobram \"taxas de processamento\" para encontrar um "
            "emprego para você ou garantir um visto de trabalho. Empregadores "
            "legítimos cobrem seus próprios custos legais e de recrutamento. "
            "Nunca viaje com visto de turista com a promessa de \"resolver a "
            "papelada depois\", especialmente em Portugal, onde essa brecha "
            "agora está firmemente fechada."
        ),
    },
]

ARTICLES = [
    {
        "title": "Step-by-step: recognising your degree in Portugal",
        "title_es": "Paso a paso: como reconocer tu titulo en Portugal",
        "title_pt": "Passo a passo: como reconhecer o seu diploma em Portugal",
        "category": "Guides",
        "content": (
            "This guide walks through the full process of having a foreign degree "
            "recognised in Portugal, from gathering documents to submitting them to "
            "DGES, including apostille and certified translation requirements."
        ),
        "content_es": (
            "Esta guia recorre el proceso completo para que un titulo extranjero sea "
            "reconocido en Portugal, desde reunir los documentos hasta presentarlos "
            "ante la DGES, incluyendo los requisitos de apostilla y traduccion "
            "jurada."
        ),
        "content_pt": (
            "Este guia percorre todo o processo de reconhecimento de um diploma "
            "estrangeiro em Portugal, desde a reuniao dos documentos ate a submissao "
            "junto a DGES, incluindo os requisitos de apostila e traducao "
            "certificada."
        ),
        "official_source_label": "DGES",
        "official_source_url": "https://www.dges.gov.pt",
    },
    {
        "title": "Understanding the EU Blue Card",
        "title_es": "Entendiendo la Tarjeta Azul de la UE",
        "title_pt": "Entendendo o Cartao Azul da UE",
        "category": "Legal",
        "content": (
            "The EU Blue Card is a work and residence permit for highly qualified "
            "non-EU nationals. This article explains eligibility, salary thresholds, "
            "and how it differs from national work permits."
        ),
        "content_es": (
            "La Tarjeta Azul de la UE es un permiso de trabajo y residencia para "
            "ciudadanos altamente cualificados de fuera de la UE. Este articulo "
            "explica la elegibilidad, los umbrales salariales y en que se diferencia "
            "de los permisos de trabajo nacionales."
        ),
        "content_pt": (
            "O Cartao Azul da UE e uma autorizacao de trabalho e residencia para "
            "cidadaos altamente qualificados de fora da UE. Este artigo explica a "
            "elegibilidade, os limites salariais e em que se diferencia das "
            "autorizacoes de trabalho nacionais."
        ),
        "official_source_label": "European Commission",
        "official_source_url": "https://ec.europa.eu",
    },
]

FEEDBACKS = [
    (5, "ux_feedback", "Very clear and easy to follow. The gap report is excellent."),
    (4, "feature_request", "Would love to see more job sources beyond France."),
]


class Command(BaseCommand):
    help = "Seed the contents app with demo News, Articles, FAQs, Official Sources and Feedback."

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush", action="store_true",
            help="Delete existing contents rows before seeding.",
        )

    @transaction.atomic
    def handle(self, *args, **opts):
        if opts["flush"]:
            self.stdout.write("Flushing existing contents rows...")
            for model in (Feedback, Article, ArticleCategory, News, NewsCategory):
                model.objects.all().delete()

        news_cats = {}
        for i, name in enumerate(NEWS_CATEGORIES):
            cat, _ = NewsCategory.objects.get_or_create(name=name, defaults={"order": i})
            news_cats[name] = cat

        art_cats = {}
        for i, name in enumerate(ARTICLE_CATEGORIES):
            cat, _ = ArticleCategory.objects.get_or_create(name=name, defaults={"order": i})
            art_cats[name] = cat

        news_made = 0
        for item in NEWS:
            if News.objects.filter(title=item["title"]).exists():
                continue
            obj = News(
                category=news_cats.get(item["category"]),
                author_id=DEMO_AUTHOR_ID,
                author_name="Editorial Team",
                title=item["title"], title_es=item["title_es"], title_pt=item["title_pt"],
                location=item["location"],
                content=item["content"], content_es=item["content_es"], content_pt=item["content_pt"],
                is_featured=(news_made == 0), is_published=True,
            )
            obj.thumbnail.save(f"news_{news_made}.png", _img(f"news_{news_made}.png"), save=False)
            obj.save()
            news_made += 1

        art_made = 0
        for item in ARTICLES:
            if Article.objects.filter(title=item["title"]).exists():
                continue
            Article.objects.create(
                category=art_cats.get(item["category"]),
                title=item["title"], title_es=item["title_es"], title_pt=item["title_pt"],
                content=item["content"], content_es=item["content_es"], content_pt=item["content_pt"],
                official_source_label=item["official_source_label"],
                official_source_url=item["official_source_url"],
                is_published=True,
            )
            art_made += 1

        fb_made = 0
        for rating, category, message in FEEDBACKS:
            Feedback.objects.create(user_id=DEMO_USER_ID, rating=rating,
                                    category=category, message=message)
            fb_made += 1

        self.stdout.write(self.style.SUCCESS(
            f"Seed done: {len(news_cats)} news-cats, {news_made} news, "
            f"{len(art_cats)} article-cats, {art_made} articles, "
            f"{fb_made} feedback."))