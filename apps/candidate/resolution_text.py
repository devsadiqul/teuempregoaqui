DISCLAIMER = {
    "en": "Institution, link, cost and timeline are indicative - verify with the official source.",
    "es": "La institucion, el enlace, el coste y los plazos son orientativos: verificalos con la fuente oficial.",
    "pt": "Instituicao, link, custo e prazos sao indicativos - confirme junto da fonte oficial.",
}

NONE_LABEL = {"en": "None", "es": "ninguno", "pt": "nenhum"}

IMPACT_LABELS = {
    "en": {5: "Very High", 4: "High", 3: "Medium", 2: "Low", 1: "Minimal"},
    "es": {5: "Muy alto", 4: "Alto", 3: "Medio", 2: "Bajo", 1: "Minimo"},
    "pt": {5: "Muito alto", 4: "Alto", 3: "Medio", 2: "Baixo", 1: "Minimo"},
}

LANGUAGE_NAMES = {
    "spanish": {"en": "Spanish", "es": "espanol", "pt": "espanhol"},
    "portuguese": {"en": "Portuguese", "es": "portugues", "pt": "portugues"},
    "french": {"en": "French", "es": "frances", "pt": "frances"},
    "german": {"en": "German", "es": "aleman", "pt": "alemao"},
    "italian": {"en": "Italian", "es": "italiano", "pt": "italiano"},
}

FALLBACK_INSTITUTION = {
    "language": {"en": "Accredited CEFR language centre",
                 "es": "Centro de idiomas acreditado (MCER)",
                 "pt": "Centro de linguas acreditado (QECR)"},
    "immigration": {"en": "National immigration authority",
                    "es": "Autoridad nacional de inmigracion",
                    "pt": "Autoridade nacional de imigracao"},
    "degree_recognition": {"en": "National ENIC-NARIC centre",
                           "es": "Centro nacional ENIC-NARIC",
                           "pt": "Centro nacional ENIC-NARIC"},
}

DOC_INSTITUTION = {
    "en": "Issuing country authority + sworn translator in target country",
    "es": "Autoridad del pais emisor + traductor jurado en el pais de destino",
    "pt": "Autoridade do pais emissor + tradutor ajuramentado no pais de destino",
}

