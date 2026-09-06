"""
Localized copy for the candidate-facing "Strengths & Weaknesses" summary.

Same pattern as resolution_text.py: plain dicts keyed by language
("en" | "es" | "pt"), formatted with .format(**ctx) by strengths.py.
This file only holds words - no scoring logic lives here.
"""

DIMENSION_LABELS = {
    "esco_occupational_match": {
        "en": "Occupational fit", "es": "Afinidad ocupacional", "pt": "Afinidade ocupacional"},
    "skills": {
        "en": "Skills match", "es": "Coincidencia de competencias", "pt": "Correspondencia de competencias"},
    "experience": {
        "en": "Work experience", "es": "Experiencia laboral", "pt": "Experiencia profissional"},
    "languages": {
        "en": "Language proficiency", "es": "Nivel de idiomas", "pt": "Nivel de idiomas"},
    "location": {
        "en": "Location fit", "es": "Compatibilidad de ubicacion", "pt": "Compatibilidade de localizacao"},
    "recognition": {
        "en": "Professional recognition", "es": "Reconocimiento profesional", "pt": "Reconhecimento profissional"},
    "education": {
        "en": "Education level", "es": "Nivel educativo", "pt": "Nivel de escolaridade"},
    "immigration_readiness": {
        "en": "Immigration readiness", "es": "Preparacion migratoria", "pt": "Preparacao migratoria"},
    "documentation_readiness": {
        "en": "Document readiness", "es": "Preparacion documental", "pt": "Preparacao documental"},
}

SUMMARY_TEXT = {
    "en": "You have {strong} clear strength(s) and {weak} area(s) worth improving for this match.",
    "es": "Tienes {strong} punto(s) fuerte(s) claros y {weak} area(s) que conviene mejorar para esta vacante.",
    "pt": "Tem {strong} ponto(s) forte(s) claros e {weak} area(s) que vale a pena melhorar para esta vaga.",
}

