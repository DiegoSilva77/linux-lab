# Guia do laboratório: KVM do zero

> Leia antes de rodar `treino 0`. Ao final você terá 3 VMs (`rhel`, `ubuntu`, `kali`) no seu Fedora, sabendo ligar, desligar, acessar e tirar snapshot delas.

---

## 1. Como a virtualização funciona no Linux

São 4 peças, e vale entender quem faz o quê:

| Peça | O que é | Analogia |
|---|---|---|
| **KVM** | Módulo do kernel Linux que usa a extensão de virtualização da CPU (Intel VT-x / AMD-V) para rodar VMs quase na velocidade nativa | O motor |
| **QEMU** | Programa que emula o resto do hardware da VM (disco, placa de rede, vídeo, USB). Cada VM ligada é um processo `qemu-kvm` no seu Fedora | A carroceria |
| **libvirt** | Serviço (daemon) que gerencia as VMs: guarda as configurações, cria as redes virtuais, liga/desliga, tira snapshots | O painel de controle |
| **virt-manager** / **virsh** | As interfaces para o libvirt: o virt-manager é gráfico, o `virsh` é de linha de comando. Fazem a mesma coisa | O volante |

É a mesma pilha usada pela Red Hat (OpenShift Virtualization), por OpenStack e Proxmox, e por baixo de muitas nuvens. Saber KVM é conhecimento de mercado, não só de laboratório.

### Onde as coisas ficam no seu Fedora
| O quê | Onde |
|---|---|
| Discos das VMs (arquivos `.qcow2`) | `/var/lib/libvirt/images/` |
| Configuração de cada VM (XML) | `/etc/libvirt/qemu/<nome>.xml` (veja com `virsh dumpxml rhel`, nunca edite à mão; use `virsh edit`) |
| Logs do QEMU por VM | `/var/log/libvirt/qemu/<nome>.log` |
| Rede virtual padrão | ponte `virbr0`, rede `192.168.122.0/24`, com DHCP e DNS (dnsmasq) e NAT para a internet |

### `qemu:///system` × `qemu:///session`
O libvirt tem duas "conexões":
- **`qemu:///system`**: VMs do sistema, com rede NAT completa. **É a que vamos usar**, e é a padrão do virt-manager.
- `qemu:///session`: VMs do seu usuário, com rede limitada.

O `virsh` sem configuração usa a `session`, o que confunde ("cadê minha VM?"). Por isso o passo 2 configura o padrão.

### O formato qcow2
- O disco "de 20 GB" começa ocupando quase nada e cresce conforme a VM grava.
- Ele suporta **snapshots internos**, que é como os cenários do `treino` voltam no tempo.

---

## 2. Instalação e verificação

Sua CPU já tem a virtualização ativada (eu conferi: flags `vmx`/`svm` presentes).

```bash
sudo dnf install @virtualization          # qemu-kvm, libvirt, virt-manager, virt-install...
sudo systemctl enable --now libvirtd
sudo usermod -aG libvirt $USER            # permite gerenciar VMs sem sudo
echo 'export LIBVIRT_DEFAULT_URI=qemu:///system' >> ~/.bashrc   # virsh passa a usar a conexão certa
```
**Faça logout e login** (ou reinicie) para o grupo e a variável valerem. Depois confira, **antes de qualquer outro comando virsh**:

```bash
virsh uri                        # TEM que mostrar qemu:///system. Se mostrar qemu:///session, pare:
                                 # o que você criar vai para o lugar errado (rode: source ~/.bashrc)
id -nG | grep -w libvirt         # o grupo já vale nesta sessão?
lsmod | grep kvm                 # deve aparecer kvm_intel ou kvm_amd
virsh list --all                 # sem erro (lista vazia por enquanto)
virsh net-list --all             # a rede 'default' deve estar active e autostart yes
```

No Fedora, a rede `default` normalmente **já vem ativa**. Se você rodar `net-start` assim mesmo, o erro "network is already active" é inofensivo. Só se ela estiver inativa:
```bash
virsh net-start default && virsh net-autostart default
```

Se a lista de *storage pools* não tiver a `default`, crie (é onde ficam discos e ISOs):
```bash
virsh pool-list --all
# se não houver 'default':
virsh pool-define-as default dir --target /var/lib/libvirt/images
virsh pool-start default && virsh pool-autostart default
```

