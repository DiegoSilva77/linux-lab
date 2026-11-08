from motor import Comando, Escolha, Quiz, Subnet, Tarefa, conteudo_igual

TITULO = "Texto, pipes e logs + subnetting"
DATAS = "16–22/11"
OBJETIVO = """
Manipular texto e logs com fluência (50% do trabalho de um analista) e dominar subnetting.
Fecha as questões 1, 6, 11 e 18 do seu diagnóstico.
Teoria: learning.lpi.org → 101 → tópicos 103.1, 103.2, 103.4, 103.7.
Arquivos de exemplo: auth.log (ataque SSH), access.log (Apache), passwd.txt, vendas.csv, frutas.txt.
"""

IP_RE = r"([0-9]{1,3}\.){3}[0-9]{1,3}"

EXERCICIOS = [
    # ── redirecionamento ──
    Escolha(id="s01.redir.1", titulo="> e >>",
            enunciado="O que `>>` faz?",
            opcoes=["Redireciona só os erros", "Acrescenta a saída padrão ao FIM do arquivo",
                    "Sobrescreve o arquivo com a saída padrão", "Envia a saída para o próximo comando"],
            correta="b",
            explicacao="`>` sobrescreve · `>>` acrescenta · `2>` redireciona o stderr · `|` liga a saída ao próximo comando."),
    Escolha(id="s01.redir.2", titulo="2>&1",
            enunciado="O que significa `2>&1`?",
            opcoes=["Manda o stderr (2) para onde o stdout (1) está apontando NAQUELE momento",
                    "Manda o stdout para o stderr", "Junta os arquivos 2 e 1",
                    "Redireciona para um arquivo chamado 1"],
            correta="a"),
    Escolha(id="s01.redir.3", titulo="A ordem importa",
            enunciado="Em `cmd 2>&1 > saida.txt`, para onde vão os ERROS?",
            opcoes=["Para saida.txt", "Para a tela", "Para /dev/null", "Para lugar nenhum"],
            correta="b",
            explicacao="""
            O shell processa da esquerda para a direita. Quando lê `2>&1`, o stdout ainda é a tela,
            então o stderr vai para a tela. Só depois o stdout é trocado para o arquivo.
            Para os dois irem para o arquivo: `cmd > saida.txt 2>&1` (ou `cmd &> saida.txt`).
            """),
    Comando(id="s01.cmd.erros", titulo="Só os erros num arquivo",
            enunciado="""
            Execute ./gera_saida.sh guardando APENAS as mensagens de erro em erros.txt
            e descartando a saída normal. Nada deve aparecer na tela.
            """,
            saida_vazia=True,
            verificar=[("erros.txt tem só as 2 linhas de erro",
                        conteudo_igual("erros.txt", "ERRO: disco cheio\nERRO: permissão negada"))],
            resposta="./gera_saida.sh 2> erros.txt > /dev/null",
            dica="Você precisa de dois redirecionamentos: um para o 2 (stderr) e outro para o 1 (stdout)."),
    Comando(id="s01.cmd.tudo", titulo="Tudo junto num arquivo",
            enunciado="Execute ./gera_saida.sh salvando stdout E stderr juntos em tudo.txt. Nada na tela.",
            saida_vazia=True,
            verificar=[("tudo.txt tem as 5 linhas", '[ "$(wc -l < tudo.txt)" -eq 5 ]'),
                       ("inclui os erros", 'grep -q "disco cheio" tudo.txt')],
            resposta="./gera_saida.sh > tudo.txt 2>&1",
            explicacao="Também vale `&> tudo.txt` (atalho do bash)."),
    Comando(id="s01.cmd.find", titulo="Sua questão 1 do diagnóstico",
            enunciado="""
            Procure em /etc todos os arquivos terminados em .conf, SEM mostrar os erros de permissão,
            salvando a lista em achados.txt. Nada deve aparecer na tela.
            """,
            saida_vazia=True,
            verificar=[("achados.txt confere com a busca correta",
                        'diff -q <(find /etc -name "*.conf" 2>/dev/null | sort) <(sort achados.txt) >/dev/null')],
            resposta='find /etc -name "*.conf" 2>/dev/null > achados.txt',
            explicacao="Em novembro você escreveu `2> /etc/null | > achados.txt`: o 'buraco negro' é /dev/null, e `| >` não existe."),
    Comando(id="s01.cmd.tee", titulo="Na tela E no arquivo",
            enunciado="Mostre na tela E salve em unicos.txt as frutas únicas de frutas.txt, em ordem alfabética.",
            esperado="sort -u frutas.txt", exigir=["tee"],
            verificar=[("unicos.txt salvo", "diff -q <(sort -u frutas.txt) unicos.txt >/dev/null")],
            resposta="sort -u frutas.txt | tee unicos.txt"),

    # ── filtros de texto ──
    Comando(id="s01.cmd.tail", titulo="Fim do log",
            enunciado="Mostre as 5 últimas linhas de auth.log.", esperado="tail -n 5 auth.log"),
    Comando(id="s01.cmd.head", titulo="Primeiros logins aceitos",
            enunciado="Mostre as 3 primeiras linhas de auth.log que contêm 'Accepted'.",
            esperado="grep Accepted auth.log | head -n 3"),
    Comando(id="s01.cmd.conta", titulo="Quantas falhas?",
            enunciado="Quantas linhas 'Failed password' existem em auth.log? O comando deve imprimir só o número.",
            esperado='grep -c "Failed password" auth.log'),
    Comando(id="s01.cmd.ips", titulo="IPs atacantes",
            enunciado="Liste os IPs ÚNICOS (sem repetição, em qualquer ordem) que tiveram 'Failed password'.",
            esperado=f"grep 'Failed password' auth.log | grep -oE '{IP_RE}' | sort -u", ordem=False,
            dica="grep -o mostra só o trecho que casou. Uma regex de IP: '([0-9]{1,3}\\.){3}[0-9]{1,3}' (use grep -oE)."),
    Comando(id="s01.cmd.top5", titulo="Top 5 atacantes (sua questão 6)",
            enunciado="""
            Mostre os 5 IPs com mais 'Failed password', com a contagem, do maior para o menor.
            Formato do uniq -c, por exemplo:  57 203.0.113.5
            """,
            esperado=f"grep 'Failed password' auth.log | grep -oE '{IP_RE}' | sort | uniq -c | sort -rn | head -5",
            dica="O padrão de ouro: ... | sort | uniq -c | sort -rn | head",
            explicacao="Decore esse pipeline: você vai usá-lo a vida toda, em qualquer log."),
    Comando(id="s01.cmd.invalid", titulo="Usuários inexistentes tentados",
            enunciado="Liste, sem repetição e em ordem alfabética, os nomes de usuário INEXISTENTES tentados (linhas com 'invalid user').",
            esperado="grep -o 'invalid user [^ ]*' auth.log | cut -d' ' -f3 | sort -u",
            dica="grep -o 'invalid user [^ ]*' pega 'invalid user NOME'; depois é só cortar o 3º campo."),
    Comando(id="s01.cmd.sucesso", titulo="Login com sucesso suspeito",
            enunciado="De qual IP veio o login com SENHA aceito ('Accepted password')? Mostre só o IP.",
            esperado=f"grep 'Accepted password' auth.log | grep -oE '{IP_RE}'",
            explicacao="""
            É o mesmo IP que fez 31 tentativas antes: brute-force BEM-SUCEDIDO. Olhe as linhas logo
            depois no auth.log: sudo lendo /etc/shadow e criação de um usuário com UID 0. É um incidente.
            """),
    Comando(id="s01.cmd.hora", titulo="Linha do tempo do atacante",
            enunciado="""
            Mostre o horário (só HH:MM:SS) da PRIMEIRA e da ÚLTIMA falha do IP 198.51.100.23, um por linha.
            """,
            esperado="grep 'Failed password.*198.51.100.23' auth.log | sed -n '1p;$p' | awk '{print $3}'",
            dica="Filtre as linhas do IP; pegue a primeira e a última (head/tail ou sed -n '1p;$p'); o horário é o 3º campo (awk)."),
    Comando(id="s01.cmd.pos", titulo="O que o atacante fez depois",
            enunciado="Mostre as 3 linhas que vêm LOGO DEPOIS do 'Accepted password' no auth.log (sem a linha do Accepted).",
            esperado="grep -A3 'Accepted password' auth.log | tail -n 3",
            dica="grep -A N mostra N linhas depois (After) de cada ocorrência."),

    Comando(id="s01.cmd.cut", titulo="cut: login e shell",
            enunciado="Do passwd.txt, mostre login e shell (campos 1 e 7) separados por ':'.",
            esperado="cut -d: -f1,7 passwd.txt"),
    Comando(id="s01.cmd.bash", titulo="Quem usa bash",
            enunciado="Liste só o login dos usuários cujo shell é /bin/bash em passwd.txt.",
            esperado="grep '/bin/bash$' passwd.txt | cut -d: -f1"),
    Comando(id="s01.cmd.uid0", titulo="Quem é root de verdade",
            enunciado="Quais usuários de passwd.txt têm UID 0? (só os logins)",
            esperado="awk -F: '$3==0{print $1}' passwd.txt",
            explicacao="Só o root deveria ter UID 0. Um 'suporte' com UID 0 é backdoor clássico de persistência."),
    Comando(id="s01.cmd.awk", titulo="awk: somar coluna",
            enunciado="Some a coluna 'valor' de vendas.csv (ignorando o cabeçalho). Imprima só o número.",
            esperado="awk -F, 'NR>1{s+=$3} END{print s}' vendas.csv"),
    Comando(id="s01.cmd.regiao", titulo="awk: total por região",
            enunciado="Mostre o total de vendas por região, no formato 'regiao total' (qualquer ordem).",
            esperado="awk -F, 'NR>1{s[$2]+=$3} END{for(r in s) print r, s[r]}' vendas.csv", ordem=False,
            dica="Use um array no awk: s[$2]+=$3, e no END percorra com for (r in s)."),
    Comando(id="s01.cmd.sed", titulo="sed sem alterar o arquivo",
            enunciado="Mostre as 3 primeiras linhas de auth.log trocando 'srv' por 'web01', SEM alterar o arquivo.",
            esperado="sed 's/srv/web01/g' auth.log | head -n 3", proibir=["sed -i"]),
    Comando(id="s01.cmd.sedi", titulo="sed alterando o arquivo",
            enunciado="Agora altere o próprio arquivo: em frutas.txt, troque 'banana' por 'BANANA' (com sed).",
            exigir=["sed"],
            verificar=[("não sobrou 'banana' minúsculo", '! grep -q "banana" frutas.txt'),
                       ("BANANA aparece 3 vezes", '[ "$(grep -c BANANA frutas.txt)" -eq 3 ]')],
            resposta="sed -i 's/banana/BANANA/g' frutas.txt"),
    Comando(id="s01.cmd.zcat", titulo="Log compactado",
            enunciado="Quantas linhas com 'Failed' existem em antigo.log.gz? Sem descompactar no disco.",
            esperado="zcat antigo.log.gz | grep -c Failed", proibir=["gunzip", "gzip -d"],
            explicacao="O logrotate compacta logs antigos. zcat, zgrep e zless leem sem descompactar."),
    Comando(id="s01.cmd.dup", titulo="Frutas repetidas",
            enunciado="Quais frutas aparecem mais de uma vez em frutas.txt? (só os nomes, ordem alfabética)",
            esperado="sort frutas.txt | uniq -d",
            explicacao="O uniq só compara linhas VIZINHAS, por isso sempre vem depois de um sort."),
    Comando(id="s01.cmd.wc", titulo="Quantas diferentes",
            enunciado="Quantas frutas DIFERENTES existem em frutas.txt? (só o número)",
            esperado="sort -u frutas.txt | wc -l",
            explicacao="Repare: 'Banana' e 'banana' contam como diferentes. Para ignorar maiúsculas: sort -fu."),
    Comando(id="s01.cmd.tr", titulo="tr: maiúsculas",
            enunciado="Mostre frutas.txt inteiro em MAIÚSCULAS.", esperado="tr 'a-z' 'A-Z' < frutas.txt"),
    Comando(id="s01.cmd.web404", titulo="Apache: quantos 404",
            enunciado="No access.log, quantas requisições retornaram status 404? (só o número)",
            esperado="awk '$9==404' access.log | wc -l",
            dica="No formato do Apache, o status é o 9º campo separado por espaço."),
    Comando(id="s01.cmd.webtop", titulo="Apache: quem mais acessou",
            enunciado="Qual IP fez mais requisições no access.log? (só o IP)",
            esperado="awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -1 | awk '{print $2}'"),
    Comando(id="s01.cmd.webscan", titulo="Apache: o que o scanner procurou",
            enunciado="Liste (sem repetição, ordem alfabética) os caminhos acessados pelo IP 45.33.32.156.",
            esperado="grep '^45.33.32.156 ' access.log | awk '{print $7}' | sort -u",
            explicacao="wp-login, .env, .git/config, backup.zip: é um scanner automático atrás de arquivos esquecidos e painéis."),

    # ── segurança ──
    Escolha(id="s01.sec.ioa", titulo="IoC × IoA (sua questão 18)", prova="",
            enunciado="Quais destes são IoAs (indicadores de ATAQUE, ou seja, comportamento)?",
            opcoes=["Hash SHA-256 de um executável malicioso",
                    "winword.exe abrindo powershell.exe -enc ...",
                    "IP de um servidor de comando e controle conhecido",
                    "Usuário loga às 3h e em seguida cria uma conta de administrador",
                    "Domínio de phishing conhecido"],
            correta="bd",
            explicacao="""
            IoC (comprometimento) = artefato/evidência: hash, IP, domínio. Fácil de trocar pelo atacante.
            IoA (ataque) = comportamento/intenção: sequência de ações. Mais difícil de o atacante esconder.
            """),
    Escolha(id="s01.sec.alerta", titulo="Evento, alerta ou incidente", prova="",
            enunciado="300 falhas de SSH seguidas de 1 login com sucesso, do mesmo IP, é:",
            opcoes=["Só um evento, pode ignorar", "Um alerta que precisa de triagem e pode virar incidente",
                    "Certamente um falso positivo", "Já é um incidente confirmado, sem precisar validar"],
            correta="b"),
    Escolha(id="s01.sec.fn", titulo="Falso negativo", prova="",
            enunciado="O SIEM NÃO alertou um ataque que realmente aconteceu. Isso é:",
            opcoes=["Falso positivo", "Falso negativo", "Verdadeiro negativo", "Verdadeiro positivo"],
            correta="b",
            explicacao="Falso negativo é o pior caso: o ataque passou sem ninguém ver. Falso positivo é alerta sem ataque real."),
    Tarefa(id="s01.vm.brute", titulo="Gere um brute-force nas VMs", host="rhel+ubuntu",
           enunciado="""
           Gere um ataque real para ver nos logs. Em cada VM, crie um usuário de teste com senha fraca:
             sudo useradd -m teste && echo 'teste:Senha123' | sudo chpasswd
           No Fedora, instale o sshpass (sudo dnf install sshpass) e rode, para cada VM:
             for i in $(seq 40); do sshpass -p errada$i ssh -o PubkeyAuthentication=no teste@rhel true; done
             sshpass -p Senha123 ssh -o PubkeyAuthentication=no teste@rhel true
           (troque rhel por ubuntu para a outra). Depois, olhe nas VMs onde isso foi parar:
           RHEL: journalctl ou /var/log/secure · Ubuntu: /var/log/auth.log. Anote em DIFERENCAS.md.
           """,
           checks=[("≥ 30 'Failed password' nos últimos 7 dias",
                    '[ "$(journalctl --since -7d | grep -c "Failed password")" -ge 30 ]'),
                   ("houve login por senha aceito", 'journalctl --since -7d | grep -q "Accepted password"')],
           dica="Se o login por senha for recusado, verifique 'PasswordAuthentication yes' no sshd_config da VM."),
    Tarefa(id="s01.relatorio", titulo="Desafio de sábado: relatório de brute-force",
           enunciado="""
           Sem IA e sem internet, escreva ~/linux-lab/relatorios/s01-bruteforce.md sobre o auth.log dos exercícios
           (ou sobre o ataque que você gerou nas VMs), contendo:
             · top 5 IPs por falhas (com o one-liner que você usou)
             · usuários tentados
             · primeira e última tentativa de cada IP
             · se houve sucesso, de qual IP e com qual usuário, e o que ele fez depois
             · recomendação de contenção
           """,
           checks=[("relatório existe", "test -f ~/linux-lab/relatorios/s01-bruteforce.md"),
                   ("tem conteúdo (mais de 150 palavras)",
                    '[ "$(wc -w < ~/linux-lab/relatorios/s01-bruteforce.md)" -gt 150 ]'),
                   ("cita o IP que teve sucesso", "grep -q 198.51.100.23 ~/linux-lab/relatorios/s01-bruteforce.md "
                    "|| grep -qi 'accepted' ~/linux-lab/relatorios/s01-bruteforce.md")]),

    # ── redes: subnetting ──
    Quiz(id="s01.sub.1", titulo="Máscara /27 (sua questão 11)", prova="102",
         enunciado="Qual é a máscara de uma /27 em decimal?", respostas=["255.255.255.224"]),
    Quiz(id="s01.sub.2", titulo="Broadcast de 192.168.10.64/27", prova="102",
         enunciado="Qual é o broadcast de 192.168.10.64/27?", respostas=["192.168.10.95"],
         explicacao="/27 → blocos de 32 endereços: .64 a .95. Rede .64, broadcast .95, hosts .65 a .94 (30 hosts)."),
    Quiz(id="s01.sub.3", titulo="Hosts em /27", prova="102",
         enunciado="Quantos hosts válidos tem uma /27?", respostas=["30"],
         explicacao="2^(32−27) − 2 = 32 − 2 = 30 (tira o endereço de rede e o de broadcast)."),
    Quiz(id="s01.sub.4", titulo="Dividir uma /24", prova="102",
         enunciado="Você precisa dividir 192.168.50.0/24 em 6 sub-redes de mesmo tamanho. Qual o prefixo de cada uma? (ex.: /25)",
         respostas=["/27", "27"],
         explicacao="6 sub-redes exigem 3 bits (2³ = 8 ≥ 6): 24 + 3 = /27, com 30 hosts cada (sobram 2 sub-redes)."),
    Quiz(id="s01.sub.5", titulo="Faixas privadas", prova="102",
         enunciado="Qual destas é a faixa privada classe B da RFC 1918? (CIDR)",
         respostas=["172.16.0.0/12"],
         explicacao="Privadas: 10.0.0.0/8, 172.16.0.0/12 (172.16 a 172.31) e 192.168.0.0/16."),
    Subnet(id="s01.subnet", titulo="Bateria de subnetting /24 a /30",
           enunciado="Bateria de subnetting. Faça de cabeça ou no papel, sem calculadora.",
           n=10, prefixos=(24, 30), meta=8),
]