TEXT = {
    "language": {
        "en": {
            "title": "Improve {language} language skills",
            "explanation": ("The role expects {language} around {target}. Your current "
                            "level ({cur}) is below requirement, which recruiters read as an "
                            "operational risk for day-to-day work and local communication."),
            "recommended_actions": [
                "Enrol in an accredited course to reach {target}",
                "Sit an official CEFR certification exam (e.g. DELE/DELF/Goethe/CELPE-Bras)",
                "Practise with language exchanges and local immersion",
            ],
            "estimated_timeline": "3 to 6 months per CEFR level",
            "estimated_cost": "EUR 200 - 800 per level (course + exam), varies by centre",
            "goal": "Reach {target} level",
        },
        "es": {
            "title": "Mejorar el nivel de {language}",
            "explanation": ("El puesto requiere {language} en torno a {target}. Tu nivel "
                            "actual ({cur}) esta por debajo de lo exigido, lo que los "
                            "reclutadores interpretan como un riesgo operativo para el "
                            "trabajo diario y la comunicacion local."),
            "recommended_actions": [
                "Matriculate en un curso acreditado para alcanzar el nivel {target}",
                "Realiza un examen oficial de certificacion MCER (p. ej. DELE/DELF/Goethe/CELPE-Bras)",
                "Practica con intercambios de idiomas e inmersion local",
            ],
            "estimated_timeline": "De 3 a 6 meses por nivel del MCER",
            "estimated_cost": "200-800 EUR por nivel (curso + examen), segun el centro",
            "goal": "Alcanzar el nivel {target}",
        },
        "pt": {
            "title": "Melhorar o nivel de {language}",
            "explanation": ("A vaga exige {language} em torno de {target}. O seu nivel "
                            "atual ({cur}) esta abaixo do exigido, o que os recrutadores "
                            "interpretam como um risco operacional para o trabalho diario "
                            "e a comunicacao local."),
            "recommended_actions": [
                "Inscreva-se num curso acreditado para atingir o nivel {target}",
                "Realize um exame oficial de certificacao QECR (ex.: DELE/DELF/Goethe/CELPE-Bras)",
                "Pratique com intercambios linguisticos e imersao local",
            ],
            "estimated_timeline": "3 a 6 meses por nivel do QECR",
            "estimated_cost": "200-800 EUR por nivel (curso + exame), varia conforme o centro",
            "goal": "Atingir o nivel {target}",
        },
    },
    "immigration": {
        "en": {
            "title": "Complete immigration regularization",
            "explanation": ("You do not yet hold definitive authorization to work in the "
                            "target country. From an employer's view this is the decisive "
                            "question - 'can I hire this person now?' - so it is typically "
                            "the single biggest barrier to an application."),
            "recommended_actions": [
                "Book an appointment with the responsible immigration authority",
                "Obtain or finalise residence and work authorization",
                "Keep proof of an in-progress process to show employers good standing",
            ],
            "estimated_timeline": "Dependent on administrative processing (often 2-9 months)",
            "estimated_cost": "EUR 80 - 400 in administrative fees (varies by permit type)",
            "goal": "Obtain residence and work authorization",
        },
        "es": {
            "title": "Completar la regularizacion migratoria",
            "explanation": ("Todavia no dispones de una autorizacion definitiva para "
                            "trabajar en el pais de destino. Desde el punto de vista del "
                            "empleador, esta es la pregunta decisiva - 'puedo contratar a "
                            "esta persona ahora?' -, por lo que suele ser la mayor barrera "
                            "para una candidatura."),
            "recommended_actions": [
                "Solicita una cita con la autoridad de extranjeria competente",
                "Obten o finaliza la autorizacion de residencia y trabajo",
                "Conserva el comprobante de un tramite en curso para demostrar tu buena situacion",
            ],
            "estimated_timeline": "Depende de la tramitacion administrativa (a menudo de 2 a 9 meses)",
            "estimated_cost": "80-400 EUR en tasas administrativas (segun el tipo de permiso)",
            "goal": "Obtener la autorizacion de residencia y trabajo",
        },
        "pt": {
            "title": "Concluir a regularizacao da imigracao",
            "explanation": ("Ainda nao tem uma autorizacao definitiva para trabalhar no "
                            "pais de destino. Do ponto de vista do empregador, esta e a "
                            "pergunta decisiva - 'posso contratar esta pessoa agora?' -, "
                            "pelo que costuma ser a maior barreira a uma candidatura."),
            "recommended_actions": [
                "Marque uma reuniao com a autoridade de imigracao competente",
                "Obtenha ou finalize a autorizacao de residencia e trabalho",
                "Guarde o comprovativo de um processo em curso para mostrar boa-fe aos empregadores",
            ],
            "estimated_timeline": "Depende da tramitacao administrativa (muitas vezes 2 a 9 meses)",
            "estimated_cost": "80-400 EUR em taxas administrativas (varia consoante o tipo de autorizacao)",
            "goal": "Obter a autorizacao de residencia e trabalho",
        },
    },
    "degree_recognition": {
        "en": {
            "title": "Complete academic recognition",
            "explanation": ("Your qualification has not been officially recognised in the "
                            "target country. Recognition confirms your degree's level and is "
                            "essential for regulated professions and strongly preferred by "
                            "employers elsewhere."),
            "recommended_actions": [
                "Submit your diploma and transcript to the recognition body",
                "Provide a Hague Apostille and certified translation if requested",
                "Request an academic-level statement of comparability",
            ],
            "estimated_timeline": "1 to 4 months (statement of comparability)",
            "estimated_cost": "EUR 0 - 200 depending on country and procedure",
            "goal": "Obtain official recognition of your degree",
        },
        "es": {
            "title": "Completar el reconocimiento academico",
            "explanation": ("Tu titulacion aun no ha sido reconocida oficialmente en el "
                            "pais de destino. El reconocimiento confirma el nivel de tu "
                            "titulo, es imprescindible para las profesiones reguladas y "
                            "muy valorado por los empleadores en general."),
            "recommended_actions": [
                "Presenta tu titulo y expediente academico ante el organismo de reconocimiento",
                "Aporta la Apostilla de La Haya y una traduccion jurada si te la solicitan",
                "Solicita una declaracion de equivalencia de nivel academico",
            ],
            "estimated_timeline": "De 1 a 4 meses (declaracion de equivalencia)",
            "estimated_cost": "0-200 EUR segun el pais y el procedimiento",
            "goal": "Obtener el reconocimiento oficial de tu titulo",
        },
        "pt": {
            "title": "Concluir o reconhecimento academico",
            "explanation": ("A sua habilitacao ainda nao foi oficialmente reconhecida no "
                            "pais de destino. O reconhecimento confirma o nivel do seu "
                            "diploma, e essencial para profissoes regulamentadas e muito "
                            "valorizado pelos empregadores em geral."),
            "recommended_actions": [
                "Submeta o seu diploma e historico ao organismo de reconhecimento",
                "Apresente a Apostila de Haia e uma traducao certificada, se solicitado",
                "Solicite uma declaracao de equivalencia de nivel academico",
            ],
            "estimated_timeline": "1 a 4 meses (declaracao de equivalencia)",
            "estimated_cost": "0-200 EUR consoante o pais e o procedimento",
            "goal": "Obter o reconhecimento oficial do seu diploma",
        },
    },
    "location": {
        "en": {
            "title": "Clarify your location / relocation preferences",
            "explanation": ("This vacancy is tied to a specific location and your profile does "
                            "not yet state a location preference or relocation willingness, so "
                            "the system cannot evidence a geographic match either way."),
            "recommended_actions": [
                "Set a preferred location or maximum commute in your profile",
                "Indicate whether you are willing to relocate within the target country",
                "Indicate whether you are open to fully remote roles, if applicable",
            ],
            "estimated_timeline": "A few minutes (profile update)",
            "estimated_cost": "Free",
            "goal": "Declare a location preference or relocation willingness",
        },
        "es": {
            "title": "Aclarar tus preferencias de ubicacion / traslado",
            "explanation": ("Esta vacante esta vinculada a una ubicacion concreta y tu perfil "
                            "aun no indica una preferencia de ubicacion ni disposicion a "
                            "trasladarte, por lo que el sistema no puede evidenciar una "
                            "coincidencia geografica en ningun sentido."),
            "recommended_actions": [
                "Define una ubicacion preferida o un tiempo maximo de desplazamiento en tu perfil",
                "Indica si estas dispuesto/a a trasladarte dentro del pais de destino",
                "Indica si aceptarias puestos totalmente remotos, si aplica",
            ],
            "estimated_timeline": "Unos minutos (actualizacion del perfil)",
            "estimated_cost": "Gratis",
            "goal": "Declarar una preferencia de ubicacion o disposicion a trasladarte",
        },
        "pt": {
            "title": "Esclarecer as suas preferencias de localizacao / mudanca",
            "explanation": ("Esta vaga esta associada a uma localizacao especifica e o seu perfil "
                            "ainda nao indica uma preferencia de localizacao nem disponibilidade "
                            "para mudanca, pelo que o sistema nao consegue evidenciar uma "
                            "correspondencia geografica em qualquer sentido."),
            "recommended_actions": [
                "Defina uma localizacao preferida ou um tempo maximo de deslocacao no seu perfil",
                "Indique se esta disponivel para se mudar dentro do pais de destino",
                "Indique se aceitaria funcoes totalmente remotas, se aplicavel",
            ],
            "estimated_timeline": "Alguns minutos (atualizacao do perfil)",
            "estimated_cost": "Gratuito",
            "goal": "Declarar uma preferencia de localizacao ou disponibilidade para mudanca",
        },
    },
    "mandatory_requirement": {
        "en": {
            "title": "Obtain the required professional licence/registration",
            "explanation": ("This occupation is legally regulated in the target country. "
                            "Without the required professional licence or registration you "
                            "are not currently eligible for this vacancy - this is a "
                            "mandatory requirement, not a ranking factor, so it is reported "
                            "separately from your score."),
            "recommended_actions": [
                "Identify the competent regulatory body for this profession",
                "Submit your qualification for professional registration/licensing",
                "Track the process status and update your profile once completed",
            ],
            "estimated_timeline": "Varies by profession and country (often 2-12 months)",
            "estimated_cost": "Varies by regulatory body",
            "goal": "Obtain the mandatory professional licence/registration",
        },
        "es": {
            "title": "Obtener la licencia/colegiacion profesional exigida",
            "explanation": ("Esta ocupacion esta legalmente regulada en el pais de destino. "
                            "Sin la licencia o colegiacion profesional exigida no eres "
                            "actualmente elegible para esta vacante - es un requisito "
                            "obligatorio, no un factor de puntuacion, por lo que se informa "
                            "por separado de tu puntuacion."),
            "recommended_actions": [
                "Identifica el organismo regulador competente para esta profesion",
                "Presenta tu titulacion para la colegiacion/licencia profesional",
                "Haz seguimiento del proceso y actualiza tu perfil al completarlo",
            ],
            "estimated_timeline": "Varia segun la profesion y el pais (a menudo 2-12 meses)",
            "estimated_cost": "Varia segun el organismo regulador",
            "goal": "Obtener la licencia/colegiacion profesional obligatoria",
        },
        "pt": {
            "title": "Obter a licenca/inscricao profissional exigida",
            "explanation": ("Esta ocupacao e legalmente regulamentada no pais de destino. "
                            "Sem a licenca ou inscricao profissional exigida, nao esta "
                            "atualmente elegivel para esta vaga - trata-se de um requisito "
                            "obrigatorio, nao de um fator de pontuacao, pelo que e reportado "
                            "separadamente da sua pontuacao."),
            "recommended_actions": [
                "Identifique o organismo regulador competente para esta profissao",
                "Submeta a sua qualificacao para inscricao/licenciamento profissional",
                "Acompanhe o processo e atualize o seu perfil quando for concluido",
            ],
            "estimated_timeline": "Varia consoante a profissao e o pais (muitas vezes 2-12 meses)",
            "estimated_cost": "Varia consoante o organismo regulador",
            "goal": "Obter a licenca/inscricao profissional obrigatoria",
        },
    },
    "skills": {
        "en": {
            "title": "Close the required skill gaps",
            "explanation": ("The vacancy lists {count} essential skill(s) you have not "
                            "declared: {listed}. Acquiring or evidencing them directly "
                            "raises your match for this and similar roles."),
            "recommended_actions": [
                "Take a short course/certification covering: {listed}",
                "Add concrete project evidence for each skill to your profile",
                "Pursue a recognised certification where one exists (e.g. Google Analytics)",
            ],
            "estimated_timeline": "2 to 12 weeks depending on the skill",
            "estimated_cost": "Free to EUR 300 (many EU/Europass resources are free)",
            "goal": "Acquire {count} missing skill(s)",
        },
        "es": {
            "title": "Cubrir las competencias requeridas que faltan",
            "explanation": ("La vacante exige {count} competencia(s) esencial(es) que no "
                            "has declarado: {listed}. Adquirirlas o demostrarlas aumenta "
                            "directamente tu compatibilidad con este y otros puestos similares."),
            "recommended_actions": [
                "Realiza un curso o certificacion breve que cubra: {listed}",
                "Anade evidencias concretas de proyectos para cada competencia en tu perfil",
                "Obten una certificacion reconocida cuando exista (p. ej. Google Analytics)",
            ],
            "estimated_timeline": "De 2 a 12 semanas segun la competencia",
            "estimated_cost": "Gratis hasta 300 EUR (muchos recursos de la UE/Europass son gratuitos)",
            "goal": "Adquirir {count} competencia(s) que falta(n)",
        },
        "pt": {
            "title": "Colmatar as competencias exigidas em falta",
            "explanation": ("A vaga exige {count} competencia(s) essencial(is) que nao "
                            "declarou: {listed}. Adquiri-las ou comprova-las aumenta "
                            "diretamente a sua compatibilidade com esta e outras vagas semelhantes."),
            "recommended_actions": [
                "Faca um curso ou certificacao curta que abranja: {listed}",
                "Acrescente evidencias concretas de projetos para cada competencia no seu perfil",
                "Obtenha uma certificacao reconhecida quando exista (ex.: Google Analytics)",
            ],
            "estimated_timeline": "2 a 12 semanas consoante a competencia",
            "estimated_cost": "Gratuito ate 300 EUR (muitos recursos da UE/Europass sao gratuitos)",
            "goal": "Adquirir {count} competencia(s) em falta",
        },
    },
    "documentation": {
        "en": {
            "title": "Complete your academic documentation",
            "explanation": ("Some supporting documents (apostille, certified translation, "
                            "grade conversion or transcript) are missing. Complete "
                            "documentation speeds up recognition and reassures employers."),
            "recommended_actions": [
                "Obtain a Hague Apostille from the issuing country's competent authority",
                "Get a certified/sworn translation in the target-country language",
                "Convert grades to the EU scale and gather course syllabi",
            ],
            "estimated_timeline": "2 to 8 weeks",
            "estimated_cost": "EUR 30 - 150 per document (apostille + sworn translation)",
            "goal": "Complete the academic documentation set",
        },
        "es": {
            "title": "Completar tu documentacion academica",
            "explanation": ("Faltan algunos documentos de respaldo (apostilla, traduccion "
                            "jurada, conversion de notas o expediente academico). Una "
                            "documentacion completa agiliza el reconocimiento y da "
                            "confianza a los empleadores."),
            "recommended_actions": [
                "Obten la Apostilla de La Haya de la autoridad competente del pais emisor",
                "Consigue una traduccion jurada en el idioma del pais de destino",
                "Convierte las notas a la escala de la UE y reune los programas de las asignaturas",
            ],
            "estimated_timeline": "De 2 a 8 semanas",
            "estimated_cost": "30-150 EUR por documento (apostilla + traduccion jurada)",
            "goal": "Completar el conjunto de documentacion academica",
        },
        "pt": {
            "title": "Completar a sua documentacao academica",
            "explanation": ("Faltam alguns documentos de suporte (apostila, traducao "
                            "certificada, conversao de notas ou historico academico). Uma "
                            "documentacao completa acelera o reconhecimento e transmite "
                            "confianca aos empregadores."),
            "recommended_actions": [
                "Obtenha a Apostila de Haia junto da autoridade competente do pais emissor",
                "Obtenha uma traducao certificada no idioma do pais de destino",
                "Converta as notas para a escala da UE e reuna os programas das disciplinas",
            ],
            "estimated_timeline": "2 a 8 semanas",
            "estimated_cost": "30-150 EUR por documento (apostila + traducao certificada)",
            "goal": "Completar o conjunto de documentacao academica",
        },
    },
}