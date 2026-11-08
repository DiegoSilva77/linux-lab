# Plano de Férias — Linux, Redes e Segurança (09/11/2026 → 31/01/2027)

> **Um plano só.** Ele junta a certificação, as férias, os projetos de portfólio e a ponte com a FIAP.
> Foi dimensionado para quem **continua trabalhando**: cerca de **13h por semana** (2h de seg a sex + 3h no sábado), com as semanas de Natal e Ano-Novo mais leves.
> Total estimado: **~140h**. Marque `[x]` conforme avança.

---

## 🎯 Ao final das férias você terá

| Resultado | Quando |
|---|---|
| **LPIC-1 completa** (provas 101 e 102): Linux multi-distro, cobra Red Hat **e** Debian/Ubuntu | 101 em ~21/12 · 102 em ~30/01 |
| **Fortinet FCF + FCA** (gratuitas) | Semanas de Natal e Ano-Novo |
| **Projeto de portfólio "Mini-SOC"**: laboratório com Wazuh, ataque real, detecção, relatório de incidente com timeline e MITRE ATT&CK | Construído aos poucos, fechado na semana 10 |
| **Lacunas do diagnóstico fechadas**: redirecionamento, permissões/SUID, subnetting, NAT/PAT, firewall stateful, DNS/TLS, IoC/IoA, triagem | Ao longo do plano |
| **GitHub `linux-lab`** com relatórios, scripts e o projeto | Toda semana |

---

## 💰 Orçamento

| Item | Custo | Observação |
|---|---|---|
| LPIC-1 prova 101 | ~US$ 165–200 (~R$ 900–1.100) | Compre o voucher até **07/12** em lpi.org. Pode ser feita online (OnVUE) e **em português** |
| LPIC-1 prova 102 | ~US$ 165–200 (~R$ 900–1.100) | Compre até **10/01** |
| Fortinet FCF + FCA | Grátis | Confirme no portal de treinamento da Fortinet |
| Laboratório (KVM + VMs) | Grátis | |
| Material de estudo | Grátis | learning.lpi.org (oficial, em português) + `man` + simulados que o Claude gera |


---

## 📅 Visão geral

| Semana | Datas | Tema principal (LPIC-1) | Redes | Segurança / Mini-SOC | Horas |
|---|---|---|---|---|---|
| 0 | 09–15/11 | Setup, vi, linha de comando | Endereçamento do próprio lab | — | ~8h |
| 1 | 16–22/11 | Texto, pipes, redirecionamento, regex | **Subnetting** | Análise de log de brute-force | 13h |
| 2 | 23–29/11 | Permissões, links, find, usuários, sudo | TCP/UDP, portas, handshake, scans | Escalada de privilégio (SUID/sudo) | 13h |
| 3 | 30/11–06/12 | Processos, systemd, agendamento | ARP, DHCP, DNS | **Wazuh no ar** + caça à persistência | 13h |
| 4 | 07–13/12 | Hardware, discos, filesystems, LVM | IPv6 básico | Imagem forense + FIM no Wazuh | 13h |
| 5 | 14–20/12 | Boot, GRUB, bibliotecas, pacotes (apt e dnf) | — | — (semana de prova) | 13h |
| 6 | 21–27/12 | 🎓 **Prova 101** + Fortinet **FCF** | — | Conceitos (via FCF) | ~7h |
| 7 | 28/12–03/01 | Fortinet **FCA** | Firewall na prática (via FCA) | — | ~7h |
| 8 | 04–10/01 | Shell, scripts (com IA), localização, X11 | — | Script de detecção → regra no Wazuh | 13h |
| 9 | 11–17/01 | Redes no Linux | **Roteador, NAT/PAT, firewall stateful** | Scan detectado via log do firewall | 13h |
| 10 | 18–24/01 | Segurança, SSH, GPG, logs, horário, MTA | Túnel SSH | **Mini-SOC final**: ataque completo + relatório | 13h |
| 11 | 25–31/01 | Revisão + 🎓 **Prova 102** | Revisão | Portfólio publicado | 13h |

---

## 🎮 Como praticar: o programa `treino`

Este arquivo é o **mapa**. A **prática** acontece no programa `treino` (pasta `treino/`), que confere cada resposta **na hora**:

| Comando | O que faz |
|---|---|
| `treino` | Menu com o progresso de cada semana |
| `treino 3` | Roda os exercícios pendentes da semana 3 |
| `treino 3 --tudo` | Refaz a semana inteira |
| `treino subnet` | 20 questões de subnetting geradas na hora |
| `treino simulado 101` / `102` | Simulado no estilo LPIC-1, com nota e correção |
| `treino erros` | Refaz o que você errou, pulou ou viu a resposta |

