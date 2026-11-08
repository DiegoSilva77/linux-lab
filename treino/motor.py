"""Motor do treino: tipos de exercício e execução no Fedora (local) e nas VMs (via SSH)."""
from __future__ import annotations

import ipaddress
import json
import os
import random
import re
import shlex
import shutil
import subprocess
import sys
import textwrap
import time
from dataclasses import dataclass, field
from pathlib import Path

import dados

BASE = Path(__file__).resolve().parent
SANDBOX = BASE / ".sandbox"
PROGRESSO = BASE / "progresso.json"
CONFIG = BASE / "config.json"
VIRSH = ["virsh", "-c", "qemu:///system"]
# Acesso PRÓPRIO do treino às VMs: chave e config em treino/.ssh, sem mexer no ~/.ssh do usuário.
# O usuário continua entrando do jeito dele (ssh usuario@IP com senha); `treino conectar` instala a chave.
SSH_DIR = BASE / ".ssh"
CHAVE = SSH_DIR / "id_ed25519"
SSH_CFG = SSH_DIR / "config"
SSH_OPTS = [
    "-F", str(SSH_CFG),
    "-o", "BatchMode=yes", "-o", "ConnectTimeout=6",
    "-o", "ControlMaster=auto", "-o", f"ControlPath={SSH_DIR}/cm-%C",
    "-o", "ControlPersist=120",
]
SSH_TREINO = f"ssh -F '{SSH_CFG}' -o BatchMode=yes -o ConnectTimeout=8"  # para usar dentro de checks locais