---

## 3. Baixar as ISOs

**Faça os downloads em paralelo agora.** Juntos passam de 10 GB.

| VM | Onde baixar | Qual arquivo |
|---|---|---|
| `rhel` | **developers.redhat.com** → crie a conta gratuita (Red Hat Developer Subscription for Individuals) → Downloads → Red Hat Enterprise Linux | **Somente a "RHEL 10.x Binary DVD (x86_64)"** (`rhel-10.x-x86_64-dvd.iso`). ⚠️ **Não use a "Boot ISO"**: ela não tem pacotes, exige registro e internet durante a instalação e dá muito mais trabalho |
| `rhel` (alternativa) | **rockylinux.org/download** | Rocky Linux 10, x86_64, ISO **DVD**. É clone do RHEL e dispensa conta e registro |
| `ubuntu` | **ubuntu.com/download/server** | Ubuntu **Server** LTS mais recente (não a Desktop) |
| `kali` | **kali.org/get-kali** → *Virtual Machines* → **QEMU** | Imagem **pronta** (`.qcow2` compactado em `.7z`). É só importar, sem instalar. Usuário e senha: `kali` / `kali` |

**RHEL ou Rocky?** O RHEL é o "de verdade" (registro e `subscription-manager`, igual em empresa). O Rocky é idêntico nos comandos e mais simples. O `treino` funciona com os dois. Recomendo o **RHEL**, porque registrar o sistema também é aprendizado.

### Confira a integridade (primeiro exercício de segurança do plano)
Cada site publica o hash SHA-256 das ISOs. Antes de usar, confira:
```bash
cd ~/Downloads
sha256sum ubuntu-*-live-server-amd64.iso
# compare com o arquivo SHA256SUMS do site (ou: sha256sum -c SHA256SUMS --ignore-missing)
```
Se o hash não bater, a ISO veio corrompida ou adulterada. Esse é um exemplo real de *supply chain attack*: já houve casos de ISOs trocadas em sites invadidos.

### Coloque as ISOs no lugar certo
O processo do QEMU roda como um usuário de sistema (`qemu`) e **não consegue ler a sua home**. Mova as ISOs para a pasta do libvirt:
```bash
sudo mv ~/Downloads/*.iso /var/lib/libvirt/images/
virsh pool-refresh default
virsh vol-list default            # as ISOs devem aparecer aqui
```
Para o Kali:
```bash
sudo dnf install p7zip p7zip-plugins
7z x kali-linux-*-qemu-amd64.7z
sudo mv kali-linux-*.qcow2 /var/lib/libvirt/images/kali.qcow2
```

---

## 4. Criar as VMs no virt-manager

Abra o **Gerenciador de máquinas virtuais** (virt-manager). Ele já conecta em "QEMU/KVM", que é a `qemu:///system`.

### VM `rhel`
1. **Arquivo → Nova máquina virtual → Mídia de instalação local (ISO)**.
2. **Procurar** → escolha a ISO do RHEL na pool `default`. O sistema operacional costuma ser detectado sozinho; se não for, digite "rhel10" ou "rocky".
   - Se a versão exata não aparecer na lista (ex.: Ubuntu 26.04), **escolha a mais próxima** (ex.: Ubuntu 25.10). Essa escolha só define padrões de hardware (VirtIO, RAM sugerida); o que é instalado é o que está na ISO.
3. **Memória: 2048 MB · CPUs: 2**.
4. **Disco: 20 GB**.
5. **Nome: `rhel`** (exatamente assim: o `treino` usa esse nome). Marque **"Personalizar configuração antes de instalar"** e clique em Concluir.
6. Na tela de configuração: **Adicionar hardware → Armazenamento → 5 GiB, tipo de barramento VirtIO**. Repita para ter **2 discos extras**.
7. **Iniciar instalação**.

