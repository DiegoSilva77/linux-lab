import re

from motor import Comando, Escolha, Marco, Quiz, Tarefa, cmd, rx

TITULO = "Segurança, SSH, GPG, logs + Mini-SOC final"
DATAS = "18–24/01"
OBJETIVO = """
Endurecer os servidores, centralizar logs e fechar o projeto principal do portfólio:
atacar, detectar, investigar e reportar. Teoria: 110.1, 110.2, 110.3, 108.
"""

GERA_CHAVE = "gpg --batch --passphrase '' --quick-gen-key 'Treino <treino@lab>' default default never >/dev/null 2>&1"

EXERCICIOS = [
    # ── segurança do host ──
    Escolha(id="s10.who", titulo="Quem está logado",
            enunciado="Qual comando mostra quem está logado E o que cada um está fazendo agora?",
            opcoes=["who", "w", "last", "id"], correta="b"),
    Escolha(id="s10.lastb", titulo="Logins que falharam",
            enunciado="Qual comando lista as tentativas de login que FALHARAM (lê /var/log/btmp)?",
            opcoes=["last", "lastb", "lastlog", "faillog"], correta="b"),
    Quiz(id="s10.lsof", titulo="Quem usa a porta",
         enunciado="Com lsof, como ver o processo que usa a porta 22?",
         respostas=[cmd(r"lsof -i ?:22( .*)?"), cmd(r"lsof -i tcp:22")], resposta="lsof -i :22"),
    Escolha(id="s10.ulimit", titulo="ulimit",
            enunciado="O que `ulimit -n` mostra?",
            opcoes=["Número de usuários", "Número máximo de arquivos abertos por processo",
                    "Número de processos", "Tamanho do disco"], correta="b"),
    Escolha(id="s10.nologin", titulo="/etc/nologin",
            enunciado="O que acontece se o arquivo /etc/nologin existir?",
            opcoes=["Ninguém mais faz login", "Usuários comuns não conseguem logar (o root consegue) e veem o conteúdo do arquivo",
                    "O root não consegue logar", "Nada"], correta="b"),
    Comando(id="s10.cmd.uid0", titulo="Auditoria rápida: UID 0",
            enunciado="Revisão de auditoria: em passwd.txt, mostre quem tem UID 0 e NÃO se chama root.",
            esperado="awk -F: '$3==0 && $1!=\"root\" {print $1}' passwd.txt"),
    Comando(id="s10.cmd.nologin", titulo="Auditoria: contas de serviço com shell",
            enunciado="Em passwd.txt, liste os logins com UID < 1000 que têm um shell de login (não terminam em nologin nem false).",
            esperado="awk -F: '$3<1000 && $7!~/(nologin|false)$/ {print $1}' passwd.txt"),

    # ── SSH ──
    Quiz(id="s10.ssh.1", titulo="Proibir root no SSH",
         enunciado="Qual linha do sshd_config impede login direto do root?",
         respostas=[rx(r"PermitRootLogin no", i=True)], resposta="PermitRootLogin no"),
    Quiz(id="s10.ssh.2", titulo="Só chave",
         enunciado="E qual linha desliga o login por senha?",
         respostas=[rx(r"PasswordAuthentication no", i=True)], resposta="PasswordAuthentication no"),
    Quiz(id="s10.ssh.3", titulo="Testar a config do sshd",
         enunciado="Qual comando testa a sintaxe do sshd_config ANTES de reiniciar (para não se trancar fora)?",
         respostas=[cmd(r"sshd -t"), cmd(r"/usr/sbin/sshd -t")], resposta="sshd -t"),
    Escolha(id="s10.ssh.4", titulo="Túnel -L",
            enunciado="O que faz `ssh -L 8080:10.10.20.10:80 ubuntu`?",
            opcoes=["Abre a porta 8080 NA SUA máquina; o que chegar nela vai, pelo túnel, até 10.10.20.10:80",
                    "Abre a porta 8080 na ubuntu", "Cria uma VPN completa", "Copia arquivos"], correta="a",
            explicacao="-L = local forward. -R = remote forward (abre a porta no servidor), muito usado por atacantes para sair da rede."),
    Comando(id="s10.cmd.keygen", titulo="Gerar chave SSH",
            enunciado="Gere um par de chaves ed25519 SEM senha nos arquivos ./chave_lab e ./chave_lab.pub.",
            verificar=[("os dois arquivos existem", "[ -f chave_lab ] && [ -f chave_lab.pub ]"),
                       ("é ed25519", "grep -q '^ssh-ed25519' chave_lab.pub"),
                       ("privada com permissão 600", '[ "$(stat -c %a chave_lab)" = 600 ]')],
            resposta="ssh-keygen -t ed25519 -N '' -f ./chave_lab -q"),
    Comando(id="s10.cmd.fp", titulo="Fingerprint",
            enunciado="Mostre o fingerprint (SHA256) da chave pública chave_lab.pub.",
            preparar="ssh-keygen -t ed25519 -N '' -f ./chave_lab -q",
            esperado="ssh-keygen -lf chave_lab.pub",
            explicacao="É esse fingerprint que o SSH mostra no primeiro acesso. Conferi-lo evita ataque man-in-the-middle."),
    Tarefa(id="s10.vm.ssh", titulo="Hardening do SSH", host="rhel",
           enunciado="""
           Na rhel: só login por chave, sem root, no máximo 3 tentativas e só para o grupo 'sshusers'
           (coloque seu usuário nele ANTES de reiniciar o sshd). Teste com sshd -t antes.
           Repare: depois disso o brute-force da semana 1 deixa de funcionar.
           """,
           checks=[("root não loga", "sshd -T | grep -qx 'permitrootlogin no'"),
                   ("sem senha", "sshd -T | grep -qx 'passwordauthentication no'"),
                   ("MaxAuthTries ≤ 3", '[ "$(sshd -T | awk \'$1=="maxauthtries"{print $2}\')" -le 3 ]'),
                   ("AllowGroups definido", "sshd -T | grep -q '^allowgroups '")]),
    Tarefa(id="s10.vm.f2b", titulo="fail2ban", host="ubuntu",
           enunciado="Na ubuntu, instale o fail2ban e ative a jail do sshd. Teste errando a senha várias vezes a partir do kali.",
           checks=[("jail sshd ativa", "fail2ban-client status sshd >/dev/null 2>&1")]),

    # ── GPG ──
    Comando(id="s10.gpg.1", titulo="GPG: gerar chave",
            enunciado="Gere uma chave GPG para 'Treino <treino@lab>', sem senha, em modo não interativo (batch).",
            verificar=[("chave existe", "gpg --list-keys treino@lab >/dev/null 2>&1")],
            resposta="gpg --batch --passphrase '' --quick-gen-key 'Treino <treino@lab>' default default never",
            dica="O modo interativo vai travar aqui. Use --batch --passphrase '' --quick-gen-key ..."),
    Comando(id="s10.gpg.2", titulo="GPG: cifrar",
            enunciado="Cifre segredo.txt para o destinatário treino@lab, gerando segredo.txt.gpg.",
            preparar=GERA_CHAVE + "; echo 'conteudo secreto' > segredo.txt",
            verificar=[("decifra para o conteúdo original",
                        "gpg --batch -q -d segredo.txt.gpg 2>/dev/null | grep -q 'conteudo secreto'")],
            resposta="gpg --batch --yes -e -r treino@lab segredo.txt"),
    Comando(id="s10.gpg.3", titulo="GPG: assinar",
            enunciado="Crie uma assinatura DESTACADA de documento.txt (arquivo documento.txt.sig).",
            preparar=GERA_CHAVE + "; echo 'contrato' > documento.txt",
            verificar=[("assinatura válida", "gpg --verify documento.txt.sig documento.txt >/dev/null 2>&1")],
            resposta="gpg --batch --yes --detach-sign documento.txt"),
    Escolha(id="s10.gpg.4", titulo="Cifrar × assinar",
            enunciado="Qual chave é usada para quê?",
            opcoes=["Cifra-se com a chave PÚBLICA do destinatário; assina-se com a sua chave PRIVADA",
                    "Cifra-se com a sua privada; assina-se com a pública do destinatário",
                    "As duas operações usam a pública", "As duas usam a privada"], correta="a"),

    # ── serviços essenciais ──
    Quiz(id="s10.time.1", titulo="chrony",
         enunciado="Comando para ver as fontes de tempo que o chrony está usando:",
         respostas=[cmd(r"chronyc sources( -v)?")], resposta="chronyc sources"),
    Escolha(id="s10.time.2", titulo="Por que o horário importa",
            enunciado="Por que o horário sincronizado (NTP) é crítico em segurança?",
            opcoes=["Para economizar energia", "Para correlacionar eventos de máquinas diferentes numa linha do tempo de incidente",
                    "Para o cron funcionar", "Não é crítico"], correta="b"),
    Quiz(id="s10.log.1", titulo="Escrever no log",
         enunciado="Comando para mandar a mensagem 'teste' para o syslog/journal:",
         respostas=[rx(r"logger( -\S+)* (teste|\"teste\"|'teste')")], resposta="logger teste"),
    Escolha(id="s10.log.2", titulo="journal persistente",
            enunciado="Como deixar o journal persistente entre reboots?",
            opcoes=["Storage=persistent em /etc/systemd/journald.conf (ou criar /var/log/journal)",
                    "Instalar o rsyslog", "Rodar journalctl --save", "Não é possível"], correta="a"),
    Escolha(id="s10.log.3", titulo="logrotate",
            enunciado="O que o logrotate faz?",
            opcoes=["Envia logs para outro servidor", "Rotaciona, compacta e apaga logs antigos conforme regras",
                    "Criptografa logs", "Lê o journal"], correta="b"),
    Escolha(id="s10.mta.1", titulo="Aliases de e-mail",
            enunciado="Você editou /etc/aliases para mandar o e-mail do root para o diego. O que falta?",
            opcoes=["Reiniciar a máquina", "Rodar newaliases", "Nada", "Rodar postfix reload"], correta="b"),
    Escolha(id="s10.mta.2", titulo="Encaminhar e-mail do usuário",
            enunciado="Qual arquivo na home do usuário encaminha os e-mails dele para outro endereço?",
            opcoes=["~/.forward", "~/.mailrc", "~/.aliases", "~/.redirect"], correta="a"),
    Escolha(id="s10.cups", titulo="Impressão (CUPS)",
            enunciado="Quais comandos são de impressão? (marque 3)",
            opcoes=["lpr", "lpq", "lprm", "lsusb"], correta="abc",
            explicacao="lpr imprime, lpq mostra a fila e lprm remove da fila. lpstat mostra o estado."),
    Tarefa(id="s10.vm.rsyslog", titulo="Logs centralizados (rhel → ubuntu)", host="rhel+ubuntu",
           enunciado="""
           Configure o rsyslog da ubuntu para RECEBER logs via TCP 514 (liberando no firewall dela)
           e o da rhel para ENVIAR tudo para 10.10.20.1:514. O verificador manda uma mensagem da rhel
           e procura na ubuntu.
           """,
           checks=[("ubuntu escutando TCP 514", "ss -Hltn 'sport = :514' | grep -q .", "ubuntu"),
                   ("rhel configurada para enviar",
                    "grep -rEqs '(@@|target=\"?10\\.10\\.20\\.1)' /etc/rsyslog.conf /etc/rsyslog.d/", "rhel"),
                   ("mensagem de teste enviada", "logger TREINO-REMOTO-$(date +%Y%m%d); sleep 3", "rhel"),
                   ("mensagem chegou na ubuntu", "grep -rqs \"TREINO-REMOTO-$(date +%Y%m%d)\" /var/log/", "ubuntu")]),

    # ── Mini-SOC ──
    Escolha(id="s10.mitre.1", titulo="MITRE: brute-force", prova="",
            enunciado="Qual técnica do ATT&CK corresponde a brute-force de senha?",
            opcoes=["T1110", "T1046", "T1053", "T1548"], correta="a"),
    Escolha(id="s10.mitre.2", titulo="MITRE: varredura", prova="",
            enunciado="E o scan de portas com nmap?",
            opcoes=["T1110", "T1046 (Network Service Discovery)", "T1098", "T1003"], correta="b"),
    Escolha(id="s10.mitre.3", titulo="MITRE: persistência", prova="",
            enunciado="Cron malicioso e chave SSH plantada são, respectivamente:",
            opcoes=["T1053.003 e T1098.004", "T1110 e T1046", "T1548.001 e T1003", "T1059 e T1021"], correta="a"),
    Escolha(id="s10.mitre.4", titulo="MITRE: SUID", prova="",
            enunciado="Escalar privilégio abusando de um binário SUID é:",
            opcoes=["T1548.001 (Setuid and Setgid)", "T1110", "T1053.003", "T1046"], correta="a"),
    Quiz(id="s10.triagem", titulo="Triagem (sua questão 17)", prova="",
         enunciado="""
         Alerta: 300 falhas de SSH e depois um login com sucesso, do mesmo IP. Ordene a resposta (letras):
           a) contenção (bloquear o IP, isolar o host, resetar a credencial)
           b) validar: o login foi do mesmo IP? o usuário é legítimo? foi alguém da equipe?
           c) lições aprendidas e melhorias
           d) escopo e linha do tempo: o que foi feito depois do login (comandos, sudo, persistência)?
           e) erradicação e recuperação (remover persistência, corrigir a falha, restaurar)
         """,
         respostas=[lambda r: re.sub(r"[^a-e]", "", r.lower()) == "bdaec"], resposta="b d a e c",
         explicacao="Em novembro você foi direto para 'isolar e escalar'. Um pleno valida e monta a linha do tempo primeiro (NIST 800-61)."),
    Marco(id="s10.ataque", titulo="Mini-SOC: ataque completo executado",
          enunciado="""
          Do kali, contra a rhel (pelo DNAT do roteador; desfaça temporariamente o hardening do SSH ou use outra porta):
            1. reconhecimento com nmap
            2. brute-force SSH num usuário com senha fraca (criado de propósito)
            3. escalada por SUID ou sudo mal configurado (semana 2)
            4. persistência com cron + chave SSH
            5. alteração em /etc/passwd
          Para cada etapa: o Wazuh alertou? Qual regra? Qual técnica do MITRE?
          Depois aplique o hardening de novo e mostre que o ataque falha.
          """),
    Tarefa(id="s10.minisoc", titulo="Mini-SOC: relatório do incidente (portfólio)",
           enunciado="""
           Monte ~/linux-lab/projetos/mini-soc/ com: README.md (o que é, diagrama, como reproduzir),
           o relatório do incidente com LINHA DO TEMPO e mapeamento MITRE ATT&CK, o playbook de triagem,
           suas regras customizadas do Wazuh e prints dos alertas (pasta img/).
           """,
           checks=[("README existe", "test -f ~/linux-lab/projetos/mini-soc/README.md"),
                   ("tem conteúdo de verdade (≥ 400 palavras no projeto)",
                    '[ "$(cat ~/linux-lab/projetos/mini-soc/*.md | wc -w)" -ge 400 ]'),
                   ("mapeia técnicas do MITRE", "grep -rqE 'T1110|T1046|T1053|T1098|T1548' ~/linux-lab/projetos/mini-soc/"),
                   ("tem linha do tempo", "grep -rqiE 'timeline|linha do tempo' ~/linux-lab/projetos/mini-soc/"),
                   ("tem prints", "ls ~/linux-lab/projetos/mini-soc/img/*.png >/dev/null 2>&1"),
                   ("está publicado no GitHub", "git -C ~/linux-lab log '@{u}' --oneline -- projetos/mini-soc 2>/dev/null | grep -q .")]),
]