def _config() -> dict:
    try:
        return json.loads(CONFIG.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


CFG = _config()


def dominio(host: str) -> str:
    """Nome da VM no libvirt (por padrão, igual ao alias SSH)."""
    return CFG.get("vms", {}).get(host, host)


def ip_vm(host: str) -> str:
    """IP da VM na rede default (192.168.122.x), pelo DHCP ou pela tabela ARP."""
    for fonte in ("lease", "arp"):
        try:
            r = subprocess.run(["virsh", "-c", "qemu:///system", "domifaddr", dominio(host), "--source", fonte],
                               capture_output=True, text=True, timeout=10)
        except (OSError, subprocess.TimeoutExpired):
            return ""
        for campo in r.stdout.split():
            if campo.startswith("192.168.122."):
                return campo.split("/")[0]
    return ""


def atualizar_ssh_cfg(usuario: str = "") -> None:
    """Regera treino/.ssh/config com os IPs atuais (o DHCP pode trocar o IP; na semana 9 a rhel sai da rede default)."""
    usuarios = CFG.get("usuarios", {})
    SSH_DIR.mkdir(mode=0o700, exist_ok=True)
    blocos = ["# Gerado pelo treino. Só o treino usa este arquivo."]
    for h, u in usuarios.items():  # usuário de cada VM (ssh usa o primeiro valor que encontrar)
        blocos += [f"Host {h}", f"    User {u}"]
    blocos += ["Host *",
              f"    User {usuario or os.environ.get('USER', '')}",
              f"    IdentityFile {CHAVE}",
              "    IdentitiesOnly yes",
              "    # VMs de laboratório são recriadas toda hora; nunca desligue essa checagem em produção",
              "    StrictHostKeyChecking no",
              "    UserKnownHostsFile /dev/null",
              "    LogLevel ERROR"]
    for h in ("rhel", "ubuntu", "kali"):
        ip = ip_vm(h)
        if ip:
            blocos += [f"Host {h}", f"    HostName {ip}"]
        elif h == "rhel":  # semana 9: rhel só na lab-interna, atrás da ubuntu
            blocos += ["Host rhel", "    HostName 10.10.20.10", "    ProxyJump ubuntu"]
    SSH_CFG.write_text("\n".join(blocos) + "\n")
    SSH_CFG.chmod(0o600)


_SSH_CFG_ATUAL = False


def _garantir_ssh_cfg():
    global _SSH_CFG_ATUAL
    if not _SSH_CFG_ATUAL:
        atualizar_ssh_cfg()
        _SSH_CFG_ATUAL = True


# ───────────────────────────── aparência ─────────────────────────────
COR = sys.stdout.isatty() and "NO_COLOR" not in os.environ


def _cor(cod):
    return (lambda s: f"\033[{cod}m{s}\033[0m") if COR else (lambda s: str(s))


verde, vermelho, amarelo, azul, negrito, cinza, magenta = (
    _cor(c) for c in ("32", "31", "33", "36", "1", "90", "35"))


def _prompt(p: str) -> str:
    return f"\001\033[36m\002{p}\001\033[0m\002" if COR else p


def txt(s: str, pre: str = "   ") -> str:
    return textwrap.indent(textwrap.dedent(s).strip("\n"), pre)


class Sair(Exception):
    """Usuário pediu para sair (salva o progresso)."""


def entrada(p: str = "› ") -> str:
    try:
        return input(_prompt(p))
    except (EOFError, KeyboardInterrupt):
        print()
        raise Sair


def norm(s: str) -> str:
    s = re.sub(r"\s+", " ", s.strip().lower())
    return s.rstrip(".").strip()


def linhas(s: str) -> list[str]:
    return [re.sub(r"\s+", " ", l.strip()) for l in s.splitlines() if l.strip()]


def rx(padrao: str, i: bool = False):
    """Resposta aceita por regex (a resposta inteira precisa casar)."""
    flags = re.I if i else 0
    return lambda r: re.fullmatch(padrao, re.sub(r"\s+", " ", r.strip()), flags) is not None


def cmd(padrao: str):
    """Comando aceito com ou sem 'sudo' na frente."""
    return rx(r"(sudo )?" + padrao)


# Cenários que exigem reboot: o "quebrar" grava a hora, e a verificação confere se houve boot depois dela.
MARCA_QUEBRA = "\ndate +%s > /var/tmp/.treino_quebra\n"
REINICIOU = '[ -f /var/tmp/.treino_quebra ] && [ "$(cat /var/tmp/.treino_quebra)" -lt "$(date -d "$(uptime -s)" +%s)" ]'


def conteudo_igual(arq: str, texto: str) -> str:
    """Script de verificação: o arquivo tem exatamente este conteúdo."""
    return f"diff -q {shlex.quote(arq)} - >/dev/null 2>&1 <<'__FIM__'\n{texto.rstrip(chr(10))}\n__FIM__"


# ───────────────────────────── execução ─────────────────────────────
def _falhou(args, code, err):
    return subprocess.CompletedProcess(args, code, "", err)


def rodar_local(comando: str, cwd, stdin_txt: str | None = None, timeout: int = 20):
    cwd = Path(cwd)
    env = dict(os.environ, LC_ALL="C.UTF-8")
    if cwd == SANDBOX or SANDBOX in cwd.parents:
        g = cwd / ".gnupg"
        g.mkdir(mode=0o700, exist_ok=True)
        env["GNUPGHOME"] = str(g)
    kw = {"input": stdin_txt} if stdin_txt is not None else {"stdin": subprocess.DEVNULL}
    try:
        return subprocess.run(["bash", "-c", comando], cwd=cwd, capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=timeout, env=env, **kw)
    except subprocess.TimeoutExpired:
        return _falhou(comando, 124, f"tempo esgotado ({timeout}s): o comando ficou esperando algo?")


def rodar_vm(host: str, script: str, root: bool = True, timeout: int = 90):
    _garantir_ssh_cfg()
    remoto = "sudo -n bash -s" if root else "bash -s"
    args = ["ssh", *SSH_OPTS, host, remoto]
    try:
        return subprocess.run(args, input="export LC_ALL=C\n" + script, capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=timeout)
    except subprocess.TimeoutExpired:
        return _falhou(args, 124, "tempo esgotado")


def problema_vm(host: str, r) -> str:
    e = r.stderr or ""
    if r.returncode == 255 and not CHAVE.exists():
        return ("o treino ainda não tem acesso às VMs: rode `treino conectar` em outro terminal "
                "(isso é o exercício s00.ssh; o que você fez dentro da VM pode estar certo)")
    if r.returncode == 255:
        return (f"o treino não conseguiu entrar na '{host}' (a VM está ligada? já rodou `treino conectar`?)"
                + (f"\n   detalhe: {r.stderr.strip().splitlines()[-1]}" if r.stderr.strip() else ""))
    if "password is required" in e or "terminal is required" in e:
        return f"o sudo na '{host}' pediu senha: configure o sudo sem senha (exercício s00.sudo)"
    return ""


def checar(checks, hosts, sb=None, ocultar=False, falar=True) -> bool:
    total = ok = 0
    avisos = set()
    for item in checks:
        desc, script = item[0], item[1]
        alvos = [item[2]] if len(item) > 2 else hosts
        for h in alvos:
            total += 1
            if h == "sandbox":
                r = rodar_local(script, sb)
            elif h == "local":
                if "SSH_TREINO" in script or str(SSH_CFG) in script:
                    _garantir_ssh_cfg()
                r = rodar_local(script, Path.home(), timeout=60)
            else:
                r = rodar_vm(h, script)
                p = problema_vm(h, r)
                if p:
                    avisos.add(p)
            passou = r.returncode == 0
            ok += passou
            if falar and not ocultar:
                rot = f"[{h}] " if h not in ("sandbox", "local") else ""
                print(f"   {'✅' if passou else '❌'} {rot}{desc}")
    if falar and ocultar:
        print(f"   {'✅' if ok == total else '🔎'} {ok} de {total} resolvidos")
    if falar:
        for a in sorted(avisos):
            print(amarelo(f"   ⚠️  {a}"))
    return ok == total


def mostrar_saida(r, max_l: int = 15):
    out = r.stdout.rstrip("\n").splitlines()
    err = r.stderr.rstrip("\n").splitlines()
    for l in out[:max_l]:
        print(cinza("   │ ") + l)
    if len(out) > max_l:
        print(cinza(f"   │ … (+{len(out) - max_l} linhas)"))
    for l in err[:6]:
        print(cinza("   │ ") + vermelho(l))
    if not out and not err:
        print(cinza("   │ (sem saída)"))


def explicar_diferenca(obt: list[str], esp: list[str]) -> str:
    if not obt:
        return "seu comando não imprimiu nada na saída padrão."
    if sorted(obt) == sorted(esp):
        return "o conteúdo está certo, mas a ORDEM não."
    if set(esp) < set(obt):
        return f"tem linhas a mais (você: {len(obt)}, esperado: {len(esp)})."
    if set(obt) < set(esp):
        return f"faltam linhas (você: {len(obt)}, esperado: {len(esp)})."
    for i, (a, b) in enumerate(zip(obt, esp)):
        if a != b:
            return f"a linha {i + 1} da sua saída não confere (você: {len(obt)} linhas, esperado: {len(esp)})."
    return f"quantidade de linhas diferente (você: {len(obt)}, esperado: {len(esp)})."


def snap_nome(ex_id: str) -> str:
    return "treino-" + re.sub(r"[^a-zA-Z0-9]+", "-", ex_id)


def snapshot(dom: str, nome: str):
    subprocess.run(VIRSH + ["snapshot-delete", dom, nome], capture_output=True)
    r = subprocess.run(VIRSH + ["snapshot-create-as", dom, nome], capture_output=True, text=True)
    return r.returncode == 0, r.stderr.strip()


def restaurar(dom: str, nome: str):
    r = subprocess.run(VIRSH + ["snapshot-revert", dom, nome], capture_output=True, text=True)
    return r.returncode == 0, r.stderr.strip()


# ───────────────────────────── progresso ─────────────────────────────
class Progresso:
    def __init__(self):
        try:
            self.d = json.loads(PROGRESSO.read_text())
        except (FileNotFoundError, json.JSONDecodeError):
            self.d = {}

    def _e(self, i):
        return self.d.setdefault(i, {"status": "", "erros": 0})

    def status(self, i) -> str:
        return self.d.get(i, {}).get("status", "")

    def erros(self, i) -> int:
        return self.d.get(i, {}).get("erros", 0)

    def registrar(self, i, st):
        e = self._e(i)
        if e["status"] != "ok":
            e["status"] = st
        e["quando"] = time.strftime("%Y-%m-%d %H:%M")
        self.salvar()

    def erro(self, i):
        self._e(i)["erros"] += 1
        self.salvar()

    def salvar(self):
        tmp = PROGRESSO.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.d, indent=1, ensure_ascii=False))
        tmp.replace(PROGRESSO)


