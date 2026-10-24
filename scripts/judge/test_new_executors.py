"""Self-test of the languages added in October 2026. Run with the judge-server virtualenv:
    cd ~/judge-server && venv/bin/python /path/to/scripts/judge/test_new_executors.py ~/judge-config/judge.yml
Prints Success / Failed for each language; a missing toolchain is reported, not fatal."""
import subprocess
import sys

import yaml

from dmoj.utils.module import load_module_from_file  # noqa: F401  (makes sure dmoj is importable)

config = yaml.safe_load(open(sys.argv[1])) if len(sys.argv) > 1 else {}
runtime = config.get('runtime', {})

samples = {
    'CPP14': ('#include <iostream>\nint main(){int a,b;std::cin>>a>>b;std::cout<<a+b<<"\\n";}', b'20 22\n', b'42'),
    'CPP20': ('#include <iostream>\n#include <ranges>\nint main(){int a,b;std::cin>>a>>b;std::cout<<a+b<<"\\n";}', b'20 22\n', b'42'),
    'JAVA': ('import java.util.*;public class Main{public static void main(String[] x){Scanner s=new Scanner(System.in);'
             'System.out.println(s.nextInt()+s.nextInt());}}', b'20 22\n', b'42'),
    'FSHARP': ('let a = stdin.ReadLine().Split() |> Array.map int\nprintfn "%d" (Array.sum a)\n', b'20 22\n', b'42'),
    'GO': ('package main\nimport "fmt"\nfunc main(){var a,b int;fmt.Scan(&a,&b);fmt.Println(a+b)}\n', b'20 22\n', b'42'),
    'KOTLIN': ('fun main(){val (a,b)=readLine()!!.split(" ").map{it.toInt()};println(a+b)}\n', b'20 22\n', b'42'),
}

failed = 0
for key, (source, data, answer) in samples.items():
    if len(sys.argv) > 2 and key not in sys.argv[2:]:
        continue
    try:
        module = __import__('dmoj.executors.' + key, fromlist=['Executor'])
        Executor = module.Executor
        Executor.runtime_dict = runtime
        executor = Executor('test_' + key.lower(), source.encode())
        process = executor.launch(time=5, wall_time=10, memory=262144,
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate(data)
        ok = out.strip() == answer
        print('%-7s %s %s' % (key, 'Success' if ok else 'Failed', '' if ok else (out + err)[:300]))
        failed += not ok
    except Exception as e:  # a missing toolchain or a compile error
        print('%-7s Failed %s: %s' % (key, type(e).__name__, str(e)[:300]))
        failed += 1
sys.exit(1 if failed else 0)
