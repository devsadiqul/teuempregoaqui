from django.core.management.base import BaseCommand
from django.db import transaction
from apps.contents.models import FAQ

FAQS = {
    "en": [
        {"question": "Is this platform free to use?",
         "answer": "Yes. The compatibility assessment, gap analysis and job matching are completely free, with no credit card required."},
        {"question": "Which countries are covered?",
         "answer": "We currently focus on Portugal, Spain, France, Germany and Italy, with job data sourced only from official EU Open Data platforms."},
        {"question": "How is my compatibility score calculated?",
         "answer": "Your profile is scored against a target occupation across six factors: experience, education, skills, languages, immigration status and documentation. Each factor is weighted to produce an overall score out of 100."},
        {"question": "Is my personal data kept private?",
         "answer": "In Private Mode your data is session-based and is deleted automatically when the session expires. In Personal Account Mode it is stored only with your explicit consent and can be deleted on request."},
        {"question": "Where do the job listings come from?",
         "answer": "Listings are obtained through the Open Data platforms of official sources such as France Travail and EURES. Each job links to its official source, and we do not represent these government entities."},
        {"question": "What is the 'How to Solve' feature?",
         "answer": "For every gap in your profile, it gives a concrete action plan with the responsible institution, an official link, estimated cost, timeline, and how many points closing the gap could add to your score."},
        {"question": "Do I need my qualification recognised to apply for jobs?",
         "answer": "Recognition is essential for regulated professions and strongly preferred by many employers. The platform shows whether your target occupation is regulated and how to start the recognition process."},
        {"question": "In which languages is the platform available?",
         "answer": "The platform, your compatibility report and the guidance are available in English, Spanish and Portuguese, so you can review everything in the language you are most comfortable with."},
    ],
    "es": [
        {"question": "Es gratuita esta plataforma?",
         "answer": "Si. La evaluacion de compatibilidad, el analisis de brechas y las coincidencias de empleo son totalmente gratuitos, sin necesidad de tarjeta de credito."},
        {"question": "Que paises estan cubiertos?",
         "answer": "Actualmente nos centramos en Portugal, Espana, Francia, Alemania e Italia, con datos de empleo procedentes unicamente de plataformas oficiales de Datos Abiertos de la UE."},
        {"question": "Como se calcula mi puntuacion de compatibilidad?",
         "answer": "Su perfil se evalua frente a una ocupacion objetivo en seis factores: experiencia, formacion, competencias, idiomas, estatus migratorio y documentacion. Cada factor se pondera para producir una puntuacion total sobre 100."},
        {"question": "Se mantiene privada mi informacion personal?",
         "answer": "En el Modo Privado sus datos se basan en la sesion y se eliminan automaticamente cuando esta expira. En el Modo de Cuenta Personal se almacenan solo con su consentimiento explicito y pueden eliminarse a peticion."},
        {"question": "De donde provienen las ofertas de empleo?",
         "answer": "Las ofertas se obtienen a traves de las plataformas de Datos Abiertos de fuentes oficiales como France Travail y EURES. Cada oferta enlaza con su fuente oficial, y no representamos a estas entidades gubernamentales."},
        {"question": "Que es la funcion 'Como Resolver'?",
         "answer": "Para cada brecha de su perfil, ofrece un plan de accion concreto con la institucion responsable, un enlace oficial, el coste estimado, el plazo y cuantos puntos podria sumar a su puntuacion cerrar esa brecha."},
        {"question": "Necesito el reconocimiento de mi titulo para solicitar empleo?",
         "answer": "El reconocimiento es esencial para las profesiones reguladas y muy valorado por muchos empleadores. La plataforma indica si su ocupacion objetivo esta regulada y como iniciar el proceso de reconocimiento."},
        {"question": "En que idiomas esta disponible la plataforma?",
         "answer": "La plataforma, su informe de compatibilidad y la orientacion estan disponibles en ingles, espanol y portugues, para que pueda revisarlo todo en el idioma que le resulte mas comodo."},
    ],
    "pt": [
        {"question": "Esta plataforma e gratuita?",
         "answer": "Sim. A avaliacao de compatibilidade, a analise de lacunas e as correspondencias de emprego sao totalmente gratuitas, sem necessidade de cartao de credito."},
        {"question": "Que paises estao abrangidos?",
         "answer": "Atualmente focamo-nos em Portugal, Espanha, Franca, Alemanha e Italia, com dados de emprego provenientes apenas de plataformas oficiais de Dados Abertos da UE."},
        {"question": "Como e calculada a minha pontuacao de compatibilidade?",
         "answer": "O seu perfil e avaliado face a uma profissao alvo em seis fatores: experiencia, formacao, competencias, idiomas, estatuto de imigracao e documentacao. Cada fator e ponderado para produzir uma pontuacao total em 100."},
        {"question": "Os meus dados pessoais sao mantidos privados?",
         "answer": "No Modo Privado, os seus dados assentam na sessao e sao eliminados automaticamente quando a sessao expira. No Modo de Conta Pessoal, sao armazenados apenas com o seu consentimento explicito e podem ser eliminados a pedido."},
        {"question": "De onde vem as ofertas de emprego?",
         "answer": "As ofertas sao obtidas atraves das plataformas de Dados Abertos de fontes oficiais como a France Travail e a EURES. Cada oferta liga a sua fonte oficial, e nao representamos estas entidades governamentais."},
        {"question": "O que e a funcionalidade 'Como Resolver'?",
         "answer": "Para cada lacuna do seu perfil, fornece um plano de acao concreto com a instituicao responsavel, uma ligacao oficial, o custo estimado, o prazo e quantos pontos colmatar a lacuna pode acrescentar a sua pontuacao."},
        {"question": "Preciso do reconhecimento da minha habilitacao para me candidatar a empregos?",
         "answer": "O reconhecimento e essencial para profissoes regulamentadas e muito valorizado por muitos empregadores. A plataforma indica se a sua profissao alvo e regulamentada e como iniciar o processo de reconhecimento."},
        {"question": "Em que idiomas esta disponivel a plataforma?",
         "answer": "A plataforma, o seu relatorio de compatibilidade e a orientacao estao disponiveis em ingles, espanhol e portugues, para que possa rever tudo no idioma em que se sente mais a vontade."},
    ],
}


class Command(BaseCommand):
    help = "Seed the FAQ table with multilingual (en/es/pt) entries."

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush", action="store_true",
            help="Delete existing FAQ rows before seeding.",
        )

    @transaction.atomic
    def handle(self, *args, **opts):
        if opts["flush"]:
            self.stdout.write("Flushing existing FAQ rows...")
            FAQ.objects.all().delete()

        created, skipped = 0, 0
        for lang, items in FAQS.items():
            for idx, item in enumerate(items):
                exists = FAQ.objects.filter(
                    language=lang, question=item["question"]).exists()
                if exists:
                    skipped += 1
                    continue
                FAQ.objects.create(
                    language=lang,
                    question=item["question"],
                    answer=item["answer"],
                    order=idx,
                    is_active=True,
                )
                created += 1

        self.stdout.write(self.style.SUCCESS(
            f"FAQ seed done: {created} created, {skipped} skipped."))