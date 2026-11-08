import re

from motor import Comando, Escolha, PerguntaVM, Quiz, Tarefa, cmd, rx

TITULO = "Processos, systemd e persistência + ARP/DHCP/DNS"
DATAS = "30/11–06/12"
OBJETIVO = """
Saber o que roda no sistema e como um atacante se esconde ali: a base de forense e
resposta a incidente (Cyber Defense Operations do 2º ano). O Mini-SOC começa aqui.
Teoria: 103.5, 103.6, 101.3, 107.2 (LPIC) + RFC 3227 (ordem de volatilidade).
"""


def _ss(r: str) -> bool:
    m = re.fullmatch(r"(sudo )?ss -([a-zA-Z]+)( .*)?", r.strip())
    if m:
        f = m.group(2)
        return "l" in f and "p" in f
    return re.search(r"lsof -i ?:22\b", r) is not None or re.search(r"fuser 22/tcp", r) is not None


EXERCICIOS = [
    # ── processos ──
    Quiz(id="s03.sig.1", titulo="Sinal padrão do kill",
         enunciado="Que sinal o kill envia por padrão? (nome ou número)", respostas=["15", "sigterm", "term"]),
    Quiz(id="s03.sig.2", titulo="O sinal que não dá para ignorar",
         enunciado="Qual sinal o processo NÃO consegue capturar nem ignorar?", respostas=["9", "sigkill", "kill"],
         explicacao="Use o 9 só em último caso: o processo morre sem fechar arquivos nem limpar o que estava fazendo."),
    Quiz(id="s03.sig.3", titulo="Recarregar configuração",
         enunciado="Que sinal muitos daemons usam para RECARREGAR a configuração sem reiniciar?",
         respostas=["1", "sighup", "hup"]),
    Quiz(id="s03.nice.1", titulo="nice",
         enunciado="Na escala do nice (−20 a 19), qual valor dá a MAIOR prioridade?", respostas=["-20"]),
    Comando(id="s03.ps.mem", titulo="Quem come memória",
            enunciado="processos.txt é a saída de um `ps aux`. Mostre só o COMANDO (11ª coluna) dos 3 processos que mais usam %MEM.",
            esperado="tail -n +2 processos.txt | sort -k4 -rn | head -3 | awk '{print $11}'",
            dica="Pule o cabeçalho (tail -n +2), ordene numericamente pela 4ª coluna (sort -k4 -rn) e use awk."),
    Comando(id="s03.ps.cpu", titulo="Quem come CPU",
            enunciado="Mostre a linha inteira do processo com MAIOR %CPU em processos.txt.",
            esperado="tail -n +2 processos.txt | sort -k3 -rn | head -1"),
    Comando(id="s03.ps.root", titulo="Processos do root",
            enunciado="Quantos processos são do usuário root em processos.txt? (só o número)",
            esperado="awk '$1==\"root\"' processos.txt | wc -l"),
    Comando(id="s03.ps.www", titulo="PIDs do www-data",
            enunciado="Liste os PIDs dos processos do usuário www-data.",
            esperado="awk '$1==\"www-data\"{print $2}' processos.txt", ordem=False),
    Quiz(id="s03.ps.susp", titulo="Processo suspeito", prova="",
         enunciado="Olhando processos.txt: qual processo é suspeito? Responda o caminho completo do executável.",
         respostas=["/tmp/.x/kworkerd"],
         explicacao="""
         Rodando de /tmp numa pasta oculta, com nome imitando thread do kernel (as reais aparecem entre [colchetes]),
         como www-data (provável invasão pelo site), com 97% de CPU e conectando num pool de mineração: é um cryptominer.
         """),

    # ── systemd e agendamento ──
    Quiz(id="s03.sd.1", titulo="Habilitar e iniciar (sua questão 4)",
         enunciado="Um único comando que habilita o nginx no boot E o inicia agora:",
         respostas=[cmd(r"systemctl enable --now nginx(\.service)?")], resposta="systemctl enable --now nginx"),
    Quiz(id="s03.sd.2", titulo="Logs de um serviço",
         enunciado="Comando para ver os logs do serviço sshd:",
         respostas=[cmd(r"journalctl (-u ?|--unit[= ])sshd(\.service)?( .*)?")], resposta="journalctl -u sshd"),
    Quiz(id="s03.sd.3", titulo="Depois de editar uma unit",
         enunciado="Você editou um arquivo .service. Qual comando faz o systemd reler as units?",
         respostas=[cmd(r"systemctl daemon-reload")], resposta="systemctl daemon-reload"),
    Escolha(id="s03.sd.4", titulo="mask × disable",
            enunciado="Qual a diferença entre `systemctl disable` e `systemctl mask`?",
            opcoes=["Nenhuma", "disable só tira do boot; mask impede o serviço de ser iniciado de QUALQUER forma",
                    "mask apaga o serviço", "disable para o serviço agora; mask só no boot"],
            correta="b"),
    Escolha(id="s03.sd.5", titulo="Targets",
            enunciado="Qual target equivale ao antigo 'runlevel 3' (multiusuário, sem interface gráfica)?",
            opcoes=["graphical.target", "rescue.target", "multi-user.target", "emergency.target"], correta="c"),
    Quiz(id="s03.cron.1", titulo="cron: a cada 15 min", prova="102",
         enunciado="Linha de cron (só os 5 campos de tempo) para rodar a cada 15 minutos:",
         respostas=["*/15 * * * *", "0,15,30,45 * * * *"]),
    Quiz(id="s03.cron.2", titulo="cron: dias úteis", prova="102",
         enunciado="E para rodar de segunda a sexta às 18:30?", respostas=["30 18 * * 1-5"]),
    Quiz(id="s03.cron.3", titulo="cron: todo dia 1", prova="102",
         enunciado="E todo dia 1º do mês às 03:00?", respostas=["0 3 1 * *"]),
    Escolha(id="s03.cron.4", titulo="Lendo cron", prova="102",
            enunciado="Quando roda `0 */6 * * *`?",
            opcoes=["A cada 6 minutos", "A cada 6 horas, no minuto 0 (00:00, 06:00, 12:00, 18:00)",
                    "Às 06:00 todo dia", "Dia 6 de cada mês"], correta="b"),
    Escolha(id="s03.cron.5", titulo="Quem pode usar cron", prova="102",
            enunciado="Existe /etc/cron.allow contendo só 'diego'. Quem pode usar crontab?",
            opcoes=["Todo mundo", "Só o diego (e o root)", "Ninguém", "Todos exceto o diego"], correta="b"),
    Quiz(id="s03.timer.1", titulo="systemd timer", prova="102",
         enunciado="No OnCalendar de um timer, como escrever 'todo dia às 02:00'?",
         respostas=["*-*-* 02:00:00", "*-*-* 02:00", "*-*-* 2:00", "*-*-* 2:00:00"]),

    # ── na VM ──
    Quiz(id="s03.ss.1", titulo="Quem escuta na porta (sua questão 3)",
         enunciado="Comando para descobrir qual processo (e PID) está escutando na porta 22:",
         respostas=[_ss], resposta="ss -tlnp  (com sudo para ver processos de outros usuários)"),
    PerguntaVM(id="s03.ss.2", titulo="PID do sshd na rhel", host="rhel",
               enunciado="Qual é o PID do processo que escuta na porta 22 da rhel?",
               cmd="ss -Htlnp 'sport = :22' | grep -o 'pid=[0-9]*' | head -1 | cut -d= -f2"),
    Tarefa(id="s03.vm.timer", titulo="Desafio de sábado: serviço monitor com timer", host="rhel+ubuntu",
           enunciado="""
           Nas duas VMs, crie:
             · um usuário de sistema 'monitor' sem shell de login (useradd -r -s /usr/sbin/nologin monitor)
             · um script /usr/local/bin/monitor.sh que imprime uso de disco, top 5 processos por memória
               e conexões ativas (pode usar IA, mas revise linha a linha)
             · /etc/systemd/system/monitor.service (Type=oneshot, User=monitor) rodando o script
             · /etc/systemd/system/monitor.timer rodando a cada 5 minutos, habilitado e ativo
           Depois, ache a saída do script no journal.
           """,
           checks=[("timer habilitado", "systemctl is-enabled --quiet monitor.timer"),
                   ("timer ativo", "systemctl is-active --quiet monitor.timer"),
                   ("serviço roda como usuário que não é root",
                    'u=$(systemctl show -p User --value monitor.service); [ -n "$u" ] && [ "$u" != root ]'),
                   ("já rodou nos últimos 15 min", "journalctl -u monitor.service --since -15min | grep -q ."),
                   ("usuário monitor sem shell de login",
                    "getent passwd monitor | cut -d: -f7 | grep -Eq 'nologin|false'")],
           dica="Timer: [Timer] OnBootSec=1min e OnUnitActiveSec=5min, [Install] WantedBy=timers.target. Depois: systemctl enable --now monitor.timer"),

    # ── segurança: persistência e forense ──
    Quiz(id="s03.rfc.1", titulo="Ordem de volatilidade (RFC 3227)", prova="",
         enunciado="""
         Ordene da MAIS volátil para a MENOS volátil (responda as letras, ex.: abcd):
           a) conteúdo do disco
           b) conexões de rede, processos e memória RAM
           c) registradores e cache da CPU
           d) mídia de backup arquivada
         """,
         respostas=[lambda r: re.sub(r"[^a-d]", "", r.lower()) == "cbad"], resposta="c b a d",
         explicacao="Colete primeiro o que some primeiro. Desligar a máquina antes de coletar a RAM destrói evidência."),
    Escolha(id="s03.pers.1", titulo="Onde procurar persistência", prova="",
            enunciado="Quais destes são lugares clássicos de PERSISTÊNCIA num Linux?",
            opcoes=["/etc/cron.d/ e crontabs de usuários", "units em /etc/systemd/system/",
                    "~/.ssh/authorized_keys", "/proc/cpuinfo", "~/.bashrc"],
            correta="abce"),
    Tarefa(id="s03.vm.wazuh", titulo="Agente Wazuh nas VMs", host="rhel+ubuntu",
           enunciado="""
           Instale o agente Wazuh nas duas VMs apontando para o seu manager (o outro PC, ou uma VM de 4 GB).
           Siga a documentação oficial do Wazuh para RPM (rhel) e DEB (ubuntu).
           Confirme no painel do Wazuh que os dois agentes aparecem como 'active'.
           """,
           checks=[("wazuh-agent ativo", "systemctl is-active --quiet wazuh-agent"),
                   ("agente conectado ao manager", "grep -q \"status='connected'\" /var/ossec/var/run/wazuh-agentd.state")]),
    Tarefa(id="s03.vm.cacada", titulo="Desafio: caça às cegas (persistências plantadas)", host="rhel", ocultar=True,
           enunciado="""
           Vou plantar 6 itens de persistência na rhel, como um atacante faria. Não vou dizer quais.
             1. Antes de mexer em qualquer coisa, colete as evidências VOLÁTEIS na ordem da RFC 3227
                (conexões, processos, usuários logados, arquivos abertos) e salve cada saída com hash.
             2. Cace e remova TODOS os itens. O verificador só diz quantos faltam.
             3. Escreva ~/linux-lab/relatorios/s03-persistencia.md com o checklist de caça e os comandos.
           Depois veja no Wazuh o que ele detectou e o que passou batido.
           """,
           quebrar=r"""
           id suporte >/dev/null 2>&1 || useradd -o -u 0 -g 0 -M -d /root -s /bin/bash suporte
           mkdir -p /usr/local/lib/.cache
           printf '#!/bin/bash\necho "$(date) beacon" >> /var/tmp/.sysupd.log\n' > /usr/local/lib/.cache/sysupd
           chmod +x /usr/local/lib/.cache/sysupd
           echo '*/5 * * * * root /usr/local/lib/.cache/sysupd' > /etc/cron.d/sysupdate
           printf '[Unit]\nDescription=D-Bus Helper\n[Service]\nExecStart=/bin/bash -c "while true; do /usr/local/lib/.cache/sysupd; sleep 300; done"\n[Install]\nWantedBy=multi-user.target\n' > /etc/systemd/system/dbus-helper.service
           systemctl daemon-reload && systemctl enable --now dbus-helper.service >/dev/null 2>&1
           mkdir -p /root/.ssh && echo 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIFakeKeyForTrainingOnlyNotARealKey0000000000 atacante@kali' >> /root/.ssh/authorized_keys
           chmod 700 /root/.ssh && chmod 600 /root/.ssh/authorized_keys
           U=$(getent passwd 1000 | cut -d: -f1); [ -n "$U" ] && echo '(/usr/local/lib/.cache/sysupd &) 2>/dev/null' >> /home/$U/.bashrc
           """,
           checks=[("item 1", "[ \"$(awk -F: '$3==0' /etc/passwd | wc -l)\" -eq 1 ]"),
                   ("item 2", "! grep -rqs sysupd /etc/cron.d /etc/crontab /var/spool/cron"),
                   ("item 3", "! systemctl cat dbus-helper.service >/dev/null 2>&1"),
                   ("item 4", "! grep -qs 'atacante@kali' /root/.ssh/authorized_keys"),
                   ("item 5", "! grep -qs sysupd /home/*/.bashrc /root/.bashrc"),
                   ("item 6", "[ ! -e /usr/local/lib/.cache/sysupd ] && ! pgrep -f sysupd >/dev/null")],
           dica="Pense: usuários com UID 0, cron, systemd, chaves SSH, arquivos de inicialização do shell, binários escondidos."),

    # ── redes: ARP, DHCP, DNS ──
    Escolha(id="s03.arp", titulo="ARP", prova="102",
            enunciado="Para que serve o ARP?",
            opcoes=["Traduzir nome em IP", "Descobrir o endereço MAC de um IP na rede local",
                    "Distribuir IPs", "Rotear entre redes"], correta="b"),
    Quiz(id="s03.dhcp", titulo="DHCP DORA", prova="102",
         enunciado="Quais são as 4 mensagens do DHCP, em ordem? (as iniciais servem)",
         respostas=[lambda r: re.sub(r"[^a-z]", "", r.lower()) in ("dora", "discoverofferrequestack",
                                                                    "discoverofferrequestacknowledge")],
         resposta="Discover, Offer, Request, Ack"),
    Quiz(id="s03.dns.1", titulo="Registro de e-mail", prova="102",
         enunciado="Qual tipo de registro DNS indica o servidor de e-mail de um domínio?", respostas=["mx"]),
    Quiz(id="s03.dns.2", titulo="Registro reverso", prova="102",
         enunciado="Qual tipo de registro faz a resolução REVERSA (IP → nome)?", respostas=["ptr"]),
    Quiz(id="s03.dns.3", titulo="Registro IPv6", prova="102",
         enunciado="Qual tipo de registro guarda um endereço IPv6?", respostas=["aaaa"]),
    Quiz(id="s03.dns.4", titulo="dig reverso", prova="102",
         enunciado="Comando dig para descobrir o nome de 8.8.8.8:", respostas=[rx(r"dig -x 8\.8\.8\.8")],
         resposta="dig -x 8.8.8.8"),
    Escolha(id="s03.dns.5", titulo="DNS e transporte", prova="102",
            enunciado="Quais são verdadeiras sobre o DNS?",
            opcoes=["Usa UDP/53 nas consultas comuns", "Usa TCP/53 em respostas grandes e transferência de zona",
                    "Usa TCP/80", "Usa ICMP"], correta="ab"),
    Quiz(id="s03.fluxo", titulo="O que acontece ao abrir google.com (sua questão 13)", prova="",
         enunciado="""
         O notebook já tem IP via DHCP. Ordene o que acontece até a página abrir (letras, ex.: abcde):
           a) handshake TCP na porta 443
           b) consulta DNS de google.com
           c) negociação TLS
           d) ARP para descobrir o MAC do gateway
           e) requisição HTTP GET
         """,
         respostas=[lambda r: re.sub(r"[^a-e]", "", r.lower()) == "dbace"], resposta="d b a c e",
         explicacao="O ARP vem antes porque até a consulta DNS precisa sair pelo gateway (quando o DNS está fora da rede local)."),
]
