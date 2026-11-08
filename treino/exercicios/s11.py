from motor import Escolha, Marco, Quiz, Tarefa

TITULO = "Prova 102 + portfólio"
DATAS = "25–31/01"
OBJETIVO = """
Consolidar, medir a evolução e deixar tudo apresentável.
Seg e qui: `treino simulado 102`. Ter e qua: `treino erros` e revisão dos tópicos fracos.
Sex: refaça o diagnóstico abaixo. Sáb (~30/01): prova.
"""

EXERCICIOS = [
    Marco(id="s11.sim1", titulo="Simulado 102 #1",
          enunciado="Rodou `treino simulado 102` e anotou os tópicos em que errou?"),
    Marco(id="s11.revisao", titulo="Revisão dos erros",
          enunciado="Rodou `treino erros` até zerar (ou quase) a lista?"),
    Marco(id="s11.sim2", titulo="Simulado 102 #2",
          enunciado="Rodou o segundo simulado com 75% ou mais?"),

    # ── diagnóstico de novembro, refeito ──
    Quiz(id="s11.diag.1", titulo="Diagnóstico: redirecionamento", prova="",
         enunciado="Rode find / -name '*.conf', descarte os erros e salve o resultado em achados.txt. Escreva o comando:",
         respostas=[lambda r: "2>/dev/null" in r.replace(" ", "") and ">achados.txt" in r.replace(" ", "").replace("2>/dev/null", "")
                    and r.strip().startswith("find")],
         resposta='find / -name "*.conf" 2>/dev/null > achados.txt'),
    Quiz(id="s11.diag.2", titulo="Diagnóstico: SUID", prova="", exato=True,
         enunciado="Octal de -rwsr-xr-- ?", respostas=["4754"]),
    Quiz(id="s11.diag.3", titulo="Diagnóstico: subnetting", prova="",
         enunciado="Broadcast de 192.168.10.64/27?", respostas=["192.168.10.95"]),
    Escolha(id="s11.diag.4", titulo="Diagnóstico: SELinux", prova="",
            enunciado="Apache em enforcing não lê /srv/site, mas as permissões estão certas. O que você faz?",
            opcoes=["setenforce 0 e pronto", "Vê o contexto (ls -Z), confirma o AVC (ausearch -m avc), aplica semanage fcontext + restorecon",
                    "chmod 777 /srv/site", "Reinstala o Apache"], correta="b"),
    Escolha(id="s11.diag.5", titulo="Diagnóstico: NAT/PAT e stateful", prova="",
            enunciado="Quais são verdadeiras?",
            opcoes=["PAT diferencia os hosts internos pela porta de origem",
                    "Firewall stateful libera as respostas de conexões já estabelecidas",
                    "DNAT serve para dispositivos internos saírem para a internet",
                    "Masquerade é um tipo de SNAT"], correta="abd"),
    Escolha(id="s11.diag.6", titulo="Diagnóstico: IoC × IoA", prova="",
            enunciado="'Processo do Apache abrindo um shell reverso' é:",
            opcoes=["IoC", "IoA"], correta="b"),
    Tarefa(id="s11.comparar", titulo="Compare com novembro",
           enunciado="""
           Releia suas respostas do diagnóstico de novembro e escreva ~/linux-lab/relatorios/evolucao.md:
           o que você errava, o que sabe agora e o que ainda quer aprofundar.
           """,
           checks=[("evolucao.md escrito", '[ "$(wc -w < ~/linux-lab/relatorios/evolucao.md 2>/dev/null || echo 0)" -gt 100 ]')]),

    # ── fechamento ──
    Marco(id="s11.prova102", titulo="🎓 Prova LPIC-1 102", enunciado="Fez a prova 102-500?"),
    Tarefa(id="s11.readme", titulo="README do linux-lab apresentável",
           enunciado="""
           O README.md do repositório deve apresentar: o que é o laboratório, o que você aprendeu
           e links para os 3 projetos em destaque (mini-soc, caça à persistência e forense de disco).
           """,
           checks=[("README com ≥ 250 palavras", '[ "$(wc -w < ~/linux-lab/README.md)" -ge 250 ]'),
                   ("linka o mini-soc", "grep -q 'mini-soc' ~/linux-lab/README.md"),
                   ("está publicado", "git -C ~/linux-lab diff --quiet '@{u}' -- README.md 2>/dev/null")]),
    Marco(id="s11.cv", titulo="CV atualizado",
          enunciado="Trocou 'domínio de Linux' no CV por evidências: LPIC-1, FCF, FCA e o link do Mini-SOC?"),
    Marco(id="s11.linkedin", titulo="Post no LinkedIn",
          enunciado="Publicou um post sobre o Mini-SOC (o que montou, o que detectou, o que aprendeu)?"),
]
