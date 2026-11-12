/* Code for the typing trainer: level 1 - a few lines, 2 - a typical solution, 3 - an algorithm. */
window.TYPING_CODE = [
    /* ---------- C++ ---------- */
    {lang: 'C++', level: 1, text: '#include <iostream>\nusing namespace std;\n\nint main() {\n    int a, b;\n    cin >> a >> b;\n    cout << a + b << endl;\n    return 0;\n}'},
    {lang: 'C++', level: 1, text: 'int n;\ncin >> n;\nif (n % 2 == 0) {\n    cout << "even";\n} else {\n    cout << "odd";\n}'},
    {lang: 'C++', level: 1, text: 'int s = 0;\nfor (int i = 1; i <= 100; i++) {\n    s += i;\n}\ncout << s << "\\n";'},
    {lang: 'C++', level: 2, text: 'long long gcd(long long a, long long b) {\n    while (b != 0) {\n        long long t = a % b;\n        a = b;\n        b = t;\n    }\n    return a;\n}'},
    {lang: 'C++', level: 2, text: 'vector<int> a(n);\nfor (int i = 0; i < n; i++) {\n    cin >> a[i];\n}\nsort(a.begin(), a.end());\ncout << a[n - 1] << "\\n";'},
    {lang: 'C++', level: 2, text: 'string s;\ngetline(cin, s);\nint vowels = 0;\nfor (char c : s) {\n    if (string("aeiou").find(tolower(c)) != string::npos) {\n        vowels++;\n    }\n}\ncout << vowels << endl;'},
    {lang: 'C++', level: 2, text: 'map<string, int> cnt;\nstring w;\nwhile (cin >> w) {\n    cnt[w]++;\n}\nfor (auto& [word, c] : cnt) {\n    cout << word << " " << c << "\\n";\n}'},
    {lang: 'C++', level: 3, text: 'int lo = 0, hi = n - 1;\nwhile (lo <= hi) {\n    int mid = lo + (hi - lo) / 2;\n    if (a[mid] == x) return mid;\n    if (a[mid] < x) lo = mid + 1;\n    else hi = mid - 1;\n}\nreturn -1;'},
    {lang: 'C++', level: 3, text: 'vector<bool> prime(n + 1, true);\nprime[0] = prime[1] = false;\nfor (int i = 2; 1LL * i * i <= n; i++) {\n    if (!prime[i]) continue;\n    for (int j = i * i; j <= n; j += i) {\n        prime[j] = false;\n    }\n}'},
    {lang: 'C++', level: 3, text: 'vector<int> dist(n, -1);\nqueue<int> q;\ndist[s] = 0;\nq.push(s);\nwhile (!q.empty()) {\n    int v = q.front();\n    q.pop();\n    for (int u : g[v]) {\n        if (dist[u] == -1) {\n            dist[u] = dist[v] + 1;\n            q.push(u);\n        }\n    }\n}'},
    {lang: 'C++', level: 3, text: 'int find(int x) {\n    return parent[x] == x ? x : parent[x] = find(parent[x]);\n}\n\nvoid unite(int a, int b) {\n    a = find(a);\n    b = find(b);\n    if (a != b) parent[a] = b;\n}'},

    /* ---------- Python ---------- */
    {lang: 'Python', level: 1, text: 'a, b = map(int, input().split())\nprint(a + b)'},
    {lang: 'Python', level: 1, text: 'name = input()\nprint("Salam, " + name + "!")'},
    {lang: 'Python', level: 1, text: 'n = int(input())\nfor i in range(1, n + 1):\n    print(i, i * i)'},
    {lang: 'Python', level: 2, text: 'n = int(input())\na = list(map(int, input().split()))\nprint(max(a), a.count(max(a)))'},
    {lang: 'Python', level: 2, text: 'def is_prime(n):\n    if n < 2:\n        return False\n    i = 2\n    while i * i <= n:\n        if n % i == 0:\n            return False\n        i += 1\n    return True'},
    {lang: 'Python', level: 2, text: 'words = input().split()\ncounts = {}\nfor w in words:\n    counts[w] = counts.get(w, 0) + 1\nfor w, c in sorted(counts.items()):\n    print(w, c)'},
    {lang: 'Python', level: 2, text: 's = input().strip()\nif s == s[::-1]:\n    print("YES")\nelse:\n    print("NO")'},
    {lang: 'Python', level: 3, text: 'from collections import deque\n\ndist = [-1] * n\ndist[0] = 0\nq = deque([0])\nwhile q:\n    v = q.popleft()\n    for u in graph[v]:\n        if dist[u] == -1:\n            dist[u] = dist[v] + 1\n            q.append(u)'},
    {lang: 'Python', level: 3, text: 'def merge_sort(a):\n    if len(a) <= 1:\n        return a\n    mid = len(a) // 2\n    left = merge_sort(a[:mid])\n    right = merge_sort(a[mid:])\n    res = []\n    i = j = 0\n    while i < len(left) and j < len(right):\n        if left[i] <= right[j]:\n            res.append(left[i])\n            i += 1\n        else:\n            res.append(right[j])\n            j += 1\n    return res + left[i:] + right[j:]'},
    {lang: 'Python', level: 3, text: 'dp = [0] * (w + 1)\nfor weight, cost in items:\n    for c in range(w, weight - 1, -1):\n        dp[c] = max(dp[c], dp[c - weight] + cost)\nprint(dp[w])'},

    /* ---------- Java ---------- */
    {lang: 'Java', level: 1, text: 'public class Main {\n    public static void main(String[] args) {\n        System.out.println("Hello, World!");\n    }\n}'},
    {lang: 'Java', level: 1, text: 'int max = a;\nif (b > max) {\n    max = b;\n}\nSystem.out.println(max);'},
    {lang: 'Java', level: 2, text: 'import java.util.Scanner;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner in = new Scanner(System.in);\n        int n = in.nextInt();\n        System.out.println(n * (n + 1) / 2);\n    }\n}'},
    {lang: 'Java', level: 2, text: 'int[] dp = new int[n + 1];\ndp[0] = 1;\nfor (int i = 1; i <= n; i++) {\n    dp[i] = dp[i - 1];\n    if (i >= 2) dp[i] += dp[i - 2];\n}\nSystem.out.println(dp[n]);'},
    {lang: 'Java', level: 2, text: 'StringBuilder sb = new StringBuilder();\nfor (int i = s.length() - 1; i >= 0; i--) {\n    sb.append(s.charAt(i));\n}\nSystem.out.println(sb.toString());'},
    {lang: 'Java', level: 3, text: 'static long power(long a, long b, long mod) {\n    long res = 1;\n    a %= mod;\n    while (b > 0) {\n        if ((b & 1) == 1) res = res * a % mod;\n        a = a * a % mod;\n        b >>= 1;\n    }\n    return res;\n}'},
    {lang: 'Java', level: 3, text: 'Map<String, Integer> count = new HashMap<>();\nfor (String w : words) {\n    count.merge(w, 1, Integer::sum);\n}\ncount.forEach((k, v) -> System.out.println(k + " " + v));'},

    /* ---------- C# ---------- */
    {lang: 'C#', level: 1, text: 'using System;\n\nclass Program {\n    static void Main() {\n        Console.WriteLine("Hello, World!");\n    }\n}'},
    {lang: 'C#', level: 1, text: 'int n = int.Parse(Console.ReadLine());\nConsole.WriteLine(n * n);'},
    {lang: 'C#', level: 2, text: 'var a = Console.ReadLine().Split(\' \');\nint sum = 0;\nforeach (var x in a) {\n    sum += int.Parse(x);\n}\nConsole.WriteLine(sum);'},
    {lang: 'C#', level: 2, text: 'static int Factorial(int n) {\n    if (n <= 1) return 1;\n    return n * Factorial(n - 1);\n}'},
    {lang: 'C#', level: 3, text: 'var list = new List<int> { 5, 3, 8, 1 };\nvar even = list.Where(x => x % 2 == 0).ToList();\nvar sorted = list.OrderBy(x => x).ToArray();\nConsole.WriteLine(string.Join(", ", sorted));'},
    {lang: 'C#', level: 3, text: 'for (int i = 0; i < n - 1; i++) {\n    for (int j = 0; j < n - 1 - i; j++) {\n        if (a[j] > a[j + 1]) {\n            (a[j], a[j + 1]) = (a[j + 1], a[j]);\n        }\n    }\n}'},

    /* ---------- JavaScript ---------- */
    {lang: 'JavaScript', level: 1, text: 'const name = "Aibek";\nconsole.log(`Salam, ${name}!`);'},
    {lang: 'JavaScript', level: 1, text: 'let sum = 0;\nfor (let i = 1; i <= 10; i++) {\n    sum += i;\n}\nconsole.log(sum);'},
    {lang: 'JavaScript', level: 2, text: 'const lines = require(\'fs\').readFileSync(0, \'utf8\').split(\'\\n\');\nconst [a, b] = lines[0].split(\' \').map(Number);\nconsole.log(a + b);'},
    {lang: 'JavaScript', level: 2, text: 'function fib(n) {\n    let a = 0, b = 1;\n    for (let i = 0; i < n; i++) {\n        [a, b] = [b, a + b];\n    }\n    return a;\n}'},
    {lang: 'JavaScript', level: 2, text: 'const nums = [4, 8, 15, 16, 23, 42];\nconst even = nums.filter(x => x % 2 === 0);\nconst total = nums.reduce((s, x) => s + x, 0);\nconsole.log(even, total);'},
    {lang: 'JavaScript', level: 3, text: 'async function load(url) {\n    const res = await fetch(url);\n    if (!res.ok) {\n        throw new Error(`HTTP ${res.status}`);\n    }\n    return res.json();\n}'},
    {lang: 'JavaScript', level: 3, text: 'document.querySelector("#btn").addEventListener("click", () => {\n    const box = document.getElementById("box");\n    box.classList.toggle("hidden");\n});'},

    /* ---------- Pascal ---------- */
    {lang: 'Pascal', level: 1, text: 'var\n  a, b: integer;\nbegin\n  readln(a, b);\n  writeln(a + b);\nend.'},
    {lang: 'Pascal', level: 2, text: 'var\n  n, i, s: integer;\nbegin\n  readln(n);\n  s := 0;\n  for i := 1 to n do\n    s := s + i;\n  writeln(s);\nend.'},
    {lang: 'Pascal', level: 2, text: 'var\n  n: integer;\nbegin\n  readln(n);\n  if n mod 2 = 0 then\n    writeln(\'even\')\n  else\n    writeln(\'odd\');\nend.'},
    {lang: 'Pascal', level: 3, text: 'function gcd(a, b: longint): longint;\nvar\n  t: longint;\nbegin\n  while b <> 0 do\n  begin\n    t := a mod b;\n    a := b;\n    b := t;\n  end;\n  gcd := a;\nend;'},

    /* ---------- Go ---------- */
    {lang: 'Go', level: 1, text: 'package main\n\nimport "fmt"\n\nfunc main() {\n    fmt.Println("Hello, World!")\n}'},
    {lang: 'Go', level: 2, text: 'var a, b int\nfmt.Scan(&a, &b)\nif a > b {\n    fmt.Println(a)\n} else {\n    fmt.Println(b)\n}'},
    {lang: 'Go', level: 3, text: 'func reverse(s []int) {\n    for i, j := 0, len(s)-1; i < j; i, j = i+1, j-1 {\n        s[i], s[j] = s[j], s[i]\n    }\n}'},

    /* ---------- HTML / CSS / SQL ---------- */
    {lang: 'HTML', level: 1, text: '<!DOCTYPE html>\n<html>\n<head>\n    <title>My page</title>\n</head>\n<body>\n    <h1>Hello!</h1>\n    <p>This is my first page.</p>\n</body>\n</html>'},
    {lang: 'HTML', level: 2, text: '<form action="/login" method="post">\n    <label for="user">Login</label>\n    <input id="user" name="user" type="text">\n    <button type="submit">Sign in</button>\n</form>'},
    {lang: 'CSS', level: 2, text: '.card {\n    display: flex;\n    gap: 12px;\n    padding: 16px;\n    border-radius: 8px;\n    background: #f5f7fa;\n}\n.card:hover {\n    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);\n}'},
    {lang: 'SQL', level: 2, text: 'SELECT name, score\nFROM students\nWHERE score >= 80\nORDER BY score DESC\nLIMIT 10;'},
    {lang: 'SQL', level: 3, text: 'SELECT c.name, COUNT(s.id) AS solved\nFROM contestants c\nJOIN submissions s ON s.user_id = c.id\nWHERE s.result = \'AC\'\nGROUP BY c.name\nHAVING COUNT(s.id) > 5;'}
];