# ───────────────────────────── contexto ─────────────────────────────
ESPECIAIS = {":dica", ":resposta", ":pular", ":sair", ":shell", ":reset", ":restaurar", ":ajuda", ":?"}
AJUDA = (":dica  ·  :resposta (mostra e segue)  ·  :pular  ·  :shell (abre terminal)  ·  "
         ":reset (recria arquivos)  ·  :restaurar (volta snapshot)  ·  :sair")


class Contexto:
    def __init__(self):
        self.prog = Progresso()

    def sandbox(self, ex, novo=True) -> Path:
        sb = SANDBOX / re.sub(r"[^\w.-]", "_", ex.id)
        if novo and sb.exists():
            subprocess.run(["chmod", "-R", "u+rwx", str(sb)], capture_output=True)
            shutil.rmtree(sb, ignore_errors=True)
        if not sb.exists():
            sb.mkdir(parents=True)
            dados.gerar(sb)
            if getattr(ex, "preparar", ""):
                rodar_local(ex.preparar, sb, timeout=60)
        return sb

    def shell(self, ex):
        if isinstance(ex, (Comando, Script)):
            sb = self.sandbox(ex, novo=False)
            rc = SANDBOX / ".bashrc_treino"
            rc.write_text('[ -f ~/.bashrc ] && . ~/.bashrc\nPS1="(treino) \\w \\$ "\n')
            print(cinza(f"   Abrindo bash em {sb}. Digite exit para voltar ao treino."))
            subprocess.run(["bash", "--rcfile", str(rc)], cwd=sb, env=dict(os.environ, GNUPGHOME=str(sb / ".gnupg")))
        elif hasattr(ex, "hosts") and ex.hosts()[0] not in ("local", "sandbox"):
            h = ex.hosts()[0]
            print(cinza(f"   Abrindo ssh {h}. Digite exit para voltar ao treino."))
            subprocess.run(["ssh", h])
        else:
            print(cinza("   Abrindo bash. Digite exit para voltar ao treino."))
            subprocess.run(["bash"], cwd=Path.home())