**Tipos de exercício**
- **comando:** você digita um comando, ele roda numa pasta com logs e arquivos de exemplo, e a saída é comparada com a esperada.
- **tarefa:** você faz algo no Fedora ou nas VMs e aperta ENTER; o treino entra por SSH e confere o estado real (usuários, LVM, firewall...).
- **cenário:** o treino tira um snapshot, **quebra** algo na VM e você conserta. `:restaurar` volta o snapshot.
- **script:** você escreve um script e o treino roda testes automáticos nele.
- **pergunta / múltipla escolha / investigação na VM:** a resposta é conferida na hora, com explicação.

Dentro de qualquer exercício: `:dica`, `:resposta`, `:pular`, `:shell` (abre um terminal no lugar certo), `:sair` (o progresso fica salvo).

> As tarefas nas VMs precisam do setup da semana 0: VMs chamadas `rhel` e `ubuntu`, `treino conectar` feito e sudo sem senha nas VMs.

---

## 📌 Regras do plano

### Rotina semanal
| Dia | O quê | Tempo |
|---|---|---|
| Seg, Ter, Qua | Conteúdo LPIC-1: 25 min de teoria (learning.lpi.org + `man`) e o resto de prática nas VMs | 2h |
| Qui | 🛡️ Segurança / Mini-SOC | 2h |
| Sex | 🌐 Redes (ou conteúdo LPIC, quando indicado) | 2h |
| Sáb | 🏁 Desafio da semana: sem internet e sem IA, só `man` e `--help` | 3h |
| Dom | **Folga.** Se quiser, mande "semana X feita" para o Claude e receba um cenário quebrado + quiz | — |
| Todo dia | 5 exercícios de subnetting (subnettingpractice.com) + Anki | 10 min |

### Para o plano ser concluído de verdade
1. **Cada semana tem "Obrigatório" e "Se sobrar tempo".** O obrigatório cabe nas 13h. O resto é bônus.
2. **Atrasou?** Corte primeiro o "Se sobrar tempo" e depois o desafio de sábado (faça uma versão menor). **Nunca corte o conteúdo da LPIC nas semanas antes da prova.**
3. **Checkpoints:** fim da semana 2, fim da semana 4 e fim da semana 9. Se estiver mais de 1 semana atrasado num checkpoint, remarque a prova (OnVUE permite) em vez de atropelar o conteúdo.
4. **Snapshot antes de qualquer coisa destrutiva.**
5. **Regra dos 15 minutos:** tente sozinho antes de pedir ajuda. Para a IA, peça explicação, não a solução.
6. **Scripts com IA:** você escreve a especificação, a IA gera, você revisa linha a linha, roda `shellcheck`, testa e documenta. Se não sabe explicar uma linha, não commita.
7. **Multi-distro:** quando fizer sentido, faça a tarefa nas duas famílias e anote a diferença em `DIFERENCAS.md`.

### Legenda
🐧 Linux · 🌐 Redes · 🛡️ Segurança · 🏁 Desafio · ✅ Autoavaliação · 📦 Entregável · 🏫 Ligação com a FIAP · `[101.x]` = objetivo oficial da LPIC-1

> Antes de começar, confira em learning.lpi.org se a versão vigente da prova ainda é a **5.0 (101-500 / 102-500)**. Se mudou, me avise que eu ajusto os números dos objetivos.

---

## 🖥️ Laboratório

> Passo a passo completo, do zero, em [`LAB-KVM.md`](LAB-KVM.md).

### No Fedora (host)
```bash
sudo dnf install @virtualization
sudo systemctl enable --now libvirtd
sudo usermod -aG libvirt $USER   # depois faça logout/login
```

### VMs
| VM | Sistema | RAM | Disco | Papel |
|---|---|---|---|---|
| `rhel` | RHEL 10 (Developer Subscription, grátis) **ou** Rocky Linux | 2 GB | 20 GB + 2 discos extras de 5 GB | Servidor família Red Hat |
| `ubuntu` | Ubuntu Server LTS | 1,5 GB | 20 GB + 1 disco extra de 5 GB | Servidor família Debian; vira **roteador** na semana 9 |
| `kali` | Kali Linux | 2 GB | 30 GB | Atacante (ligue só quando precisar) |
| Wazuh manager | **Use o seu outro PC**, onde você já instalou o Wazuh. Se não der, uma VM de 4 GB | — | — | SIEM do Mini-SOC |

> O host tem 16 GB. Rode no máximo 3 VMs ao mesmo tempo e feche o navegador pesado quando estiver com o lab todo ligado. `rhel` e `ubuntu` **sem interface gráfica**.

### Topologia final (a partir da semana 9)
```
                   Internet
                      │
     [rede "default" do libvirt — NAT 192.168.122.0/24] ─── Wazuh (outro PC, rede bridge)
          │                          │
        kali                  ubuntu eth0
                              ubuntu eth1  = ROTEADOR + FIREWALL (nftables)
                                    │
               [rede "lab-interna" — isolada, 10.10.20.0/24]
                                    │
                                  rhel
```

---

## Semana 0 — Setup do laboratório (09–15/11) · ~8h