No instalador do RHEL (Anaconda):
- **Destino da instalação:** selecione **SOMENTE o disco de 20 GB (vda)**. ⚠️ Se marcar os discos de 5 GB, o instalador usa os três e o exercício de LVM da semana 4 fica sem disco livre.
- **Seleção de software:** *Minimal Install* (instalação mínima).
- **Rede e nome do host:** **ligue a placa de rede (botão ON)**, que às vezes vem desligada. Nome: `rhel`.
- **Senha de root:** defina uma. **Criação de usuário:** seu usuário, marcando "**tornar administrador**" (entra no grupo `wheel`).
- **Conectar à Red Hat:** **pule** (clique em Done sem registrar). Com a ISO DVD, a origem da instalação é *Local media* e tudo é instalado sem internet.
  Depois que o sistema subir, registre pelo terminal da VM: `sudo rhc connect` (ou `sudo subscription-manager register --username SEU_LOGIN_RED_HAT`). O usuário é o **login do site da Red Hat**, não `root`. Sem registro, o `dnf` não tem repositórios para atualizar e instalar pacotes.

### VM `ubuntu`
Mesmo caminho: nome **`ubuntu`**, **1536 MB · 2 CPUs · 20 GB + 1 disco extra de 5 GB (VirtIO)**.

No instalador do Ubuntu Server:
- Tipo de instalação: **Ubuntu Server** (o padrão).
- Rede: deixe em DHCP.
- **Armazenamento:** "usar o disco inteiro" e escolha **SOMENTE o disco de 20 GB**. Mesmo motivo da `rhel`: o disco de 5 GB é para a semana 4.
- Perfil: seu usuário, nome do servidor `ubuntu`.
- **Marque "Install OpenSSH server"**. Sem isso, não dá para entrar por SSH.
- Snaps em destaque: não marque nenhum.

### VM `kali` (importação, sem instalar)
**Arquivo → Nova máquina virtual → Importar imagem de disco existente** → escolha `kali.qcow2` → SO "Debian 12" (ou o mais próximo) → **2048 MB · 2 CPUs** → nome **`kali`**.

### Depois da instalação
- Ao reiniciar, o virt-manager normalmente já tira a ISO. Se a VM bootar no instalador de novo: VM desligada → Detalhes (ícone 💡) → *CDROM SATA* → **Desconectar**.
- Dentro de cada VM, atualize: `sudo dnf upgrade` (rhel) ou `sudo apt update && sudo apt full-upgrade` (ubuntu).

---

## 5. Usando as VMs no dia a dia

### No virt-manager
- **Duplo clique** na VM abre o console (a tela dela).
- O **mouse ficou preso** dentro da VM? Aperte **Ctrl + Alt** (os da esquerda) para soltar.
- Os botões ▶ ⏸ ⏻ na barra ligam, pausam e desligam.

### No terminal (`virsh`): o que você vai usar sempre
| Comando | O que faz |
|---|---|
| `virsh list --all` | Lista as VMs e o estado (running / shut off) |
| `virsh start rhel` | Liga |
| `virsh shutdown rhel` | Desliga **com educação** (como apertar o botão de energia: o sistema faz o shutdown) |
| `virsh destroy rhel` | Desliga **na marra**, como puxar da tomada. ⚠️ Apesar do nome, **não apaga nada** |
| `virsh reboot rhel` | Reinicia |
| `virsh domifaddr rhel` | **Mostra o IP da VM** (pelo DHCP do libvirt), sem precisar entrar nela |
| `virsh net-dhcp-leases default` | IPs entregues a todas as VMs |
| `virsh autostart rhel` | Liga a VM junto com o Fedora (opcional; com 16 GB, prefiro ligar só quando for usar) |
| `virsh dominfo rhel` | RAM, CPUs e estado |
| `virsh edit rhel` | Edita a configuração XML (com validação) |
| `virsh undefine rhel --remove-all-storage` | ⚠️ **Apaga** a VM e os discos. Cuidado |

### Snapshots
```bash
virsh snapshot-create-as rhel limpo        # cria (com a VM ligada, salva até a memória)
virsh snapshot-list rhel                   # lista
virsh snapshot-revert rhel limpo           # volta no tempo
virsh snapshot-delete rhel limpo           # apaga o snapshot (a VM fica como está)
```
Snapshot **não é backup**: ele mora dentro do mesmo arquivo `.qcow2`. Se o arquivo for apagado, vai junto.

