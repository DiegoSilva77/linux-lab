from motor import Escolha, Marco, Quiz

TITULO = "Fortinet FCA (Ano-Novo)"
DATAS = "28/12–03/01"
OBJETIVO = """
Semana leve: FCA (FortiGate Operator). Anote como o FortiGate faz política, NAT e inspeção
stateful: na semana 9 você monta o equivalente em Linux, na mão.
⚠️  Compre o voucher da 102 até 10/01 e agende para ~30/01.
"""

EXERCICIOS = [
    Marco(id="s07.fca.curso", titulo="FCA: curso FortiGate Operator",
          enunciado="Concluiu o curso FortiGate Operator no portal de treinamento da Fortinet?"),
    Marco(id="s07.fca.prova", titulo="FCA: prova", enunciado="Passou na prova Fortinet Certified Associate (FCA)?"),
    Escolha(id="s07.pol", titulo="Ordem das políticas", prova="",
            enunciado="Num FortiGate (e na maioria dos firewalls), como as políticas são avaliadas?",
            opcoes=["Todas de uma vez, vale a mais restritiva", "De cima para baixo; vale a PRIMEIRA que casar",
                    "De baixo para cima", "Em ordem alfabética"], correta="b",
            explicacao="Por isso regras específicas vêm antes das genéricas, e no fim há um 'deny all' implícito."),
    Escolha(id="s07.utm", titulo="UTM / NGFW", prova="",
            enunciado="O que um NGFW/UTM faz além de um firewall de portas?",
            opcoes=["Só NAT", "Inspeção de aplicação, IPS, antivírus, filtro web, inspeção SSL...",
                    "Só VPN", "Nada além"], correta="b"),
    Quiz(id="s07.anotacao", titulo="Anotações para a semana 9", prova="",
         enunciado="Você criou ~/linux-lab/seguranca/firewall.md com o que aprendeu sobre política, NAT e stateful? (sim/não)",
         respostas=["sim", "s"]),
]
