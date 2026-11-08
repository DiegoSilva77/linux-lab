from motor import SSH_TREINO, Escolha, Marco, PerguntaVM, Quiz, Tarefa, cmd, rx

TITULO = "Setup do laboratório (KVM do zero)"
DATAS = "09–15/11"
OBJETIVO = """
Montar o laboratório entendendo cada peça: KVM, ISOs, VMs `rhel`, `ubuntu` e `kali`, virsh, SSH por chave,
sudo sem senha (para o treino conferir suas tarefas), snapshots, Git e o básico do vi.
📖 Leia ~/linux-lab/LAB-KVM.md junto: cada exercício aponta a seção do guia.
"""

V = "virsh -c qemu:///system"


def _disco_intacto(dev: str) -> str:
    return f'[ "$(lsblk -n {dev} 2>/dev/null | wc -l)" -eq 1 ] && ! pvs {dev} >/dev/null 2>&1'


EXERCICIOS = [
    # ── instalar e entender ──
    Tarefa(id="s00.kvm", titulo="KVM e virt-manager instalados (guia §2)",
           enunciado="""
           No Fedora:
             sudo dnf install @virtualization
             sudo systemctl enable --now libvirtd
             sudo usermod -aG libvirt $USER
           Depois faça logout/login (ou reinicie) para o grupo novo valer.
           """,
           checks=[("módulo kvm carregado", "lsmod | grep -q '^kvm'"),
                   ("virt-manager instalado", "rpm -q virt-manager >/dev/null"),
                   ("serviço de virtualização ativo",
                    "systemctl is-active --quiet libvirtd || systemctl is-active --quiet virtqemud"),
                   ("seu usuário está no grupo libvirt", "getent group libvirt | grep -qw \"$USER\""),
                   ("você acessa o libvirt do sistema sem senha",
                    "timeout 10 virsh -c qemu:///system -q list --all </dev/null >/dev/null 2>&1")],
           dica="Se o grupo falhar, rode o usermod. Se só o último falhar, reinicie o PC para o grupo valer na sessão."),
    Escolha(id="s00.conc.1", titulo="Quem é quem: KVM",
            enunciado="Qual peça é o MÓDULO DO KERNEL que usa a extensão de virtualização da CPU?",
            opcoes=["QEMU", "KVM", "libvirt", "virt-manager"], correta="b"),
    Escolha(id="s00.conc.2", titulo="Quem é quem: QEMU",
            enunciado="Qual peça EMULA o hardware da VM (disco, placa de rede, vídeo) e aparece como um processo por VM ligada?",
            opcoes=["QEMU", "KVM", "libvirt", "virsh"], correta="a"),
    Escolha(id="s00.conc.3", titulo="Quem é quem: libvirt",
            enunciado="Qual peça é o serviço que GERENCIA as VMs (configurações, redes virtuais, snapshots)?",
            opcoes=["QEMU", "KVM", "libvirt", "qcow2"], correta="c"),
    Escolha(id="s00.conc.4", titulo="virsh × virt-manager",
            enunciado="Qual a diferença entre virsh e virt-manager?",
            opcoes=["virsh é para Red Hat e virt-manager para Ubuntu",
                    "Fazem a mesma coisa (falam com o libvirt): um por linha de comando, outro gráfico",
                    "virt-manager é mais poderoso, virsh só lista VMs", "virsh cria VMs e virt-manager só liga"],
            correta="b"),
    Escolha(id="s00.conc.5", titulo="system × session",
            enunciado="Por que usar a conexão qemu:///system?",
            opcoes=["É mais rápida", "É onde ficam as VMs do sistema, com a rede NAT completa (a mesma que o virt-manager usa)",
                    "Não precisa de KVM", "É a única que tem snapshot"], correta="b"),
    Tarefa(id="s00.uri", titulo="virsh apontando para a conexão certa (guia §2)",
           enunciado="""
           Para não ter que digitar -c qemu:///system sempre:
             echo 'export LIBVIRT_DEFAULT_URI=qemu:///system' >> ~/.bashrc
           Abra um terminal novo e teste: virsh uri  (deve mostrar qemu:///system)
           """,
           checks=[("variável no ~/.bashrc", "grep -q 'LIBVIRT_DEFAULT_URI=qemu:///system' ~/.bashrc")]),
    Tarefa(id="s00.rede", titulo="Rede virtual 'default' ativa (guia §2)",
           enunciado="""
           Confira a rede NAT padrão do libvirt (é nela que as VMs ganham IP 192.168.122.x):
             virsh net-list --all
           Se não estiver ativa:  virsh net-start default && virsh net-autostart default
           Veja também a ponte no Fedora:  ip -br a show virbr0
           """,
           checks=[("rede default ativa", f"{V} net-info default 2>/dev/null | grep -Eq '^Active:[[:space:]]+yes'"),
                   ("liga sozinha no boot", f"{V} net-info default 2>/dev/null | grep -Eq '^Autostart:[[:space:]]+yes'")]),
    Tarefa(id="s00.pool", titulo="Pool de armazenamento 'default' (guia §2)",
           enunciado="""
           A pool 'default' é a pasta /var/lib/libvirt/images, onde ficam discos e ISOs.
             virsh pool-list --all
           Se não existir:
             virsh pool-define-as default dir --target /var/lib/libvirt/images
             virsh pool-start default && virsh pool-autostart default
           """,
           checks=[("pool default ativa", f"{V} pool-info default 2>/dev/null | grep -Eq '^State:[[:space:]]+running'")]),

    # ── ISOs ──
    Tarefa(id="s00.isos", titulo="ISOs baixadas e no lugar certo (guia §3)",
           enunciado="""
           Baixe (em paralelo, são vários GB):
             · RHEL 10 Binary DVD  → developers.redhat.com (conta grátis)   ou   Rocky Linux 10 → rockylinux.org
             · Ubuntu Server LTS  → ubuntu.com/download/server
           Confira os hashes (próximo exercício) e mova para a pool:
             sudo mv ~/Downloads/*.iso /var/lib/libvirt/images/ && virsh pool-refresh default
           """,
           checks=[("ISO do RHEL/Rocky na pool",
                    f"{V} pool-refresh default >/dev/null 2>&1; {V} vol-list default | grep -Eiq '(rhel|rocky).*\\.iso'"),
                   ("ISO do Ubuntu na pool", f"{V} vol-list default | grep -Eiq 'ubuntu.*\\.iso'")],
           dica="Se a ISO ficar na sua home, o QEMU (que roda como usuário 'qemu') não consegue ler: 'Permission denied'."),
    Escolha(id="s00.hash.1", titulo="Por que conferir o hash da ISO",
            enunciado="Por que conferir o SHA-256 da ISO com o publicado no site oficial?",
            opcoes=["Para acelerar a instalação",
                    "Para garantir que o arquivo não veio corrompido nem adulterado (ataque à cadeia de suprimentos)",
                    "Para descompactar a ISO", "Não serve para nada se o site tem HTTPS"],
            correta="b",
            explicacao="Já houve casos reais de ISOs trocadas por versões com backdoor em sites invadidos. HTTPS protege o transporte, não o arquivo no servidor."),
    Quiz(id="s00.hash.2", titulo="Conferindo contra o SHA256SUMS",
         enunciado="Na pasta com a ISO e o arquivo SHA256SUMS do site, qual comando confere só os arquivos que você baixou?",
         respostas=[rx(r"sha256sum (-c|--check) SHA256SUMS --ignore-missing"),
                    rx(r"sha256sum --ignore-missing (-c|--check) SHA256SUMS")],
         resposta="sha256sum -c SHA256SUMS --ignore-missing",
         dica="sha256sum -c lê uma lista de hashes e confere; --ignore-missing pula os arquivos da lista que você não baixou."),
    Marco(id="s00.hash.3", titulo="Hashes conferidos",
          enunciado="Você conferiu o SHA-256 das duas ISOs e os dois deram OK?"),

    # ── criar VMs ──
    Tarefa(id="s00.vms", titulo="VMs rhel e ubuntu criadas (guia §4)",
           enunciado="""
           Siga a seção 4 do guia. Resumo:
             rhel   → 2048 MB · 2 CPUs · 20 GB + 2 discos EXTRAS de 5 GB (VirtIO) · instalação mínima
             ubuntu → 1536 MB · 2 CPUs · 20 GB + 1 disco EXTRA de 5 GB (VirtIO) · marque o OpenSSH server
           Nomes EXATOS: rhel e ubuntu.
           ⚠️  Nos dois instaladores, instale SOMENTE no disco de 20 GB: os extras são para a semana 4.
           ⚠️  No RHEL, ligue a placa de rede no instalador e marque seu usuário como administrador.
           """,
           checks=[("VM rhel existe", f"{V} dominfo rhel >/dev/null 2>&1"),
                   ("VM ubuntu existe", f"{V} dominfo ubuntu >/dev/null 2>&1"),
                   ("rhel tem 3 discos (1 + 2 extras)",
                    f"[ $({V} domblklist rhel --details | grep -c ' disk ') -ge 3 ]"),
                   ("ubuntu tem 2 discos (1 + 1 extra)",
                    f"[ $({V} domblklist ubuntu --details | grep -c ' disk ') -ge 2 ]"),
                   ("as duas estão rodando com KVM (não emulação)",
                    f"{V} dumpxml rhel | grep -q \"type='kvm'\" && {V} dumpxml ubuntu | grep -q \"type='kvm'\"")],
           dica="Usou outro nome? Crie treino/config.json com {\"vms\": {\"rhel\": \"seu-nome\", \"ubuntu\": \"outro\"}}."),

    # ── operar ──
    Quiz(id="s00.virsh.1", titulo="virsh: listar tudo",
         enunciado="Comando virsh que lista TODAS as VMs, inclusive as desligadas:",
         respostas=[rx(r"virsh( -c qemu:///system)? list --all")], resposta="virsh list --all"),
    Quiz(id="s00.virsh.2", titulo="virsh: ligar",
         enunciado="Comando para ligar a VM rhel:", respostas=[rx(r"virsh( -c qemu:///system)? start rhel")],
         resposta="virsh start rhel"),
    Quiz(id="s00.virsh.3", titulo="virsh: desligar com educação",
         enunciado="Comando para desligar a rhel do jeito certo (o sistema faz o shutdown normal):",
         respostas=[rx(r"virsh( -c qemu:///system)? shutdown rhel")], resposta="virsh shutdown rhel"),
    Escolha(id="s00.virsh.4", titulo="virsh destroy",
            enunciado="O que `virsh destroy rhel` faz?",
            opcoes=["Apaga a VM e o disco", "Desliga na marra, como puxar da tomada (não apaga nada)",
                    "Apaga só os snapshots", "Reinicia a VM"], correta="b",
            explicacao="Para APAGAR a VM é `virsh undefine rhel --remove-all-storage`. Esse sim é perigoso."),
    Quiz(id="s00.virsh.5", titulo="virsh: descobrir o IP",
         enunciado="Comando que mostra o IP da rhel sem entrar nela:",
         respostas=[rx(r"virsh( -c qemu:///system)? domifaddr rhel( .*)?"),
                    rx(r"virsh( -c qemu:///system)? net-dhcp-leases default")],
         resposta="virsh domifaddr rhel"),
    Escolha(id="s00.virsh.6", titulo="Mouse preso",
            enunciado="Clicou no console da VM e o mouse ficou preso lá dentro. Como solta?",
            opcoes=["Esc", "Ctrl + Alt (da esquerda)", "Alt + F4", "Reiniciar a VM"], correta="b"),
    Tarefa(id="s00.ligar", titulo="Na prática: desligar e ligar pelo terminal",
           enunciado="""
           Pratique no terminal (não no virt-manager):
             virsh shutdown ubuntu   → espere → virsh list --all  (shut off)
             virsh start ubuntu      → virsh domifaddr ubuntu
           Deixe as duas VMs LIGADAS no final.
           """,
           checks=[("rhel ligada", f"{V} domstate rhel | grep -q running"),
                   ("ubuntu ligada", f"{V} domstate ubuntu | grep -q running"),
                   ("ubuntu tem IP", f"{V} domifaddr ubuntu | grep -q 192.168.122.")]),

    # ── acesso ──
    Tarefa(id="s00.ssh", titulo="Entrar nas VMs por SSH (guia §5)",
           enunciado="""
           No dia a dia você entra nas VMs pelo terminal do Fedora, digitando IP e senha:
             1. virsh domifaddr rhel       (anote o IP; idem para a ubuntu)
             2. ssh seu_usuario@IP          (na 1ª vez: yes; depois a senha) · exit para sair
           Para o treino conseguir CORRIGIR suas tarefas nas VMs, ele precisa de acesso próprio:
             3. treino conectar            (em outro terminal; pede a senha de cada VM uma vez)
           Isso cria uma chave só do treino em ~/linux-lab/treino/.ssh. Seu ~/.ssh não muda e
           você continua entrando com senha.
           """,
           checks=[("treino entra na rhel", f"{SSH_TREINO} rhel true"),
                   ("treino entra na ubuntu", f"{SSH_TREINO} ubuntu true")],
           dica="Connection refused = servidor SSH parado na VM (rhel: sudo systemctl enable --now sshd · "
                "ubuntu: sudo apt install -y openssh-server). Depois rode `treino conectar` de novo."),
    Tarefa(id="s00.sudo", titulo="sudo sem senha (só nas VMs do laboratório)", host="rhel+ubuntu",
           enunciado="""
           Para conferir suas tarefas, o treino lê arquivos de root nas VMs, então precisa de sudo sem senha.
           Faça isso SÓ em VM de laboratório, nunca num servidor de verdade. Em cada VM:
             echo "$USER ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/treino
             sudo chmod 440 /etc/sudoers.d/treino
           """,
           onde="DENTRO de cada VM (entre com ssh seu_usuario@IP)",
           checks=[("sudo sem senha", "true")],
           dica="O treino só confere isto depois de `treino conectar` (exercício s00.ssh). "
                "Para testar você mesmo, dentro da VM: sudo -k; sudo -n true && echo ok"),
    Tarefa(id="s00.discos", titulo="Discos extras intactos para a semana 4", host="rhel+ubuntu",
           enunciado="""
           Confira que o instalador NÃO usou os discos extras. Na VM: lsblk
           (vda = sistema; vdb/vdc devem aparecer sem partições).
           Se o instalador usou: o mais rápido é recriar a VM, instalando só no vda.
           """,
           checks=[("rhel: /dev/vdb livre", _disco_intacto("/dev/vdb"), "rhel"),
                   ("rhel: /dev/vdc livre", _disco_intacto("/dev/vdc"), "rhel"),
                   ("ubuntu: /dev/vdb livre", _disco_intacto("/dev/vdb"), "ubuntu")]),
    Tarefa(id="s00.repos", titulo="Repositórios funcionando e sistemas atualizados", host="rhel+ubuntu",
           enunciado="""
           rhel: registre (se não fez no instalador) com  sudo rhc connect  ou  sudo subscription-manager register
                 e depois  sudo dnf upgrade -y
           ubuntu: sudo apt update && sudo apt full-upgrade -y
           (Rocky não precisa de registro.)
           """,
           checks=[("rhel enxerga o repositório BaseOS", "dnf repolist 2>/dev/null | grep -qi baseos", "rhel"),
                   ("ubuntu com lista de pacotes atualizada",
                    "[ -n \"$(find /var/lib/apt/lists -name '*Packages*' -mtime -7 2>/dev/null | head -1)\" ]", "ubuntu")],
           dica="Registrado mas 'No repositories available'? Sua conta Red Hat não tem a assinatura Developer ativa. "
                "Entre em developers.redhat.com, aceite os termos, confira em access.redhat.com/management/subscriptions "
                "e depois, na rhel: sudo subscription-manager refresh && sudo dnf repolist"),
    Tarefa(id="s00.snap", titulo="Snapshot 'limpo' das duas VMs (guia §5)",
           enunciado="""
           Com tudo instalado e atualizado, crie o snapshot 'limpo' de cada VM e TESTE voltar um deles:
             virsh snapshot-create-as rhel limpo
             virsh snapshot-create-as ubuntu limpo
             (crie um arquivo qualquer na rhel)  →  virsh snapshot-revert rhel limpo  →  o arquivo sumiu?
           Nos cenários de "quebrar e consertar", o treino tira snapshots sozinho.
           """,
           checks=[("snapshot 'limpo' na rhel", f"{V} snapshot-list rhel --name | grep -qx limpo"),
                   ("snapshot 'limpo' na ubuntu", f"{V} snapshot-list ubuntu --name | grep -qx limpo")]),
    Escolha(id="s00.snap.2", titulo="Snapshot é backup?",
            enunciado="Snapshot substitui backup?",
            opcoes=["Sim", "Não: ele mora dentro do mesmo arquivo .qcow2; se o arquivo se perder, o snapshot vai junto",
                    "Sim, se a VM estiver desligada", "Só no RHEL"], correta="b"),

    # ── Git ──
    Tarefa(id="s00.git", titulo="Repositório linux-lab no GitHub",
           enunciado="""
           Transforme ~/linux-lab num repositório e publique (o .gitignore já existe):
             cd ~/linux-lab && git init -b main
             crie DIFERENCAS.md (tabela RHEL × Ubuntu que você preenche ao longo do plano)
             git add . && git commit -m "início do laboratório"
             crie o repositório no GitHub → git remote add origin ... → git push -u origin main
           """,
           checks=[("é um repositório git", "git -C ~/linux-lab rev-parse --is-inside-work-tree >/dev/null 2>&1"),
                   ("remote aponta para o GitHub", "git -C ~/linux-lab remote get-url origin 2>/dev/null | grep -q github.com"),
                   ("DIFERENCAS.md existe", "test -f ~/linux-lab/DIFERENCAS.md"),
                   ("pasta .sandbox do treino ignorada", "git -C ~/linux-lab check-ignore -q treino/.sandbox/x"),
                   ("já fez push", "git -C ~/linux-lab rev-parse -q --verify '@{u}' >/dev/null 2>&1")]),

    # ── vi ──
    Marco(id="s00.vimtutor", titulo="vimtutor completo",
          enunciado="Rode `vimtutor` e faça as 7 lições (~30 min). O vi cai na LPIC-1 e é o editor de todo servidor."),
    Quiz(id="s00.vi.1", titulo="vi: salvar e sair", exato=True,
         enunciado="No vi, no modo normal, qual comando salva e sai?",
         respostas=[":wq", ":x", "ZZ", ":wq!"], resposta=":wq  (ou :x ou ZZ)"),
    Quiz(id="s00.vi.2", titulo="vi: sair sem salvar", exato=True,
         enunciado="E para sair DESCARTANDO as alterações?", respostas=[":q!"]),
    Quiz(id="s00.vi.3", titulo="vi: apagar linha", exato=True,
         enunciado="Qual comando apaga a linha inteira onde está o cursor?", respostas=["dd"]),
    Quiz(id="s00.vi.4", titulo="vi: desfazer", exato=True,
         enunciado="Qual tecla desfaz a última alteração?", respostas=["u"]),
    Quiz(id="s00.vi.5", titulo="vi: buscar", exato=True,
         enunciado="Como buscar a palavra 'erro' para frente no arquivo?", respostas=["/erro"]),
    Quiz(id="s00.vi.6", titulo="vi: última linha", exato=True,
         enunciado="Como ir para a ÚLTIMA linha do arquivo?", respostas=["G", ":$"]),
    Quiz(id="s00.vi.7", titulo="vi: copiar e colar", exato=True,
         enunciado="Quais teclas copiam a linha atual e colam abaixo? (escreva juntas, ex.: abc)",
         respostas=["yyp"], resposta="yy (copia) + p (cola abaixo) → yyp"),
    Quiz(id="s00.vi.8", titulo="vi: substituir no arquivo todo", exato=True,
         enunciado="Comando para trocar TODAS as ocorrências de http por https no arquivo inteiro:",
         respostas=[":%s/http/https/g"]),

    # ── rede do lab ──
    Quiz(id="s00.net.1", titulo="Rede padrão do libvirt",
         enunciado="Qual é a rede (em CIDR) da rede 'default' (NAT) do libvirt, onde suas VMs ganham IP?",
         respostas=["192.168.122.0/24"]),
    PerguntaVM(id="s00.net.2", titulo="Gateway da rhel", host="rhel", root=False,
               enunciado="Qual é o gateway padrão da VM rhel? (só o IP)",
               cmd="ip route show default | awk '{print $3; exit}'",
               dica="Na VM: ip route  (a linha 'default via ...')",
               explicacao="É o IP do seu Fedora na ponte virbr0. Ele faz NAT para as VMs saírem para a internet."),
    PerguntaVM(id="s00.net.3", titulo="DNS da ubuntu", host="ubuntu", root=False,
               enunciado="Qual 'nameserver' aparece em /etc/resolv.conf da ubuntu?",
               cmd="awk '/^nameserver/{print $2; exit}' /etc/resolv.conf",
               explicacao="""
               127.0.0.53 é o stub do systemd-resolved: um resolvedor local que repassa para o DNS real.
               Para ver o DNS de verdade: resolvectl status. Anote essa diferença em DIFERENCAS.md.
               """),
    Escolha(id="s00.net.4", titulo="Como a VM chega na internet",
            enunciado="Sua VM tem IP 192.168.122.50. Como ela acessa a internet?",
            opcoes=["Ela recebe um IP público do seu provedor",
                    "O Fedora faz NAT: troca o IP de origem 192.168.122.50 pelo IP dele antes de mandar para o roteador",
                    "Ela usa a placa Wi-Fi do notebook diretamente",
                    "O libvirt cria uma VPN até a internet"],
            correta="b",
            explicacao="É NAT (mais precisamente masquerade/PAT). Na semana 9 você monta um roteador NAT na mão."),

    # ── se sobrar tempo ──
    Tarefa(id="s00.kali", titulo="Se sobrar tempo: importar o Kali (guia §3 e §4)",
           enunciado="""
           Baixe a imagem QEMU pronta do Kali (kali.org/get-kali → Virtual Machines → QEMU), extraia com 7z,
           mova o .qcow2 para /var/lib/libvirt/images/kali.qcow2 e importe no virt-manager
           (Importar imagem de disco existente · 2048 MB · nome kali). Login: kali / kali. TROQUE a senha.
           Se não der tempo agora, faça antes da sexta da semana 2 (é lá que o kali entra).
           """,
           checks=[("VM kali existe", f"{V} dominfo kali >/dev/null 2>&1")]),
]