# ───────────────────────────── exercícios ─────────────────────────────
@dataclass(kw_only=True)
class Ex:
    id: str
    titulo: str
    enunciado: str = ""
    dica: str = ""
    explicacao: str = ""
    prova: str | None = None
    tipo = "exercício"

    def solucao(self) -> str:
        return ""

    def mostrar(self):
        print(txt(self.enunciado))

    def explicar(self):
        if self.explicacao:
            print(magenta(txt("📘 " + textwrap.dedent(self.explicacao).strip())))

    def especial(self, ctx, c):
        if c == ":sair":
            raise Sair
        if c == ":pular":
            return "pulou"
        if c == ":dica":
            print(amarelo(txt("💡 " + textwrap.dedent(self.dica or "Não tenho dica para este. Se travou, :resposta.").strip())))
            return None
        if c == ":resposta":
            print(amarelo("   Resposta:"))
            print(txt(self.solucao(), "     "))
            self.explicar()
            return "viu"
        if c == ":shell":
            ctx.shell(self)
            return None
        if c == ":reset" and isinstance(self, (Comando, Script)):
            if isinstance(self, Script):
                print(amarelo("   Em exercícios de script o :reset não apaga seu script. Apague-o você mesmo se quiser."))
                return None
            ctx.sandbox(self, novo=True)
            print(cinza("   Arquivos do exercício recriados."))
            return None
        if c == ":restaurar" and isinstance(self, Tarefa) and self.quebrar:
            for h in self.hosts():
                ok, err = restaurar(dominio(h), snap_nome(self.id))
                print(f"   {'✅' if ok else '❌'} {h} restaurada {err}")
            return None
        print(cinza("   " + AJUDA))
        return None

    def loop(self, ctx, avaliar, enter_avalia=False, prompt="› "):
        tent = 0
        while True:
            r = entrada(prompt)
            c = r.strip()
            if c in ESPECIAIS:
                res = self.especial(ctx, c)
                if res in ("pulou", "viu"):
                    return res
                continue
            if not c and not enter_avalia:
                continue
            if avaliar(r):
                print(verde("   ✅ Correto!"))
                self.explicar()
                return "ok"
            tent += 1
            ctx.prog.erro(self.id)
            print(vermelho("   ❌ Ainda não.") + cinza(f"  tentativa {tent} · :dica · :resposta · :pular"))