### Acesso por SSH (é assim que você vai trabalhar)
O console do virt-manager é bom para instalar e para emergências (rede quebrada, boot quebrado). No dia a dia, entre pelo terminal do Fedora, onde copiar e colar funciona (colar = **Ctrl+Shift+V**):
```bash
virsh domifaddr rhel                     # ex.: 192.168.122.44
ssh seu_usuario@192.168.122.44           # 1ª vez: yes; depois a senha · exit para sair
```
**Connection refused** = o servidor SSH não está rodando na VM. Pela janela da VM:
rhel → `sudo systemctl enable --now sshd` · ubuntu → `sudo apt install -y openssh-server && sudo systemctl enable --now ssh`.

O IP pode mudar depois de vários dias desligada (o DHCP empresta por tempo limitado): confira de novo com `virsh domifaddr`. Na semana 9 você fixa os IPs.

**Acesso do treino:** para corrigir suas tarefas, o treino precisa entrar nas VMs sozinho. Rode uma vez `treino conectar`: ele cria uma chave só dele (em `~/linux-lab/treino/.ssh`) e pede a senha de cada VM. Seu `~/.ssh` não é tocado. Rode de novo se recriar uma VM.

---

## 6. Recursos: quanto cabe no seu PC

Seu Fedora: **16 GB de RAM** e uns **8 GB já em uso** com o que você costuma deixar aberto.

| Cenário | RAM das VMs | Resultado |
|---|---|---|
| `rhel` + `ubuntu` | 3,5 GB | Tranquilo |
| `rhel` + `ubuntu` + `kali` | 5,5 GB | OK, fechando abas pesadas do navegador |
| + Wazuh numa VM (4 GB) | 9,5 GB | Apertado: use o **outro PC** para o Wazuh |

Desligue o que não estiver usando (`virsh shutdown`). VM desligada não consome RAM.

---

## 7. Problemas comuns

| Sintoma | Causa provável | Solução |
|---|---|---|
| `virsh list` não mostra VMs que existem no virt-manager | `virsh` conectado na `session` | `export LIBVIRT_DEFAULT_URI=qemu:///system` (passo 2) ou `virsh -c qemu:///system ...` |
| Criou pool/rede, mas o `virsh pool-list` (ou o virt-manager) não mostra; `pool-start` falha | O terminal ainda estava na `session` (variável não carregada): o item foi criado lá | `virsh -c qemu:///session pool-undefine default`, depois `source ~/.bashrc`, confira `virsh uri` e refaça |
| "Permission denied" ao escolher a ISO | ISO dentro da sua home | Mova para `/var/lib/libvirt/images/` (passo 3) |
| "Network 'default' is not active" | Rede padrão desligada | `virsh net-start default && virsh net-autostart default` |
| VM muito lenta; virt-manager mostra "QEMU TCG" em vez de "KVM" | KVM não está ativo | `lsmod \| grep kvm`; confira VT-x/AMD-V ligado na BIOS |
| "Failed to connect socket... permission denied" | Grupo `libvirt` ainda não vale | Logout/login (ou `newgrp libvirt`) |
| VM pega IP 192.168.122.x mas não sai para a internet ("Network is unreachable", timeouts) | **Docker instalado no host**: ele muda a política do FORWARD do firewall para DROP e bloqueia o tráfego das VMs | Teste: `sudo iptables -S FORWARD \| head -1` mostra `-P FORWARD DROP`. Correção definitiva: `/etc/docker/daemon.json` com `{"ip-forward-no-drop": true}`, `sudo systemctl restart docker` e `sudo iptables -P FORWARD ACCEPT` (ou reinicie) |
| VM sem internet | Placa desligada no instalador (RHEL) | Dentro da VM: `nmcli con up enp1s0` (ou o nome que aparecer em `ip -br a`) e `nmcli con mod enp1s0 connection.autoconnect yes` |
| VM boota no instalador de novo | ISO ainda conectada | Desconecte o CDROM (seção 4) |
| *Begin Installation* desativado; *Software Selection* diz "Red Hat CDN requires registration" | Você está usando a **Boot ISO** | Troque pela ISO **DVD**: VM desligada → Detalhes (💡) → CDROM SATA → escolha a `...-dvd.iso` |
| `dnf` sem repositórios no RHEL | Sistema não registrado | `sudo rhc connect` ou `sudo subscription-manager register` |