> ▶ **Prática interativa:** `treino 0` (42 exercícios: cada passo do setup é conferido automaticamente, mais conceitos de KVM, virsh, vi e a rede do lab).
> 📖 **Guia passo a passo:** [`LAB-KVM.md`](LAB-KVM.md): como o KVM funciona, onde baixar cada ISO, como criar, ligar e acessar as VMs, e problemas comuns.

> As férias começam no dia 13. Esta semana é só para deixar tudo pronto. **Comece os downloads no primeiro dia**, porque são vários GB.

### Dia a dia sugerido
| Dia | O quê | Guia |
|---|---|---|
| Seg (09/11) | Ler o guia §1; instalar KVM; criar conta Red Hat Developer; **disparar os downloads** (RHEL DVD, Ubuntu Server, Kali QEMU) | §1–§3 |
| Ter (10/11) | Conferir hashes; mover ISOs para a pool; criar e instalar a `rhel` (com os 2 discos extras) | §3–§4 |
| Qua (11/11) | Criar e instalar a `ubuntu`; praticar virsh (ligar, desligar, descobrir IP) | §4–§5 |
| Qui (12/11) | Entrar nas VMs por `ssh usuario@IP`; `treino conectar`; sudo sem senha; registrar o RHEL e atualizar as duas | §5 |
| Sex–Dom | Snapshot `limpo`; repositório no GitHub; `vimtutor`; resto do `treino 0`; (se der) importar o Kali | §5 |

### Obrigatório
- [ ] KVM instalado e entendido: o que fazem KVM, QEMU, libvirt e virt-manager/virsh
- [ ] ISOs do RHEL (ou Rocky) e do Ubuntu Server baixadas, **com hash conferido**, na pool `default`
- [ ] VMs `rhel` e `ubuntu` instaladas (mínimas, sem GUI), **só no disco de 20 GB**
- [ ] Ligar, desligar e descobrir o IP das VMs pelo `virsh`
- [ ] Entrar nas duas VMs com `ssh usuario@IP`; `treino conectar` feito; sudo sem senha nas VMs
- [ ] RHEL registrado; as duas atualizadas
- [ ] Snapshot `limpo` das duas, com teste de restauração
- [ ] `[103.8]` `vimtutor` completo
- [ ] Repositório `linux-lab` no GitHub com `ROTEIRO.md`, `LAB-KVM.md`, `DIFERENCAS.md` e o `treino`
- [ ] Instalar o Anki

### Se sobrar tempo
- [ ] Importar o `kali` (senão, até a semana 2)
- [ ] OverTheWire Bandit, níveis 0–10

---

## Semana 1 — Texto, pipes e logs (16–22/11) · 13h

> ▶ **Prática interativa:** `treino 1` (41 exercícios: 27 comandos reais em logs de ataque, redirecionamento, subnetting, IoC/IoA).

**Por quê:** 50% do trabalho de um analista é filtrar texto e log. Esta semana fecha a sua **questão 1** e a **questão 6** do diagnóstico.

