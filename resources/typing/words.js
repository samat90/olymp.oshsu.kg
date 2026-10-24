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

window.TYPING_CODE = [
    {lang: 'C++', text: '#include <iostream>\nusing namespace std;\n\nint main() {\n    int a, b;\n    cin >> a >> b;\n    cout << a + b << endl;\n    return 0;\n}'},
    {lang: 'C++', text: 'long long gcd(long long a, long long b) {\n    while (b != 0) {\n        long long t = a % b;\n        a = b;\n        b = t;\n    }\n    return a;\n}'},
    {lang: 'C++', text: 'vector<int> a(n);\nfor (int i = 0; i < n; i++) {\n    cin >> a[i];\n}\nsort(a.begin(), a.end());\ncout << a[n - 1] << "\\n";'},
    {lang: 'C++', text: 'int lo = 0, hi = n - 1;\nwhile (lo <= hi) {\n    int mid = (lo + hi) / 2;\n    if (a[mid] == x) return mid;\n    if (a[mid] < x) lo = mid + 1;\n    else hi = mid - 1;\n}\nreturn -1;'},
    {lang: 'Python', text: 'n = int(input())\na = list(map(int, input().split()))\nprint(max(a), a.count(max(a)))'},
    {lang: 'Python', text: 'def is_prime(n):\n    if n < 2:\n        return False\n    i = 2\n    while i * i <= n:\n        if n % i == 0:\n            return False\n        i += 1\n    return True'},
    {lang: 'Python', text: 'from collections import deque\n\ndist = [-1] * n\ndist[0] = 0\nq = deque([0])\nwhile q:\n    v = q.popleft()\n    for u in graph[v]:\n        if dist[u] == -1:\n            dist[u] = dist[v] + 1\n            q.append(u)'},
    {lang: 'Python', text: 'words = input().split()\ncounts = {}\nfor w in words:\n    counts[w] = counts.get(w, 0) + 1\nfor w, c in sorted(counts.items()):\n    print(w, c)'},
    {lang: 'Java', text: 'import java.util.Scanner;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner in = new Scanner(System.in);\n        int n = in.nextInt();\n        System.out.println(n * (n + 1) / 2);\n    }\n}'},
    {lang: 'Java', text: 'int[] dp = new int[n + 1];\ndp[0] = 1;\nfor (int i = 1; i <= n; i++) {\n    dp[i] = dp[i - 1];\n    if (i >= 2) dp[i] += dp[i - 2];\n}\nSystem.out.println(dp[n]);'},
    {lang: 'JavaScript', text: 'const lines = require(\'fs\').readFileSync(0, \'utf8\').split(\'\\n\');\nconst [a, b] = lines[0].split(\' \').map(Number);\nconsole.log(a + b);'},
    {lang: 'JavaScript', text: 'function fib(n) {\n    let a = 0, b = 1;\n    for (let i = 0; i < n; i++) {\n        [a, b] = [b, a + b];\n    }\n    return a;\n}'},
    {lang: 'Pascal', text: 'var\n  n, i, s: integer;\nbegin\n  readln(n);\n  s := 0;\n  for i := 1 to n do\n    s := s + i;\n  writeln(s);\nend.'}
];
