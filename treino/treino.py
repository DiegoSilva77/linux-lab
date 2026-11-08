#!/usr/bin/env python3
"""treino: exercícios interativos do Plano de Férias (Linux, redes e segurança).

Uso:
  treino                 menu
  treino 3               semana 3 (só o que falta)
  treino 3 --tudo        semana 3 inteira, inclusive o que já acertou
  treino subnet          subnetting livre (20 questões)
  treino simulado 101    simulado LPIC-1 101 (ou 102)
  treino erros           refaz o que você pulou, viu a resposta ou errou
  treino progresso       mostra o progresso
  treino conectar        dá ao treino acesso às VMs (para ele corrigir as tarefas)
"""
import argparse
import importlib
import random
import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import motor  # noqa: E402
from motor import (AJUDA, Comando, Contexto, Escolha, Quiz, Sair, Script, Subnet, amarelo, azul,  # noqa: E402
                   cinza, entrada, negrito, txt, verde, vermelho)

SEMANAS = list(range(12))
_CACHE = {}


def carregar(n: int):
    if n not in _CACHE:
        m = importlib.import_module(f"exercicios.s{n:02d}")
        for e in m.EXERCICIOS:
            if isinstance(e, (Quiz, Escolha)) and e.prova is None:
                e.prova = "101" if 1 <= n <= 5 else "102" if 8 <= n <= 10 else ""
        _CACHE[n] = m
    return _CACHE[n]


def todos():
    for n in SEMANAS:
        for e in carregar(n).EXERCICIOS:
            yield n, e


def barra(f: float, w: int = 14) -> str:
    k = round(f * w)
    return verde("█" * k) + cinza("░" * (w - k))


def painel(ctx):
    print(negrito("\n  PLANO DE FÉRIAS · treino interativo\n"))
    for n in SEMANAS:
        m = carregar(n)
        ids = [e.id for e in m.EXERCICIOS]
        ok = sum(ctx.prog.status(i) == "ok" for i in ids)
        print(f"  {n:>2}  {barra(ok / len(ids))} {ok:>3}/{len(ids):<3} {m.TITULO}  {cinza(m.DATAS)}")


def rodar_lista(ctx, exs) -> bool:
    for i, e in enumerate(exs, 1):
        print("\n" + negrito(f"── [{i}/{len(exs)}] {e.titulo}") + cinza(f"   {e.tipo} · {e.id}"))
        try:
            st = e.rodar(ctx)
        except Sair:
            print(cinza("   Progresso salvo. Até a próxima."))
            return False
        ctx.prog.registrar(e.id, st)
    return True


def rodar_semana(ctx, n: int, tudo=False):
    m = carregar(n)
    exs = [e for e in m.EXERCICIOS if tudo or ctx.prog.status(e.id) != "ok"]
    print(negrito(f"\n═══ Semana {n}: {m.TITULO}  ({m.DATAS})"))
    print(txt(m.OBJETIVO))
    if not exs:
        print(verde("\n   Tudo concluído nesta semana! (use --tudo para refazer)"))
        return
    print(cinza(f"\n   {len(exs)} exercício(s) pendente(s). Comandos disponíveis:\n   {AJUDA}"))
    if rodar_lista(ctx, exs):
        ok = sum(ctx.prog.status(e.id) == "ok" for e in m.EXERCICIOS)
        print(negrito(f"\n   Semana {n}: {ok}/{len(m.EXERCICIOS)} concluídos."))
        faltam = [e for e in m.EXERCICIOS if ctx.prog.status(e.id) != "ok"]
        if faltam:
            print(amarelo(f"   Faltam {len(faltam)}. Rode `treino {n}` de novo para continuar neles."))


def revisar_erros(ctx):
    exs = [e for _, e in todos()
           if ctx.prog.status(e.id) in ("viu", "pulou", "falhou")
           or (ctx.prog.erros(e.id) > 0 and ctx.prog.status(e.id) != "ok")]
    if not exs:
        print(verde("   Nada para revisar. 👏"))
        return
    print(negrito(f"\n═══ Revisão: {len(exs)} exercício(s)"))
    rodar_lista(ctx, exs)