# EXPLANATIONS[dimension][classification][lang] -> template string.
# classification is one of: strength | developing | weakness
EXPLANATIONS = {
    "esco_occupational_match": {
        "strength": {
            "en": "Your declared field and experience line up well with this occupation ({score}/100) - recruiters should read your background as directly relevant.",
            "es": "Tu campo y experiencia declarados encajan bien con esta ocupacion ({score}/100): los reclutadores deberian ver tu perfil como directamente relevante.",
            "pt": "A sua area e experiencia declaradas encaixam bem nesta ocupacao ({score}/100) - os recrutadores devem ver o seu perfil como diretamente relevante.",
        },
        "developing": {
            "en": "Your background is only partly aligned with this occupation ({score}/100); recruiters may see it as a related but not perfect fit.",
            "es": "Tu perfil solo encaja parcialmente con esta ocupacion ({score}/100); los reclutadores podrian verlo como afin pero no perfecto.",
            "pt": "O seu perfil encaixa apenas parcialmente nesta ocupacao ({score}/100); os recrutadores podem ve-lo como afim mas nao perfeito.",
        },
        "weakness": {
            "en": "There isn't enough information yet to confirm your fit for this occupation - add your education or experience details so this can be assessed properly.",
            "es": "Todavia no hay informacion suficiente para confirmar tu afinidad con esta ocupacion: anade tu educacion o experiencia para que se pueda evaluar bien.",
            "pt": "Ainda nao ha informacao suficiente para confirmar a sua afinidade com esta ocupacao - adicione a sua formacao ou experiencia para que isto possa ser avaliado corretamente.",
        },
    },
    "skills": {
        "strength": {
            "en": "You match {matched} of the skills this role asks for ({score}/100) - a strong technical fit.",
            "es": "Cumples {matched} de las competencias que pide este puesto ({score}/100): una buena base tecnica.",
            "pt": "Cumpre {matched} das competencias pedidas para esta vaga ({score}/100) - uma boa base tecnica.",
        },
        "developing": {
            "en": "You already match some required skills, but {missing} are still missing from your profile ({score}/100).",
            "es": "Ya cumples algunas competencias requeridas, pero aun faltan {missing} en tu perfil ({score}/100).",
            "pt": "Ja cumpre algumas competencias exigidas, mas ainda faltam {missing} no seu perfil ({score}/100).",
        },
        "weakness": {
            "en": "None of this role's essential skills are on your profile yet ({missing} missing) - this is the fastest area to improve your match.",
            "es": "Ninguna de las competencias esenciales del puesto figura aun en tu perfil ({missing} pendientes): es el area donde mas rapido puedes mejorar tu compatibilidad.",
            "pt": "Nenhuma das competencias essenciais desta vaga consta ainda no seu perfil ({missing} em falta) - e a area onde pode melhorar mais rapido a sua compatibilidade.",
        },
    },
    "general_skills": {
        "strength": {
            "en": "You have skills declared on your profile ({score}/100), which supports your general employability.",
            "es": "Tienes competencias declaradas en tu perfil ({score}/100), lo que respalda tu empleabilidad general.",
            "pt": "Tem competencias declaradas no seu perfil ({score}/100), o que apoia a sua empregabilidade geral.",
        },
        "developing": {
            "en": "Your declared skills only partly support your general employability so far ({score}/100).",
            "es": "Las competencias que has declarado solo respaldan parcialmente tu empleabilidad general por ahora ({score}/100).",
            "pt": "As competencias que declarou apoiam apenas parcialmente a sua empregabilidade geral por agora ({score}/100).",
        },
        "weakness": {
            "en": "No skills are declared on your profile yet - adding them helps every future match, not just this one.",
            "es": "Aun no has declarado competencias en tu perfil: anadirlas ayuda en cualquier futura vacante, no solo en esta.",
            "pt": "Ainda nao declarou competencias no seu perfil - adiciona-las ajuda em qualquer futura vaga, nao apenas nesta.",
        },
    },
    "general_language_level": {
        "strength": {
            "en": "Your best declared language level is a real asset for working across the EU ({score}/100).",
            "es": "Tu mejor nivel de idioma declarado es un activo real para trabajar en la UE ({score}/100).",
            "pt": "O seu melhor nivel de idioma declarado e um ativo real para trabalhar na UE ({score}/100).",
        },
        "developing": {
            "en": "You have a declared language level, but reaching a higher one would broaden your general employability ({score}/100).",
            "es": "Tienes un nivel de idioma declarado, pero alcanzar uno mas alto ampliaria tu empleabilidad general ({score}/100).",
            "pt": "Tem um nivel de idioma declarado, mas atingir um nivel mais alto ampliaria a sua empregabilidade geral ({score}/100).",
        },
        "weakness": {
            "en": "No language proficiency is declared yet - even one certified language substantially widens the roles you can be matched to.",
            "es": "Aun no has declarado ningun idioma: incluso un idioma certificado amplia mucho las vacantes con las que puedes coincidir.",
            "pt": "Ainda nao declarou nenhum idioma - mesmo um idioma certificado amplia bastante as vagas com que pode ser compativel.",
        },
    },
    "experience": {
        "strength": {
            "en": "Your years of experience and its relevance to the role are a solid strength ({score}/100).",
            "es": "Tus anos de experiencia y su relevancia para el puesto son un punto fuerte ({score}/100).",
            "pt": "Os seus anos de experiencia e a sua relevancia para a vaga sao um ponto forte ({score}/100).",
        },
        "developing": {
            "en": "Your experience counts in your favour, but its relevance or length is only partial for this role ({score}/100).",
            "es": "Tu experiencia juega a tu favor, pero su relevancia o duracion es solo parcial para este puesto ({score}/100).",
            "pt": "A sua experiencia conta a seu favor, mas a relevancia ou duracao e apenas parcial para esta vaga ({score}/100).",
        },
        "weakness": {
            "en": "No work experience is on file - add your work history so it can be counted towards your match.",
            "es": "No hay experiencia laboral registrada: anade tu historial laboral para que cuente en tu compatibilidad.",
            "pt": "Nao ha experiencia profissional registada - adicione o seu historico profissional para que conte na sua compatibilidade.",
        },
    },
    "languages": {
        "strength": {
            "en": "Your {language} level comfortably meets what this role expects ({score}/100).",
            "es": "Tu nivel de {language} cumple sin problemas lo que exige este puesto ({score}/100).",
            "pt": "O seu nivel de {language} cumpre sem problemas o exigido para esta vaga ({score}/100).",
        },
        "developing": {
            "en": "Your {language} level is close to what's required but not quite there yet ({score}/100).",
            "es": "Tu nivel de {language} esta cerca de lo requerido, pero aun no lo alcanza del todo ({score}/100).",
            "pt": "O seu nivel de {language} esta perto do exigido, mas ainda nao o atinge totalmente ({score}/100).",
        },
        "weakness": {
            "en": "This role requires {language} at {level}, and no matching proficiency is on file yet - this is likely to be read as a real operational risk.",
            "es": "Este puesto requiere {language} en nivel {level}, y aun no hay un nivel declarado que lo cubra: es probable que se interprete como un riesgo operativo real.",
            "pt": "Esta vaga exige {language} no nivel {level}, e ainda nao ha um nivel declarado que o cubra - e provavel que isto seja lido como um risco operacional real.",
        },
    },
    "location": {
        "strength": {
            "en": "Your location preference lines up well with where this role is based ({score}/100).",
            "es": "Tu preferencia de ubicacion encaja bien con la sede de este puesto ({score}/100).",
            "pt": "A sua preferencia de localizacao encaixa bem com a sede desta vaga ({score}/100).",
        },
        "developing": {
            "en": "Your preferred location differs from the vacancy, but your declared willingness to relocate softens the gap ({score}/100).",
            "es": "Tu ubicacion preferida difiere de la vacante, pero tu disposicion a mudarte reduce esa diferencia ({score}/100).",
            "pt": "A sua localizacao preferida difere da vaga, mas a sua disponibilidade para mudar de local reduz essa diferenca ({score}/100).",
        },
        "weakness": {
            "en": "No location preference or relocation willingness is declared yet - add one so recruiters can judge geographic fit fairly.",
            "es": "Aun no has declarado una ubicacion preferida ni disposicion a mudarte: anadela para que los reclutadores puedan valorar bien la compatibilidad geografica.",
            "pt": "Ainda nao declarou uma localizacao preferida nem disponibilidade para mudar - adicione isso para que os recrutadores possam avaliar bem a compatibilidade geografica.",
        },
    },
    "recognition": {
        "strength": {
            "en": "Your diploma/professional recognition for this country is already verified ({score}/100) - a real advantage over other candidates.",
            "es": "Tu reconocimiento de titulo/profesion para este pais ya esta verificado ({score}/100): una ventaja real frente a otros candidatos.",
            "pt": "O seu reconhecimento de diploma/profissao para este pais ja esta verificado ({score}/100) - uma vantagem real face a outros candidatos.",
        },
        "developing": {
            "en": "Your recognition process is underway but not complete yet ({score}/100).",
            "es": "Tu proceso de reconocimiento esta en marcha pero aun no ha terminado ({score}/100).",
            "pt": "O seu processo de reconhecimento esta em curso mas ainda nao esta concluido ({score}/100).",
        },
        "weakness": {
            "en": "This occupation requires formal recognition and none is on file yet - this can block the application outright, so it's worth prioritising.",
            "es": "Esta ocupacion exige reconocimiento formal y aun no hay ninguno registrado: esto puede bloquear la candidatura, por lo que conviene priorizarlo.",
            "pt": "Esta ocupacao exige reconhecimento formal e ainda nao ha nenhum registado - isto pode bloquear a candidatura, por isso vale a pena priorizar.",
        },
    },
    "education": {
        "strength": {
            "en": "Your qualification level is a strong asset for the EU labour market in general ({score}/100).",
            "es": "Tu nivel de formacion es un buen activo para el mercado laboral europeo en general ({score}/100).",
            "pt": "O seu nivel de formacao e um bom trunfo para o mercado de trabalho europeu em geral ({score}/100).",
        },
        "developing": {
            "en": "Your qualification is on file but its level or field relevance only partly helps your general employability ({score}/100).",
            "es": "Tu titulacion esta registrada, pero su nivel o relevancia solo ayuda parcialmente a tu empleabilidad general ({score}/100).",
            "pt": "A sua formacao esta registada, mas o seu nivel ou relevancia so ajuda parcialmente a sua empregabilidade geral ({score}/100).",
        },
        "weakness": {
            "en": "No education record is on file - adding your highest qualification will materially improve your general employability reading.",
            "es": "No hay ningun registro educativo: anadir tu titulacion mas alta mejorara notablemente tu lectura de empleabilidad general.",
            "pt": "Nao ha nenhum registo de formacao - adicionar a sua qualificacao mais alta vai melhorar significativamente a sua leitura de empregabilidade geral.",
        },
    },
    "immigration_readiness": {
        "strength": {
            "en": "Your immigration/work-authorization status is already favourable for working in the EU ({score}/100).",
            "es": "Tu situacion migratoria/autorizacion de trabajo ya es favorable para trabajar en la UE ({score}/100).",
            "pt": "A sua situacao migratoria/autorizacao de trabalho ja e favoravel para trabalhar na UE ({score}/100).",
        },
        "developing": {
            "en": "Your work authorization is pending, which keeps this only partly resolved for now ({score}/100).",
            "es": "Tu autorizacion de trabajo esta pendiente, por lo que este punto sigue solo parcialmente resuelto ({score}/100).",
            "pt": "A sua autorizacao de trabalho esta pendente, pelo que este ponto continua apenas parcialmente resolvido ({score}/100).",
        },
        "weakness": {
            "en": "Work authorization is either not in place or not declared yet - this is a foundational step to resolve before anything else.",
            "es": "La autorizacion de trabajo no esta en regla o aun no se ha declarado: es un paso base que conviene resolver antes que nada.",
            "pt": "A autorizacao de trabalho nao esta em ordem ou ainda nao foi declarada - e um passo de base a resolver antes de tudo o resto.",
        },
    },
    "documentation_readiness": {
        "strength": {
            "en": "Your supporting documents (diploma, apostille, translations, etc.) are largely in order ({score}/100).",
            "es": "Tu documentacion de apoyo (titulo, apostilla, traducciones, etc.) esta en gran parte lista ({score}/100).",
            "pt": "A sua documentacao de apoio (diploma, apostila, traducoes, etc.) esta em grande parte pronta ({score}/100).",
        },
        "developing": {
            "en": "Some supporting documents are ready, but others are still missing ({score}/100).",
            "es": "Algunos documentos de apoyo ya estan listos, pero otros aun faltan ({score}/100).",
            "pt": "Alguns documentos de apoio ja estao prontos, mas outros ainda faltam ({score}/100).",
        },
        "weakness": {
            "en": "No supporting documents (diploma, apostille, certified translation...) are declared yet - gathering these early avoids delays later.",
            "es": "Aun no se ha declarado ningun documento de apoyo (titulo, apostilla, traduccion jurada...): reunirlos con antelacion evita retrasos mas adelante.",
            "pt": "Ainda nao foi declarado nenhum documento de apoio (diploma, apostila, traducao certificada...) - reuni-los com antecedencia evita atrasos mais tarde.",
        },
    },
}