### 🐧 Seg — `[103.1]` Linha de comando
- [ ] Variáveis de ambiente (`env`, `export`, `PATH`), `history`, `type`, `which`, `man` (seções), `uname`
- [ ] Aspas: diferença entre `'...'`, `"..."` e `\`

### 🐧 Ter — `[103.2]` Filtros de texto
- [ ] `cat`, `head`, `tail -f`, `less`, `cut`, `sort`, `uniq -c`, `wc`, `tr`, `nl`, `paste`, `split`, `od`
- [ ] `zcat`/`bzcat`/`xzcat`; `sha256sum` e `md5sum`

### 🐧 Qua — `[103.4]` `[103.7]` Redirecionamento e regex
- [ ] `>`, `>>`, `<`, `2>`, `2>&1`, `&>`, `/dev/null`, `tee`, `xargs`. Faça 10 exemplos próprios
- [ ] Testar a diferença entre `cmd > arq 2>&1` e `cmd 2>&1 > arq`
- [ ] `grep` (`-i -v -r -E -o -c -n`), regex básica e estendida, `sed` (substituir, apagar linha, `-i`)

### 🛡️ Qui — Brute-force nos logs
- [ ] Gerar ~50 tentativas de SSH com senha errada contra `rhel` e `ubuntu` (um laço no Fedora já serve) e **1 login com sucesso** no meio
- [ ] Achar os eventos: `/var/log/secure` ou journal (RHEL) vs `/var/log/auth.log` (Ubuntu) → `DIFERENCAS.md`
- [ ] `journalctl -u sshd --since today`, `-p err`, `-o json`
- [ ] Glossário em `seguranca/glossario.md`: **IoC vs IoA** (2 exemplos de cada, sua **questão 18**), evento × alerta × incidente, falso positivo × falso negativo

### 🌐 Sex — Subnetting (sua **questão 11**)
- [ ] Faixas privadas (RFC 1918), CIDR, máscara, rede, broadcast, hosts válidos
- [ ] À mão: `192.168.10.64/27`, `10.0.5.130/26`, `172.16.8.200/29`
- [ ] Dividir `192.168.50.0/24` em 6 sub-redes e listar todas

### 🏁 Sáb — "Relatório de brute-force"
Sem IA e sem internet, escreva `relatorios/s01-bruteforce.md` com:
- top 5 IPs por falhas (o one-liner que você escreveu);
- usuários tentados;
- primeira e última tentativa de cada IP;
- se houve sucesso, de qual IP e com qual usuário;
- o que esse usuário fez depois (`last`, journal);
- recomendação de contenção.

### ✅ Eu consigo (sem consultar)
- [ ] Explicar `2>&1` e por que a ordem importa
- [ ] Montar `grep | grep -o | sort | uniq -c | sort -rn | head`
- [ ] Calcular rede, broadcast e hosts de /24 a /30 em menos de 1 minuto

---

## Semana 2 — Permissões, usuários e escalada (23–29/11) · 13h

> ▶ **Prática interativa:** `treino 2` (58 exercícios: chmod/SUID/links/find na prática, cenário de escalada de privilégio, empresa fictícia nas VMs, leitura de tcpdump).

**Por quê:** fecha as **questões 2, 7 e 10**. Permissão errada é uma das portas de entrada mais comuns para virar root.

### 🐧 Seg — `[104.5]` Permissões
- [ ] Octal e simbólico, `chmod`, `chown`, `chgrp`, `umask` (calcule o resultado para arquivo e diretório)
- [ ] **SUID (4), SGID (2), sticky (1)** em arquivo e diretório; `s`/`S` e `t`/`T`

### 🐧 Ter — `[104.6]` `[104.7]` Links, FHS e busca
- [ ] Hard link × soft link, testando com `ls -li` e apagando o original
- [ ] Para que serve cada diretório do FHS (`/etc`, `/var`, `/opt`, `/usr`, `/srv`, `/tmp`, `/proc`, `/dev`…)
- [ ] `find` por nome, tamanho, data, dono e permissão, com `-exec`; `locate`/`updatedb`, `whereis`, `which`

### 🐧 Qua — `[107.1]` `[110.1]` Usuários e sudo
- [ ] `useradd`/`usermod`/`userdel`, `groupadd`, `passwd`, `chage`; bloquear (`usermod -L`) e expirar
- [ ] Campos de `/etc/passwd`, `/etc/shadow` e `/etc/group`; `/etc/skel`
- [ ] `adduser` (Ubuntu) × `useradd` → `DIFERENCAS.md`
- [ ] `sudo`, `visudo`, `/etc/sudoers.d/`, grupo `wheel` (RHEL) × `sudo` (Ubuntu)

### 🛡️ Qui — Escalada de privilégio
- [ ] `find / -perm -4000 2>/dev/null` nas duas VMs; pesquisar 3 binários no GTFOBins
- [ ] Dar SUID ao `find` e escalar de usuário comum para root. Desfazer
- [ ] Criar regra de sudo sem senha para o `vim` e escalar. Desfazer
- [ ] Anotar como **detectar** e **prevenir** cada caso

### 🌐 Sex — TCP/UDP e scans (sua **questão 12**)
- [ ] TCP × UDP; portas 22, 25, 53, 80, 88, 389, 443, 445, 3389 (`/etc/services`)
- [ ] `tcpdump` de um SSH do Fedora para a `rhel`: identificar SYN, SYN-ACK, ACK e FIN/RST
- [ ] Do `kali`: `nmap -sT` e `nmap -sS` contra a `rhel`, **capturando no alvo**. Explicar a diferença no tráfego

### 🏁 Sáb — "Empresa fictícia" (nas duas distros)
- grupos `financeiro` e `ti`, com 2 usuários cada;
- `estagiario` com conta que expira em 30 dias;
- `/srv/financeiro`: só o grupo lê e escreve, arquivos novos herdam o grupo (SGID) e ninguém apaga arquivo de outro (sticky);
- grupo `ti` pode reiniciar o `sshd` via sudo, **e só isso**;
- documente como você testou cada requisito.

### Se sobrar tempo
- [ ] ACLs (`getfacl`/`setfacl`): o `estagiario` lê um único arquivo de `/srv/financeiro`
- [ ] Rodar `linpeas.sh` como usuário comum e ler o relatório

### ✅ Eu consigo
- [ ] Ler `-rwsr-xr--`, dizer o octal (4754) e o risco
- [ ] Dizer o que `umask 027` gera
- [ ] Explicar 2 formas de virar root num servidor mal configurado e como prevenir

### 🚩 Checkpoint 1
Semanas 0–2 concluídas? Se estiver mais de 1 semana atrasado, comprima a semana 3 (corte o "Se sobrar tempo").

---

## Semana 3 — Processos, systemd e persistência (30/11–06/12) · 13h · 🏫 DFIR

> ▶ **Prática interativa:** `treino 3` (35 exercícios: processos, cron/systemd, serviço com timer nas VMs, cenário de caça às persistências, ARP/DHCP/DNS).

**Por quê:** saber o que roda no sistema é a base de forense e resposta a incidente, o que adianta Cyber Defense Operations do 2º ano. O Mini-SOC começa aqui.

### 🐧 Seg — `[103.5]` `[103.6]` Processos
- [ ] `ps aux`, `ps -ef --forest`, `top`, `pgrep`, `pkill`, `kill` (sinais 1, 9 e 15), `jobs`, `bg`, `fg`, `nohup`, `tmux`
- [ ] `nice`, `renice`; `free`, `uptime`
- [ ] `/proc/<pid>/`: `cmdline`, `exe`, `fd`

### 🐧 Ter — `[101.3]` systemd
- [ ] `systemctl` (`status`, `enable --now`, `mask`, `list-units --failed`, `daemon-reload`), targets, `shutdown`, `wall`
- [ ] Escrever uma unit própria em `/etc/systemd/system/` com `User=` e `Restart=on-failure`

### 🐧 Qua — `[107.2]` Agendamento
- [ ] `cron` (sintaxe, `crontab -e`, `/etc/cron.d/`, `cron.allow`), `at`, **systemd timers**

### 🛡️ Qui — Wazuh + persistência
- [ ] Instalar o agente Wazuh na `rhel` e no `ubuntu`, apontando para o seu manager (o outro PC)
- [ ] Plantar 4 persistências na `rhel`: cron de usuário, serviço systemd, chave em `authorized_keys`, linha no `.bashrc`
- [ ] Ver o que o Wazuh pegou e o que não pegou → anotar
- [ ] 🏫 Ler o resumo da **RFC 3227** (ordem de volatilidade)

### 🌐 Sex — ARP, DHCP, DNS (sua **questão 13**)
- [ ] Capturar ARP (`ip neigh`, `tcpdump arp`) e o DHCP DORA ao renovar o IP de uma VM
- [ ] `dig`, `dig +trace`, `dig -x`; registros A, AAAA, CNAME, MX, TXT, NS, PTR
- [ ] Escrever o fluxo completo de "digitei google.com": DHCP → ARP → DNS → TCP → TLS → HTTP

### 🏁 Sáb — "Caça às cegas"
Restaure o snapshot e peça ao Claude um script que plante persistências que você não conhece. Rode o script e depois:
1. colete as evidências voláteis **na ordem da RFC 3227** (conexões, processos, usuários logados, arquivos abertos), salvando cada saída com hash;
2. encontre todas as persistências;
3. escreva `relatorios/s03-persistencia.md` com o checklist de caça e os comandos.

### ✅ Eu consigo
- [ ] Descobrir qual processo e PID escuta numa porta (`ss -tlnp`)
- [ ] Criar uma unit e um timer do zero
- [ ] Listar 5 lugares onde procurar persistência num Linux

---

## Semana 4 — Hardware, discos e evidência forense (07–13/12) · 13h · 🏫 DFIR

> ▶ **Prática interativa:** `treino 4` (32 exercícios: LVM/ext4/swap conferidos nas VMs, cenário de fstab quebrado, hash/dd/strings, IPv6, subnetting).

> ⚠️ **Compre o voucher da 101 até 07/12** e agende a prova para ~21/12.

### 🐧 Seg — `[101.1]` Hardware
- [ ] `lspci`, `lsusb`, `lsblk`, `lsmod`, `modprobe`, `/proc`, `/sys`, `/dev`, udev (o conceito)

### 🐧 Ter — `[104.1]` `[102.1]` Partições, filesystems e LVM
- [ ] `fdisk` (MBR), `gdisk`/`parted` (GPT), `mkfs.ext4`, `mkfs.xfs`, `mkfs.vfat`, `mkswap`/`swapon`
- [ ] LVM: `pvcreate`, `vgcreate`, `lvcreate`, `lvextend -r`

### 🐧 Qua — `[104.2]` `[104.3]` Integridade e montagem
- [ ] `df -h`, `du -sh`, `fsck`/`e2fsck`, `xfs_repair`, `tune2fs`
- [ ] `mount`, `umount`, `/etc/fstab` com UUID (`blkid`), `mount -a`, opções `noexec`, `nosuid` e `ro`

### 🛡️ Qui — Imagem forense e integridade 🏫
- [ ] Criar arquivos num disco extra, apagar alguns, gerar a imagem com `dd`, tirar `sha256sum` antes e depois
- [ ] Montar a imagem **somente leitura** (`-o ro,loop`) e recuperar um apagado (`photorec`)
- [ ] Ativar o **FIM** do Wazuh em `/etc` e alterar `/etc/passwd` para ver o alerta

### 🌐 Sex — IPv6 e revisão
- [ ] IPv6: formato, abreviação, link-local (`fe80::`), `ip -6 a`
- [ ] Simulado de subnetting: 20 questões cronometradas (meta: 85%)

### 🏁 Sáb — "Disco cheio em produção"
- `/dados` (LV) está cheio: estenda sem desmontar, adicionando um disco novo ao VG.
- Quebre o `fstab` de propósito (UUID errado), reinicie e recupere pelo **emergency mode**. Faça nas duas distros.

### ✅ Eu consigo
- [ ] Do disco cru até um LV montado no boot, em menos de 10 min
- [ ] Explicar por que uma imagem forense precisa de hash e de cadeia de custódia

### 🚩 Checkpoint 2
Se o conteúdo das semanas 1–4 não estiver firme, remarque a 101 para o início de janeiro e use a semana 6 para revisar.

---

## Semana 5 — Boot e pacotes + reta final da 101 (14–20/12) · 13h

> ▶ **Prática interativa:** `treino 5` (33 exercícios: boot/GRUB, apt e dnf, cenários de target errado e senha de root perdida).

### 🐧 Seg — `[101.2]` `[102.2]` Boot e GRUB
- [ ] BIOS × UEFI, bootloader, kernel, initramfs, systemd; `dmesg`, `journalctl -b`
- [ ] GRUB2: parâmetros de kernel no boot, `grub2-mkconfig` (RHEL) × `update-grub` (Ubuntu)

### 🐧 Ter — `[102.3]` `[102.6]` Bibliotecas e virtualização
- [ ] `ldd`, `ldconfig`, `/etc/ld.so.conf`, `LD_LIBRARY_PATH`
- [ ] Linux como convidado de virtualização: VM × container, `cloud-init`, `machine-id`

### 🐧 Qua — `[102.4]` Debian
- [ ] `apt` (`update`, `upgrade`, `install`, `remove`, `purge`, `show`, `search`), `dpkg` (`-i`, `-l`, `-L`, `-S`, `-r`), `/etc/apt/sources.list.d/`

### 🐧 Qui — `[102.5]` Red Hat
- [ ] `dnf` (`install`, `remove`, `search`, `provides`, `history`, `history undo`), `rpm` (`-qa`, `-qi`, `-ql`, `-qf`, `-V`), `/etc/yum.repos.d/`; noção de `zypper`
- [ ] Tabela dnf ↔ apt em `DIFERENCAS.md`

### 🐧 Sex — Simulado 101 #1
- [ ] Simulado completo cronometrado (60 questões, 90 min) e lista dos erros por objetivo

### 🏁 Sáb — Revisão dirigida
- [ ] Revisar só os objetivos em que errou + simulado #2

### ✅ Eu consigo
- [ ] Descobrir de qual pacote veio um arquivo, nas duas famílias
- [ ] Descrever o processo de boot do firmware até o login

---

## Semana 6 — 🎓 Prova 101 + Fortinet FCF (21–27/12) · ~7h · semana de Natal

> ▶ **Prática interativa:** `treino 6` (6 itens: prova 101 e FCF).

- [ ] **Prova LPIC-1 101** (~21/12)
- [ ] Fortinet **FCF**: cursos "Getting Started in Cybersecurity" e "Technical Introduction to Cybersecurity" + prova 🏫 (Hacker Mindset)
- [ ] Anki: 10 min por dia para não esfriar

---

## Semana 7 — Fortinet FCA (28/12–03/01) · ~7h · semana de Ano-Novo

> ▶ **Prática interativa:** `treino 7` (5 itens: FCA).

> ⚠️ **Compre o voucher da 102 até 10/01** e agende para ~30/01.

- [ ] Fortinet **FCA** (FortiGate Operator): curso + prova
- [ ] Ao assistir, anote em `seguranca/firewall.md`: o que é política, NAT, inspeção stateful e UTM no FortiGate. Na semana 9 você vai montar o equivalente em Linux
- [ ] Anki e subnetting diários

---

## Semana 8 — Shell e scripts (04–10/01) · 13h · 🏫 Coding for Security

> ▶ **Prática interativa:** `treino 8` (30 exercícios: 6 scripts com testes automáticos, backup.sh feito com IA testado de verdade, locale/X11).

### 🐧 Seg — `[105.1]` Ambiente do shell
- [ ] `/etc/profile`, `/etc/profile.d/`, `~/.bashrc`, `~/.bash_profile`; shell de login × interativo; `alias`, funções, `PATH`

### 🐧 Ter — `[105.2]` Scripts na mão (o que cai na prova)
- [ ] Shebang, `$1 $@ $# $?`, `test`/`[ ]`, `if`, `for`, `while`, `read`, `seq`, `exit`, `exec`
- [ ] Escrever **na mão** um script de 15–20 linhas: recebe um usuário e mostra grupos, último login e processos

