from motor import Escolha, Marco

TITULO = "Prova 101 + Fortinet FCF (Natal)"
DATAS = "21–27/12"
OBJETIVO = """
Semana leve: a prova 101 e os cursos da Fortinet FCF (vídeo + prova, gratuitos).
Mantenha o Anki e o `treino subnet` 10 min por dia para não esfriar.
"""

EXERCICIOS = [
    Marco(id="s06.prova101", titulo="🎓 Prova LPIC-1 101",
          enunciado="Fez a prova 101-500? (online pela Pearson OnVUE, em português)"),
    Marco(id="s06.fcf.1", titulo="FCF: Getting Started in Cybersecurity",
          enunciado="Concluiu o curso 'Getting Started in Cybersecurity' no portal de treinamento da Fortinet?"),
    Marco(id="s06.fcf.2", titulo="FCF: Technical Introduction to Cybersecurity",
          enunciado="Concluiu o curso 'Technical Introduction to Cybersecurity'?"),
    Marco(id="s06.fcf.3", titulo="FCF: prova",
          enunciado="Passou na prova Fortinet Certified Fundamentals (FCF)?"),
    Escolha(id="s06.cia", titulo="Tríade CIA", prova="",
            enunciado="Um ransomware cifra os arquivos do servidor de arquivos. Qual pilar da tríade CIA foi atingido PRIMEIRO?",
            opcoes=["Confidencialidade", "Integridade", "Disponibilidade", "Autenticidade"], correta="c",
            explicacao="Os dados ficaram indisponíveis. Se o grupo também vazar os dados (dupla extorsão), atinge a confidencialidade."),
    Escolha(id="s06.defesa", titulo="Defesa em profundidade", prova="",
            enunciado="O que é 'defesa em profundidade'?",
            opcoes=["Comprar o firewall mais caro", "Várias camadas de controle, para que a falha de uma não comprometa tudo",
                    "Monitorar só a rede interna", "Usar só antivírus"], correta="b"),
]