@dataclass(kw_only=True)
class Quiz(Ex):
    respostas: list = field(default_factory=list)
    resposta: str = ""
    exato: bool = False
    tipo = "pergunta"

    def solucao(self):
        return self.resposta or str(self.respostas[0])

    def confere(self, r: str) -> bool:
        for a in self.respostas:
            if callable(a):
                try:
                    if a(r.strip()):
                        return True
                except Exception:
                    pass
            elif self.exato:
                if re.sub(r"\s+", " ", r.strip()) == a:
                    return True
            elif norm(r) == norm(a):
                return True
        return False

    def rodar(self, ctx):
        self.mostrar()
        return self.loop(ctx, self.confere)


@dataclass(kw_only=True)
class Escolha(Ex):
    opcoes: list = field(default_factory=list)
    correta: str = "a"
    tipo = "múltipla escolha"

    def mostrar(self):
        print(txt(self.enunciado))
        for i, o in enumerate(self.opcoes):
            print(f"     {chr(97 + i)}) {o}")
        if len(self.correta) > 1:
            print(cinza(f"     (marque {len(self.correta)} letras, ex.: ac)"))

    def confere(self, r: str) -> bool:
        return "".join(sorted(set(re.sub(r"[^a-z]", "", r.lower())))) == "".join(sorted(self.correta))

    def solucao(self):
        return "\n".join(f"{l}) {self.opcoes[ord(l) - 97]}" for l in self.correta)

    def rodar(self, ctx):
        self.mostrar()
        return self.loop(ctx, self.confere)


@dataclass(kw_only=True)
class Comando(Ex):
    """Você digita um comando; ele roda numa pasta com arquivos de exemplo e é conferido."""
    esperado: str = ""          # comando de referência: a saída do seu precisa ser igual
    verificar: list = field(default_factory=list)  # [(descrição, script)] conferidos na pasta depois
    preparar: str = ""
    ordem: bool = True
    exigir: list = field(default_factory=list)
    proibir: list = field(default_factory=list)
    saida_vazia: bool = False
    resposta: str = ""
    tipo = "comando"

    def solucao(self):
        return self.resposta or self.esperado

    def referencia(self, sb):
        return linhas(rodar_local(self.esperado, sb).stdout) if self.esperado else None

    def testar(self, c, sb, ref, falar=True) -> bool:
        for t in self.exigir:
            if t not in c:
                falar and print(amarelo(f"   ⚠️  Neste exercício você precisa usar {t!r}."))
                return False
        for t in self.proibir:
            if t in c:
                falar and print(amarelo(f"   ⚠️  Neste exercício não vale usar {t!r}."))
                return False
        r = rodar_local(c, sb)
        if falar:
            mostrar_saida(r)
        if self.saida_vazia and (r.stdout.strip() or r.stderr.strip()):
            falar and print(amarelo("   ⚠️  Nada deveria aparecer na tela."))
            return False
        if ref is not None:
            obt = linhas(r.stdout)
            a, b = (obt, ref) if self.ordem else (sorted(obt), sorted(ref))
            if a != b:
                falar and print(amarelo("   ↳ " + explicar_diferenca(obt, ref)))
                return False
        if self.verificar:
            return checar(self.verificar, ["sandbox"], sb, falar=falar)
        return True

    def rodar(self, ctx):
        sb = ctx.sandbox(self, novo=True)
        self.mostrar()
        print(cinza(f"   📁 roda em {sb}\n   digite o comando · :shell abre um terminal lá · :reset recria os arquivos"))
        ref = self.referencia(sb)
        return self.loop(ctx, lambda c: self.testar(c, sb, ref), prompt="$ ")