### 🐧 Qua — Scripts com IA (como você vai trabalhar)
Para cada script: **especificação** em `specs/` → IA gera → **revisão linha a linha** → `shellcheck` → **teste** nas duas distros (inclusive com entrada errada) → README com os bugs que você achou.
- [ ] `backup.sh`: backup com rotação (mantém os 7 últimos), logando com `logger`
- [ ] `detecta-mudancas.sh`: avisa se apareceu um **novo binário SUID** ou uma **nova chave** em `authorized_keys` desde a última execução, e registra com `logger`

### 🛡️ Qui — Regra customizada no Wazuh
- [ ] Rodar o `detecta-mudancas.sh` por timer (semana 3), mandar a saída ao syslog e criar uma **regra customizada no Wazuh** que alerta quando ele detecta algo
- [ ] Testar plantando um SUID novo

### 🐧 Sex — `[107.3]` `[106]` Localização e interface gráfica (teoria)
- [ ] `locale`, `LANG`, `localectl`, `timedatectl`, `/etc/timezone` × `/etc/localtime`, `iconv`
- [ ] X11 × Wayland, display managers, acessibilidade. **Só teoria:** leia o material da LPI e faça os exercícios dele

### 🏁 Sáb — Sem IA
- [ ] Escrever do zero, sem consultar, um script que lê um arquivo de log e conta as linhas por nível (INFO/WARN/ERROR)