# ACTIONS[template_key][classification][lang] -> concrete "what to do next"
# text. Distinct from EXPLANATIONS on purpose: EXPLANATIONS says *why* the
# dimension currently looks the way it does; ACTIONS says *what to do about
# it* - every dimension gets one, including strengths (so nothing in the
# response is ever left unexplained).
ACTIONS = {
    "esco_occupational_match": {
        "strength": {
            "en": "No action needed here - keep your education and experience details up to date so this stays accurate.",
            "es": "Aqui no hace falta ninguna accion: mantén actualizados tu formacion y tu experiencia para que esto siga siendo exacto.",
            "pt": "Aqui nao e preciso nenhuma acao - mantenha a sua formacao e experiencia atualizadas para que isto continue exato.",
        },
        "developing": {
            "en": "Add more detail about how your field of study and past roles relate to this occupation, or mark your experience as more directly related if it is.",
            "es": "Anade mas detalle sobre como tu formacion y tus puestos anteriores se relacionan con esta ocupacion, o marca tu experiencia como mas directamente relacionada si lo es.",
            "pt": "Adicione mais detalhe sobre como a sua formacao e cargos anteriores se relacionam com esta ocupacao, ou marque a sua experiencia como mais diretamente relacionada se for o caso.",
        },
        "weakness": {
            "en": "Fill in your education record and work history - without them the system cannot judge how well your background fits this occupation.",
            "es": "Completa tu registro educativo y tu historial laboral: sin ellos el sistema no puede valorar cuanto encaja tu perfil con esta ocupacion.",
            "pt": "Preencha o seu registo educativo e historico profissional - sem eles o sistema nao consegue avaliar o quanto o seu perfil encaixa nesta ocupacao.",
        },
    },
    "skills": {
        "strength": {
            "en": "Keep this list current, and consider getting your top skills formally verified (certificate, test, portfolio) to strengthen it further.",
            "es": "Manten esta lista actualizada y considera verificar formalmente tus competencias principales (certificado, prueba, portafolio) para reforzarla aun mas.",
            "pt": "Mantenha esta lista atualizada e considere verificar formalmente as suas principais competencias (certificado, teste, portefolio) para a reforcar ainda mais.",
        },
        "developing": {
            "en": "Add the missing skill(s) to your profile: {listed_missing}. Each one you add and can back up (course, certificate, project) raises this score directly.",
            "es": "Anade a tu perfil la(s) competencia(s) que faltan: {listed_missing}. Cada una que anadas y puedas respaldar (curso, certificado, proyecto) sube esta puntuacion directamente.",
            "pt": "Adicione ao seu perfil a(s) competencia(s) em falta: {listed_missing}. Cada uma que adicionar e conseguir comprovar (curso, certificado, projeto) aumenta esta pontuacao diretamente.",
        },
        "weakness": {
            "en": "Add the required skill(s) to your profile: {listed_missing}. If you don't have them yet, a short course or certificate for each is the fastest path to a visible score increase.",
            "es": "Anade a tu perfil la(s) competencia(s) requerida(s): {listed_missing}. Si aun no las tienes, un curso corto o un certificado por cada una es la via mas rapida para subir la puntuacion de forma visible.",
            "pt": "Adicione ao seu perfil a(s) competencia(s) exigida(s): {listed_missing}. Se ainda nao as tem, um curso curto ou certificado para cada uma e o caminho mais rapido para um aumento visivel na pontuacao.",
        },
    },
    "general_skills": {
        "strength": {
            "en": "No action needed - keep adding new skills as you learn them so your profile keeps reflecting your full range.",
            "es": "No hace falta ninguna accion: sigue anadiendo nuevas competencias a medida que las aprendas para que tu perfil refleje siempre todo tu rango.",
            "pt": "Nao e preciso nenhuma acao - continue a adicionar novas competencias a medida que as aprende para que o seu perfil reflita sempre todo o seu leque.",
        },
        "developing": {
            "en": "List more of your skills, not just the ones for one specific job - a broader list improves how you match with other vacancies too.",
            "es": "Enumera mas de tus competencias, no solo las de un puesto concreto: una lista mas amplia mejora tu compatibilidad con otras vacantes tambien.",
            "pt": "Liste mais das suas competencias, nao apenas as de uma vaga especifica - uma lista mais ampla melhora a sua compatibilidade com outras vagas tambem.",
        },
        "weakness": {
            "en": "Add at least your core skills to your profile - this is a quick win that improves how you match with every vacancy, not just one.",
            "es": "Anade al menos tus competencias principales a tu perfil: es una mejora rapida que ayuda en cualquier vacante, no solo en esta.",
            "pt": "Adicione pelo menos as suas competencias principais ao seu perfil - e uma melhoria rapida que ajuda em qualquer vaga, nao apenas nesta.",
        },
    },
    "experience": {
        "strength": {
            "en": "No action needed - just keep your work history up to date as you gain more experience.",
            "es": "No hace falta ninguna accion: mantén tu historial laboral actualizado a medida que ganes mas experiencia.",
            "pt": "Nao e preciso nenhuma acao - mantenha o seu historico profissional atualizado a medida que ganha mais experiencia.",
        },
        "developing": {
            "en": "Add any missing roles or years to your work history, and describe your responsibilities so the relevance to this role is clearer.",
            "es": "Anade a tu historial laboral cualquier puesto o ano que falte, y describe tus responsabilidades para que la relevancia con este puesto sea mas clara.",
            "pt": "Adicione ao seu historico profissional quaisquer cargos ou anos em falta, e descreva as suas responsabilidades para que a relevancia para esta vaga fique mais clara.",
        },
        "weakness": {
            "en": "Add your work history (roles, dates, responsibilities) - without it, experience cannot be counted towards your score at all.",
            "es": "Anade tu historial laboral (puestos, fechas, responsabilidades): sin el, la experiencia no puede contar en absoluto para tu puntuacion.",
            "pt": "Adicione o seu historico profissional (cargos, datas, responsabilidades) - sem isso, a experiencia nao pode contar de todo para a sua pontuacao.",
        },
    },
    "languages": {
        "strength": {
            "en": "No action needed for this role - keep the certificate/level on file up to date if you take a new exam.",
            "es": "No hace falta ninguna accion para este puesto: manten actualizado el certificado/nivel si realizas un nuevo examen.",
            "pt": "Nao e preciso nenhuma acao para esta vaga - mantenha o certificado/nivel atualizado se fizer um novo exame.",
        },
        "developing": {
            "en": "Take an official {language} exam to confirm your level, or keep studying towards {level} - each level up raises this score substantially.",
            "es": "Realiza un examen oficial de {language} para confirmar tu nivel, o sigue estudiando hacia {level}: cada nivel que subes aumenta esta puntuacion de forma notable.",
            "pt": "Faca um exame oficial de {language} para confirmar o seu nivel, ou continue a estudar rumo a {level} - cada nivel que sobe aumenta esta pontuacao de forma significativa.",
        },
        "weakness": {
            "en": "Enrol in a {language} course targeting {level} and declare your current level once you have it - this is usually the single highest-impact fix available.",
            "es": "Matriculate en un curso de {language} orientado al nivel {level} y declara tu nivel actual en cuanto lo tengas: suele ser la mejora individual de mayor impacto disponible.",
            "pt": "Inscreva-se num curso de {language} com foco no nivel {level} e declare o seu nivel atual assim que o tiver - costuma ser a melhoria individual de maior impacto disponivel.",
        },
    },
    "general_language_level": {
        "strength": {
            "en": "No action needed - consider adding a second language to widen the range of countries/roles you match with.",
            "es": "No hace falta ninguna accion: considera anadir un segundo idioma para ampliar el rango de paises/puestos con los que puedes coincidir.",
            "pt": "Nao e preciso nenhuma acao - considere adicionar um segundo idioma para ampliar o leque de paises/vagas com que pode ser compativel.",
        },
        "developing": {
            "en": "Keep progressing towards the next CEFR level (e.g. B1 -> B2) and get it certified once reached.",
            "es": "Sigue avanzando hacia el siguiente nivel del MCER (p. ej. B1 -> B2) y certificalo en cuanto lo alcances.",
            "pt": "Continue a avancar para o proximo nivel do QECR (ex.: B1 -> B2) e certifique-o assim que o atingir.",
        },
        "weakness": {
            "en": "Declare at least one language level on your profile, even a basic one - this alone unlocks matching against far more vacancies.",
            "es": "Declara al menos un nivel de idioma en tu perfil, aunque sea basico: solo con eso se desbloquea la compatibilidad con muchas mas vacantes.",
            "pt": "Declare pelo menos um nivel de idioma no seu perfil, mesmo que basico - so isso ja desbloqueia a compatibilidade com muito mais vagas.",
        },
    },
    "location": {
        "strength": {
            "en": "No action needed here.",
            "es": "Aqui no hace falta ninguna accion.",
            "pt": "Aqui nao e preciso nenhuma acao.",
        },
        "developing": {
            "en": "If you can, set your preferred location to match the vacancy's location exactly, or confirm you're willing to relocate for the right role.",
            "es": "Si puedes, ajusta tu ubicacion preferida para que coincida exactamente con la de la vacante, o confirma que estas dispuesto a mudarte para el puesto adecuado.",
            "pt": "Se puder, ajuste a sua localizacao preferida para coincidir exatamente com a da vaga, ou confirme que esta disponivel para mudar de local pela vaga certa.",
        },
        "weakness": {
            "en": "Declare a preferred location, or mark yourself as willing to relocate/change country - recruiters otherwise cannot tell if location works for you.",
            "es": "Declara una ubicacion preferida, o marca que estas dispuesto a mudarte de ciudad o pais: de lo contrario los reclutadores no pueden saber si la ubicacion te funciona.",
            "pt": "Declare uma localizacao preferida, ou indique que esta disponivel para mudar de cidade/pais - caso contrario, os recrutadores nao conseguem saber se a localizacao lhe convem.",
        },
    },
    "recognition": {
        "strength": {
            "en": "No action needed - your recognition is verified, just keep the documentation on file in case it's requested.",
            "es": "No hace falta ninguna accion: tu reconocimiento esta verificado, solo conserva la documentacion por si te la solicitan.",
            "pt": "Nao e preciso nenhuma acao - o seu reconhecimento esta verificado, apenas guarde a documentacao caso seja solicitada.",
        },
        "developing": {
            "en": "Follow up with the competent authority to complete your recognition process, and upload proof once you receive it.",
            "es": "Haz seguimiento con la autoridad competente para completar tu proceso de reconocimiento, y sube el justificante en cuanto lo recibas.",
            "pt": "Faca o acompanhamento junto da autoridade competente para concluir o seu processo de reconhecimento, e carregue o comprovativo assim que o receber.",
        },
        "weakness": {
            "en": "Start the diploma/professional recognition process with the competent authority for your target country as soon as possible - this can block eligibility outright, so it should be a top priority.",
            "es": "Inicia cuanto antes el proceso de reconocimiento de titulo/profesion ante la autoridad competente de tu pais de destino: puede bloquear la elegibilidad, por lo que debe ser tu prioridad.",
            "pt": "Inicie o quanto antes o processo de reconhecimento de diploma/profissao junto da autoridade competente do seu pais de destino - isto pode bloquear a elegibilidade, por isso deve ser prioridade.",
        },
    },
    "education": {
        "strength": {
            "en": "No action needed - just keep your qualification and its recognition status up to date.",
            "es": "No hace falta ninguna accion: solo manten actualizada tu titulacion y su estado de reconocimiento.",
            "pt": "Nao e preciso nenhuma acao - apenas mantenha a sua qualificacao e o respetivo estado de reconhecimento atualizados.",
        },
        "developing": {
            "en": "If you have a higher qualification than what's on file, add it, or clarify how your field of study relates to the roles you're targeting.",
            "es": "Si tienes una titulacion superior a la registrada, anadela, o aclara como tu campo de estudio se relaciona con los puestos que buscas.",
            "pt": "Se tiver uma qualificacao superior a registada, adicione-a, ou esclareca como a sua area de estudo se relaciona com as vagas que procura.",
        },
        "weakness": {
            "en": "Add your highest completed qualification to your profile (level and field of study) - this is required for any general employability reading.",
            "es": "Anade a tu perfil tu titulacion mas alta completada (nivel y campo de estudio): es necesaria para cualquier lectura de empleabilidad general.",
            "pt": "Adicione ao seu perfil a sua qualificacao mais alta concluida (nivel e area de estudo) - e necessaria para qualquer leitura de empregabilidade geral.",
        },
    },
    "immigration_readiness": {
        "strength": {
            "en": "No action needed - keep your documentation ready in case it's requested by an employer or authority.",
            "es": "No hace falta ninguna accion: manten tu documentacion lista por si un empleador o autoridad la solicita.",
            "pt": "Nao e preciso nenhuma acao - mantenha a sua documentacao pronta caso seja solicitada por um empregador ou autoridade.",
        },
        "developing": {
            "en": "Follow up on your pending work authorization with the relevant national authority and update your status once it's resolved.",
            "es": "Haz seguimiento de tu autorizacion de trabajo pendiente ante la autoridad nacional correspondiente y actualiza tu estado en cuanto se resuelva.",
            "pt": "Faca o acompanhamento da sua autorizacao de trabalho pendente junto da autoridade nacional competente e atualize o seu estado assim que for resolvida.",
        },
        "weakness": {
            "en": "Contact the national immigration authority for your target country to clarify or start your work authorization process - this underlies almost everything else.",
            "es": "Contacta con la autoridad nacional de inmigracion de tu pais de destino para aclarar o iniciar tu proceso de autorizacion de trabajo: es la base de casi todo lo demas.",
            "pt": "Contacte a autoridade nacional de imigracao do seu pais de destino para esclarecer ou iniciar o seu processo de autorizacao de trabalho - isto e a base de quase tudo o resto.",
        },
    },
    "documentation_readiness": {
        "strength": {
            "en": "No action needed - just keep copies of your documents accessible for when they're requested.",
            "es": "No hace falta ninguna accion: solo manten copias de tus documentos accesibles para cuando te las soliciten.",
            "pt": "Nao e preciso nenhuma acao - apenas mantenha copias dos seus documentos acessiveis para quando forem solicitados.",
        },
        "developing": {
            "en": "Gather the remaining documents (e.g. apostille, certified translation, grade conversion) - each one you add raises this score.",
            "es": "Reune los documentos que faltan (p. ej. apostilla, traduccion jurada, conversion de notas): cada uno que anadas sube esta puntuacion.",
            "pt": "Reuna os documentos em falta (ex.: apostila, traducao certificada, conversao de notas) - cada um que adicionar aumenta esta pontuacao.",
        },
        "weakness": {
            "en": "Start gathering your diploma, academic transcript and an apostille/certified translation now - these can take weeks to obtain, so starting early avoids delays.",
            "es": "Empieza ya a reunir tu titulo, expediente academico y una apostilla/traduccion jurada: pueden tardar semanas en obtenerse, asi que empezar pronto evita retrasos.",
            "pt": "Comece ja a reunir o seu diploma, historico academico e uma apostila/traducao certificada - podem demorar semanas a obter, por isso comecar cedo evita atrasos.",
        },
    },
}

TOP_OPPORTUNITY_TEXT = {
    "en": "Your single biggest opportunity: improving \"{label}\" could take your {score_group} score from {current}/100 to about {potential}/100 (+{gain} points).",
    "es": "Tu mayor oportunidad: mejorar \"{label}\" podria llevar tu puntuacion de {score_group} de {current}/100 a unos {potential}/100 (+{gain} puntos).",
    "pt": "A sua maior oportunidade: melhorar \"{label}\" pode levar a sua pontuacao de {score_group} de {current}/100 para cerca de {potential}/100 (+{gain} pontos).",
}

SCORE_GROUP_LABELS = {
    "job_fit": {"en": "job match", "es": "compatibilidad con el puesto", "pt": "compatibilidade com a vaga"},
    "general_employability": {"en": "general employability", "es": "empleabilidad general", "pt": "empregabilidade geral"},
}