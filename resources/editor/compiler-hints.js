/* Code hints for the standalone Compiler page only (not loaded on the problem page).
 * Keywords, snippets, library names and identifiers from the file and its neighbours. */
(function (window) {
    'use strict';

    function words(s) { return s.split(/\s+/).filter(Boolean); }

    var C_KW = words('auto bool break case catch char class const constexpr continue default delete do double else enum ' +
        'explicit extern false float for friend goto if inline int long namespace new nullptr operator private protected ' +
        'public return short signed sizeof static struct switch template this throw true try typedef typename union ' +
        'unsigned using virtual void volatile while');
    var C_LIB = words('cin cout cerr endl string vector map unordered_map set unordered_set multiset queue priority_queue ' +
        'stack deque list pair make_pair tuple array bitset optional sort stable_sort reverse min max swap abs pow sqrt ' +
        'gcd lcm accumulate iota fill unique lower_bound upper_bound binary_search next_permutation max_element ' +
        'min_element count find erase insert push_back pop_back emplace_back front back begin end size empty clear ' +
        'to_string stoi stoll stod getline printf scanf puts putchar getchar sprintf memset memcpy strlen strcmp ' +
        'int64_t uint64_t size_t INT_MAX INT_MIN LLONG_MAX ios_base sync_with_stdio tie std main');

    var JAVA_KW = words('abstract assert boolean break byte case catch char class continue default do double else enum ' +
        'extends final finally float for if implements import instanceof int interface long new package private ' +
        'protected public return short static super switch synchronized this throw throws try var void while record ' +
        'true false null');
    var JAVA_LIB = words('System String Math Integer Long Double Character Boolean StringBuilder Scanner ArrayList ' +
        'LinkedList HashMap TreeMap HashSet TreeSet PriorityQueue ArrayDeque Arrays Collections List Map Set Queue ' +
        'Deque Stack BufferedReader InputStreamReader PrintWriter StringTokenizer Iterator Optional Random Objects ' +
        'length size get put add remove contains isEmpty append toString equals compareTo parseInt valueOf charAt ' +
        'substring split nextInt nextLine readLine println printf');

    var CS_KW = words('abstract as base bool break byte case catch char checked class const continue decimal default ' +
        'delegate do double else enum event explicit extern false finally fixed float for foreach goto if implicit in ' +
        'int interface internal is lock long namespace new null object operator out override params private ' +
        'protected public readonly ref return sbyte sealed short sizeof static string struct switch this throw true ' +
        'try typeof uint ulong unchecked unsafe ushort using var virtual void volatile while');
    var CS_LIB = words('Console WriteLine ReadLine Write Math List Dictionary HashSet Queue Stack StringBuilder ' +
        'Convert Array String Int32 Int64 Environment Linq Where Select OrderBy ToList ToArray Sum Max Min Count ' +
        'Split Trim Parse TryParse Add Remove Contains Length');

    var JS_KW = words('async await break case catch class const continue debugger default delete do else export extends ' +
        'false finally for function if import in instanceof let new null return super switch this throw true try ' +
        'typeof undefined var void while yield of');
    var JS_LIB = words('console log Math JSON Array Object parseInt parseFloat Number String Boolean Map Set Promise ' +
        'require process module exports readline fs readFileSync split join map filter reduce forEach push pop ' +
        'shift slice splice indexOf includes sort reverse keys values entries toString length');

    var PY_KW = words('False None True and as assert async await break class continue def del elif else except finally ' +
        'for from global if import in is lambda nonlocal not or pass raise return try while with yield');
    var PY_LIB = words('print input len range int float str list dict set tuple sorted reversed enumerate zip map ' +
        'filter sum min max abs round open isinstance type bool any all pow divmod chr ord bin hex oct format iter ' +
        'next append extend pop sort split join strip replace startswith endswith lower upper items keys values add ' +
        'remove sys stdin stdout readline math sqrt gcd floor ceil pi inf collections defaultdict Counter deque ' +
        'itertools permutations combinations product heapq heappush heappop bisect bisect_left bisect_right ' +
        'functools lru_cache random randint re string');

    var GO_KW = words('break case chan const continue default defer else fallthrough for func go goto if import ' +
        'interface map package range return select struct switch type var true false nil iota');
    var GO_LIB = words('int int64 uint64 string float64 bool byte rune error append cap close copy delete len make new ' +
        'panic print println recover fmt Println Printf Sprintf Print Scan Scanf Scanln Sscanf Fscan bufio NewReader ' +
        'NewWriter NewScanner Flush os Stdin Stdout strings Split Join Fields TrimSpace Repeat strconv Atoi Itoa sort ' +
        'Ints Strings Slice math Sqrt Abs Max Min');

    var KT_KW = words('abstract as break by catch class companion const continue crossinline data do else enum false ' +
        'final finally for fun if in infix inline interface internal is it lateinit noinline null object open ' +
        'operator out override private protected public return sealed super suspend this throw true try typealias ' +
        'val var vararg when where while');
    var KT_LIB = words('println print readLine readln listOf mutableListOf mapOf mutableMapOf setOf mutableSetOf ' +
        'arrayOf intArrayOf IntArray LongArray String Int Long Double Boolean Char List Map Set StringBuilder ' +
        'toInt toLong toDouble split trim map filter forEach sum sorted sortedBy joinToString size indices until ' +
        'downTo step first last min max count');

    var PAS_KW = words('and array as begin break case const continue div do downto else end except exit false file ' +
        'finally for function goto if implementation in interface label mod nil not of or packed procedure ' +
        'program record repeat set shl shr string then to true try type unit until uses var while with xor');
    var PAS_LIB = words('integer longint int64 real double extended boolean char byte word cardinal writeln write ' +
        'readln read length copy pos delete insert inttostr strtoint abs sqr sqrt trunc round ord chr sin cos ' +
        'random randomize inc dec low high setlength');

    var FS_KW = words('abstract and as begin class default delegate do done downcast downto elif else end exception ' +
        'extern false finally for fun function if in inherit inline interface lazy let match member module mutable ' +
        'namespace new null of open or override private public rec return static struct then to true try type ' +
        'use val void when while with yield');
    var FS_LIB = words('printfn printf sprintf failwith string int float bool List Array Seq Map Set Option ' +
        'List.map List.filter List.fold Seq.map Seq.sum Array.sort Console.ReadLine Console.WriteLine');

    // Snippets: [trigger, description, body]. ${n:placeholder} and $0 as in VS Code.
    var SNIP_C = [
        ['main', 'main()', 'int main() {\n\t$0\n\treturn 0;\n}'],
        ['for', 'for', 'for (int ${1:i} = 0; ${1:i} < ${2:n}; ${1:i}++) {\n\t$0\n}'],
        ['forr', 'for range', 'for (auto& ${1:x} : ${2:v}) {\n\t$0\n}'],
        ['while', 'while', 'while (${1:cond}) {\n\t$0\n}'],
        ['if', 'if', 'if (${1:cond}) {\n\t$0\n}'],
        ['ifelse', 'if / else', 'if (${1:cond}) {\n\t$2\n} else {\n\t$0\n}'],
        ['switch', 'switch', 'switch (${1:x}) {\n\tcase ${2:1}:\n\t\t$0\n\t\tbreak;\n\tdefault:\n\t\tbreak;\n}'],
        ['struct', 'struct', 'struct ${1:Name} {\n\t$0\n};'],
        ['cout', 'cout', 'cout << ${1:x} << endl;'],
        ['cin', 'cin', 'cin >> ${1:x};'],
        ['fastio', 'fast I/O', 'ios_base::sync_with_stdio(false);\ncin.tie(nullptr);'],
        ['inc', '#include <bits/stdc++.h>', '#include <bits/stdc++.h>\nusing namespace std;\n'],
        ['vec', 'vector', 'vector<${1:int}> ${2:v}(${3:n});'],
        ['printf', 'printf', 'printf("${1:%d}\\n", ${2:x});'],
        ['scanf', 'scanf', 'scanf("${1:%d}", &${2:x});']
    ];
    var SNIP_PY = [
        ['main', 'if __name__', 'def main():\n\t$0\n\n\nif __name__ == "__main__":\n\tmain()'],
        ['for', 'for', 'for ${1:i} in range(${2:n}):\n\t$0'],
        ['fore', 'for in', 'for ${1:x} in ${2:items}:\n\t$0'],
        ['while', 'while', 'while ${1:cond}:\n\t$0'],
        ['if', 'if', 'if ${1:cond}:\n\t$0'],
        ['ifelse', 'if / else', 'if ${1:cond}:\n\t$2\nelse:\n\t$0'],
        ['def', 'def', 'def ${1:name}(${2:args}):\n\t$0'],
        ['class', 'class', 'class ${1:Name}:\n\tdef __init__(self${2}):\n\t\t$0'],
        ['try', 'try / except', 'try:\n\t$1\nexcept ${2:Exception} as e:\n\t$0'],
        ['with', 'with open', 'with open(${1:"file.txt"}) as ${2:f}:\n\t$0'],
        ['ints', 'read ints', 'list(map(int, input().split()))'],
        ['fastin', 'fast input', 'import sys\ninput = sys.stdin.readline\n'],
        ['lc', 'list comprehension', '[${1:x} for ${2:x} in ${3:items}]']
    ];
    var SNIP_JAVA = [
        ['main', 'main()', 'public static void main(String[] args) {\n\t$0\n}'],
        ['sout', 'System.out.println', 'System.out.println(${1});'],
        ['for', 'for', 'for (int ${1:i} = 0; ${1:i} < ${2:n}; ${1:i}++) {\n\t$0\n}'],
        ['fore', 'for each', 'for (${1:int} ${2:x} : ${3:items}) {\n\t$0\n}'],
        ['while', 'while', 'while (${1:cond}) {\n\t$0\n}'],
        ['if', 'if', 'if (${1:cond}) {\n\t$0\n}'],
        ['ifelse', 'if / else', 'if (${1:cond}) {\n\t$2\n} else {\n\t$0\n}'],
        ['class', 'class', 'public class ${1:Main} {\n\t$0\n}'],
        ['scanner', 'Scanner', 'Scanner ${1:sc} = new Scanner(System.in);'],
        ['reader', 'BufferedReader', 'BufferedReader ${1:br} = new BufferedReader(new InputStreamReader(System.in));'],
        ['try', 'try / catch', 'try {\n\t$1\n} catch (${2:Exception} e) {\n\t$0\n}']
    ];
    var SNIP_CS = [
        ['main', 'Main()', 'static void Main() {\n\t$0\n}'],
        ['cw', 'Console.WriteLine', 'Console.WriteLine(${1});'],
        ['cr', 'Console.ReadLine', 'Console.ReadLine()'],
        ['for', 'for', 'for (int ${1:i} = 0; ${1:i} < ${2:n}; ${1:i}++) {\n\t$0\n}'],
        ['foreach', 'foreach', 'foreach (var ${1:x} in ${2:items}) {\n\t$0\n}'],
        ['while', 'while', 'while (${1:cond}) {\n\t$0\n}'],
        ['if', 'if', 'if (${1:cond}) {\n\t$0\n}'],
        ['ifelse', 'if / else', 'if (${1:cond}) {\n\t$2\n} else {\n\t$0\n}'],
        ['class', 'class', 'class ${1:Name} {\n\t$0\n}'],
        ['try', 'try / catch', 'try {\n\t$1\n} catch (${2:Exception} e) {\n\t$0\n}']
    ];
    var SNIP_JS = [
        ['function', 'function', 'function ${1:name}(${2:args}) {\n\t$0\n}'],
        ['arrow', 'arrow function', 'const ${1:name} = (${2:args}) => {\n\t$0\n};'],
        ['for', 'for', 'for (let ${1:i} = 0; ${1:i} < ${2:n}; ${1:i}++) {\n\t$0\n}'],
        ['forof', 'for of', 'for (const ${1:x} of ${2:items}) {\n\t$0\n}'],
        ['while', 'while', 'while (${1:cond}) {\n\t$0\n}'],
        ['if', 'if', 'if (${1:cond}) {\n\t$0\n}'],
        ['ifelse', 'if / else', 'if (${1:cond}) {\n\t$2\n} else {\n\t$0\n}'],
        ['log', 'console.log', 'console.log(${1});'],
        ['class', 'class', 'class ${1:Name} {\n\tconstructor(${2}) {\n\t\t$0\n\t}\n}'],
        ['try', 'try / catch', 'try {\n\t$1\n} catch (${2:e}) {\n\t$0\n}'],
        ['readline', 'read lines', 'const lines = require("fs").readFileSync(0, "utf8").split("\\n");']
    ];
    var SNIP_GO = [
        ['main', 'main()', 'func main() {\n\t$0\n}'],
        ['func', 'func', 'func ${1:name}(${2:args}) ${3:int} {\n\t$0\n}'],
        ['for', 'for', 'for ${1:i} := 0; ${1:i} < ${2:n}; ${1:i}++ {\n\t$0\n}'],
        ['forr', 'for range', 'for ${1:i}, ${2:v} := range ${3:items} {\n\t$0\n}'],
        ['if', 'if', 'if ${1:cond} {\n\t$0\n}'],
        ['ifelse', 'if / else', 'if ${1:cond} {\n\t$2\n} else {\n\t$0\n}'],
        ['switch', 'switch', 'switch ${1:x} {\ncase ${2:1}:\n\t$0\ndefault:\n}'],
        ['struct', 'struct', 'type ${1:Name} struct {\n\t$0\n}'],
        ['pl', 'fmt.Println', 'fmt.Println(${1})'],
        ['scan', 'fmt.Scan', 'fmt.Scan(&${1:x})'],
        ['reader', 'bufio reader', 'reader := bufio.NewReader(os.Stdin)\nwriter := bufio.NewWriter(os.Stdout)\ndefer writer.Flush()']
    ];
    var SNIP_KT = [
        ['main', 'main()', 'fun main() {\n\t$0\n}'],
        ['fun', 'fun', 'fun ${1:name}(${2:args}): ${3:Int} {\n\t$0\n}'],
        ['for', 'for', 'for (${1:i} in 0 until ${2:n}) {\n\t$0\n}'],
        ['fore', 'for in', 'for (${1:x} in ${2:items}) {\n\t$0\n}'],
        ['while', 'while', 'while (${1:cond}) {\n\t$0\n}'],
        ['if', 'if', 'if (${1:cond}) {\n\t$0\n}'],
        ['ifelse', 'if / else', 'if (${1:cond}) {\n\t$2\n} else {\n\t$0\n}'],
        ['when', 'when', 'when (${1:x}) {\n\t${2:1} -> $0\n\telse -> {}\n}'],
        ['class', 'class', 'class ${1:Name}(${2}) {\n\t$0\n}'],
        ['pl', 'println', 'println(${1})'],
        ['ints', 'read ints', 'readLine()!!.split(" ").map { it.toInt() }']
    ];
    var SNIP_PAS = [
        ['program', 'program', 'program ${1:Name};\nvar\n\t$2\nbegin\n\t$0\nend.'],
        ['for', 'for', 'for ${1:i} := ${2:1} to ${3:n} do begin\n\t$0\nend;'],
        ['while', 'while', 'while ${1:cond} do begin\n\t$0\nend;'],
        ['repeat', 'repeat', 'repeat\n\t$0\nuntil ${1:cond};'],
        ['if', 'if', 'if ${1:cond} then begin\n\t$0\nend;'],
        ['ifelse', 'if / else', 'if ${1:cond} then begin\n\t$2\nend else begin\n\t$0\nend;'],
        ['case', 'case', 'case ${1:x} of\n\t${2:1}: $0\nend;'],
        ['procedure', 'procedure', 'procedure ${1:Name}(${2});\nbegin\n\t$0\nend;'],
        ['function', 'function', 'function ${1:Name}(${2}): ${3:integer};\nbegin\n\t$0\nend;'],
        ['wl', 'writeln', 'writeln(${1});'],
        ['rl', 'readln', 'readln(${1});']
    ];
    var SNIP_FS = [
        ['let', 'let', 'let ${1:name} = $0'],
        ['fun', 'function', 'let ${1:name} ${2:x} =\n    $0'],
        ['for', 'for', 'for ${1:i} in 0 .. ${2:n} - 1 do\n    $0'],
        ['while', 'while', 'while ${1:cond} do\n    $0'],
        ['if', 'if', 'if ${1:cond} then\n    $2\nelse\n    $0'],
        ['match', 'match', 'match ${1:x} with\n| ${2:_} -> $0'],
        ['pf', 'printfn', 'printfn "${1}"']
    ];

    var LANGS = {
        cpp: {kw: C_KW, lib: C_LIB, snip: SNIP_C},
        python: {kw: PY_KW, lib: PY_LIB, snip: SNIP_PY},
        java: {kw: JAVA_KW, lib: JAVA_LIB, snip: SNIP_JAVA},
        csharp: {kw: CS_KW, lib: CS_LIB, snip: SNIP_CS},
        javascript: {kw: JS_KW, lib: JS_LIB, snip: SNIP_JS},
        go: {kw: GO_KW, lib: GO_LIB, snip: SNIP_GO},
        kotlin: {kw: KT_KW, lib: KT_LIB, snip: SNIP_KT},
        pascal: {kw: PAS_KW, lib: PAS_LIB, snip: SNIP_PAS, nocase: true},
        fsharp: {kw: FS_KW, lib: FS_LIB, snip: SNIP_FS}
    };

    var IDENT = /[A-Za-z_][A-Za-z0-9_]{2,}/g;

    function identifiers(text, counts) {
        var m;
        IDENT.lastIndex = 0;
        while ((m = IDENT.exec(text))) counts[m[0]] = (counts[m[0]] || 0) + 1;
    }

    // Inside a comment or a string nothing is offered.
    function inCommentOrString(line, lang) {
        var inStr = null;
        for (var i = 0; i < line.length; i++) {
            var ch = line[i];
            if (inStr) {
                if (ch === '\\') { i++; continue; }
                if (ch === inStr) inStr = null;
                continue;
            }
            if (ch === '"' || (ch === "'" && lang !== 'pascal' && lang !== 'fsharp') || (ch === '`' && lang === 'javascript')) {
                inStr = ch;
            } else if (lang === 'pascal' && ch === "'") {
                inStr = ch;
            } else if (lang === 'python' && ch === '#') {
                return true;
            } else if (lang !== 'python' && ch === '/' && line[i + 1] === '/') {
                return true;
            }
        }
        return inStr !== null;
    }

    var registered = false;

    /* options.neighbours(model) returns texts of the other files of the same folder. */
    function register(monaco, options) {
        if (registered || !monaco) return;
        registered = true;
        options = options || {};
        var Kind = monaco.languages.CompletionItemKind;
        var Rule = monaco.languages.CompletionItemInsertTextRule;

        Object.keys(LANGS).forEach(function (lang) {
            var def = LANGS[lang];
            var known = {};
            def.kw.forEach(function (w) { known[w] = true; });
            def.lib.forEach(function (w) { known[w] = true; });
            var triggers = {};
            def.snip.forEach(function (sn) { triggers[sn[0]] = true; known[sn[0]] = true; });

            monaco.languages.registerCompletionItemProvider(lang, {
                provideCompletionItems: function (model, position) {
                    var before = model.getValueInRange({
                        startLineNumber: position.lineNumber, startColumn: 1,
                        endLineNumber: position.lineNumber, endColumn: position.column
                    });
                    if (inCommentOrString(before, lang)) return {suggestions: []};
                    var word = model.getWordUntilPosition(position);
                    var range = {
                        startLineNumber: position.lineNumber, endLineNumber: position.lineNumber,
                        startColumn: word.startColumn, endColumn: word.endColumn
                    };
                    var items = [];

                    // Identifiers from this file and its neighbours (the word being typed is not offered).
                    var counts = Object.create(null);
                    identifiers(model.getValue(), counts);
                    var extra = options.neighbours ? options.neighbours(model) : [];
                    extra.forEach(function (text) { identifiers(text, counts); });
                    var shown = 0;
                    Object.keys(counts).forEach(function (name) {
                        if (known[name] || shown > 400) return;
                        if (name === word.word && counts[name] < 2) return;
                        shown++;
                        items.push({label: name, kind: Kind.Variable, insertText: name, range: range, sortText: '0' + name});
                    });

                    def.snip.forEach(function (s) {
                        items.push({
                            label: s[0], kind: Kind.Snippet, detail: s[1], insertText: s[2], range: range,
                            insertTextRules: Rule.InsertAsSnippet, sortText: '1' + s[0], filterText: s[0]
                        });
                    });
                    def.kw.forEach(function (w) {
                        if (triggers[w]) return;
                        items.push({label: w, kind: Kind.Keyword, insertText: w, range: range, sortText: '2' + w});
                    });
                    def.lib.forEach(function (w) {
                        if (triggers[w]) return;
                        items.push({label: w, kind: Kind.Function, insertText: w, range: range, sortText: '3' + w});
                    });
                    return {suggestions: items};
                }
            });
        });
    }

    window.OlympHints = {register: register};
})(window);