### Se sobrar tempo
- [ ] 🏫 Refazer o relatório da semana 1 em **Python** (`analisa_log.py`) e comparar: quando vale Bash e quando vale Python?

### ✅ Eu consigo
- [ ] Ler um script de 50 linhas e explicar o que faz
- [ ] Apontar 3 erros comuns em scripts gerados por IA

---

## Semana 9 — Redes no Linux + roteador do lab (11–17/01) · 13h · 🏫 Network Security

> ▶ **Prática interativa:** `treino 9` (19 exercícios: rede lab-interna, NAT, firewall stateful e DNAT conferidos, 3 cenários de rede quebrada).

**Por quê:** fecha as **questões 14 e 15**. Você vai **construir** NAT e firewall stateful, como fez no FortiGate, só que na mão.

### 🐧🌐 Seg — `[109.1]` Fundamentos
- [ ] TCP, UDP, ICMP; portas; IPv4 e IPv6; máscaras (já dominado, revisar rápido)

### 🐧🌐 Ter — `[109.2]` `[109.4]` Configuração persistente e DNS
- [ ] `nmcli` (RHEL) × **netplan** (Ubuntu): IP estático, DNS e gateway → `DIFERENCAS.md`
- [ ] `hostnamectl`, `/etc/hosts`, `/etc/nsswitch.conf`, `/etc/resolv.conf`, `systemd-resolved`, `getent hosts`

