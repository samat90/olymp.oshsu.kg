/* Word lists and code snippets for the typing trainer. */
window.TYPING_WORDS = {
    ru: ('и в не на я быть он с что а по это она этот к но они мы как из у который то за свой весь год от так ' +
         'о для ты же все тот мочь вы человек такой его сказать только или ещё бы себя один как уже до время ' +
         'если сам когда другой вот говорить наш мой знать стать при чтобы дело жизнь кто первый очень два день ' +
         'её новый рука даже во со раз где там под можно ну какой после их работа без самый потом надо хотеть ' +
         'ли слово идти большой должен место иметь ничто то сейчас тут лицо каждый друг нет теперь ни глаз тоже ' +
         'тогда видеть вопрос через да здесь дом да потому сторона какой-то думать сделать страна жить чем мир ' +
         'об последний случай голова более делать что-то смотреть ребёнок просто конечно сила российский конец ' +
         'перед несколько вид система всегда работать между три деньги город вода земля дорога книга школа ' +
         'урок задача ответ число код строка файл папка данные сервер сайт программа алгоритм массив цикл ' +
         'условие функция переменная значение ошибка тест память время скорость клавиша палец буква текст ' +
         'студент учитель класс олимпиада решение балл место победа команда игра утро вечер ночь неделя месяц ' +
         'солнце небо гора река море лес поле дерево цветок кошка собака птица окно дверь стол стул лампа ' +
         'чай хлеб молоко яблоко сад друг мама папа брат сестра семья радость мечта путь свет тепло').split(' '),
    en: ('the be to of and a in that have it for not on with he as you do at this but his by from they we say ' +
         'her she or an will my one all would there their what so up out if about who get which go me when make ' +
         'can like time no just him know take people into year your good some could them see other than then ' +
         'now look only come its over think also back after use two how our work first well way even new want ' +
         'because any these give day most us is was are been has had were said did made find long down side ' +
         'code file line loop array value string number function class method object return true false null ' +
         'input output error test case data server client query index list map key sort search graph tree node ' +
         'edge path cost sum max min count result answer problem solution contest score team rank level speed ' +
         'water house world school book light hand place right small large great point home water night city ' +
         'tree river mountain green blue red black white happy quick brown fox jumps lazy dog morning evening').split(' '),
    ky: ('жана бул мен сен ал биз силер алар үй китеп мектеп окуучу мугалим суу нан жер асман күн ай жыл убакыт ' +
         'адам бала эне ата дос жакшы жаман чоң кичине жаңы эски кызыл ак кара көк сары жашыл бир эки үч төрт ' +
         'беш алты жети сегиз тогуз он жүз миң окуу жазуу иштөө баруу келүү көрүү билүү сүйлөө угуу ойноо тамак ' +
         'шаар айыл тоо көл дарыя токой гүл дарак мышык ит ат кой уй эшик терезе стол отургуч компьютер ' +
         'программа маселе жооп суроо сабак университет студент илим билим тил сөз сүйлөм кат ысым кыргыз эмгек ' +
         'бакыт сүйүү достук тынчтык кубаныч жылуу суук ысык кеч эрте бүгүн эртең кечээ азыр дайыма көп аз баары ' +
         'ким эмне кайда качан кантип ооба жок рахмат жол машина поезд учак дүкөн базар акча баа сатуу алуу берүү ' +
         'жасоо ачуу жабуу жуу уктоо ойлоо түшүнүү үйрөнүү окутуу эсептөө сан тамга сап бет дептер калем кагаз ' +
         'доска класс топ команда оюн жеңиш мелдеш олимпиада алгоритм маалымат тармак сайт файл код текст ' +
         'ачкыч клавиатура чычкан экран').split(' ')
};

/* Sentences for the last lessons: capitals, punctuation and digits together. */
window.TYPING_PHRASES = {
    ru: [
        'Тише едешь - дальше будешь.', 'Без труда не выловишь и рыбку из пруда.', 'Семь раз отмерь, один раз отрежь.',
        'Повторение - мать учения.', 'Не имей сто рублей, а имей сто друзей.', 'Делу время, потехе час.',
        'Ученье - свет, а неученье - тьма.', 'Кто ищет, тот всегда найдёт.', 'Одна голова хорошо, а две лучше.',
        'Ош - один из самых древних городов Средней Азии.', 'Иссык-Куль не замерзает даже зимой.',
        'Высота пика Ленина - 7134 метра.', 'В неделе 7 дней, а в году 12 месяцев.',
        'Олимпиада начнётся в 10:00, у вас будет 5 задач и 4 часа.', 'Программа прошла 25 тестов из 30.',
        'Сначала прочитай условие, потом пиши код!', 'Где ошибка: в цикле или в условии?',
        'Быстрая печать экономит время на олимпиаде.', 'Сегодня на уроке мы решали задачи на массивы.',
        'Компьютер выполняет миллиарды операций в секунду.', 'Не смотри на клавиатуру: пальцы сами найдут клавиши.',
        'Вчера было холодно, а сегодня светит солнце.', 'Мы поедем в горы в субботу, 15 мая.',
        'Чтобы печатать быстро, сначала печатай без ошибок.'
    ],
    en: [
        'Practice makes perfect.', 'The quick brown fox jumps over the lazy dog.', 'Slow and steady wins the race.',
        'Where there is a will, there is a way.', 'Actions speak louder than words.', 'Better late than never.',
        'Knowledge is power.', 'Two heads are better than one.', 'Every expert was once a beginner.',
        'Read the problem twice, then write the code.', 'My program passed 28 of 30 tests!',
        'The contest starts at 10:00 and lasts 5 hours.', 'Is the bug in the loop or in the condition?',
        'Osh is one of the oldest cities in Central Asia.', 'Lake Issyk-Kul does not freeze in winter.',
        'A computer can do billions of operations per second.', 'Do not look at the keys; let your fingers find them.',
        'Today we learned how to sort an array.', 'First type without mistakes, then type fast.',
        'There are 7 days in a week and 12 months in a year.', 'Good code is easy to read.'
    ],
    ky: [
        'Ынтымак бар жерде ырыс бар.', 'Жети өлчөп, бир кес.', 'Эл ичи - өнөр кенчи.',
        'Билимдүү миңди жыгат, билектүү бирди жыгат.', 'Окуу - билим булагы.', 'Китеп - билимдин булагы.',
        'Ош - Борбордук Азиядагы эң байыркы шаарлардын бири.', 'Ысык-Көл кышында да тоңбойт.',
        'Бир жумада 7 күн, бир жылда 12 ай бар.', 'Олимпиада саат 10:00до башталат.',
        'Программа 30 тесттин 25ин өттү!', 'Адегенде шартты оку, анан код жаз.',
        'Ката циклдеби же шарттабы?', 'Бүгүн сабакта массивдер боюнча маселе чыгардык.',
        'Компьютер секундасына миллиарддаган амал аткарат.', 'Клавиатурага карабай терүүнү үйрөн.',
        'Адегенде катасыз тер, анан тез тер.', 'Биз шембиде тоого барабыз.', 'Мен мектепте окуйм.'
    ]
};
