"""Arquivos de exemplo usados nos exercícios de comando (semente fixa: sempre iguais)."""
import gzip
import os
import random
import time
from datetime import datetime, timedelta
from pathlib import Path

FALHAS = {"203.0.113.5": 57, "198.51.100.23": 31, "192.0.2.44": 23, "203.0.113.99": 14,
          "45.33.32.156": 9, "198.51.100.7": 4, "172.16.5.4": 2}
VALIDOS = ["root", "diego", "maria"]
INVALIDOS = ["admin", "test", "oracle", "guest", "pi"]
RUIDO = [
    ("CRON", "pam_unix(cron:session): session opened for user root(uid=0) by (uid=0)"),
    ("CRON", "pam_unix(cron:session): session closed for user root"),
    ("systemd-logind", "New session 7 of user diego."),
    ("systemd-logind", "Removed session 6."),
]

PASSWD = """\
root:x:0:0:root:/root:/bin/bash
bin:x:1:1:bin:/bin:/usr/sbin/nologin
daemon:x:2:2:daemon:/sbin:/usr/sbin/nologin
sshd:x:74:74:Privilege-separated SSH:/usr/share/empty.sshd:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
mysql:x:27:27:MySQL Server:/var/lib/mysql:/bin/false
diego:x:1000:1000:Diego:/home/diego:/bin/bash
maria:x:1001:1001:Maria Souza:/home/maria:/bin/bash
joao:x:1002:1002:Joao Lima:/home/joao:/bin/zsh
backup:x:1003:1003::/home/backup:/bin/sh
suporte:x:0:0::/root:/bin/bash
nobody:x:65534:65534:Kernel Overflow User:/:/usr/sbin/nologin
"""

VENDAS = """\
produto,regiao,valor
notebook,sul,4500
mouse,norte,80
teclado,sul,150
monitor,leste,1200
notebook,oeste,4700
headset,norte,300
mouse,leste,90
monitor,sul,1150
cadeira,oeste,900
teclado,norte,170
webcam,leste,250
notebook,norte,4400
"""

FRUTAS = ["banana", "maca", "uva", "banana", "laranja", "Banana", "kiwi", "uva",
          "manga", "banana", "pera", "maca", "abacaxi"]

PROCESSOS = """\
USER         PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root           1  0.0  0.3 171820 13200 ?        Ss   08:00   0:02 /usr/lib/systemd/systemd --switched-root
root         612  0.0  0.2  23800  9100 ?        Ss   08:00   0:00 /usr/lib/systemd/systemd-journald
root         780  0.0  0.1  15400  6200 ?        Ss   08:00   0:00 sshd: /usr/sbin/sshd -D [listener]
root         801  0.1  0.5 251000 21000 ?        Ssl  08:00   0:05 /usr/sbin/NetworkManager --no-daemon
mysql        950  1.2  9.8 1830000 401000 ?      Ssl  08:01   2:10 /usr/sbin/mariadbd
www-data    1010  0.3  2.1 210000 86000 ?        S    08:01   0:20 /usr/sbin/apache2 -k start
www-data    1011  0.2  1.9 210000 78000 ?        S    08:01   0:15 /usr/sbin/apache2 -k start
www-data    1666 97.5  4.4 520000 180000 ?       R    09:12  58:31 /tmp/.x/kworkerd -o pool.minexmr.com:4444
diego       2200  0.0  0.1  10200  5100 pts/0    Ss   09:30   0:00 -bash
diego       2310  0.5  6.2 900000 254000 pts/0   Sl+  09:31   0:40 python3 relatorio.py
root        2400  0.0  0.0      0     0 ?        I    09:40   0:00 [kworker/u8:2-events]
root        2501  0.0  0.1  12000  4100 ?        Ss   09:41   0:00 /usr/sbin/crond -n
"""

GERA_SAIDA = """\
#!/bin/bash
echo "processando arquivo 1"
echo "ERRO: disco cheio" >&2
echo "processando arquivo 2"
echo "ERRO: permissão negada" >&2
echo "concluído"
"""

