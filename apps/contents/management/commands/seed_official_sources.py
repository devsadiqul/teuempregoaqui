from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.contents.models import OfficialSource


_PNG_1PX = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4"
    "890000000a49444154789c6360000002000100ffff03000006000557bfabd400"
    "00000049454e44ae426082"
)

SOURCES = [
    {
        "name": "AIMA", "url": "https://aima.gov.pt", "country": "Portugal", "order": 0,
        "description": "Agency for Integration, Migration and Asylum, handling residence and immigration matters in Portugal.",
        "description_es": "Agencia para la Integracion, Migracion y Asilo, encargada de los tramites de residencia e inmigracion en Portugal.",
        "description_pt": "Agencia para a Integracao, Migracoes e Asilo, responsavel pelos processos de residencia e imigracao em Portugal.",
    },
    {
        "name": "DGES", "url": "https://www.dges.gov.pt", "country": "Portugal", "order": 1,
        "description": "Directorate-General for Higher Education, which recognises foreign qualifications in Portugal.",
        "description_es": "Direccion General de Educacion Superior, que reconoce titulos extranjeros en Portugal.",
        "description_pt": "Direcao-Geral do Ensino Superior, que reconhece habilitacoes estrangeiras em Portugal.",
    },
    {
        "name": "EURES", "url": "https://eures.europa.eu", "country": "European Union", "order": 2,
        "description": "The official EU-wide job mobility portal, aggregating vacancies across member states.",
        "description_es": "El portal oficial de movilidad laboral de toda la UE, que agrega ofertas de los estados miembros.",
        "description_pt": "O portal oficial de mobilidade profissional de toda a UE, que agrega ofertas dos estados-membros.",
    },
    {
        "name": "France Travail", "url": "https://www.francetravail.fr", "country": "France", "order": 3,
        "description": "France's public employment service and the source of live job offers via its official Open Data API.",
        "description_es": "El servicio publico de empleo de Francia y la fuente de ofertas en vivo a traves de su API oficial de Datos Abiertos.",
        "description_pt": "O servico publico de emprego de Franca e a fonte de ofertas em tempo real atraves da sua API oficial de Dados Abertos.",
    },
    {
        "name": "SEPE", "url": "https://www.sepe.es", "country": "Spain", "order": 4,
        "description": "Spain's State Public Employment Service and an official Open Data source.",
        "description_es": "El Servicio Publico de Empleo Estatal de Espana y una fuente oficial de Datos Abiertos.",
        "description_pt": "O Servico Publico de Emprego Estatal de Espanha e uma fonte oficial de Dados Abertos.",
    },
    {
        "name": "IEFP", "url": "https://www.iefp.pt", "country": "Portugal", "order": 5,
        "description": "Portugal's Institute for Employment and Vocational Training.",
        "description_es": "El Instituto de Empleo y Formacion Profesional de Portugal.",
        "description_pt": "O Instituto do Emprego e Formacao Profissional de Portugal.",
    },
]


class Command(BaseCommand):
    help = "Seed Official Sources with multilingual (en/es/pt) descriptions."

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush", action="store_true",
            help="Delete existing OfficialSource rows before seeding.",
        )

    @transaction.atomic
    def handle(self, *args, **opts):
        if opts["flush"]:
            self.stdout.write("Flushing existing OfficialSource rows...")
            OfficialSource.objects.all().delete()

        created, skipped = 0, 0
        for src in SOURCES:
            if OfficialSource.objects.filter(name=src["name"]).exists():
                skipped += 1
                continue
            obj = OfficialSource(
                name=src["name"], url=src["url"], country=src["country"],
                order=src["order"], is_active=True,
                description=src["description"],
                description_es=src["description_es"],
                description_pt=src["description_pt"],
            )
            obj.icon.save(f"{src['name'].lower().replace(' ', '_')}.png",
                          ContentFile(_PNG_1PX), save=False)
            obj.save()
            created += 1

        self.stdout.write(self.style.SUCCESS(
            f"Official sources seed done: {created} created, {skipped} skipped."))
