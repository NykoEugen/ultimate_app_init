from __future__ import annotations

from typing import List

from app.services.quest_content_builder import (
    QuestChoiceSpec,
    QuestNodeSpec,
    QuestSpec,
)


FALLEN_CROWN_ACT_I_ID = 2001
FALLEN_CROWN_ACT_II_ID = 2002
FALLEN_CROWN_ACT_III_ID = 2003
FALLEN_CROWN_ACT_IV_ID = 2004
FALLEN_CROWN_ACT_V_ID = 2005
FALLEN_CROWN_START_NODE_ID = "fallen_crown_a1_q1"


def fallen_crown_blueprint() -> List[QuestSpec]:
    """Declarative blueprint for the “Saga of the Fallen Crown” quest line."""

    act_i_nodes = [
        QuestNodeSpec(
            id=FALLEN_CROWN_START_NODE_ID,
            title="Пробудження серед попелу",
            body=(
                "Ти приходиш до тями серед згарища зруйнованого села, не пам’ятаючи власного імені. "
                "Механіка: RNG-перевірка на пошук спорядження (кидай d10 — 6+ означає, що ти знаходиш тимчасову зброю; "
                "1–5 — отримуєш травму і починаєш з `debuff` на наступний крок). "
                "Пам’ятай зафіксувати результат для подальших наслідків."
            ),
            is_start=True,
            choices=[
                QuestChoiceSpec(
                    id="fallen_crown_a1_q1_scavenge",
                    label="Кинути жереб: обшукати руїни",
                    reward_xp=40,
                    next_node_id="fallen_crown_a1_q2",
                ),
                QuestChoiceSpec(
                    id="fallen_crown_a1_q1_press_on",
                    label="Просто підвестися і рушити далі, прийнявши втрати",
                    reward_xp=30,
                    next_node_id="fallen_crown_a1_q2",
                ),
            ],
        ),
        QuestNodeSpec(
            id="fallen_crown_a1_q2",
            title="Дорога через спалений ліс",
            body=(
                "Обвуглені дерева тягнуться, наче сторожі. Серед уламків ти знаходиш пораненого вартового, "
                "який ледве тримається. RNG: кинь d6, результат 4+ — встигаєш зупинити кров і здобуваєш його довіру; "
                "нижче — вартовий помирає, але лишає тобі жетон."
            ),
            choices=[
                QuestChoiceSpec(
                    id="fallen_crown_a1_q2_aid_guard",
                    label="Спробувати врятувати вартового",
                    reward_xp=45,
                    next_node_id="fallen_crown_a1_q3",
                ),
                QuestChoiceSpec(
                    id="fallen_crown_a1_q2_take_token",
                    label="Прийняти жетон і продовжити шлях",
                    reward_xp=35,
                    next_node_id="fallen_crown_a1_q3",
                ),
            ],
        ),
        QuestNodeSpec(
            id="fallen_crown_a1_q3",
            title="Долина Розсипу",
            body=(
                "Перше поселення ледве тримається. Місцеві бояться ночі і просять допомоги. "
                "Механіка: короткі навчальні завдання — кидай d4 для дрібних RNG-подій (успіх дає бонусні ресурси)."
            ),
            choices=[
                QuestChoiceSpec(
                    id="fallen_crown_a1_q3_help_villagers",
                    label="Взяти кілька дрібних доручень",
                    reward_xp=45,
                    next_node_id="fallen_crown_a1_q4",
                ),
                QuestChoiceSpec(
                    id="fallen_crown_a1_q3_focus_self",
                    label="Зайнятися власними потребами, пообіцявши повернутися",
                    reward_xp=35,
                    next_node_id="fallen_crown_a1_q4",
                ),
            ],
        ),
        QuestNodeSpec(
            id="fallen_crown_a1_q4",
            title="Кам’яні знаки",
            body=(
                "На старих валунах викарбувані символи, що світяться вночі. "
                "Ти можеш розкрити їх значення або просто позначити локацію. "
                "Успішна перевірка знань (RNG d8, 5+) відкриває короткий лор та додає +1 до прихованого трекеру репутації Ордену."
            ),
            choices=[
                QuestChoiceSpec(
                    id="fallen_crown_a1_q4_study",
                    label="Дослідити знаки до світанку",
                    reward_xp=50,
                    next_node_id="fallen_crown_a1_q5",
                ),
                QuestChoiceSpec(
                    id="fallen_crown_a1_q4_mark",
                    label="Позначити камені і повернутися до села",
                    reward_xp=40,
                    next_node_id="fallen_crown_a1_q5",
                ),
            ],
        ),
        QuestNodeSpec(
            id="fallen_crown_a1_q5",
            title="Нічне вторгнення",
            body=(
                "У темряві на поселення нападають створіння з попелу. "
                "Це навчальна оборонна подія: 3 кроки RNG (d6). Крит-успіх 6 — рідкісна трофейна кістка, "
                "крит-провал 1 — тимчасова травма."
            ),
            choices=[
                QuestChoiceSpec(
                    id="fallen_crown_a1_q5_defend",
                    label="Встати на захист, координуючи жителів",
                    reward_xp=55,
                    next_node_id="fallen_crown_a1_q6",
                ),
            ],
        ),
        QuestNodeSpec(
            id="fallen_crown_a1_q6",
            title="Шахтний притулок",
            body=(
                "Вдосвіта ти вирушаєш до закинутої шахти, де могли сховатися вцілілі. "
                "Механіка: пошук виживших (d6). Успіх — знаходиш групу, провал — порожнеча, але натрапляєш на підказку."
            ),
            choices=[
                QuestChoiceSpec(
                    id="fallen_crown_a1_q6_search",
                    label="Обшукати тунелі та відголоси",
                    reward_xp=50,
                    next_node_id="fallen_crown_a1_q7",
                ),
                QuestChoiceSpec(
                    id="fallen_crown_a1_q6_signal",
                    label="Покликати та чекати відповіді, економлячи сили",
                    reward_xp=40,
                    next_node_id="fallen_crown_a1_q7",
                ),
            ],
        ),
        QuestNodeSpec(
            id="fallen_crown_a1_q7",
            title="Перший уламок печаті",
            body=(
                "У глибині шахти лежить уламок стародавньої печаті. "
                "Від нього відчувається резонанс, знайомий і тривожний. "
                "Візьми його — це постійний сюжетний предмет (1/5)."
            ),
            choices=[
                QuestChoiceSpec(
                    id="fallen_crown_a1_q7_claim",
                    label="Підняти уламок і заховати його",
                    reward_xp=55,
                    next_node_id="fallen_crown_a1_q8",
                ),
            ],
        ),
        QuestNodeSpec(
            id="fallen_crown_a1_q8",
            title="Сірі Провідники",
            body=(
                "Таємнича група мандрівників у сірих плащах стежить за тобою. "
                "Вони пропонують допомогу, але вимагають клятву мовчання. "
                "Репутаційний вибір: прийми їх патронаж (фракція Провідників) або відмовся."
            ),
            choices=[
                QuestChoiceSpec(
                    id="fallen_crown_a1_q8_accept",
                    label="Прийняти клятву мовчання",
                    reward_xp=60,
                    next_node_id="fallen_crown_a1_q9",
                ),
                QuestChoiceSpec(
                    id="fallen_crown_a1_q8_decline",
                    label="Відмовитися і йти власним шляхом",
                    reward_xp=50,
                    next_node_id="fallen_crown_a1_q9",
                ),
            ],
        ),
        QuestNodeSpec(
            id="fallen_crown_a1_q9",
            title="Ритуал очищення",
            body=(
                "Провідники проводять ритуал біля озера попелу. "
                "Ти можеш пройти очищення (отримати `buff` на RNG) або втекти, боячись втратити волю. "
                "Рішення впливає на майбутні взаємини з Провідниками."
            ),
            choices=[
                QuestChoiceSpec(
                    id="fallen_crown_a1_q9_ritual",
                    label="Стати в коло і прийняти очищення",
                    reward_xp=60,
                    next_node_id="fallen_crown_a1_q10",
                ),
                QuestChoiceSpec(
                    id="fallen_crown_a1_q9_run",
                    label="Втекти, поки піснеспіви не скували волю",
                    reward_xp=45,
                    next_node_id="fallen_crown_a1_q10",
                ),
            ],
        ),
        QuestNodeSpec(
            id="fallen_crown_a1_q10",
            title="Бачення Згаслого Трону",
            body=(
                "У снах ти бачиш трон, занурений у тінь, і чуєш голос короля, який кличе тебе на північ. "
                "Фінал Акта I: зафіксуй отримані `buff/debuff`, розкрий журнал прогресу."
            ),
            is_final=True,
            choices=[
                QuestChoiceSpec(
                    id="fallen_crown_a1_q10_sworn",
                    label="Поклястися відшукати голос",
                    reward_xp=70,
                    next_node_id="fallen_crown_a2_q11",
                ),
            ],
        ),
    ]

    act_ii_nodes = [
        QuestNodeSpec(
            id="fallen_crown_a2_q11",
            title="Сліди Ордену",
            body=(
                "Ти дізнаєшся, що колись був частиною Ордену Вартових Печаті. "
                "Пошук архівів у руїнах дає змогу згадати фрагменти. "
                "RNG: перевірка розвідки (d8) визначає, скільки документів вціліло."
            ),
            is_start=True,
            choices=[
                QuestChoiceSpec(
                    id="fallen_crown_a2_q11_search",
                    label="Переглянути архіви до останньої сторінки",
                    reward_xp=65,
                    next_node_id="fallen_crown_a2_q12",
                ),
                QuestChoiceSpec(
                    id="fallen_crown_a2_q11_move_on",
                    label="Забрати лише ключові записи та йти далі",
                    reward_xp=55,
                    next_node_id="fallen_crown_a2_q12",
                ),
            ],
        ),
        QuestNodeSpec(
            id="fallen_crown_a2_q12",
            title="Вибір фракції",
            body=(
                "Мисливці хочуть знищити чудовиськ, алхіміки — вивчати їх. "
                "Вибір фракції впливає на доступних NPC і подальші бонуси. "
                "Познач у своєму журналі: `reputation.hunters` чи `reputation.alchemists`."
            ),
            choices=[
                QuestChoiceSpec(
                    id="fallen_crown_a2_q12_hunters",
                    label="Приєднатися до Мисливців",
                    reward_xp=70,
                    next_node_id="fallen_crown_a2_q13",
                ),
                QuestChoiceSpec(
                    id="fallen_crown_a2_q12_alchemists",
                    label="Стати поруч із Алхіміками",
                    reward_xp=70,
                    next_node_id="fallen_crown_a2_q13",
                ),
            ],
        ),
        QuestNodeSpec(
            id="fallen_crown_a2_q13",
            title="Зниклі мандрівники",
            body=(
                "У передмісті пропали караванники. "
                "Розслідування відкриває прихований тунель. "
                "Моральний вибір: рятувати заручників або зосередитися на доказах змови."
            ),
            choices=[
                QuestChoiceSpec(
                    id="fallen_crown_a2_q13_rescue",
                    label="Визволити заручників негайно",
                    reward_xp=65,
                    next_node_id="fallen_crown_a2_q14",
                ),
                QuestChoiceSpec(
                    id="fallen_crown_a2_q13_investigate",
                    label="Спростувати сліди і зібрати докази",
                    reward_xp=60,
                    next_node_id="fallen_crown_a2_q14",
                ),
            ],
        ),
        QuestNodeSpec(
            id="fallen_crown_a2_q14",
            title="Дівчина зі згадками",
            body=(
                "На площі тебе зупиняє дівчина, яка впізнає твоє обличчя. "
                "Вона знає тебе як лицаря Ордену. "
                "Запиши в щоденнику її ім’я — Елара — вона повертатиметься в ключових сценах."
            ),
            choices=[
                QuestChoiceSpec(
                    id="fallen_crown_a2_q14_listen",
                    label="Вислухати Елару до кінця",
                    reward_xp=60,
                    next_node_id="fallen_crown_a2_q15",
                ),
                QuestChoiceSpec(
                    id="fallen_crown_a2_q14_deny",
                    label="Заперечити і відштовхнути минуле",
                    reward_xp=55,
                    next_node_id="fallen_crown_a2_q15",
                ),
            ],
        ),
        QuestNodeSpec(
            id="fallen_crown_a2_q15",
            title="Втеча від Інквізиторів",
            body=(
                "Твою присутність помітили Інквізитори. "
                "Послідовність дій: кидки на спритність (серія d6, три кроки). "
                "Крит-успіх = алмазний жетон Алхіміків, крит-провал = втрата ресурсу."
            ),
            choices=[
                QuestChoiceSpec(
                    id="fallen_crown_a2_q15_escape",
                    label="Улаштувати хаос і прорватися",
                    reward_xp=70,
                    next_node_id="fallen_crown_a2_q16",
                ),
                QuestChoiceSpec(
                    id="fallen_crown_a2_q15_hide",
                    label="Залягти в тіні й перечекати",
                    reward_xp=60,
                    next_node_id="fallen_crown_a2_q16",
                ),
            ],
        ),
        QuestNodeSpec(
            id="fallen_crown_a2_q16",
            title="Друга частина печаті",
            body=(
                "Під храмом ти знаходиш другу частину печаті. "
                "Вона реагує на першу й майже спаюється. "
                "Занотуй: тепер у тебе 2/5 уламків."
            ),
            choices=[
                QuestChoiceSpec(
                    id="fallen_crown_a2_q16_take",
                    label="Взяти уламок і відчути його вагу",
                    reward_xp=75,
                    next_node_id="fallen_crown_a2_q17",
                ),
            ],
        ),
        QuestNodeSpec(
            id="fallen_crown_a2_q17",
            title="Оборона міста",
            body=(
                "Демони прориваються в місто. "
                "Ланцюг RNG «Оборона» — п’ять кроків, кожен впливає на мораль міста. "
                "Занотуй лічильник `city_morale`."
            ),
            choices=[
                QuestChoiceSpec(
                    id="fallen_crown_a2_q17_command",
                    label="Очолити стіну і координувати стрільців",
                    reward_xp=75,
                    next_node_id="fallen_crown_a2_q18",
                ),
                QuestChoiceSpec(
                    id="fallen_crown_a2_q17_strike",
                    label="Вирушити в контратаку",
                    reward_xp=70,
                    next_node_id="fallen_crown_a2_q18",
                ),
            ],
        ),
        QuestNodeSpec(
            id="fallen_crown_a2_q18",
            title="Тінь прокляття",
            body=(
                "Ти дізнаєшся, що саме твій минулий вчинок запустив прокляття. "
                "Моральна дилема: прийняти провину чи перекласти на Орден."
            ),
            choices=[
                QuestChoiceSpec(
                    id="fallen_crown_a2_q18_accept",
                    label="Визнати провину і шукати спокуту",
                    reward_xp=80,
                    next_node_id="fallen_crown_a2_q19",
                ),
                QuestChoiceSpec(
                    id="fallen_crown_a2_q18_deflect",
                    label="Звинуватити Орден і їх накази",
                    reward_xp=70,
                    next_node_id="fallen_crown_a2_q19",
                ),
            ],
        ),
        QuestNodeSpec(
            id="fallen_crown_a2_q19",
            title="Сумнів у пам’яті",
            body=(
                "Ти ставиш під сумнів усе: чи справді пам’ять стерта, чи ти сам закрив правду. "
                "Механіка: перевірка волі (d10). Низький результат — `debuff` на моральні вибори."
            ),
            choices=[
                QuestChoiceSpec(
                    id="fallen_crown_a2_q19_reflect",
                    label="Зануритися в медитацію",
                    reward_xp=70,
                    next_node_id="fallen_crown_a2_q20",
                ),
                QuestChoiceSpec(
                    id="fallen_crown_a2_q19_repress",
                    label="Відкинути сумніви і рухатися далі",
                    reward_xp=65,
                    next_node_id="fallen_crown_a2_q20",
                ),
            ],
        ),
        QuestNodeSpec(
            id="fallen_crown_a2_q20",
            title="Перехрестя істини",
            body=(
                "Фінал Акта II. Ти вирішуєш: знищити докази, щоб сховати темні вчинки Ордену, "
                "або продовжити пошук правди, ризикуючи репутацією. "
                "Результат додає маркери `truth_seeker` чи `veil_keeper`."
            ),
            is_final=True,
            choices=[
                QuestChoiceSpec(
                    id="fallen_crown_a2_q20_destroy",
                    label="Спалити документи і захистити Орден",
                    reward_xp=85,
                    next_node_id="fallen_crown_a3_q21",
                ),
                QuestChoiceSpec(
                    id="fallen_crown_a2_q20_seek",
                    label="Зберегти всі докази і рушити до істини",
                    reward_xp=90,
                    next_node_id="fallen_crown_a3_q21",
                ),
            ],
        ),
    ]

    act_iii_nodes = [
        QuestNodeSpec(
            id="fallen_crown_a3_q21",
            title="Союзники серед розбійників",
            body=(
                "Щоб підготуватися до війни фракцій, ти шукаєш союзників серед розбійників Розірваної Дороги. "
                "Потрібно переконати їх, використовуючи `reputation` з попередніх актів."
            ),
            is_start=True,
            choices=[
                QuestChoiceSpec(
                    id="fallen_crown_a3_q21_bargain",
                    label="Укласти криваву угоду",
                    reward_xp=95,
                    next_node_id="fallen_crown_a3_q22",
                ),
                QuestChoiceSpec(
                    id="fallen_crown_a3_q21_intimidate",
                    label="Залякати авторитетом Ордену",
                    reward_xp=85,
                    next_node_id="fallen_crown_a3_q22",
                ),
            ],
        ),
        QuestNodeSpec(
            id="fallen_crown_a3_q22",
            title="Відновлення кузні",
            body=(
                "Стара кузня Ордену ще може працювати. "
                "Механіка: мульти-step завдання (3 кроки) — зібрати ресурси, полагодити механику, "
                "розпалити жар. Нагорода: доступ до крафту реліквій."
            ),
            choices=[
                QuestChoiceSpec(
                    id="fallen_crown_a3_q22_repair",
                    label="Організувати ремонт",
                    reward_xp=90,
                    next_node_id="fallen_crown_a3_q23",
                ),
                QuestChoiceSpec(
                    id="fallen_crown_a3_q22_delegate",
                    label="Доручити роботу союзникам, контролюючи процес",
                    reward_xp=85,
                    next_node_id="fallen_crown_a3_q23",
                ),
            ],
        ),
        QuestNodeSpec(
            id="fallen_crown_a3_q23",
            title="Підземні розкопки",
            body=(
                "У катакомбах під кузнею заховано артефакти. "
                "Ланцюг на 5 кроків із випадковими знахідками: крит-успіх = рідкісна зброя, "
                "крит-провал = травма, що впливає на майбутні квести."
            ),
            choices=[
                QuestChoiceSpec(
                    id="fallen_crown_a3_q23_descend",
                    label="Спуститися особисто",
                    reward_xp=95,
                    next_node_id="fallen_crown_a3_q24",
                ),
                QuestChoiceSpec(
                    id="fallen_crown_a3_q23_send_team",
                    label="Відправити загін і координувати зверху",
                    reward_xp=85,
                    next_node_id="fallen_crown_a3_q24",
                ),
            ],
        ),
        QuestNodeSpec(
            id="fallen_crown_a3_q24",
            title="Третя частина печаті",
            body=(
                "В глибині знаходиться третя частина печаті. "
                "Вона відкриває фрагмент пророцтва: справжній король ще живий, але втікає від темряви."
            ),
            choices=[
                QuestChoiceSpec(
                    id="fallen_crown_a3_q24_unite",
                    label="З’єднати уламки і відчути імпульс",
                    reward_xp=100,
                    next_node_id="fallen_crown_a3_q25",
                ),
            ],
        ),
        QuestNodeSpec(
            id="fallen_crown_a3_q25",
            title="Проклятий Провісник",
            body=(
                "Фанатик називає тебе Проклятим Провісником. "
                "Він пропонує культові обітниці, щоб приборкати печатку. "
                "Рішення впливає на майбутні `buff/debuff` під час битв."
            ),
            choices=[
                QuestChoiceSpec(
                    id="fallen_crown_a3_q25_accept",
                    label="Прийняти обітницю (здобути темний дар)",
                    reward_xp=90,
                    next_node_id="fallen_crown_a3_q26",
                ),
                QuestChoiceSpec(
                    id="fallen_crown_a3_q25_reject",
                    label="Відкинути фанатика",
                    reward_xp=90,
                    next_node_id="fallen_crown_a3_q26",
                ),
            ],
        ),
        QuestNodeSpec(
            id="fallen_crown_a3_q26",
            title="Напад на форпост",
            body=(
                "Військо інквізиції тримає форпост. "
                "Штурм — п’ять RNG-кроків із крит-подіями. Зафіксуй втрати серед союзників."
            ),
            choices=[
                QuestChoiceSpec(
                    id="fallen_crown_a3_q26_assault",
                    label="Очолити лобову атаку",
                    reward_xp=100,
                    next_node_id="fallen_crown_a3_q27",
                ),
                QuestChoiceSpec(
                    id="fallen_crown_a3_q26_sabotage",
                    label="Організувати диверсію перед штурмом",
                    reward_xp=95,
                    next_node_id="fallen_crown_a3_q27",
                ),
            ],
        ),
        QuestNodeSpec(
            id="fallen_crown_a3_q27",
            title="Тяжкий вибір",
            body=(
                "Під час штурму ти бачиш шанс зрадити союзників і захопити ресурси. "
                "Або врятувати їх, ризикуючи планом. Цей вибір формує майбутні зради."
            ),
            choices=[
                QuestChoiceSpec(
                    id="fallen_crown_a3_q27_betray",
                    label="Зрадити і забрати здобич",
                    reward_xp=105,
                    next_node_id="fallen_crown_a3_q28",
                ),
                QuestChoiceSpec(
                    id="fallen_crown_a3_q27_save",
                    label="Врятувати союзників, жертвуючи вигодою",
                    reward_xp=95,
                    next_node_id="fallen_crown_a3_q28",
                ),
            ],
        ),
        QuestNodeSpec(
            id="fallen_crown_a3_q28",
            title="Зрада в лавах",
            body=(
                "Один зі спільників зникає вночі, викравши частину припасів. "
                "Перевір репутацію: високі значення — шанс повернути, низькі — посилена темрява."
            ),
            choices=[
                QuestChoiceSpec(
                    id="fallen_crown_a3_q28_pursue",
                    label="Переслідувати зрадника",
                    reward_xp=95,
                    next_node_id="fallen_crown_a3_q29",
                ),
                QuestChoiceSpec(
                    id="fallen_crown_a3_q28_let_go",
                    label="Дозволити йому втекти і зосередитися на меті",
                    reward_xp=90,
                    next_node_id="fallen_crown_a3_q29",
                ),
            ],
        ),
        QuestNodeSpec(
            id="fallen_crown_a3_q29",
            title="Загибель наставника",
            body=(
                "Твій наставник падає, рятуючи тебе. "
                "Це змінює ваші мотивації і додає маркер `mentor_fallen`. "
                "Запиши його останні слова: «Король ще дихає…»."
            ),
            choices=[
                QuestChoiceSpec(
                    id="fallen_crown_a3_q29_vow",
                    label="Поклястися помститися",
                    reward_xp=105,
                    next_node_id="fallen_crown_a3_q30",
                ),
            ],
        ),
        QuestNodeSpec(
            id="fallen_crown_a3_q30",
            title="Справжній король",
            body=(
                "Фінал Акта III. Ти дізнаєшся, що король живий, але ховається, бо заражений темрявою. "
                "Визнач свій наступний крок: знайти його чи викрити змову."
            ),
            is_final=True,
            choices=[
                QuestChoiceSpec(
                    id="fallen_crown_a3_q30_seek",
                    label="Рушити на пошуки короля",
                    reward_xp=110,
                    next_node_id="fallen_crown_a4_q31",
                ),
            ],
        ),
    ]

    act_iv_nodes = [
        QuestNodeSpec(
            id="fallen_crown_a4_q31",
            title="Тінь у столиці",
            body=(
                "Ти входиш до столиці, видаючи себе за мандрівного купця. "
                "Механіка: таймер — 10 хв реального часу на збір інформації. "
                "Високий результат зменшує підозру охорони."
            ),
            is_start=True,
            choices=[
                QuestChoiceSpec(
                    id="fallen_crown_a4_q31_trade",
                    label="Вести торгівлю і збирати чутки",
                    reward_xp=120,
                    next_node_id="fallen_crown_a4_q32",
                ),
                QuestChoiceSpec(
                    id="fallen_crown_a4_q31_smuggle",
                    label="Використати незаконні канали",
                    reward_xp=110,
                    next_node_id="fallen_crown_a4_q32",
                ),
            ],
        ),
        QuestNodeSpec(
            id="fallen_crown_a4_q32",
            title="Шпигуни палацу",
            body=(
                "У палаці діють шпигуни різних фракцій. "
                "Знайди їх і обери, з ким співпрацювати. "
                "Рішення впливає на доступ до майбутніх завдань."
            ),
            choices=[
                QuestChoiceSpec(
                    id="fallen_crown_a4_q32_expose",
                    label="Викрити шпигунів і використати їхню мережу",
                    reward_xp=120,
                    next_node_id="fallen_crown_a4_q33",
                ),
                QuestChoiceSpec(
                    id="fallen_crown_a4_q32_bribe",
                    label="Підкупити найкорисніших",
                    reward_xp=115,
                    next_node_id="fallen_crown_a4_q33",
                ),
            ],
        ),
        QuestNodeSpec(
            id="fallen_crown_a4_q33",
            title="Напівбожевільний король",
            body=(
                "Ти зустрічаєш короля: він заражений темрявою і говорить уривками пророцтв. "
                "Запиши ключові фрази — вони стануть підказками в Акті V."
            ),
            choices=[
                QuestChoiceSpec(
                    id="fallen_crown_a4_q33_plead",
                    label="Попросити його довіритися",
                    reward_xp=125,
                    next_node_id="fallen_crown_a4_q34",
                ),
                QuestChoiceSpec(
                    id="fallen_crown_a4_q33_confront",
                    label="Змусити його говорити силою",
                    reward_xp=115,
                    next_node_id="fallen_crown_a4_q34",
                ),
            ],
        ),
        QuestNodeSpec(
            id="fallen_crown_a4_q34",
            title="Четвертий уламок",
            body=(
                "У підземеллі палацу ти знаходиш четвертий шматок печаті. "
                "Його охороняє фантом твого минулого. "
                "Бій на таймері: витрать 5 хв на опис дій та кидки."
            ),
            choices=[
                QuestChoiceSpec(
                    id="fallen_crown_a4_q34_claim",
                    label="Подолати фантом і забрати уламок",
                    reward_xp=130,
                    next_node_id="fallen_crown_a4_q35",
                ),
            ],
        ),
        QuestNodeSpec(
            id="fallen_crown_a4_q35",
            title="Стародавнє зло",
            body=(
                "Пробуджується істота, пов’язана з печаттю. "
                "Вона отруює місто мареннями. "
                "Механіка: таймерні місії (5 хв) для нейтралізації вузлів темряви."
            ),
            choices=[
                QuestChoiceSpec(
                    id="fallen_crown_a4_q35_suppress",
                    label="Спрямувати Провідників на придушення тьми",
                    reward_xp=125,
                    next_node_id="fallen_crown_a4_q36",
                ),
                QuestChoiceSpec(
                    id="fallen_crown_a4_q35_binding",
                    label="Використати алхімічні печаті",
                    reward_xp=125,
                    next_node_id="fallen_crown_a4_q36",
                ),
            ],
        ),
        QuestNodeSpec(
            id="fallen_crown_a4_q36",
            title="Місто чи печатка",
            body=(
                "Ти маєш вибір: врятувати місто від руйнування або забезпечити печатку. "
                "Вибір вплине на фінал і доступні союзники в Акті V."
            ),
            choices=[
                QuestChoiceSpec(
                    id="fallen_crown_a4_q36_city",
                    label="Врятувати місто, жертвуючи частиною сили печаті",
                    reward_xp=135,
                    next_node_id="fallen_crown_a4_q37",
                ),
                QuestChoiceSpec(
                    id="fallen_crown_a4_q36_seal",
                    label="Зберегти печатку, дозволивши місту впасти",
                    reward_xp=140,
                    next_node_id="fallen_crown_a4_q37",
                ),
            ],
        ),
        QuestNodeSpec(
            id="fallen_crown_a4_q37",
            title="Втеча катакомбами",
            body=(
                "Катакомби руйнуються. "
                "Ти маєш серію таймерних перевірок, аби вивести свій загін. "
                "Провал додає `debuff` на старт Акта V."
            ),
            choices=[
                QuestChoiceSpec(
                    id="fallen_crown_a4_q37_lead",
                    label="Прокласти шлях особисто",
                    reward_xp=130,
                    next_node_id="fallen_crown_a4_q38",
                ),
                QuestChoiceSpec(
                    id="fallen_crown_a4_q37_order",
                    label="Наказати іншим вести людей, а самостійно стримувати обвал",
                    reward_xp=125,
                    next_node_id="fallen_crown_a4_q38",
                ),
            ],
        ),
        QuestNodeSpec(
            id="fallen_crown_a4_q38",
            title="Дух наставника",
            body=(
                "У тіні катакомб ти зустрічаєш дух наставника. "
                "Він вказує на приховану правду та просить зробити вибір серця."
            ),
            choices=[
                QuestChoiceSpec(
                    id="fallen_crown_a4_q38_listen",
                    label="Прийняти пораду духа",
                    reward_xp=130,
                    next_node_id="fallen_crown_a4_q39",
                ),
                QuestChoiceSpec(
                    id="fallen_crown_a4_q38_refuse",
                    label="Ігнорувати тінь минулого",
                    reward_xp=120,
                    next_node_id="fallen_crown_a4_q39",
                ),
            ],
        ),
        QuestNodeSpec(
            id="fallen_crown_a4_q39",
            title="Втрати серед союзників",
            body=(
                "Один з головних союзників гине — залежно від попередніх виборів це може бути Провідник, "
                "Мисливець або Алхімік. Відзнач, кого ти втратив, це змінює реакції у фіналі."
            ),
            choices=[
                QuestChoiceSpec(
                    id="fallen_crown_a4_q39_mourn",
                    label="Віддати шану і продовжити місію",
                    reward_xp=140,
                    next_node_id="fallen_crown_a4_q40",
                ),
            ],
        ),
        QuestNodeSpec(
            id="fallen_crown_a4_q40",
            title="Світ у мороці",
            body=(
                "Фінал Акта IV. Темрява огортає королівство, але ти знаходиш останню підказку про місце п’ятої печаті. "
                "Запиши координати храму у серці бурі."
            ),
            is_final=True,
            choices=[
                QuestChoiceSpec(
                    id="fallen_crown_a4_q40_forward",
                    label="Готуватися до останнього походу",
                    reward_xp=145,
                    next_node_id="fallen_crown_a5_q41",
                ),
            ],
        ),
    ]

    act_v_nodes = [
        QuestNodeSpec(
            id="fallen_crown_a5_q41",
            title="Храм бурі",
            body=(
                "Останній шлях веде крізь бурю до храму. "
                "Механіка: 7–10 кроків RNG із `buff/debuff`, здобутими раніше. "
                "Ресурси та союзники визначають складність."
            ),
            is_start=True,
            choices=[
                QuestChoiceSpec(
                    id="fallen_crown_a5_q41_enter",
                    label="Увійти до храму, покладаючись на союзників",
                    reward_xp=160,
                    next_node_id="fallen_crown_a5_q42",
                ),
                QuestChoiceSpec(
                    id="fallen_crown_a5_q41_solo",
                    label="Увійти на самоті, приймаючи ризики",
                    reward_xp=155,
                    next_node_id="fallen_crown_a5_q42",
                ),
            ],
        ),
        QuestNodeSpec(
            id="fallen_crown_a5_q42",
            title="Випробування пам’яті",
            body=(
                "У храмі ти проходиш випробування пам’яті. "
                "Кожен крок — RNG-тест (d10). Успіх відновлює спогади, провал додає сумнівів."
            ),
            choices=[
                QuestChoiceSpec(
                    id="fallen_crown_a5_q42_face",
                    label="Зустріти спогади очима",
                    reward_xp=160,
                    next_node_id="fallen_crown_a5_q43",
                ),
                QuestChoiceSpec(
                    id="fallen_crown_a5_q42_resist",
                    label="Опиратися голосам минулого",
                    reward_xp=150,
                    next_node_id="fallen_crown_a5_q43",
                ),
            ],
        ),
        QuestNodeSpec(
            id="fallen_crown_a5_q43",
            title="Істинне ім’я",
            body=(
                "Ти згадуєш своє справжнє ім’я та титул у Ордені. "
                "Від цього залежить, як реагують союзники і тіні короля."
            ),
            choices=[
                QuestChoiceSpec(
                    id="fallen_crown_a5_q43_claim",
                    label="Прийняти ім’я і промовити його вголос",
                    reward_xp=165,
                    next_node_id="fallen_crown_a5_q44",
                ),
                QuestChoiceSpec(
                    id="fallen_crown_a5_q43_hide",
                    label="Приховати ім’я навіть від себе",
                    reward_xp=155,
                    next_node_id="fallen_crown_a5_q44",
                ),
            ],
        ),
        QuestNodeSpec(
            id="fallen_crown_a5_q44",
            title="Битва з тінню",
            body=(
                "Фінальна битва з тінню короля. "
                "Залежно від `city_morale`, `truth_seeker` та фракцій ти отримуєш різні бонуси. "
                "Бій триває 10 хв реального часу з описом кожної фази."
            ),
            choices=[
                QuestChoiceSpec(
                    id="fallen_crown_a5_q44_light",
                    label="Спрямувати світло печаті",
                    reward_xp=170,
                    next_node_id="fallen_crown_a5_q45",
                ),
                QuestChoiceSpec(
                    id="fallen_crown_a5_q44_shadow",
                    label="Використати темні дари фанатика",
                    reward_xp=170,
                    next_node_id="fallen_crown_a5_q45",
                ),
            ],
        ),
        QuestNodeSpec(
            id="fallen_crown_a5_q45",
            title="Жертва",
            body=(
                "Битва вимагає жертви: або ти, або твій найближчий супутник. "
                "Рішення визначає, хто переживе фінал."
            ),
            choices=[
                QuestChoiceSpec(
                    id="fallen_crown_a5_q45_self",
                    label="Пожертвувати собою",
                    reward_xp=175,
                    next_node_id="fallen_crown_a5_q46",
                ),
                QuestChoiceSpec(
                    id="fallen_crown_a5_q45_companion",
                    label="Дозволити супутнику впасти",
                    reward_xp=165,
                    next_node_id="fallen_crown_a5_q46",
                ),
            ],
        ),
        QuestNodeSpec(
            id="fallen_crown_a5_q46",
            title="Розрив печаті",
            body=(
                "Чотири уламки з’єднуються з п’ятим, і ти вирішуєш долю прокляття. "
                "Результат залежить від обраних фракцій та маркерів правди."
            ),
            choices=[
                QuestChoiceSpec(
                    id="fallen_crown_a5_q46_break",
                    label="Зламати печатку і звільнити світ",
                    reward_xp=180,
                    next_node_id="fallen_crown_a5_q47",
                ),
                QuestChoiceSpec(
                    id="fallen_crown_a5_q46_bind",
                    label="Посилити печатку і стати її володарем",
                    reward_xp=180,
                    next_node_id="fallen_crown_a5_q47",
                ),
            ],
        ),
        QuestNodeSpec(
            id="fallen_crown_a5_q47",
            title="Очищення чи знищення",
            body=(
                "Наслідки рішення: світ очищається або занурюється в темряву. "
                "Занотуй, як змінюється ландшафт і реакція фракцій."
            ),
            choices=[
                QuestChoiceSpec(
                    id="fallen_crown_a5_q47_restore",
                    label="Спрямувати силу на зцілення земель",
                    reward_xp=185,
                    next_node_id="fallen_crown_a5_q48",
                ),
                QuestChoiceSpec(
                    id="fallen_crown_a5_q47_dominate",
                    label="Придушити все довкола власною волею",
                    reward_xp=185,
                    next_node_id="fallen_crown_a5_q48",
                ),
            ],
        ),
        QuestNodeSpec(
            id="fallen_crown_a5_q48",
            title="Післятінь",
            body=(
                "Епілог: обери майбутнє світу. "
                "Визнач, які фракції вижили, які міста відродяться, хто відгукнеться на твоє ім’я."
            ),
            choices=[
                QuestChoiceSpec(
                    id="fallen_crown_a5_q48_rebuild",
                    label="Почати відродження королівства",
                    reward_xp=190,
                    next_node_id="fallen_crown_a5_q49",
                ),
                QuestChoiceSpec(
                    id="fallen_crown_a5_q48_rule",
                    label="Створити новий порядок під власним прапором",
                    reward_xp=190,
                    next_node_id="fallen_crown_a5_q49",
                ),
            ],
        ),
        QuestNodeSpec(
            id="fallen_crown_a5_q49",
            title="Пробудження світанку",
            body=(
                "Світ прокидається після бурі. "
                "Оціни наслідки: які землі очищено, які ще потребують уваги, хто з союзників живий."
            ),
            choices=[
                QuestChoiceSpec(
                    id="fallen_crown_a5_q49_reflect",
                    label="Озирнутися на шлях і прийняти його",
                    reward_xp=195,
                    next_node_id="fallen_crown_a5_q50",
                ),
            ],
        ),
        QuestNodeSpec(
            id="fallen_crown_a5_q50",
            title="Титул героя",
            body=(
                "Фінал Акта V і всієї саги. "
                "Визнач титул героя залежно від твоїх виборів: Рятівник, Узурпатор або Забутий. "
                "Цей крок фіксує кінцівку."
            ),
            is_final=True,
            choices=[
                QuestChoiceSpec(
                    id="fallen_crown_a5_q50_redeemer",
                    label="Прийняти титул Рятівника",
                    reward_xp=200,
                ),
                QuestChoiceSpec(
                    id="fallen_crown_a5_q50_usurper",
                    label="Проголосити себе Узурпатором",
                    reward_xp=200,
                ),
                QuestChoiceSpec(
                    id="fallen_crown_a5_q50_forgotten",
                    label="Зникнути, залишившись Забутим",
                    reward_xp=200,
                ),
            ],
        ),
    ]

    return [
        QuestSpec(
            id=FALLEN_CROWN_ACT_I_ID,
            title="Сага про Згасле Королівство — Акт I: Попіл і Тиша",
            description="Початок подорожі героя без пам’яті та перший уламок печаті.",
            nodes=act_i_nodes,
        ),
        QuestSpec(
            id=FALLEN_CROWN_ACT_II_ID,
            title="Сага про Згасле Королівство — Акт II: Примари минулого",
            description="Герой відкриває правду про Орден та робить моральні вибори.",
            nodes=act_ii_nodes,
        ),
        QuestSpec(
            id=FALLEN_CROWN_ACT_III_ID,
            title="Сага про Згасле Королівство — Акт III: Кров і Прах",
            description="Війна фракцій, зради та пошук справжнього короля.",
            nodes=act_iii_nodes,
        ),
        QuestSpec(
            id=FALLEN_CROWN_ACT_IV_ID,
            title="Сага про Згасле Королівство — Акт IV: Тінь на троні",
            description="Політичні інтриги у столиці та четвертий уламок печаті.",
            nodes=act_iv_nodes,
        ),
        QuestSpec(
            id=FALLEN_CROWN_ACT_V_ID,
            title="Сага про Згасле Королівство — Акт V: Відродження",
            description="Фінальне зіткнення, останній уламок і вибір майбутнього світу.",
            nodes=act_v_nodes,
        ),
    ]


__all__ = [
    "FALLEN_CROWN_ACT_I_ID",
    "FALLEN_CROWN_ACT_II_ID",
    "FALLEN_CROWN_ACT_III_ID",
    "FALLEN_CROWN_ACT_IV_ID",
    "FALLEN_CROWN_ACT_V_ID",
    "FALLEN_CROWN_START_NODE_ID",
    "fallen_crown_blueprint",
]