REQS = {"10.0.0.15": 120, "10.0.0.22": 64, "45.33.32.156": 33, "10.0.0.31": 17, "192.0.2.10": 8}
NORMAIS = ["/", "/index.html", "/produtos", "/carrinho", "/api/estoque", "/css/site.css", "/img/logo.png"]
SCAN = ["/wp-login.php", "/.env", "/admin", "/phpmyadmin/", "/.git/config", "/backup.zip", "/login"]


def _linha_syslog(t, proc, msg):
    return f"Nov {t.day:2d} {t:%H:%M:%S} srv {proc}: {msg}"


def _auth_log(rng):
    ev = []
    for ip, n in FALHAS.items():
        for _ in range(n):
            porta = rng.randint(30000, 65000)
            pid = rng.randint(2000, 9000)
            if rng.random() < 0.45:
                msg = f"Failed password for invalid user {rng.choice(INVALIDOS)} from {ip} port {porta} ssh2"
            else:
                msg = f"Failed password for {rng.choice(VALIDOS)} from {ip} port {porta} ssh2"
            ev.append((f"sshd[{pid}]", msg, ip))
    for _ in range(20):
        proc, msg = rng.choice(RUIDO)
        ev.append((f"{proc}[{rng.randint(2000, 9000)}]", msg, ""))
    for _ in range(3):
        ev.append((f"sshd[{rng.randint(2000, 9000)}]",
                   f"Accepted publickey for diego from 192.168.122.1 port {rng.randint(30000, 65000)} ssh2: ED25519 SHA256:q1w2e3r4t5y6",
                   "192.168.122.1"))
    rng.shuffle(ev)
    ult = max(i for i, e in enumerate(ev) if e[2] == "198.51.100.23")
    pid = rng.randint(2000, 9000)
    ev[ult + 1:ult + 1] = [
        (f"sshd[{pid}]", "Accepted password for maria from 198.51.100.23 port 51122 ssh2", "198.51.100.23"),
        (f"sshd[{pid}]", "pam_unix(sshd:session): session opened for user maria(uid=1001) by (uid=0)", ""),
        ("sudo", "   maria : TTY=pts/1 ; PWD=/home/maria ; USER=root ; COMMAND=/usr/bin/cat /etc/shadow", ""),
        (f"useradd[{pid + 40}]", "new user: name=suporte, UID=0, GID=0, home=/root, shell=/bin/bash", ""),
    ]
    t = datetime(2026, 11, 16, 8, 0, 0)
    out = []
    for proc, msg, _ in ev:
        t += timedelta(seconds=rng.randint(3, 40))
        out.append(_linha_syslog(t, proc, msg))
    return "\n".join(out) + "\n"


def _auth_antigo(rng):
    ev = [f"Failed password for root from 10.9.8.7 port {rng.randint(30000, 65000)} ssh2" for _ in range(12)]
    ev += [m for _, m in rng.choices(RUIDO, k=6)]
    rng.shuffle(ev)
    t = datetime(2026, 11, 9, 22, 0, 0)
    out = []
    for m in ev:
        t += timedelta(seconds=rng.randint(5, 60))
        out.append(_linha_syslog(t, f"sshd[{rng.randint(2000, 9000)}]", m))
    return "\n".join(out) + "\n"


def _access_log(rng):
    ev = []
    for ip, n in REQS.items():
        for _ in range(n):
            if ip == "45.33.32.156":
                ev.append((ip, rng.choice(SCAN), rng.choice([404, 404, 404, 403]), "zgrab/0.x"))
            else:
                st = rng.choices([200, 304, 404, 500], [80, 10, 6, 4])[0]
                ev.append((ip, rng.choice(NORMAIS), st, "Mozilla/5.0 (X11; Linux x86_64) Firefox/140.0"))
    rng.shuffle(ev)
    t = datetime(2026, 11, 16, 10, 0, 0)
    out = []
    for ip, path, st, ua in ev:
        t += timedelta(seconds=rng.randint(1, 20))
        metodo = "POST" if path in ("/carrinho", "/wp-login.php", "/login") and rng.random() < 0.5 else "GET"
        tam = 0 if st == 304 else rng.randint(200, 9000)
        out.append(f'{ip} - - [16/Nov/2026:{t:%H:%M:%S} -0300] "{metodo} {path} HTTP/1.1" {st} {tam} "-" "{ua}"')
    return "\n".join(out) + "\n"