def simulado(ctx, prova: str, n: int = 40):
    pool = [e for _, e in todos() if isinstance(e, (Quiz, Escolha)) and e.prova == prova]
    random.shuffle(pool)
    pool = pool[:n]
    print(negrito(f"\n═══ Simulado LPIC-1 {prova}: {len(pool)} questões, sem dicas"))
    print(cinza("   A prova real tem 60 questões em 90 min; a aprovação fica perto de 65–70% de acerto. :sair encerra.\n"))
    t0 = time.time()
    erradas = []
    feitas = 0
    for i, e in enumerate(pool, 1):
        print(negrito(f"[{i}/{len(pool)}]"))
        e.mostrar()
        try:
            r = entrada("› ")
        except Sair:
            break
        if r.strip() == ":sair":
            break
        feitas += 1
        if not e.confere(r):
            erradas.append((e, r))
        print()
    if not feitas:
        return
    acertos = feitas - len(erradas)
    pct = 100 * acertos / feitas
    mins = (time.time() - t0) / 60
    cor = verde if pct >= 70 else amarelo if pct >= 60 else vermelho
    print(negrito("\n═══ Resultado: ") + cor(f"{acertos}/{feitas} ({pct:.0f}%)") + cinza(f"  em {mins:.0f} min"))
    for e, r in erradas:
        print("\n" + vermelho("✗ ") + negrito(e.titulo) + cinza(f"  ({e.id})"))
        print(cinza("   sua resposta: ") + (r.strip() or "(vazia)"))
        print(cinza("   correta: ") + e.solucao().replace("\n", " | "))
        e.explicar()
    hist = ctx.prog.d.setdefault("_simulados", [])
    hist.append({"prova": prova, "quando": time.strftime("%Y-%m-%d %H:%M"), "acertos": acertos, "total": feitas})
    ctx.prog.salvar()


def menu(ctx):
    while True:
        painel(ctx)
        print(cinza("\n  número = semana  ·  s = subnetting livre  ·  101 / 102 = simulado  ·  e = revisar erros  ·  q = sair"))
        try:
            op = entrada("\n  escolha: ").strip().lower()
        except Sair:
            return
        try:
            if op in ("q", ":sair", "sair"):
                return
            if op == "s":
                Subnet(id="livre.subnet", titulo="Subnetting livre", n=20, prefixos=(16, 30), meta=0).rodar(ctx)
            elif op in ("101", "102"):
                simulado(ctx, op)
            elif op == "e":
                revisar_erros(ctx)
            elif op.isdigit() and int(op) in SEMANAS:
                rodar_semana(ctx, int(op))
        except Sair:
            pass