### 🐧🌐 Qua — `[109.3]` Troubleshooting
- [ ] `ip`, `ss`, `ping`, `traceroute`, `tracepath`, `nc`, `dig`, `host`
- [ ] Método em camadas: link → IP → gateway → DNS → porta → aplicação, com os comandos de cada etapa

### 🌐 Qui — Montar o roteador
- [ ] Criar a rede isolada `lab-interna` no virt-manager; 2ª placa no `ubuntu`; `rhel` só na `lab-interna`
- [ ] IPs estáticos (`ubuntu` 10.10.20.1, `rhel` 10.10.20.10) e `ip_forward` persistente
- [ ] **nftables** no `ubuntu`: masquerade (PAT) para a `lab-interna` sair; ver as traduções em `conntrack -L`

### 🌐🛡️ Sex — Firewall stateful
- [ ] Política padrão `drop` no `forward`, liberando `established,related` e só o necessário
- [ ] Repetir **sem** `established,related` e explicar o que quebra (stateful × stateless)
- [ ] **DNAT**: o `kali` acessa o SSH da `rhel` pela porta 2222 do roteador
- [ ] Regra que **loga** pacotes descartados; mandar esse log ao Wazuh e ver o scan do `kali` aparecer

### 🏁 Sáb — "Rede quebrada"
Peça ao Claude 3 cenários (gateway errado, DNS errado, regra de firewall bloqueando). Diagnostique e corrija, registrando os comandos de cada camada em `relatorios/s09-rede.md`.

### ✅ Eu consigo
- [ ] Explicar NAT, PAT, SNAT e DNAT com o meu lab como exemplo
- [ ] Explicar stateful × stateless
- [ ] Diagnosticar "pinga IP mas não navega" no Linux

### 🚩 Checkpoint 3
O lab de rede está funcionando? Se não, simplifique a semana 10: faça o ataque sem o roteador, com `kali` e `rhel` na mesma rede.

---

## Semana 10 — Segurança + Mini-SOC final (18–24/01) · 13h · 🏫 DFIR + Offensive

> ▶ **Prática interativa:** `treino 10` (35 exercícios: hardening de SSH, fail2ban, GPG, rsyslog remoto, MITRE, triagem, Mini-SOC conferido).

