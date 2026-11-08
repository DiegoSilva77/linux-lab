import re

from motor import REINICIOU, MARCA_QUEBRA, Comando, Escolha, Marco, PerguntaVM, Quiz, Tarefa, cmd, rx

TITULO = "Boot, GRUB, bibliotecas e pacotes · reta final da 101"
DATAS = "14–20/12"
OBJETIVO = """
Controlar como o sistema sobe e o que está instalado, nas duas famílias.
Teoria: 101.2, 102.2, 102.3, 102.4, 102.5, 102.6. Na sexta e no sábado: `treino simulado 101`.
"""

EXERCICIOS = [
    # ── boot ──
    Quiz(id="s05.boot.1", titulo="Ordem do boot",
         enunciado="""
         Ordene o boot (letras):
           a) systemd (PID 1)   b) firmware BIOS/UEFI   c) kernel   d) GRUB   e) initramfs
         """,
         respostas=[lambda r: re.sub(r"[^a-e]", "", r.lower()) == "bdcea"], resposta="b d c e a"),
    Quiz(id="s05.boot.2", titulo="Mensagens do kernel",
         enunciado="Comando clássico para ver as mensagens do kernel (buffer do boot):",
         respostas=[cmd(r"dmesg( .*)?"), cmd(r"journalctl -k( .*)?"), cmd(r"journalctl -b -k")], resposta="dmesg"),
    Quiz(id="s05.boot.3", titulo="Logs do boot anterior",
         enunciado="Com journalctl, como ver os logs do boot ANTERIOR (útil depois de um travamento)?",
         respostas=[cmd(r"journalctl -b -1( .*)?"), cmd(r"journalctl --boot=-1( .*)?")], resposta="journalctl -b -1",
         explicacao="Só funciona com journal persistente (/var/log/journal existe). No RHEL você pode precisar criá-lo."),
    Escolha(id="s05.boot.4", titulo="BIOS × UEFI",
            enunciado="Quais são verdadeiras sobre UEFI?",
            opcoes=["Usa uma partição ESP (FAT32) com os bootloaders", "Só funciona com MBR",
                    "Suporta Secure Boot", "Não existe em servidores"], correta="ac"),
    Quiz(id="s05.grub.1", titulo="GRUB no RHEL",
         enunciado="Comando para regenerar a configuração do GRUB2 no RHEL (BIOS):",
         respostas=[cmd(r"grub2-mkconfig -o /boot/grub2/grub\.cfg")],
         resposta="grub2-mkconfig -o /boot/grub2/grub.cfg",
         explicacao="No RHEL moderno também existe o grubby para mexer em parâmetros do kernel."),
    Quiz(id="s05.grub.2", titulo="GRUB no Ubuntu",
         enunciado="E o atalho equivalente no Ubuntu?", respostas=[cmd("update-grub")], resposta="update-grub"),
    Quiz(id="s05.grub.3", titulo="Parâmetro de kernel",
         enunciado="Que parâmetro de kernel você adiciona no GRUB para subir direto no rescue.target?",
         respostas=["systemd.unit=rescue.target", "rescue", "single", "1", "s"], resposta="systemd.unit=rescue.target"),
    Quiz(id="s05.grub.4", titulo="Arquivo de padrões do GRUB",
         enunciado="Em qual arquivo você muda os padrões do GRUB (timeout, parâmetros) antes de regenerar a configuração?",
         respostas=["/etc/default/grub"]),

    # ── bibliotecas e virtualização ──
    Quiz(id="s05.lib.1", titulo="Dependências de um binário",
         enunciado="Comando que mostra as bibliotecas compartilhadas de que um binário depende:",
         respostas=[rx(r"ldd( \S+)?")], resposta="ldd /caminho/do/binario"),
    Comando(id="s05.lib.2", titulo="ldd na prática",
            enunciado="Mostre só os NOMES (1ª coluna) das bibliotecas de que /usr/bin/ls depende.",
            esperado="ldd /usr/bin/ls | awk '{print $1}'"),
    Quiz(id="s05.lib.3", titulo="Cache de bibliotecas",
         enunciado="Comando que atualiza o cache de bibliotecas depois de instalar uma lib em /usr/local/lib:",
         respostas=[cmd("ldconfig")], resposta="ldconfig"),
    Quiz(id="s05.lib.4", titulo="Caminho extra de libs",
         enunciado="Qual variável de ambiente acrescenta diretórios de bibliotecas só para um comando?",
         respostas=["LD_LIBRARY_PATH"], exato=True,
         explicacao="Atacantes abusam disso (e do LD_PRELOAD) para injetar código. Por isso o sudo limpa essas variáveis."),
    Escolha(id="s05.virt.1", titulo="VM × container",
            enunciado="Qual a principal diferença entre VM e container?",
            opcoes=["Container é mais lento", "A VM tem kernel próprio; o container compartilha o kernel do host",
                    "Container precisa de hipervisor", "Não há diferença"], correta="b"),
    Escolha(id="s05.virt.2", titulo="Clonar VM",
            enunciado="Ao clonar uma VM Linux, o que deve ser regenerado para evitar conflitos?",
            opcoes=["/etc/machine-id e as chaves de host do SSH", "O kernel", "O /etc/passwd", "Nada"],
            correta="a",
            explicacao="O cloud-init faz isso automaticamente em nuvem, junto com hostname, usuário e chaves."),

    # ── Debian ──
    Quiz(id="s05.deb.1", titulo="dpkg: de onde veio o arquivo",
         enunciado="No Debian/Ubuntu, comando para descobrir de qual pacote veio /usr/bin/ss:",
         respostas=[cmd(r"dpkg (-S|--search) /usr/bin/ss")], resposta="dpkg -S /usr/bin/ss"),
    Quiz(id="s05.deb.2", titulo="dpkg: arquivos de um pacote",
         enunciado="E para listar os arquivos instalados pelo pacote openssh-server?",
         respostas=[cmd(r"dpkg (-L|--listfiles) openssh-server")], resposta="dpkg -L openssh-server"),
    Escolha(id="s05.deb.3", titulo="remove × purge",
            enunciado="Diferença entre `apt remove` e `apt purge`:",
            opcoes=["Nenhuma", "purge também apaga os arquivos de configuração", "remove apaga as configurações",
                    "purge só limpa o cache"], correta="b"),
    Escolha(id="s05.deb.4", titulo="update × upgrade",
            enunciado="O que faz `apt update`?",
            opcoes=["Atualiza os pacotes instalados", "Atualiza a LISTA de pacotes disponíveis nos repositórios",
                    "Atualiza o kernel", "Atualiza o apt"], correta="b"),
    Quiz(id="s05.deb.5", titulo="Repositórios no Ubuntu",
         enunciado="Em que diretório ficam os arquivos de repositórios adicionais do apt?",
         respostas=["/etc/apt/sources.list.d", "/etc/apt/sources.list.d/"]),
    PerguntaVM(id="s05.deb.6", titulo="Investigação na ubuntu", host="ubuntu", root=False,
               enunciado="De qual pacote veio o comando ss na ubuntu? (só o nome do pacote)",
               cmd="dpkg -S ss 2>/dev/null | grep -E ': (/usr)?/bin/ss$' | head -1 | cut -d: -f1"),
    Tarefa(id="s05.deb.7", titulo="Instalar e purgar", host="ubuntu",
           enunciado="Na ubuntu, instale o pacote 'tree' com apt e depois remova-o COM os arquivos de configuração.",
           checks=[("o histórico do apt mostra o purge",
                    "grep -Eq 'Commandline: apt(-get)? (purge|remove --purge|autoremove --purge) .*tree' /var/log/apt/history.log"),
                   ("tree não está mais instalado", "! dpkg -l tree 2>/dev/null | grep -q '^ii'")]),

    # ── Red Hat ──
    Comando(id="s05.rpm.1", titulo="rpm: de onde veio (no seu Fedora)",
            enunciado="No seu Fedora: de qual pacote veio /usr/bin/ls? Use o rpm.",
            esperado="rpm -qf /usr/bin/ls"),
    Comando(id="s05.rpm.2", titulo="rpm: arquivos de configuração",
            enunciado="Liste os arquivos de CONFIGURAÇÃO do pacote bash (com rpm).",
            esperado="rpm -qc bash"),
    Comando(id="s05.rpm.3", titulo="Quantos pacotes",
            enunciado="Quantos pacotes RPM estão instalados no seu Fedora? (só o número)",
            esperado="rpm -qa | wc -l"),
    Quiz(id="s05.rpm.4", titulo="rpm -V",
         enunciado="Qual opção do rpm VERIFICA se os arquivos de um pacote foram alterados (útil em resposta a incidente)?",
         respostas=["-V", "--verify"], exato=True,
         explicacao="rpm -Va verifica TODOS os pacotes. Um 5 na saída = hash diferente. Binário do sistema alterado é sinal de rootkit."),
    Quiz(id="s05.rpm.5", titulo="Quem fornece um arquivo",
         enunciado="Comando dnf para descobrir qual pacote (instalado ou não) fornece o arquivo /usr/bin/dig:",
         respostas=[cmd(r"dnf (provides|whatprovides) /usr/bin/dig")], resposta="dnf provides /usr/bin/dig"),
    Quiz(id="s05.rpm.6", titulo="Desfazer transação",
         enunciado="Comando dnf para desfazer a ÚLTIMA transação:",
         respostas=[cmd(r"dnf history undo last")], resposta="dnf history undo last"),
    Quiz(id="s05.rpm.7", titulo="Repositórios no RHEL",
         enunciado="Em que diretório ficam os arquivos .repo do dnf?",
         respostas=["/etc/yum.repos.d", "/etc/yum.repos.d/"]),
    Escolha(id="s05.rpm.8", titulo="zypper",
            enunciado="O zypper (cai na LPIC) é o gerenciador de pacotes de qual distribuição?",
            opcoes=["Debian", "openSUSE/SUSE", "Arch", "Alpine"], correta="b"),
    PerguntaVM(id="s05.rpm.9", titulo="Investigação na rhel", host="rhel", root=False,
               enunciado="De qual pacote veio o comando ss na rhel? (só o NOME, sem versão)",
               cmd="rpm -qf --qf '%{NAME}\\n' /usr/bin/ss",
               explicacao="Compare com a ubuntu: o nome do pacote muda entre famílias (anote em DIFERENCAS.md)."),

    # ── cenários de boot ──
    Tarefa(id="s05.vm.target", titulo="Cenário: VM que sobe no lugar errado", host="rhel",
           enunciado="""
           Vou mudar o target padrão da rhel. REINICIE a VM e veja no console o que acontece.
           Conserte para ela voltar a subir normal (multiusuário, com rede).
           """,
           quebrar="systemctl set-default rescue.target >/dev/null 2>&1" + MARCA_QUEBRA,
           checks=[("target padrão é multi-user", '[ "$(systemctl get-default)" = multi-user.target ]'),
                   ("você reiniciou depois da quebra", REINICIOU)],
           dica="systemctl get-default / set-default. No console, a senha de root pode ser pedida para entrar no rescue."),
    Tarefa(id="s05.vm.root", titulo="Cenário: senha de root perdida", host="rhel",
           enunciado="""
           Vou trocar a senha de root da rhel por uma aleatória. Sem usar sudo (finja que não tem),
           RESETE a senha de root pelo GRUB (rd.break no RHEL) para:  Treino123!
           Não esqueça do SELinux (touch /.autorelabel) antes de reiniciar.
           """,
           quebrar='echo "root:$(head -c 24 /dev/urandom | base64)" | chpasswd',
           checks=[("a senha do root agora é Treino123!",
                    r"""h=$(getent shadow root | cut -d: -f2)
                    python3 -W ignore -c 'import crypt,sys; sys.exit(0 if crypt.crypt("Treino123!", sys.argv[1]) == sys.argv[1] else 1)' "$h" 2>/dev/null \
                    || perl -e 'exit(crypt("Treino123!", $ARGV[0]) eq $ARGV[0] ? 0 : 1)' "$h" """)],
           dica="No GRUB, aperte 'e', adicione rd.break no fim da linha 'linux', Ctrl+X. Depois: mount -o remount,rw /sysroot · chroot /sysroot · passwd · touch /.autorelabel"),
    Marco(id="s05.simulado", titulo="Simulados da 101",
          enunciado="Rode `treino simulado 101` pelo menos 2 vezes (sexta e sábado). Meta: 75% ou mais antes da prova."),
]