def _app_log(rng):
    msgs = {"INFO": ["usuário autenticado", "relatório gerado", "cache atualizado", "requisição concluída"],
            "WARN": ["uso de disco acima de 80%", "resposta lenta do banco", "certificado vence em 20 dias"],
            "ERROR": ["falha ao conectar no banco", "timeout na API de estoque", "permissão negada em /srv/dados"]}
    niveis = ["INFO"] * 40 + ["WARN"] * 12 + ["ERROR"] * 5
    rng.shuffle(niveis)
    t = datetime(2026, 11, 16, 9, 0, 0)
    out = []
    for n in niveis:
        t += timedelta(seconds=rng.randint(10, 300))
        out.append(f"{t:%Y-%m-%d %H:%M:%S} [{n}] {rng.choice(msgs[n])}")
    return "\n".join(out) + "\n"


def _disco(p: Path, rng):
    data = bytearray(rng.randbytes(1024 * 1024))
    for off, s in ((300_000, b"\x00SENHA=Tr0ub4dor&3\x00"), (600_000, b"\x00relatorio_financeiro_2026.xlsx\x00")):
        data[off:off + len(s)] = s
    p.write_bytes(bytes(data))


def _arvore(a: Path):
    arquivos = {
        "etc/app.conf": b"porta=8080\nlog=/var/log/app.log\n",
        "etc/db.conf": b"host=localhost\nuser=app\n",
        "etc/notas.txt": b"lembrar de trocar a senha do banco\n",
        "var/log/grande.log": b"x" * (2 * 1024 * 1024),
        "var/log/pequeno.log": b"linha\n" * 2000,
        "var/log/vazio.log": b"",
        "home/ana/.bashrc": b"alias ll='ls -l'\n",
        "home/ana/backup.tar": b"\0" * (1536 * 1024),
        "home/ana/script.sh": b"#!/bin/bash\necho ola\n",
        "home/ana/vazio.txt": b"",
        "tmp/.oculto": b"nada aqui\n",
        "tmp/ferramenta": b"#!/bin/sh\nid\n",
        "opt/antigo1.txt": b"velho\n",
        "opt/antigo2.conf": b"velho=1\n",
    }
    for rel, conteudo in arquivos.items():
        p = a / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(conteudo)
    (a / "tmp/ferramenta").chmod(0o4755)
    (a / "home/ana/script.sh").chmod(0o755)
    velho = time.time() - 60 * 86400
    for rel in ("opt/antigo1.txt", "opt/antigo2.conf"):
        os.utime(a / rel, (velho, velho))


def gerar(sb: Path):
    rng = random.Random(42)
    (sb / "auth.log").write_text(_auth_log(rng))
    (sb / "antigo.log.gz").write_bytes(gzip.compress(_auth_antigo(rng).encode(), mtime=0))
    (sb / "access.log").write_text(_access_log(rng))
    (sb / "app.log").write_text(_app_log(rng))
    (sb / "passwd.txt").write_text(PASSWD)
    (sb / "vendas.csv").write_text(VENDAS)
    (sb / "frutas.txt").write_text("\n".join(FRUTAS) + "\n")
    (sb / "processos.txt").write_text(PROCESSOS)
    s = sb / "gera_saida.sh"
    s.write_text(GERA_SAIDA)
    s.chmod(0o755)
    _disco(sb / "disco.img", rng)
    _arvore(sb / "arvore")
    (sb / ".gnupg").mkdir(mode=0o700, exist_ok=True)