def conectar():
    """Cria a chave do treino e instala nas VMs. Você digita a senha de cada VM uma vez."""
    import json
    import subprocess
    print(negrito("\n═══ Dar ao treino acesso às VMs"))
    print(txt("""
    O treino entra nas VMs com uma chave SÓ DELE (fica em ~/linux-lab/treino/.ssh).
    Seu ~/.ssh não é tocado: você continua entrando com `ssh usuario@IP` e senha.
    Rode de novo se recriar uma VM ou se o treino disser que não consegue entrar."""))
    cfg = dict(motor.CFG)
    usuarios = dict(cfg.get("usuarios", {}))
    motor.SSH_DIR.mkdir(mode=0o700, exist_ok=True)
    if not motor.CHAVE.exists():
        subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-C", "treino-lab", "-f", str(motor.CHAVE)],
                       check=True)
    falhas = 0
    for h in ("rhel", "ubuntu"):
        ip = motor.ip_vm(h)
        if not ip:
            print(amarelo(f"\n   {h}: não achei o IP (a VM está ligada?). Pulei."))
            falhas += 1
            continue
        padrao = usuarios.get(h) or __import__("os").environ.get("USER", "")
        try:
            u = entrada(f"\n   Seu usuário na {h} [{padrao}]: ").strip() or padrao
        except Sair:
            return 1
        usuarios[h] = u
        cfg["usuarios"] = usuarios
        motor.CONFIG.write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n")
        motor.CFG.clear()
        motor.CFG.update(cfg)
        motor.atualizar_ssh_cfg()
        print(negrito(f"\n   {h} ({ip}): ") + f"digite a senha do {u} nessa VM")
        r = subprocess.run(["ssh-copy-id", "-i", str(motor.CHAVE) + ".pub",
                            "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null",
                            "-o", "LogLevel=ERROR", f"{u}@{ip}"], capture_output=False)
        ok = r.returncode == 0 and subprocess.run(["ssh", *motor.SSH_OPTS, h, "true"]).returncode == 0
        print(("   " + verde("✅ treino entra na " + h)) if ok else ("   " + vermelho("❌ falhou na " + h)))
        falhas += not ok
    return 1 if falhas else 0


def autoteste():
    """Confere se cada exercício aceita a própria resposta (para quem mantém o treino)."""
    from motor import Contexto as C
    ctx = C()
    ids, falhas = set(), 0
    for n, e in todos():
        if e.id in ids:
            print(vermelho(f"id duplicado: {e.id}"))
            falhas += 1
        ids.add(e.id)
        ok = True
        if isinstance(e, Quiz):
            primeira = e.respostas[0]
            ok = e.confere(primeira if isinstance(primeira, str) else e.resposta.split("  (")[0])
        elif isinstance(e, Escolha):
            ok = all(ord(l) - 97 < len(e.opcoes) for l in e.correta)
        elif isinstance(e, Comando):
            sb = ctx.sandbox(e, novo=True)
            ok = e.testar(e.solucao(), sb, e.referencia(sb), falar=False)
        elif isinstance(e, Script):
            sb = ctx.sandbox(e, novo=True)
            (sb / e.arquivo).write_text(e.resposta)
            ok = e.testar(sb, falar=False)
        if not ok:
            falhas += 1
            print(vermelho(f"FALHOU: {e.id}  ({e.titulo})"))
    print(f"{len(ids)} exercícios, {falhas} falha(s)")
    shutil.rmtree(Path(__file__).resolve().parent / ".sandbox", ignore_errors=True)
    return 1 if falhas else 0


def main():
    ap = argparse.ArgumentParser(prog="treino", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("alvo", nargs="?", help="número da semana, subnet, simulado, erros, progresso ou conectar")
    ap.add_argument("extra", nargs="?", help="101 ou 102 (para simulado)")
    ap.add_argument("--tudo", action="store_true", help="refaz também o que já acertou")
    ap.add_argument("--autoteste", action="store_true", help=argparse.SUPPRESS)
    a = ap.parse_args()
    if a.autoteste:
        sys.exit(autoteste())
    if a.alvo == "conectar":
        sys.exit(conectar())
    ctx = Contexto()
    try:
        if a.alvo is None:
            menu(ctx)
        elif a.alvo.isdigit():
            if int(a.alvo) not in SEMANAS:
                ap.error("semanas vão de 0 a 11")
            rodar_semana(ctx, int(a.alvo), a.tudo)
        elif a.alvo == "subnet":
            Subnet(id="livre.subnet", titulo="Subnetting livre", n=20, prefixos=(16, 30), meta=0).rodar(ctx)
        elif a.alvo == "simulado":
            simulado(ctx, a.extra or "101")
        elif a.alvo == "erros":
            revisar_erros(ctx)
        elif a.alvo == "progresso":
            painel(ctx)
        else:
            ap.error(f"não conheço '{a.alvo}'")
    except Sair:
        pass


if __name__ == "__main__":
    main()
