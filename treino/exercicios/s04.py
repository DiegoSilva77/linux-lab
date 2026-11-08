import ipaddress

from motor import REINICIOU, MARCA_QUEBRA, Comando, Escolha, Quiz, Subnet, Tarefa, cmd, rx

TITULO = "Hardware, discos, LVM e evidência forense + IPv6"
DATAS = "07–13/12"
OBJETIVO = """
Gerenciar discos como em produção e dar os primeiros passos em evidência forense (ISO 27037).
⚠️  Compre o voucher da 101 até 07/12 e agende a prova para ~21/12.
Teoria: 101.1, 102.1, 104.1, 104.2, 104.3.
Nas VMs com VirtIO, os discos extras aparecem como /dev/vdb e /dev/vdc (confira com lsblk).
"""


def _ipv6(certo):
    def f(r):
        try:
            return r.strip() == ipaddress.ip_address(certo).compressed
        except ValueError:
            return False
    return f


EXERCICIOS = [
    # ── hardware ──
    Quiz(id="s04.hw.1", titulo="Dispositivos PCI", enunciado="Comando que lista os dispositivos PCI:",
         respostas=[cmd(r"lspci( -[a-zA-Z]+)*")], resposta="lspci"),
    Quiz(id="s04.hw.2", titulo="Dispositivos USB", enunciado="E os dispositivos USB?",
         respostas=[cmd(r"lsusb( -[a-zA-Z]+)*")], resposta="lsusb"),
    Quiz(id="s04.hw.3", titulo="Módulos carregados", enunciado="Comando que lista os módulos do kernel carregados:",
         respostas=[cmd("lsmod")], resposta="lsmod"),
    Quiz(id="s04.hw.4", titulo="Remover módulo", enunciado="Comando para descarregar o módulo 'usb_storage' (com dependências):",
         respostas=[cmd(r"modprobe -r usb_storage")], resposta="modprobe -r usb_storage",
         explicacao="Bloquear usb_storage (blacklist em /etc/modprobe.d/) é uma medida clássica contra vazamento por pendrive."),
    Escolha(id="s04.hw.5", titulo="/proc × /sys",
            enunciado="Sobre /proc e /sys:",
            opcoes=["São diretórios no disco com logs", "São sistemas de arquivos virtuais gerados pelo kernel na memória",
                    "/proc guarda programas e /sys guarda bibliotecas", "Só existem no RHEL"],
            correta="b"),
    Escolha(id="s04.hw.6", titulo="udev",
            enunciado="O que o udev faz?",
            opcoes=["Gerencia usuários", "Cria e gerencia os arquivos de dispositivo em /dev quando o hardware aparece",
                    "Atualiza o kernel", "Monta o /home"], correta="b"),

    # ── discos e filesystems ──
    Quiz(id="s04.fs.1", titulo="Partições primárias MBR",
         enunciado="Quantas partições PRIMÁRIAS o MBR permite?", respostas=["4"],
         explicacao="Por isso existem as partições estendidas/lógicas. O GPT permite 128 por padrão e discos acima de 2 TiB."),
    Escolha(id="s04.fs.2", titulo="Ferramentas de partição",
            enunciado="Qual ferramenta foi feita especificamente para tabelas GPT?",
            opcoes=["fdisk", "gdisk", "mkfs", "fsck"], correta="b",
            explicacao="Hoje o fdisk também entende GPT, mas gdisk/sgdisk e parted são as clássicas para GPT."),
    Escolha(id="s04.fs.3", titulo="Encolher filesystem",
            enunciado="Qual destes NÃO pode ser reduzido (encolhido)?",
            opcoes=["ext4", "XFS", "Os dois podem", "Nenhum pode"], correta="b",
            explicacao="O XFS só cresce. O ext4 encolhe, mas desmontado (resize2fs). Anote em DIFERENCAS.md: RHEL usa XFS e Ubuntu usa ext4."),
    Quiz(id="s04.fs.4", titulo="Campos do fstab",
         enunciado="Quantos campos tem uma linha do /etc/fstab?", respostas=["6"],
         explicacao="dispositivo · ponto de montagem · tipo · opções · dump · pass (ordem do fsck no boot)."),
    Quiz(id="s04.fs.5", titulo="Testar o fstab",
         enunciado="Comando que monta tudo do fstab que ainda não está montado (para testar ANTES de reiniciar):",
         respostas=[cmd(r"mount -a")], resposta="mount -a"),
    Quiz(id="s04.fs.6", titulo="Descobrir UUID",
         enunciado="Comando que mostra o UUID das partições:",
         respostas=[cmd(r"blkid( .*)?"), cmd(r"lsblk -f( .*)?")], resposta="blkid  (ou lsblk -f)"),
    Quiz(id="s04.fs.7", titulo="Opção noexec",
         enunciado="Qual opção de montagem impede executar binários na partição?", respostas=["noexec"]),
    Quiz(id="s04.fs.8", titulo="Opção nosuid",
         enunciado="E qual faz o kernel ignorar o bit SUID nos arquivos da partição?", respostas=["nosuid"]),
    Quiz(id="s04.lvm.1", titulo="LVM: estender com o filesystem",
         enunciado="Qual opção do lvextend estende também o filesystem, no mesmo comando?",
         respostas=["-r", "--resizefs"]),
    Escolha(id="s04.lvm.2", titulo="LVM: ordem",
            enunciado="Qual é a ordem para usar LVM num disco novo?",
            opcoes=["lvcreate → vgcreate → pvcreate", "pvcreate → vgcreate → lvcreate → mkfs",
                    "mkfs → pvcreate → lvcreate", "vgcreate → pvcreate → mkfs"], correta="b"),
    Quiz(id="s04.fsck", titulo="Reparar XFS",
         enunciado="O fsck não repara XFS. Qual ferramenta repara?", respostas=["xfs_repair"]),

    # ── na VM ──
    Tarefa(id="s04.vm.lvm", titulo="LVM do zero", host="rhel",
           enunciado="""
           Na rhel, com os discos extras (/dev/vdb e /dev/vdc):
             · PVs nos dois discos, VG 'vg_dados' com os dois
             · LV 'lv_dados' de 3 GiB, formatado em XFS
             · montado em /dados no boot, via UUID no /etc/fstab (teste com mount -a)
           """,
           checks=[("VG vg_dados existe", "vgs vg_dados >/dev/null 2>&1"),
                   ("VG usa 2 PVs", '[ "$(vgs --noheadings -o pv_count vg_dados | tr -d " ")" -ge 2 ]'),
                   ("LV lv_dados existe", "lvs vg_dados/lv_dados >/dev/null 2>&1"),
                   ("/dados montado com XFS", '[ "$(findmnt -n -o FSTYPE /dados)" = xfs ]'),
                   ("fstab usa UUID para /dados", "grep -Eq '^UUID=[^ ]+[[:space:]]+/dados[[:space:]]' /etc/fstab")],
           dica="pvcreate /dev/vdb /dev/vdc · vgcreate vg_dados /dev/vdb /dev/vdc · lvcreate -n lv_dados -L 3G vg_dados · mkfs.xfs /dev/vg_dados/lv_dados · blkid"),
    Tarefa(id="s04.vm.lvext", titulo="Desafio de sábado: disco cheio em produção", host="rhel",
           enunciado="O /dados ficou pequeno. Estenda lv_dados para PELO MENOS 6 GiB SEM desmontar, e o filesystem junto.",
           checks=[("LV com ≥ 6 GiB",
                    '[ "$(lvs --noheadings --units m --nosuffix -o lv_size vg_dados/lv_dados | cut -d. -f1 | tr -d " ")" -ge 6000 ]'),
                   ("filesystem acompanhou (df ≥ 5,9 GiB)",
                    '[ "$(df -BM --output=size /dados | tail -1 | tr -dc 0-9)" -ge 5900 ]'),
                   ("continua montado", "findmnt /dados >/dev/null")]),
    Tarefa(id="s04.vm.ext4", titulo="ext4 com opções de segurança", host="ubuntu",
           enunciado="""
           Na ubuntu, com o disco extra (/dev/vdb): crie uma partição GPT, formate em ext4 e monte em /backup
           no boot, via UUID, com as opções nosuid, noexec e nodev.
           """,
           checks=[("/backup é ext4", '[ "$(findmnt -n -o FSTYPE /backup)" = ext4 ]'),
                   ("com noexec, nosuid e nodev",
                    "o=$(findmnt -n -o OPTIONS /backup); echo $o | grep -q noexec && echo $o | grep -q nosuid && echo $o | grep -q nodev"),
                   ("fstab usa UUID", "grep -Eq '^UUID=[^ ]+[[:space:]]+/backup[[:space:]]' /etc/fstab")]),
    Tarefa(id="s04.vm.swap", titulo="Swap em arquivo", host="rhel",
           enunciado="Na rhel, crie um swap de 512 MiB em /swapfile, ative e deixe persistente no fstab.",
           checks=[("/swapfile ativo", "swapon --show=NAME --noheadings | grep -qx /swapfile"),
                   ("permissão 600", '[ "$(stat -c %a /swapfile)" = 600 ]'),
                   ("no fstab", "grep -Eq '^/swapfile[[:space:]]' /etc/fstab")],
           dica="dd if=/dev/zero of=/swapfile bs=1M count=512 · chmod 600 · mkswap · swapon. No XFS, evite fallocate para swap."),
    Tarefa(id="s04.vm.fstab", titulo="Cenário: fstab quebrado", host="rhel",
           enunciado="""
           Vou colocar uma linha com um UUID inexistente no /etc/fstab da rhel.
           Depois, REINICIE a VM (sudo reboot) e veja o que acontece no console (virt-manager).
           Conserte pelo emergency mode, sem restaurar snapshot.
           """,
           quebrar='mkdir -p /arquivo && echo "UUID=00000000-dead-beef-0000-000000000000 /arquivo xfs defaults 0 0" >> /etc/fstab' + MARCA_QUEBRA,
           checks=[("fstab sem o UUID inválido", "! grep -q dead-beef /etc/fstab"),
                   ("mount -a sem erros", "mount -a"),
                   ("sistema subiu normal", "systemctl is-system-running | grep -Eq 'running|degraded'"),
                   ("você reiniciou depois da quebra", REINICIOU)],
           dica="No emergency mode, a raiz pode estar só-leitura: mount -o remount,rw / · edite o fstab · systemctl daemon-reload · reboot"),

    # ── forense ──
    Comando(id="s04.for.hash", titulo="Hash de evidência",
            enunciado="Gere o SHA-256 de disco.img e salve em disco.img.sha256, no formato do próprio sha256sum.",
            verificar=[("sha256sum -c confere", "sha256sum -c disco.img.sha256 >/dev/null 2>&1")],
            resposta="sha256sum disco.img > disco.img.sha256"),
    Comando(id="s04.for.dd", titulo="Cópia bit a bit",
            enunciado="Faça uma cópia bit a bit de disco.img para evidencia.img usando dd.",
            exigir=["dd"], verificar=[("cópia idêntica", "cmp -s disco.img evidencia.img")],
            resposta="dd if=disco.img of=evidencia.img bs=4M status=none"),
    Comando(id="s04.for.check", titulo="Conferir integridade",
            enunciado="Já existe disco.img.sha256. Verifique a integridade de disco.img contra ele.",
            preparar="sha256sum disco.img > disco.img.sha256",
            esperado="sha256sum -c disco.img.sha256"),
    Comando(id="s04.for.strings", titulo="Texto escondido na imagem",
            enunciado="disco.img é uma 'imagem' cheia de dados aleatórios. Encontre a linha que começa com SENHA= dentro dela.",
            esperado="strings disco.img | grep SENHA=",
            dica="O comando strings extrai sequências de texto legível de arquivos binários.",
            explicacao="strings é uma das primeiras ferramentas de forense e de análise de malware (você verá no 2º ano)."),
    Escolha(id="s04.for.why", titulo="Por que hash e custódia", prova="",
            enunciado="Por que gerar o hash da evidência ANTES e DEPOIS da cópia, e registrar quem a manipulou?",
            opcoes=["Para comprimir a imagem", "Para provar que a evidência não foi alterada (integridade e cadeia de custódia)",
                    "Para criptografar a evidência", "Só por boa prática, sem valor legal"], correta="b",
            explicacao="Sem isso a evidência pode ser contestada. É o centro da ISO 27037, que você verá em Cyber Defense Operations."),
    Tarefa(id="s04.vm.fim", titulo="FIM do Wazuh em /etc", host="rhel",
           enunciado="""
           Ative o monitoramento de integridade (syscheck) do Wazuh em TEMPO REAL para /etc na rhel
           (em /var/ossec/etc/ossec.conf, atributo realtime="yes"), reinicie o agente e altere /etc/motd.
           Confira o alerta no painel do Wazuh.
           """,
           checks=[("syscheck realtime em /etc",
                    "grep -Eq '<directories[^>]*realtime=\"yes\"[^>]*>[^<]*/etc' /var/ossec/etc/ossec.conf"),
                   ("agente ativo", "systemctl is-active --quiet wazuh-agent")]),

    # ── IPv6 ──
    Quiz(id="s04.v6.1", titulo="Abreviar IPv6", prova="102",
         enunciado="Escreva na forma mais curta: 2001:0db8:0000:0000:0000:ff00:0042:8329",
         respostas=[_ipv6("2001:db8::ff00:42:8329")], resposta="2001:db8::ff00:42:8329",
         explicacao="Tire os zeros à esquerda de cada bloco e troque UMA sequência de blocos zerados por ::"),
    Quiz(id="s04.v6.2", titulo="Link-local", prova="102",
         enunciado="Qual o prefixo dos endereços IPv6 link-local? (CIDR)", respostas=["fe80::/10"]),
    Quiz(id="s04.v6.3", titulo="Loopback IPv6", prova="102",
         enunciado="Qual o endereço de loopback em IPv6?", respostas=["::1"]),
    Subnet(id="s04.subnet", titulo="Bateria de subnetting /16 a /30",
           enunciado="Agora com prefixos maiores. Meta: 8 de 10.", n=10, prefixos=(16, 30), meta=8),
]