@dataclass(kw_only=True)
class Script(Ex):
    """Você escreve um script num arquivo; ENTER roda os testes automáticos."""
    arquivo: str
    testes: list = field(default_factory=list)
    preparar: str = ""
    resposta: str = ""
    tipo = "script"

    def solucao(self):
        return self.resposta

    def testar(self, sb, falar=True) -> bool:
        arq = sb / self.arquivo
        if not arq.exists():
            falar and print(amarelo(f"   Ainda não existe {arq}."))
            return False
        tudo = True
        for t in self.testes:
            args = " ".join(shlex.quote(a) for a in t.get("args", []))
            r = rodar_local(f"bash ./{self.arquivo} {args}", sb, stdin_txt=t.get("stdin", ""))
            ok = True
            motivos = []
            if "saida" in t and linhas(r.stdout) != linhas(t["saida"]):
                ok = False
                motivos.append(f"saída esperada: {t['saida']!r}\n      sua saída:     {r.stdout.strip()!r}")
            if "codigo" in t and r.returncode != t["codigo"]:
                ok = False
                motivos.append(f"código de saída esperado {t['codigo']}, o seu foi {r.returncode}")
            if t.get("stderr") and not r.stderr.strip():
                ok = False
                motivos.append("deveria escrever uma mensagem no stderr (>&2)")
            if falar:
                desc = t.get("desc") or f"./{self.arquivo} {args}".strip()
                if "stdin" in t:
                    desc += f"   (entrada: {t['stdin']!r})"
                print(f"   {'✅' if ok else '❌'} {desc}")
                for m in motivos:
                    print(cinza(f"      {m}"))
                if not ok and r.stderr.strip() and not t.get("stderr"):
                    print(cinza("      stderr: ") + vermelho(r.stderr.strip().splitlines()[-1]))
            tudo &= ok
        if falar and shutil.which("shellcheck"):
            sc = subprocess.run(["shellcheck", "-f", "gcc", str(arq)], capture_output=True, text=True)
            n = len(sc.stdout.splitlines())
            print(cinza(f"   shellcheck: {'nenhum aviso' if n == 0 else f'{n} aviso(s): rode shellcheck {arq}'}"))
        return tudo

    def rodar(self, ctx):
        sb = ctx.sandbox(self, novo=False)
        self.mostrar()
        print(cinza(f"   📝 escreva o script em {sb / self.arquivo}\n"
                    f"   (:shell abre um terminal na pasta; use vim/nano) · ENTER roda os testes"))
        return self.loop(ctx, lambda _: self.testar(sb), enter_avalia=True)


@dataclass(kw_only=True)
class Tarefa(Ex):
    """Você faz algo no Fedora ou nas VMs; ENTER confere o estado real do sistema."""
    host: str = "local"          # "local", "rhel", "ubuntu" ou "rhel+ubuntu"
    checks: list = field(default_factory=list)
    quebrar: str = ""            # cenário: script que quebra algo antes (com snapshot)
    ocultar: bool = False        # não revela o que falta, só quantos
    resposta: str = ""
    onde: str = ""               # sobrescreve o texto "Faça a tarefa ..." quando a checagem é local mas o trabalho não
    tipo = "tarefa"

    def hosts(self):
        return self.host.split("+")

    def solucao(self):
        return self.resposta or "Sem gabarito único: use as dicas, o man e a documentação."

    def _cenario(self) -> bool:
        print(amarelo(f"   ⚠️  Cenário: vou QUEBRAR algo em {' e '.join(self.hosts())}. "
                      f"Antes, tiro um snapshot ({snap_nome(self.id)})."))
        if entrada("   Continuar? [s/N] ").strip().lower() != "s":
            return False
        for h in self.hosts():
            ok, err = snapshot(dominio(h), snap_nome(self.id))
            if not ok:
                print(vermelho(f"   Não consegui tirar snapshot de '{dominio(h)}': {err}"))
                if entrada("   Quebrar mesmo assim? [s/N] ").strip().lower() != "s":
                    return False
            r = rodar_vm(h, self.quebrar, timeout=60)
            p = problema_vm(h, r)
            if p:
                print(vermelho("   " + p))
                return False
        print(vermelho("   💥 Pronto, quebrei. Agora é com você.") + cinza("  (:restaurar volta ao snapshot)"))
        return True

    def rodar(self, ctx):
        self.mostrar()
        if self.quebrar and not self._cenario():
            return "pulou"
        onde = self.onde or ("no seu Fedora" if self.hosts() == ["local"] else "em " + " e ".join(self.hosts()))
        print(cinza(f"   Faça a tarefa {onde} (em outro terminal ou com :shell). ENTER confere."))
        return self.loop(ctx, lambda _: checar(self.checks, self.hosts(), ocultar=self.ocultar), enter_avalia=True)


