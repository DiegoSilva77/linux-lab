from motor import SSH_TREINO, Escolha, Quiz, Subnet, Tarefa, cmd, rx

TITULO = "Redes no Linux + roteador NAT/firewall"
DATAS = "11–17/01"
OBJETIVO = """
Configurar rede nas duas famílias e CONSTRUIR na mão o que você viu no FortiGate:
roteamento, NAT/PAT, DNAT e firewall stateful com nftables. Fecha as questões 14 e 15.
Teoria: 109.1, 109.2, 109.3, 109.4.
"""

CON = "C=$(nmcli -g NAME,DEVICE con show --active | awk -F: '$2!=\"lo\"{print $1; exit}')"

EXERCICIOS = [
    # ── conceitos ──
    Escolha(id="s09.nat.1", titulo="NAT × PAT (sua questão 15)",
            enunciado="Sua casa tem 10 dispositivos e 1 IP público. O roteador usa:",
            opcoes=["NAT 1:1 (um IP público para cada IP interno)",
                    "PAT / masquerade: todos saem pelo mesmo IP público e são diferenciados pela PORTA de origem",
                    "Roteamento puro, sem tradução", "DNAT"], correta="b"),
    Escolha(id="s09.nat.2", titulo="SNAT × DNAT",
            enunciado="Você quer que quem acessa IP_PUBLICO:2222 chegue no SSH de um servidor interno. Isso é:",
            opcoes=["SNAT", "DNAT (port forward)", "PAT", "Masquerade"], correta="b",
            explicacao="SNAT/masquerade troca a ORIGEM (para sair). DNAT troca o DESTINO (para entrar)."),
    Escolha(id="s09.fw.1", titulo="Stateful × stateless (sua questão 15)",
            enunciado="O que um firewall STATEFUL faz que um stateless não faz?",
            opcoes=["Bloqueia por porta", "Acompanha as conexões e libera automaticamente as respostas (established/related)",
                    "Faz VPN", "Bloqueia por IP"], correta="b"),
    Escolha(id="s09.diag", titulo="Pinga IP mas não navega (sua questão 14)",
            enunciado="`ping 8.8.8.8` funciona, mas `ping google.com` não. Qual o primeiro suspeito e o comando no Linux?",
            opcoes=["Cabo solto; ethtool", "DNS; resolvectl status / cat /etc/resolv.conf / dig google.com",
                    "Gateway; ip route", "Firewall; nft list ruleset"], correta="b"),
    Escolha(id="s09.camadas", titulo="Método de troubleshooting",
            enunciado="Qual a ordem mais sensata para diagnosticar 'o site não abre'?",
            opcoes=["aplicação → DNS → IP → link", "link → IP → gateway → DNS → porta → aplicação",
                    "DNS → link → aplicação → IP", "reiniciar tudo"], correta="b"),
    Quiz(id="s09.nmcli", titulo="IP estático com nmcli",
         enunciado="Comando nmcli para definir o IP 10.10.20.10/24 na conexão chamada 'lab' (só o endereço):",
         respostas=[cmd(r"nmcli (c|con|connection) (mod|modify) lab ipv4\.addresses 10\.10\.20\.10/24( .*)?")],
         resposta="nmcli con mod lab ipv4.addresses 10.10.20.10/24 ipv4.method manual"),
    Quiz(id="s09.netplan", titulo="netplan",
         enunciado="No Ubuntu, depois de editar o YAML em /etc/netplan/, qual comando aplica a configuração?",
         respostas=[cmd(r"netplan (try|apply)")], resposta="netplan apply  (ou netplan try, que desfaz se você perder o acesso)"),
    Escolha(id="s09.nss", titulo="nsswitch",
            enunciado="Em /etc/nsswitch.conf, a linha `hosts: files dns` significa:",
            opcoes=["Consulta o DNS e depois o /etc/hosts", "Consulta o /etc/hosts primeiro e depois o DNS",
                    "Só usa o DNS", "Bloqueia o DNS"], correta="b",
            explicacao="Atacantes alteram o /etc/hosts para desviar domínios. Ele é verificado ANTES do DNS."),
    Quiz(id="s09.getent", titulo="Resolver como o sistema resolve",
         enunciado="Qual comando resolve um nome seguindo o nsswitch (inclui /etc/hosts), ao contrário do dig?",
         respostas=[rx(r"getent hosts( \S+)?"), rx(r"getent ahosts( \S+)?")], resposta="getent hosts nome"),
    Quiz(id="s09.hostname", titulo="Hostname persistente",
         enunciado="Comando para definir o hostname 'srv01' de forma persistente:",
         respostas=[cmd(r"hostnamectl (set-hostname|hostname) srv01")], resposta="hostnamectl set-hostname srv01"),
    Escolha(id="s09.ferr", titulo="Ferramentas",
            enunciado="Qual comando mostra o caminho (os saltos) até um destino?",
            opcoes=["ss", "traceroute / tracepath", "dig", "nc"], correta="b"),
    Subnet(id="s09.subnet", titulo="Bateria de subnetting (revisão)",
           enunciado="Revisão antes de montar a rede do lab. Meta: 9 de 10.", n=10, prefixos=(16, 30), meta=9),

    # ── laboratório ──
    Tarefa(id="s09.vm.rede", titulo="Montar a rede lab-interna", host="local",
           enunciado="""
           1. No virt-manager: Editar → Detalhes da conexão → Redes virtuais → crie 'lab-interna' ISOLADA, sem DHCP.
           2. Adicione uma 2ª placa na ubuntu ligada à lab-interna.
           3. Na rhel, troque a placa da rede default pela lab-interna (ela só fica na rede interna).
           4. ubuntu eth1 = 10.10.20.1/24 (netplan) · rhel = 10.10.20.10/24, gateway 10.10.20.1, DNS 1.1.1.1 (nmcli)
           5. Como o Fedora não alcança mais a rhel direto, entre por salto (ProxyJump) pela ubuntu:
                ssh -J seu_usuario@IP_DA_UBUNTU seu_usuario@10.10.20.10
              (o treino faz o mesmo salto sozinho quando a rhel some da rede default)
           """,
           checks=[("rede lab-interna existe", "virsh -c qemu:///system net-info lab-interna >/dev/null 2>&1"),
                   ("rhel acessível via ubuntu (salto)", f"{SSH_TREINO} rhel true"),
                   ("rhel com 10.10.20.10/24", "ip -4 addr | grep -q 'inet 10.10.20.10/24'", "rhel"),
                   ("rhel fora da rede default", "! ip -4 addr | grep -q 'inet 192.168.122.'", "rhel"),
                   ("ubuntu com 10.10.20.1/24", "ip -4 addr | grep -q 'inet 10.10.20.1/24'", "ubuntu")]),
    Tarefa(id="s09.vm.nat", titulo="Roteador com NAT (nftables)", host="ubuntu",
           enunciado="""
           Faça a ubuntu rotear a lab-interna para a internet:
             · ip_forward ligado e persistente (/etc/sysctl.d/)
             · nftables com masquerade para 10.10.20.0/24 saindo pela placa da rede default
             · regras salvas em /etc/nftables.conf e serviço nftables habilitado
           Depois, na rhel: ping 8.8.8.8 e ping example.com. E na ubuntu: conntrack -L (veja a tradução das portas).
           """,
           checks=[("roteamento ativo", '[ "$(sysctl -n net.ipv4.ip_forward)" = 1 ]'),
                   ("roteamento persistente",
                    "grep -rqsE '^[[:space:]]*net\\.ipv4\\.ip_forward[[:space:]]*=[[:space:]]*1' /etc/sysctl.conf /etc/sysctl.d/"),
                   ("masquerade configurado", "nft list ruleset | grep -q masquerade"),
                   ("regras salvas em /etc/nftables.conf", "grep -q masquerade /etc/nftables.conf"),
                   ("nftables habilitado no boot", "systemctl is-enabled --quiet nftables"),
                   ("rhel sai para a internet", "ping -c1 -W3 8.8.8.8 >/dev/null", "rhel"),
                   ("rhel resolve nomes", "getent hosts example.com >/dev/null", "rhel")],
           dica="table ip nat { chain postrouting { type nat hook postrouting priority 100; oifname \"enp1s0\" ip saddr 10.10.20.0/24 masquerade } }  (confira o nome da placa com ip -br a)"),
    Tarefa(id="s09.vm.fw", titulo="Firewall stateful no roteador", host="ubuntu",
           enunciado="""
           Na ubuntu, chain forward com política DROP, liberando:
             · tráfego established,related
             · a lab-interna saindo para a internet
             · e uma regra que LOGA o que for descartado (log prefix "FW-DROP ")
           Depois, TIRE o established,related por um momento e explique (em relatorios/s09-rede.md) o que quebra.
           """,
           checks=[("forward com policy drop", "nft list ruleset | grep -Eq 'hook forward.*policy drop'"),
                   ("libera established/related", "nft list ruleset | grep -q established"),
                   ("loga descartes", "nft list ruleset | grep -q 'log prefix'"),
                   ("rhel continua navegando", "curl -sS -m 8 -o /dev/null https://example.com", "rhel")]),
    Tarefa(id="s09.vm.dnat", titulo="Port forward: Fedora → rhel:22 pela porta 2222", host="local",
           enunciado="""
           Configure DNAT na ubuntu: quem acessar IP_DA_UBUNTU (rede 192.168.122.x) na porta 2222
           deve cair no SSH da rhel (10.10.20.10:22). Lembre de liberar no forward (ct status dnat).
           """,
           checks=[("DNAT configurado", "nft list ruleset | grep -q dnat", "ubuntu"),
                   ("ssh -p 2222 na ubuntu cai na rhel",
                    f'IP=$({SSH_TREINO} ubuntu "ip -4 -o addr show scope global" | awk \'{{print $4}}\' | cut -d/ -f1 | grep "^192.168.122" | head -1); '
                    f'[ -n "$IP" ] && [ "$({SSH_TREINO} -p 2222 -o HostName=$IP ubuntu hostname)" = "$({SSH_TREINO} rhel hostname)" ]')]),

    # ── cenários ──
    Tarefa(id="s09.cen.gw", titulo="Cenário: rhel sem internet (1/3)", host="rhel",
           enunciado="A rhel parou de acessar a internet. Diagnostique em camadas e corrija de forma persistente.",
           quebrar=CON + """
           nohup bash -c "sleep 2; nmcli con mod '$C' ipv4.gateway 10.10.20.254 && nmcli con up '$C'" >/dev/null 2>&1 &
           """,
           checks=[("rhel alcança 8.8.8.8", "ping -c1 -W3 8.8.8.8 >/dev/null"),
                   ("correção persistente", CON + '; [ "$(nmcli -g ipv4.gateway con show "$C")" = 10.10.20.1 ]')]),
    Tarefa(id="s09.cen.dns", titulo="Cenário: pinga IP mas não abre site (2/3)", host="rhel",
           enunciado="Agora a rhel pinga 8.8.8.8, mas não resolve nomes. Diagnostique e corrija de forma persistente.",
           quebrar=CON + """
           nohup bash -c "sleep 2; nmcli con mod '$C' ipv4.dns 10.10.20.53 ipv4.ignore-auto-dns yes && nmcli con up '$C'" >/dev/null 2>&1 &
           """,
           checks=[("rhel resolve example.com", "getent hosts example.com >/dev/null"),
                   ("DNS quebrado removido da conexão", CON + '; ! nmcli -g ipv4.dns con show "$C" | grep -q 10.10.20.53')]),
    Tarefa(id="s09.cen.fw", titulo="Cenário: só HTTPS não funciona (3/3)", host="ubuntu",
           enunciado="A rhel resolve nomes e pinga, mas nenhum site HTTPS abre. O problema está no roteador. Ache e corrija.",
           quebrar="""
           nft add table inet manutencao
           nft add chain inet manutencao fwd '{ type filter hook forward priority -10; }'
           nft add rule inet manutencao fwd tcp dport 443 drop
           """,
           checks=[("rhel abre HTTPS", "curl -sS -m 8 -o /dev/null https://example.com", "rhel"),
                   ("regra de bloqueio removida", "! nft list ruleset | grep -q 'dport 443 drop'")],
           dica="nft list ruleset mostra TODAS as tabelas, não só a sua. Repare na prioridade das chains."),
]
