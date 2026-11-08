from motor import Comando, Escolha, Marco, Quiz, Tarefa, cmd, rx

TITULO = "Permissões, usuários e escalada + TCP/UDP"
DATAS = "23–29/11"
OBJETIVO = """
Dominar o modelo de permissões e entender como ele é abusado para virar root.
Fecha as questões 2, 7, 10 e 12 do diagnóstico.
Teoria: 104.5, 104.6, 104.7, 107.1 e 110.1 (learning.lpi.org).
"""

TCPDUMP = """
10:00:01.000 IP 192.168.122.50.41000 > 192.168.122.10.22: Flags [S], seq 100
10:00:01.001 IP 192.168.122.10.22 > 192.168.122.50.41000: Flags [S.], seq 500, ack 101
10:00:01.001 IP 192.168.122.50.41000 > 192.168.122.10.22: Flags [R], seq 101
10:00:01.002 IP 192.168.122.50.41000 > 192.168.122.10.80: Flags [S], seq 100
10:00:01.002 IP 192.168.122.10.80 > 192.168.122.50.41000: Flags [R.], seq 0, ack 101
10:00:01.003 IP 192.168.122.50.41000 > 192.168.122.10.443: Flags [S], seq 100
10:00:02.003 IP 192.168.122.50.41001 > 192.168.122.10.443: Flags [S], seq 100
"""