@dataclass(kw_only=True)
class PerguntaVM(Ex):
    """Pergunta cuja resposta certa é lida na VM na hora (você precisa investigar lá)."""
    host: str = "rhel"
    cmd: str = ""
    root: bool = True
    tipo = "investigação na VM"

    def hosts(self):
        return [self.host]

    def _buscar(self):
        r = rodar_vm(self.host, self.cmd, root=self.root)
        self.__dict__["_esp"] = r.stdout.strip() if r.returncode == 0 else ""
        if not self._esp:
            print(vermelho(f"   Não consegui obter a resposta na '{self.host}'. ") + cinza(problema_vm(self.host, r)))
        return self._esp

    def solucao(self):
        return self.__dict__.get("_esp") or f"(rode na {self.host}: {self.cmd})"

    def rodar(self, ctx):
        self.mostrar()
        print(cinza(f"   Investigue na {self.host} (:shell abre ssh) e responda aqui."))
        self.__dict__["_esp"] = ""

        def av(r):
            esp = self.__dict__.get("_esp") or self._buscar()
            return bool(esp) and norm(r) == norm(esp)
        return self.loop(ctx, av)


@dataclass(kw_only=True)
class Subnet(Ex):
    """Bateria de subnetting gerada na hora."""
    n: int = 10
    prefixos: tuple = (24, 30)
    meta: int = 8
    tipo = "subnetting"

    def rodar(self, ctx):
        self.mostrar()
        print(cinza(f"   {self.n} questões, meta {self.meta}. Para cada uma: rede, broadcast, hosts válidos e máscara."))
        rng = random.Random()
        blocos = [ipaddress.ip_network(b) for b in ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16")]
        acertos = 0
        for i in range(self.n):
            b = rng.choice(blocos)
            ip = b.network_address + rng.randrange(b.num_addresses)
            p = rng.randint(*self.prefixos)
            net = ipaddress.ip_network(f"{ip}/{p}", strict=False)
            certo = {"rede": str(net.network_address), "broadcast": str(net.broadcast_address),
                     "hosts": str(2 ** (32 - p) - 2), "máscara": str(net.netmask)}
            print(negrito(f"\n   [{i + 1}/{self.n}] {ip}/{p}"))
            erros = []
            for campo in ("rede", "broadcast", "hosts", "máscara"):
                r = entrada(f"     {campo}: ").strip()
                if r == ":sair":
                    raise Sair
                r = r.split("/")[0]
                if r != certo[campo]:
                    erros.append(campo)
            if erros:
                ctx.prog.erro(self.id)
                print(vermelho(f"     ❌ errou: {', '.join(erros)}") + cinza(
                    f"  → rede {certo['rede']} · broadcast {certo['broadcast']} · hosts {certo['hosts']} · máscara {certo['máscara']}"))
            else:
                acertos += 1
                print(verde("     ✅"))
        print(negrito(f"\n   Resultado: {acertos}/{self.n}"))
        if acertos >= self.meta:
            print(verde("   ✅ Meta batida!"))
            return "ok"
        print(amarelo(f"   Meta: {self.meta}. Treine mais com `treino subnet` e refaça."))
        return "falhou"


@dataclass(kw_only=True)
class Marco(Ex):
    """Algo fora do terminal (curso, prova, post). Você confirma quando fizer."""
    tipo = "marco"

    def rodar(self, ctx):
        self.mostrar()
        r = entrada("   Concluído? [s/N] ").strip().lower()
        if r == ":sair":
            raise Sair
        return "ok" if r == "s" else "pulou"
