from motor import Escolha, Marco, Quiz, Script, Tarefa, cmd, rx

TITULO = "Shell e scripts (na mão e com IA)"
DATAS = "04–10/01"
OBJETIVO = """
Escrever o básico de Bash na mão (cai na prova) e usar IA do jeito que o mercado usa:
você especifica, revisa, testa e se responsabiliza.
Teoria: 105.1, 105.2, 107.3 e 106 (só teoria).
"""

EXERCICIOS = [
    # ── conceitos ──
    Quiz(id="s08.var.1", titulo="$#", exato=True,
         enunciado="Num script, qual variável guarda a QUANTIDADE de argumentos recebidos?", respostas=["$#"]),
    Quiz(id="s08.var.2", titulo="$?", exato=True,
         enunciado="Qual variável guarda o código de saída do ÚLTIMO comando?", respostas=["$?"]),
    Quiz(id="s08.var.3", titulo="$0", exato=True,
         enunciado="Qual variável guarda o nome do próprio script?", respostas=["$0"]),
    Escolha(id="s08.var.4", titulo='"$@" × "$*"',
            enunciado='Qual a diferença entre "$@" e "$*"?',
            opcoes=['"$@" mantém cada argumento separado; "$*" junta todos numa string só',
                    "Nenhuma", '"$*" só pega o primeiro argumento', '"$@" ignora argumentos com espaço'],
            correta="a",
            explicacao='Quase sempre você quer "$@" (com aspas), para não quebrar argumentos que têm espaço.'),
    Quiz(id="s08.exit", titulo="Sucesso", enunciado="Qual código de saída indica SUCESSO?", respostas=["0"]),
    Escolha(id="s08.test.1", titulo="Testes de arquivo",
            enunciado="Qual teste é verdadeiro se o caminho existe E é um arquivo regular?",
            opcoes=["[ -d x ]", "[ -f x ]", "[ -z x ]", "[ -x x ]"], correta="b"),
    Escolha(id="s08.test.2", titulo="Comparar números",
            enunciado="Dentro de [ ], como comparar se o NÚMERO $a é maior que $b?",
            opcoes=["[ $a > $b ]", "[ $a -gt $b ]", "[ $a => $b ]", "[ $a gt $b ]"], correta="b",
            explicacao="Dentro de [ ], o > é redirecionamento: [ $a > $b ] cria um arquivo chamado $b!"),
    Escolha(id="s08.test.3", titulo="String vazia",
            enunciado="Qual teste é verdadeiro quando a variável $nome está VAZIA?",
            opcoes=['[ -n "$nome" ]', '[ -z "$nome" ]', '[ -e "$nome" ]', '[ -s "$nome" ]'], correta="b"),
    Escolha(id="s08.set", titulo="set -euo pipefail",
            enunciado="O que `set -euo pipefail` faz? (marque 3)",
            opcoes=["-e: sai do script se um comando falhar", "-u: erro ao usar variável não definida",
                    "-o pipefail: o pipeline falha se QUALQUER comando dele falhar", "-e: ativa o modo de debug"],
            correta="abc"),
    Escolha(id="s08.source", titulo="source × ./script",
            enunciado="Qual a diferença entre `source script.sh` e `./script.sh`?",
            opcoes=["source roda no shell ATUAL (variáveis e cd continuam valendo); ./ roda num shell filho",
                    "Nenhuma", "./ roda no shell atual", "source exige permissão de execução"], correta="a"),
    Quiz(id="s08.export", titulo="Exportar variável",
         enunciado="Qual comando torna a variável EDITOR visível para os processos filhos (com o valor vim)?",
         respostas=[rx(r"export EDITOR=(vim|\"vim\"|'vim')")], resposta="export EDITOR=vim"),
    Escolha(id="s08.prof.1", titulo="Shell de login",
            enunciado="Num shell de LOGIN (ex.: via ssh), quais arquivos o bash lê? (marque 2)",
            opcoes=["/etc/profile", "~/.bash_profile (ou ~/.profile)", "/etc/bash_logout", "~/.bash_history"],
            correta="ab",
            explicacao="Num shell interativo que NÃO é de login (abrir um terminal na interface gráfica), ele lê o ~/.bashrc."),
    Quiz(id="s08.prof.2", titulo="Alias permanente",
         enunciado="Em qual arquivo você coloca um alias pessoal para valer em todo terminal novo?",
         respostas=["~/.bashrc", ".bashrc", "/home/usuario/.bashrc"]),
    Quiz(id="s08.prof.3", titulo="Para todos os usuários",
         enunciado="Em qual DIRETÓRIO você coloca um script .sh para configurar o ambiente de login de TODOS os usuários?",
         respostas=["/etc/profile.d", "/etc/profile.d/"]),

    # ── scripts na mão (cai na prova) ──
    Script(id="s08.sc.ola", titulo="Script 1: ola.sh", arquivo="ola.sh",
           enunciado="""
           Escreva ola.sh:
             ./ola.sh Diego   → imprime  Olá, Diego!
             ./ola.sh         → imprime uma mensagem de uso no STDERR e sai com código 1
           """,
           testes=[{"args": ["Diego"], "saida": "Olá, Diego!", "codigo": 0},
                   {"args": ["Ana"], "saida": "Olá, Ana!", "codigo": 0},
                   {"args": [], "saida": "", "codigo": 1, "stderr": True,
                    "desc": "sem argumento: uso no stderr e código 1"}],
           resposta='#!/bin/bash\nif [ $# -ne 1 ]; then\n    echo "uso: $0 NOME" >&2\n    exit 1\nfi\necho "Olá, $1!"\n'),
    Script(id="s08.sc.maior", titulo="Script 2: maior.sh", arquivo="maior.sh",
           enunciado="""
           Escreva maior.sh, que recebe dois números e imprime o maior. Se forem iguais, imprime: iguais
           """,
           testes=[{"args": ["3", "9"], "saida": "9"}, {"args": ["10", "2"], "saida": "10"},
                   {"args": ["5", "5"], "saida": "iguais"}, {"args": ["-3", "-1"], "saida": "-1"}],
           resposta='#!/bin/bash\nif [ "$1" -gt "$2" ]; then\n    echo "$1"\nelif [ "$1" -lt "$2" ]; then\n    echo "$2"\nelse\n    echo iguais\nfi\n'),
    Script(id="s08.sc.existe", titulo="Script 3: existe.sh", arquivo="existe.sh",
           enunciado="""
           Escreva existe.sh CAMINHO:
             se for diretório → imprime  diretório      (código 0)
             se for arquivo   → imprime  arquivo        (código 0)
             se não existir   → imprime  não existe     (código 2)
           """,
           testes=[{"args": ["arvore"], "saida": "diretório", "codigo": 0},
                   {"args": ["auth.log"], "saida": "arquivo", "codigo": 0},
                   {"args": ["nada.txt"], "saida": "não existe", "codigo": 2}],
           resposta='#!/bin/bash\nif [ -d "$1" ]; then\n    echo "diretório"\nelif [ -f "$1" ]; then\n    echo "arquivo"\nelse\n    echo "não existe"\n    exit 2\nfi\n'),
    Script(id="s08.sc.soma", titulo="Script 4: soma.sh (lendo do stdin)", arquivo="soma.sh",
           enunciado="Escreva soma.sh: lê números do STDIN, um por linha, e imprime a soma (entrada vazia → 0).",
           testes=[{"stdin": "1\n2\n3\n", "saida": "6"}, {"stdin": "10\n-4\n", "saida": "6"},
                   {"stdin": "", "saida": "0"}],
           resposta='#!/bin/bash\ntotal=0\nwhile read -r n; do\n    [ -z "$n" ] && continue\n    total=$((total + n))\ndone\necho "$total"\n'),
    Script(id="s08.sc.niveis", titulo="Desafio de sábado: conta_niveis.sh", arquivo="conta_niveis.sh",
           enunciado="""
           Sem IA e sem internet: conta_niveis.sh ARQUIVO conta as linhas de cada nível de log
           ([INFO], [WARN], [ERROR]) e imprime exatamente:
             INFO: n
             WARN: n
             ERROR: n
           (use app.log para testar; há também mini.log, com algum nível zerado)
           """,
           preparar="printf '2026-01-01 10:00:00 [INFO] a\\n2026-01-01 10:00:01 [ERROR] b\\n2026-01-01 10:00:02 [INFO] c\\n' > mini.log",
           testes=[{"args": ["app.log"], "saida": "INFO: 40\nWARN: 12\nERROR: 5"},
                   {"args": ["mini.log"], "saida": "INFO: 2\nWARN: 0\nERROR: 1"}],
           resposta='#!/bin/bash\nfor n in INFO WARN ERROR; do\n    echo "$n: $(grep -c "\\[$n\\]" "$1")"\ndone\n'),
    Script(id="s08.sc.shell", titulo="Script 5: usuarios_shell.sh", arquivo="usuarios_shell.sh",
           enunciado="usuarios_shell.sh ARQUIVO_PASSWD SHELL lista (na ordem do arquivo) os logins que usam aquele shell.",
           testes=[{"args": ["passwd.txt", "/bin/bash"], "saida": "root\ndiego\nmaria\nsuporte"},
                   {"args": ["passwd.txt", "/bin/zsh"], "saida": "joao"}],
           resposta='#!/bin/bash\nawk -F: -v s="$2" \'$7 == s {print $1}\' "$1"\n'),

    # ── scripts com IA (fluxo de mercado) ──
    Tarefa(id="s08.ia.backup", titulo="Com IA: backup.sh (especificar → revisar → testar)",
           enunciado="""
           1. Escreva a especificação em ~/linux-lab/specs/backup.md:
                uso: backup.sh ORIGEM DESTINO
                cria DESTINO/backup-AAAAMMDD-HHMMSS.tar.gz com o conteúdo de ORIGEM
                mantém só os 7 backups mais recentes no DESTINO
                registra no journal com logger; se ORIGEM não existir, mensagem no stderr e código ≠ 0
           2. Peça à IA, REVISE linha a linha e salve em ~/linux-lab/scripts/backup.sh (executável).
           3. Instale o shellcheck (sudo dnf install ShellCheck) e zere os avisos.
           4. Em ~/linux-lab/scripts/README.md, registre pelo menos 1 bug ou risco que você achou no código da IA.
           O verificador roda seu script de verdade 9 vezes e confere a rotação (leva uns 10 segundos).
           """,
           checks=[("backup.sh existe e é executável", "test -x ~/linux-lab/scripts/backup.sh"),
                   ("especificação escrita", "test -s ~/linux-lab/specs/backup.md"),
                   ("passa no shellcheck", "shellcheck ~/linux-lab/scripts/backup.sh"),
                   ("falha com origem inexistente", "! ~/linux-lab/scripts/backup.sh /nao/existe /tmp >/dev/null 2>&1"),
                   ("rotação: 9 execuções deixam 7 backups com o conteúdo",
                    'T=$(mktemp -d); mkdir -p $T/src $T/dst; echo oi > $T/src/a; '
                    'for i in $(seq 9); do ~/linux-lab/scripts/backup.sh $T/src $T/dst >/dev/null 2>&1 || exit 1; sleep 1.1; done; '
                    '[ "$(ls $T/dst | wc -l)" -eq 7 ] && tar -tzf "$(ls -t $T/dst/* | head -1)" | grep -q "a$"; r=$?; rm -rf $T; exit $r'),
                   ("README registra bugs da revisão", "grep -qi 'bug' ~/linux-lab/scripts/README.md")]),
    Tarefa(id="s08.ia.detecta", titulo="Com IA: detecta-mudancas.sh + regra no Wazuh", host="rhel",
           enunciado="""
           Especifique (specs/detecta-mudancas.md), gere com IA e revise um script que avisa via logger
           se apareceu um NOVO binário SUID ou uma NOVA chave em qualquer authorized_keys desde a última execução.
           Instale na rhel em /usr/local/bin/detecta-mudancas.sh, rodando por um systemd timer a cada 10 min.
           Depois crie uma regra customizada no Wazuh (no manager) que alerta quando ele registrar algo.
           Teste: chmod u+s num binário qualquer e espere o alerta.
           """,
           checks=[("script instalado e executável", "test -x /usr/local/bin/detecta-mudancas.sh"),
                   ("existe um timer para ele", "systemctl list-timers --all --no-legend | grep -qi detecta"),
                   ("o script está no seu repositório", "test -f ~/linux-lab/scripts/detecta-mudancas.sh", "local")]),

    # ── localização e interface gráfica ──
    Escolha(id="s08.loc.1", titulo="Prioridade de locale",
            enunciado="Qual variável tem PRIORIDADE sobre todas as outras de locale?",
            opcoes=["LANG", "LC_ALL", "LC_MESSAGES", "LANGUAGE"], correta="b"),
    Quiz(id="s08.loc.2", titulo="Fuso horário",
         enunciado="Comando para mudar o fuso horário para America/Sao_Paulo com timedatectl:",
         respostas=[cmd(r"timedatectl set-timezone America/Sao_Paulo")],
         resposta="timedatectl set-timezone America/Sao_Paulo"),
    Escolha(id="s08.loc.3", titulo="/etc/localtime",
            enunciado="O que é o /etc/localtime?",
            opcoes=["Um script", "Normalmente um link simbólico para o arquivo de fuso em /usr/share/zoneinfo/",
                    "O relógio do hardware", "O log do NTP"], correta="b"),
    Quiz(id="s08.loc.4", titulo="Converter codificação",
         enunciado="Comando para converter velho.txt de ISO-8859-1 para UTF-8 (mostrando na tela):",
         respostas=[rx(r"iconv -f (iso-8859-1|iso8859-1|latin1) -t utf-?8 velho\.txt", i=True)],
         resposta="iconv -f ISO-8859-1 -t UTF-8 velho.txt"),
    Escolha(id="s08.x11.1", titulo="DISPLAY",
            enunciado="Para que serve a variável DISPLAY?",
            opcoes=["Resolução da tela", "Diz a qual servidor X os programas gráficos devem se conectar",
                    "Tamanho da fonte", "Qual monitor está ligado"], correta="b"),
    Escolha(id="s08.x11.2", titulo="X pelo SSH",
            enunciado="Como rodar um programa gráfico remoto pela sessão SSH?",
            opcoes=["ssh -X servidor", "ssh -L servidor", "ssh -D servidor", "Não é possível"], correta="a"),
    Escolha(id="s08.x11.3", titulo="Display managers",
            enunciado="Quais são display managers (tela de login gráfica)?",
            opcoes=["GDM", "SDDM", "LightDM", "Xorg"], correta="abc",
            explicacao="Xorg é o servidor gráfico; Wayland é o protocolo que o substitui nas distros atuais."),
    Escolha(id="s08.x11.4", titulo="Acessibilidade",
            enunciado="Qual ferramenta é um leitor de tela para pessoas com deficiência visual no GNOME?",
            opcoes=["Orca", "Xeyes", "GOK", "xrandr"], correta="a"),
]