EXERCICIOS = [
    # ── permissões: leitura ──
    Quiz(id="s02.oct.1", titulo="Octal (sua questão 2)", exato=True,
         enunciado="Qual o octal de  -rwsr-xr--  ?", respostas=["4754"],
         explicacao="SUID=4 · dono rwx=7 · grupo r-x=5 · outros r--=4 → 4754."),
    Quiz(id="s02.oct.2", titulo="Octal com SGID", exato=True,
         enunciado="Qual o octal de  drwxrwsr-x  ?", respostas=["2775"]),
    Quiz(id="s02.oct.3", titulo="Octal do /tmp", exato=True,
         enunciado="Qual o octal de  drwxrwxrwt  (o /tmp)?", respostas=["1777"]),
    Quiz(id="s02.oct.4", titulo="Octal simples", exato=True,
         enunciado="Qual o octal de  -rw-r-----  ?", respostas=["640", "0640"]),
    Quiz(id="s02.oct.5", titulo="S maiúsculo", exato=True,
         enunciado="Qual o octal de  -rwSr--r--  ?", respostas=["4644"],
         explicacao="S maiúsculo = SUID ligado, mas SEM o x por baixo (rw-). Geralmente é erro de configuração."),
    Quiz(id="s02.umask.1", titulo="umask 027: arquivo",
         enunciado="Com umask 027, qual a permissão (octal) de um ARQUIVO novo?", respostas=["640", "0640"],
         explicacao="Arquivos partem de 666 e diretórios de 777. Tire os bits do umask: 666−027 → 640; 777−027 → 750."),
    Quiz(id="s02.umask.2", titulo="umask 027: diretório",
         enunciado="E de um DIRETÓRIO novo, com umask 027?", respostas=["750", "0750"]),
    Quiz(id="s02.umask.3", titulo="umask 077",
         enunciado="Com umask 077, qual a permissão de um arquivo novo?", respostas=["600", "0600"]),
    Escolha(id="s02.esp.1", titulo="SUID",
            enunciado="O que o SUID faz num executável?",
            opcoes=["Só o dono pode executá-lo", "Ele roda com os privilégios do DONO do arquivo, não de quem executa",
                    "Ele roda com os privilégios do grupo", "Impede que o arquivo seja apagado"],
            correta="b",
            explicacao="É assim que o /usr/bin/passwd (dono root) consegue gravar no /etc/shadow quando você troca sua senha."),
    Escolha(id="s02.esp.2", titulo="SGID em diretório",
            enunciado="O que o SGID faz num DIRETÓRIO?",
            opcoes=["Arquivos criados dentro herdam o GRUPO do diretório", "Só o grupo pode entrar",
                    "Arquivos não podem ser apagados", "Arquivos criados ficam executáveis"],
            correta="a"),
    Escolha(id="s02.esp.3", titulo="Sticky bit",
            enunciado="O que o sticky bit faz num diretório como o /tmp?",
            opcoes=["Deixa os arquivos só leitura", "Só o dono do arquivo (ou root) pode apagar ou renomear o arquivo",
                    "Apaga os arquivos no reboot", "Impede a criação de diretórios"],
            correta="b"),

    # ── permissões: prática ──
    Comando(id="s02.cmd.640", titulo="chmod numérico",
            enunciado="Deixe relatorio.txt como rw-r----- usando notação NUMÉRICA.",
            preparar="echo dados > relatorio.txt; chmod 777 relatorio.txt", exigir=["chmod"],
            verificar=[("permissão 640", '[ "$(stat -c %a relatorio.txt)" = 640 ]')],
            resposta="chmod 640 relatorio.txt"),
    Comando(id="s02.cmd.simb", titulo="chmod simbólico",
            enunciado="publico.txt está 666. Usando notação SIMBÓLICA, tire a escrita do grupo e dos outros (sem mexer no resto).",
            preparar="echo x > publico.txt; chmod 666 publico.txt", exigir=["chmod"], proibir=["644"],
            verificar=[("permissão 644", '[ "$(stat -c %a publico.txt)" = 644 ]')],
            resposta="chmod go-w publico.txt"),
    Comando(id="s02.cmd.suid", titulo="Ligar SUID",
            enunciado="Dê SUID ao arquivo 'programa' (que está 755), sem mudar o resto.",
            preparar="printf '#!/bin/sh\\necho oi\\n' > programa; chmod 755 programa",
            verificar=[("permissão 4755", '[ "$(stat -c %a programa)" = 4755 ]')],
            resposta="chmod u+s programa"),
    Comando(id="s02.cmd.sticky", titulo="Diretório estilo /tmp",
            enunciado="Crie o diretório compartilhado/ com permissão rwxrwxrwt.",
            verificar=[("é diretório com 1777", '[ -d compartilhado ] && [ "$(stat -c %a compartilhado)" = 1777 ]')],
            resposta="mkdir compartilhado && chmod 1777 compartilhado"),
    Comando(id="s02.cmd.sgid", titulo="Diretório de equipe",
            enunciado="Crie projeto/ com rwxrwx--- e SGID (arquivos novos herdam o grupo).",
            verificar=[("é diretório com 2770", '[ -d projeto ] && [ "$(stat -c %a projeto)" = 2770 ]')],
            resposta="mkdir projeto && chmod 2770 projeto"),
    Comando(id="s02.cmd.lns", titulo="Link simbólico",
            enunciado="Crie o link SIMBÓLICO 'atalho' apontando para alvo.txt.",
            preparar="echo conteudo > alvo.txt",
            verificar=[("atalho é symlink para alvo.txt", '[ -L atalho ] && [ "$(readlink atalho)" = alvo.txt ]')],
            resposta="ln -s alvo.txt atalho"),
    Comando(id="s02.cmd.ln", titulo="Hard link",
            enunciado="Crie o hard link 'copia_dura' para alvo.txt.",
            preparar="echo conteudo > alvo.txt",
            verificar=[("mesmo inode", '[ "$(stat -c %i alvo.txt)" = "$(stat -c %i copia_dura)" ]'),
                       ("contador de links = 2", '[ "$(stat -c %h alvo.txt)" = 2 ]')],
            resposta="ln alvo.txt copia_dura"),
    Escolha(id="s02.links", titulo="Apagando o original",
            enunciado="Você criou 'atalho' (simbólico) e 'copia_dura' (hard) para alvo.txt. Aí apaga alvo.txt. O que acontece?",
            opcoes=["atalho quebra; copia_dura continua com o conteúdo", "Os dois quebram",
                    "Os dois continuam funcionando", "copia_dura quebra; atalho continua"],
            correta="a",
            explicacao="O hard link é outro nome para o mesmo inode: os dados só somem quando o último nome é apagado. O simbólico aponta para um CAMINHO."),

    # ── find e FHS ──
    Comando(id="s02.find.conf", titulo="find por nome",
            enunciado="Liste todos os arquivos regulares em arvore/ terminados em .conf.",
            esperado="find arvore -type f -name '*.conf'", ordem=False),
    Comando(id="s02.find.size", titulo="find por tamanho",
            enunciado="Liste os arquivos em arvore/ maiores que 1 MiB.",
            esperado="find arvore -type f -size +1M", ordem=False),
    Comando(id="s02.find.vazio", titulo="find vazios",
            enunciado="Liste os arquivos VAZIOS em arvore/.",
            esperado="find arvore -type f -empty", ordem=False),
    Comando(id="s02.find.mtime", titulo="find por data",
            enunciado="Liste os arquivos em arvore/ modificados há MAIS de 30 dias.",
            esperado="find arvore -type f -mtime +30", ordem=False),
    Comando(id="s02.find.suid", titulo="Caçar SUID",
            enunciado="Liste os arquivos com SUID em arvore/.",
            esperado="find arvore -perm -4000", ordem=False,
            explicacao="Num servidor real: find / -perm -4000 2>/dev/null. Todo SUID fora do padrão é suspeito."),
    Comando(id="s02.find.oculto", titulo="Arquivos ocultos",
            enunciado="Liste os arquivos ocultos (nome começando com ponto) em arvore/.",
            esperado="find arvore -type f -name '.*'", ordem=False),
    Comando(id="s02.find.exec", titulo="find com -exec",
            enunciado="Para cada .log em arvore/, mostre o tamanho em bytes e o nome usando wc -c, um arquivo por vez (-exec).",
            esperado="find arvore -name '*.log' -exec wc -c {} \\;", ordem=False),
    Quiz(id="s02.fhs.1", titulo="FHS: configuração",
         enunciado="Em que diretório ficam os arquivos de configuração do sistema?", respostas=["/etc", "/etc/"]),
    Quiz(id="s02.fhs.2", titulo="FHS: logs",
         enunciado="E os logs?", respostas=["/var/log", "/var/log/"]),
    Quiz(id="s02.fhs.3", titulo="FHS: serviços",
         enunciado="Diretório para dados servidos pelo sistema (ex.: arquivos de um site ou FTP)?",
         respostas=["/srv", "/srv/"]),
    Quiz(id="s02.fhs.4", titulo="FHS: terceiros",
         enunciado="Diretório para software de terceiros, instalado fora do gerenciador de pacotes?",
         respostas=["/opt", "/opt/"]),
    Escolha(id="s02.fhs.5", titulo="which, whereis, locate",
            enunciado="Qual comando procura numa BASE DE DADOS (atualizada pelo updatedb), e não no disco na hora?",
            opcoes=["which", "whereis", "locate", "find"], correta="c"),

    # ── usuários e sudo ──
    Quiz(id="s02.user.1", titulo="/etc/passwd: shell", prova="102",
         enunciado="Em /etc/passwd, qual o número do campo que guarda o shell?", respostas=["7"]),
    Quiz(id="s02.user.2", titulo="/etc/passwd: UID", prova="102",
         enunciado="E qual o número do campo do UID?", respostas=["3"]),
    Escolha(id="s02.user.3", titulo="O 'x' no passwd", prova="102",
            enunciado="O que significa o 'x' no 2º campo do /etc/passwd?",
            opcoes=["Conta desativada", "O hash da senha está em /etc/shadow", "Usuário sem senha", "Usuário do sistema"],
            correta="b"),
    Escolha(id="s02.user.4", titulo="Algoritmo do hash", prova="102",
            enunciado="No /etc/shadow, um hash começando com $6$ usa qual algoritmo? E $y$?",
            opcoes=["$6$ = MD5 e $y$ = SHA-256", "$6$ = SHA-512 e $y$ = yescrypt",
                    "$6$ = bcrypt e $y$ = SHA-512", "$6$ = DES e $y$ = Argon2"],
            correta="b"),
    Quiz(id="s02.user.5", titulo="Bloquear usuário (sua questão 7)", prova="102",
         enunciado="Comando para BLOQUEAR a senha do usuário joao sem apagar a conta:",
         respostas=[cmd(r"usermod -L joao"), cmd(r"passwd -l joao")], resposta="usermod -L joao  (ou passwd -l joao)",
         explicacao="Atenção: `usermod -l` (L minúsculo) RENOMEIA o usuário. O -L maiúsculo é que bloqueia (Lock)."),
    Quiz(id="s02.user.6", titulo="Expirar conta", prova="102",
         enunciado="Comando para fazer a conta do joao expirar (ficar inutilizável) imediatamente, usando chage:",
         respostas=[cmd(r"chage -E ?0 joao")], resposta="chage -E 0 joao"),
    Quiz(id="s02.user.7", titulo="Modelo da home", prova="102",
         enunciado="Qual diretório tem os arquivos copiados para a home de cada usuário novo?",
         respostas=["/etc/skel", "/etc/skel/"]),
    Quiz(id="s02.user.8", titulo="Editar o sudoers", prova="102",
         enunciado="Qual comando você deve usar para editar o /etc/sudoers com segurança?",
         respostas=[cmd("visudo")], resposta="visudo",
         explicacao="O visudo valida a sintaxe antes de salvar. Um sudoers quebrado pode te trancar fora do root."),
    Escolha(id="s02.user.9", titulo="Grupo de admins", prova="102",
            enunciado="Qual grupo dá direito a sudo por padrão no RHEL e no Ubuntu, respectivamente?",
            opcoes=["admin e root", "wheel e sudo", "sudo e wheel", "root e admin"], correta="b"),

    # ── escalada de privilégio ──
    Quiz(id="s02.priv.1", titulo="Virando root com find SUID", prova="",
         enunciado="O /usr/bin/find está com SUID de root. Qual comando com find abre um shell de root?",
         respostas=[lambda r: "find" in r and "-exec" in r and re_sh_p(r)],
         resposta="find . -exec /bin/sh -p \\; -quit",
         dica="O find executa comandos com -exec. E o sh/bash só mantém o privilégio do SUID com a opção -p.",
         explicacao="Esse tipo de truque está catalogado no GTFOBins (gtfobins.github.io). Todo analista deve conhecer."),
    Tarefa(id="s02.vm.privesc", titulo="Cenário: 3 falhas de escalada plantadas", host="rhel",
           enunciado="""
           Vou plantar 3 configurações que permitem a um usuário comum virar root na rhel
           (e criar o usuário 'treino' para você testar). Sua missão:
             1. ENCONTRAR as 3 (dica: SUIDs fora do padrão e regras de sudo)
             2. TESTAR a escalada como 'treino' (sudo -iu treino) para entender o risco
             3. CORRIGIR as 3 e anotar no relatório como detectar e prevenir
           """,
           quebrar="""
           chmod u+s /usr/bin/find
           id treino >/dev/null 2>&1 || useradd -m treino
           echo 'treino ALL=(ALL) NOPASSWD: /usr/bin/vim' > /etc/sudoers.d/90-treino-vim
           chmod 440 /etc/sudoers.d/90-treino-vim
           cp /usr/bin/bash /usr/local/bin/ferramenta && chmod 4755 /usr/local/bin/ferramenta
           """,
           checks=[("find sem SUID", "[ ! -u /usr/bin/find ]"),
                   ("regra de sudo do vim removida",
                    "! grep -rqs 'NOPASSWD: /usr/bin/vim' /etc/sudoers /etc/sudoers.d"),
                   ("SUID da ferramenta removido", "[ ! -u /usr/local/bin/ferramenta ]")],
           dica="find / -perm -4000 2>/dev/null e compare com o que é normal. sudo -l -U treino mostra as regras dele."),
    Tarefa(id="s02.vm.empresa", titulo="Desafio de sábado: empresa fictícia", host="rhel+ubuntu",
           enunciado="""
           Nas DUAS VMs, sem consultar a internet:
             · grupos 'financeiro' e 'ti'
             · ana e bruno no financeiro; carlos e daniela no ti
             · usuário 'estagiario' com conta que EXPIRA (data no futuro, ~30 dias)
             · /srv/financeiro: dono root, grupo financeiro, só o grupo lê/escreve,
               arquivos novos herdam o grupo (SGID) e ninguém apaga arquivo dos outros (sticky)
             · o grupo ti pode reiniciar o serviço SSH via sudo, e SÓ isso
           """,
           checks=[("grupos financeiro e ti", "getent group financeiro >/dev/null && getent group ti >/dev/null"),
                   ("ana e bruno no financeiro",
                    "id -nG ana | grep -qw financeiro && id -nG bruno | grep -qw financeiro"),
                   ("carlos e daniela no ti", "id -nG carlos | grep -qw ti && id -nG daniela | grep -qw ti"),
                   ("estagiario com data de expiração",
                    "chage -l estagiario | grep -i 'account expires' | grep -viq never"),
                   ("/srv/financeiro 3770 com grupo financeiro",
                    '[ "$(stat -c %a:%G /srv/financeiro)" = "3770:financeiro" ]'),
                   ("carlos pode reiniciar o SSH via sudo",
                    "sudo -l -U carlos | grep -Eq 'systemctl restart sshd?(\\.service)?'"),
                   ("carlos NÃO tem sudo total",
                    "! sudo -l -U carlos | grep -Eq '\\) (NOPASSWD: )?ALL$' && ! id -nG carlos | grep -Eqw 'wheel|sudo'")],
           dica="Regra de sudo por grupo: %ti ALL=(root) /usr/bin/systemctl restart sshd  (no Ubuntu o serviço é ssh)."),
    Tarefa(id="s02.vm.acl", titulo="Extra: ACL para o estagiário", host="rhel+ubuntu",
           enunciado="Crie /srv/financeiro/relatorio.txt e dê ao estagiario permissão de LEITURA só nele, via ACL.",
           checks=[("ACL user:estagiario:r--",
                    "getfacl -p /srv/financeiro/relatorio.txt 2>/dev/null | grep -q '^user:estagiario:r--'")],
           dica="setfacl -m u:estagiario:r arquivo · getfacl arquivo. Ele também precisa de x no diretório (ACL no /srv/financeiro)."),

    # ── redes: TCP/UDP e scans ──
    Quiz(id="s02.porta.1", titulo="Porta 22", prova="102", enunciado="Qual serviço usa a porta 22/tcp?", respostas=["ssh"]),
    Quiz(id="s02.porta.2", titulo="Porta 53", prova="102", enunciado="E a porta 53?", respostas=["dns"]),
    Quiz(id="s02.porta.3", titulo="Porta 445", prova="102", enunciado="E a 445/tcp?",
         respostas=["smb", "cifs", "smb/cifs", "samba"]),
    Quiz(id="s02.porta.4", titulo="Porta 389", prova="102", enunciado="E a 389?", respostas=["ldap"]),
    Quiz(id="s02.porta.5", titulo="Porta 88", prova="102", enunciado="E a 88? (pense em Active Directory)",
         respostas=["kerberos"]),
    Quiz(id="s02.porta.6", titulo="Porta 3389", prova="102", enunciado="E a 3389?", respostas=["rdp"]),
    Quiz(id="s02.porta.7", titulo="Porta 25", prova="102", enunciado="E a 25?", respostas=["smtp"]),
    Quiz(id="s02.porta.8", titulo="Onde estão as portas", prova="102",
         enunciado="Qual arquivo do Linux lista os nomes de serviços e suas portas?", respostas=["/etc/services"]),
    Escolha(id="s02.tcp.1", titulo="TCP × UDP", prova="102",
            enunciado="Quais afirmações são verdadeiras?",
            opcoes=["TCP estabelece conexão (handshake) e garante entrega e ordem",
                    "UDP não tem handshake nem garantia de entrega",
                    "DNS nunca usa TCP", "HTTP/1.1 roda sobre UDP"],
            correta="ab",
            explicacao="O DNS usa UDP/53 nas consultas comuns e TCP/53 em respostas grandes e transferência de zona."),
    Escolha(id="s02.scan.1", titulo="SYN scan (sua questão 12)", prova="",
            enunciado="No SYN scan (nmap -sS), depois de receber SYN-ACK de uma porta aberta, o nmap:",
            opcoes=["Responde ACK e completa a conexão", "Responde RST e nunca completa a conexão",
                    "Não responde nada", "Manda FIN"],
            correta="b",
            explicacao="Por não completar o handshake, muitas aplicações nem registram a conexão. Por isso é 'stealth'. Já o -sT completa."),
    Quiz(id="s02.dump.1", titulo="Lendo tcpdump: quem escaneia", prova="",
         enunciado="Leia esta captura:\n" + TCPDUMP + "\nQual IP é o scanner?", respostas=["192.168.122.50"]),
    Quiz(id="s02.dump.2", titulo="Lendo tcpdump: porta aberta", prova="",
         enunciado="Na mesma captura:\n" + TCPDUMP + "\nQual porta está ABERTA?", respostas=["22"],
         explicacao="[S.] é SYN-ACK: a porta respondeu que aceita conexão. Depois o scanner manda [R] (RST)."),
    Escolha(id="s02.dump.3", titulo="Lendo tcpdump: 80 e 443", prova="",
            enunciado="Ainda na captura:\n" + TCPDUMP + "\nComo estão as portas 80 e 443?",
            opcoes=["80 fechada (respondeu RST) e 443 filtrada (sem resposta, o scanner repetiu o SYN)",
                    "As duas abertas", "80 filtrada e 443 fechada", "As duas fechadas"],
            correta="a"),
    Marco(id="s02.nmap", titulo="Na prática: nmap do kali com tcpdump no alvo",
          enunciado="""
          Do kali, rode nmap -sT e depois nmap -sS contra a rhel, com `sudo tcpdump -nn -i any host IP_DO_KALI`
          rodando na rhel. Compare as capturas e anote a diferença em relatorios/s02-scans.md.
          """),
]


def re_sh_p(r: str) -> bool:
    import re
    return re.search(r"\b(ba)?sh -p\b", r) is not None