### 🐧 Seg — `[110.1]` `[110.2]` Segurança do host
- [ ] `who`, `w`, `last`, `lastb`, `lsof`, `fuser`, `ulimit`, `/etc/nologin`, desativar serviços desnecessários
- [ ] Revisão de SUID, `sudo` e `chage` (já visto)

### 🐧 Ter — `[110.3]` Criptografia e SSH
- [ ] Hardening do SSH: só chave, `PermitRootLogin no`, `AllowGroups`, `MaxAuthTries`; `ssh-agent`
- [ ] Túneis SSH (`-L` e `-R`): o que são e por que um atacante usa
- [ ] GPG: gerar chave, cifrar, decifrar, assinar e verificar

### 🐧 Qua — `[108]` Serviços essenciais
- [ ] `[108.1]` `chrony`, `timedatectl`, `hwclock` (por que o horário certo importa em forense)
- [ ] `[108.2]` `rsyslog`, `journald`, `logrotate`, `logger`
- [ ] `[108.3]` `[108.4]` MTA (aliases, `mail`) e CUPS: **só teoria**, 30 min

### 🛡️ Qui + 🏁 Sáb — **Mini-SOC: o ataque final** (projeto de portfólio)
Do `kali`, execute a cadeia completa contra a `rhel` (pelo DNAT do roteador):
1. reconhecimento com `nmap`;
2. brute-force SSH num usuário com senha fraca, criado de propósito com o SSH ainda **sem** hardening;
3. escalada pelo SUID ou sudo mal configurado da semana 2;
4. persistência com cron + chave SSH;
5. alteração em `/etc/passwd`.

Depois, como analista:
- [ ] Para cada etapa: o Wazuh alertou? Qual regra? Qual técnica do **MITRE ATT&CK**?
- [ ] Coleta volátil (RFC 3227) + **timeline** do incidente
- [ ] **Playbook de triagem** para "brute-force seguido de login com sucesso" (sua **questão 17**): validar → escopo → timeline → contenção → erradicação → recuperação → lições aprendidas
- [ ] Aplicar o hardening do SSH, repetir o ataque e mostrar que ele falha

### 📦 Entregável principal
`projetos/mini-soc/`: diagrama, regras customizadas, playbook, relatório do incidente com timeline e mapeamento MITRE, e prints.

---

## Semana 11 — Reta final da 102 + portfólio (25–31/01) · 13h

> ▶ **Prática interativa:** `treino 11` (14 itens: diagnóstico refeito, prova 102, README, CV).

- [ ] **Seg:** simulado 102 #1 cronometrado (60 questões, 90 min) e lista dos erros por objetivo
- [ ] **Ter–Qua:** revisão dos objetivos fracos (provavelmente 106, 107.3 e 108, que você viu só na teoria)
- [ ] **Qui:** simulado 102 #2
- [ ] **Sex:** README do `linux-lab` apresentável, com os projetos em destaque; refazer as 20 perguntas do diagnóstico e comparar com as respostas de novembro
- [ ] **Sáb (~30/01):** 🎓 **Prova LPIC-1 102**
- [ ] **Dom:** atualizar o CV, trocando "domínio de Linux" por LPIC-1, FCF, FCA e o link do Mini-SOC, e fazer um post no LinkedIn sobre o projeto

---

## 🚫 Fora deste plano (de propósito)

Para o plano caber em ~140h, estes temas ficaram de fora. Eles são cobertos pelo 2º ano da FIAP:

| Tema | Onde vai aparecer |
|---|---|
| Análise de malware a fundo (gdb, engenharia reversa) | Malware Analysis |
| Azure e cloud security | Cloud Security |
| Exploração web (DVWA, OWASP) | Software Exploitation |
| OSINT e CTI | Cyber Threat Intelligence |
| GRC e LGPD | Security GRC |
| Ataques a AD, containers, Ansible | Offensive Security / DevSecOps |
| IA & ML Security | IA & ML Security |
| RHCSA | Decisão: LPIC-1 agora. Reavalie depois |

---

## 📊 Progresso

| Semana | Tema | Concluída | Autoavaliação (0–10) |
|---|---|---|---|
| 0 | Setup | [ ] | |
| 1 | Texto, pipes, logs + subnetting | [ ] | |
| 2 | Permissões, usuários, privesc + TCP/UDP | [ ] | |
| 3 | Processos, systemd, persistência + ARP/DHCP/DNS | [ ] | |
| 4 | Discos, LVM, forense + IPv6 | [ ] | |
| 5 | Boot, pacotes, simulados 101 | [ ] | |
| 6 | 🎓 Prova 101 + FCF | [ ] | |
| 7 | FCA | [ ] | |
| 8 | Shell e scripts + regra no Wazuh | [ ] | |
| 9 | Redes no Linux + roteador NAT/firewall | [ ] | |
| 10 | Segurança + Mini-SOC final | [ ] | |
| 11 | 🎓 Prova 102 + portfólio | [ ] | |
