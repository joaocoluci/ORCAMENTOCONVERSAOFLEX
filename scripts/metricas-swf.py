"""Metricas de conversao Flex -> HTML5 a partir do constant pool dos SWF.

Uso:
    python metricas-swf.py <dir_txt> <nome_workspace_flex> [--json saida.json]

<dir_txt>              diretorio com os .txt gerados por extrai-swf-abc.py
<nome_workspace_flex>  fragmento que identifica o projeto no caminho de origem
                       embutido nos SWF, ex.: "Cotacao-VC-Flex"

Emite, por SWF e por classe: membros, handlers MXML, bindings, widgets,
servicos custom, popups detectados e o indice/horas do modelo calibrado.
"""

import argparse
import collections
import glob
import io
import json
import os
import re
import sys

# Modelo calibrado (ver references/modelo-calibragem.md)
HORAS_BASE = 8.0
FATOR_INDICE = 0.18
HORAS_POR_POPUP = 2.5

RE_MEMBRO = re.compile(
    r"^(?:[A-Za-z0-9_.]+:)?([A-Za-z0-9_]+)/(?:[a-z_]+:)?([A-Za-z0-9_]+)(?:/(?:get|set))?$"
)
RE_WIDGET = re.compile(r"^_([A-Za-z0-9]+)_([A-Za-z][A-Za-z0-9]*?)(\d+)_[ic]$")
RE_INDICE_BINDING = re.compile(r"^_\d+")
RE_POPUP = re.compile(r"^(Popup|PopUp)", re.IGNORECASE)


def classes_do_arquivo(linhas, workspace):
    """Nomes de classe custom, derivados dos caminhos de fonte embutidos no SWF."""
    fontes = sorted(
        {
            linha.split("src;")[-1]
            for linha in linhas
            if workspace in linha and linha.endswith((".mxml", ".as"))
        }
    )
    classes = {
        os.path.basename(f.replace(";", "/").replace("\\", "/")).rsplit(".", 1)[0]
        for f in fontes
    }
    return fontes, classes


def analisa(caminho, workspace, prefixos_servico):
    linhas = open(caminho, encoding="utf-8").read().split("\n")
    fontes, classes = classes_do_arquivo(linhas, workspace)
    if not classes:
        return None

    membros = collections.defaultdict(set)
    handlers = collections.defaultdict(set)
    bindings = collections.Counter()
    widgets = collections.defaultdict(collections.Counter)

    for linha in linhas:
        m = RE_MEMBRO.match(linha)
        if m and m.group(1) in classes:
            classe, membro = m.group(1), m.group(2)
            if RE_INDICE_BINDING.match(membro):
                continue
            if membro.startswith("___"):
                handlers[classe].add(membro)
            elif membro.startswith("_"):
                bindings[classe] += 1
            else:
                membros[classe].add(membro)
        w = RE_WIDGET.match(linha)
        if w and w.group(1) in classes:
            widgets[w.group(1)][w.group(2)] += 1

    conjunto = set(linhas)
    servicos = sorted(
        x
        for x in conjunto
        if any(x.startswith(p) for p in prefixos_servico) and "." in x
    )
    popups = sorted(c for c in classes if RE_POPUP.match(c))

    return {
        "fontes": len(fontes),
        "classes": sorted(classes),
        "membros": {c: sorted(membros[c]) for c in sorted(classes)},
        "handlers": {c: len(handlers[c]) for c in sorted(classes)},
        "bindings": {c: bindings[c] for c in sorted(classes)},
        "widgets": {c: dict(widgets[c]) for c in sorted(classes)},
        "servicos": servicos,
        "popups": popups,
    }


def horas(total_membros, total_widgets, total_servicos, qtd_popups):
    indice = total_membros + 0.5 * total_widgets + 2 * total_servicos
    return indice, HORAS_BASE + FATOR_INDICE * indice + HORAS_POR_POPUP * qtd_popups


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("dir_txt")
    ap.add_argument("workspace")
    ap.add_argument(
        "--servicos",
        default="",
        help="prefixos de service provider custom, separados por virgula",
    )
    ap.add_argument("--json", dest="saida_json")
    args = ap.parse_args()

    prefixos = [p.strip() for p in args.servicos.split(",") if p.strip()]
    resultado = {}

    for caminho in sorted(glob.glob(os.path.join(args.dir_txt, "*.txt"))):
        nome = os.path.basename(caminho)[:-4]
        dados = analisa(caminho, args.workspace, prefixos)
        if not dados:
            continue

        tot_membros = sum(len(v) for v in dados["membros"].values())
        tot_widgets = sum(sum(v.values()) for v in dados["widgets"].values())
        indice, h = horas(
            tot_membros, tot_widgets, len(dados["servicos"]), len(dados["popups"])
        )
        dados["totais"] = {
            "membros": tot_membros,
            "widgets": tot_widgets,
            "servicos": len(dados["servicos"]),
            "popups": len(dados["popups"]),
            "indice": round(indice, 1),
            "horas": round(h, 1),
        }
        resultado[nome] = dados

        print("=" * 72)
        print(
            f"{nome} | fontes={dados['fontes']} membros={tot_membros} "
            f"widgets={tot_widgets} servicos={len(dados['servicos'])} "
            f"popups={len(dados['popups'])}"
        )
        for classe in dados["classes"]:
            print(
                f"   {classe:32s} membros={len(dados['membros'][classe]):3d} "
                f"handlers={dados['handlers'][classe]:3d} "
                f"bind={dados['bindings'][classe]:3d} "
                f"widgets={sum(dados['widgets'][classe].values()):3d}"
            )
        if dados["servicos"]:
            print("   servicos:", ", ".join(dados["servicos"]))
        print(f"   >> indice={indice:.1f}  horas={h:.1f}")

    if args.saida_json:
        with open(args.saida_json, "w", encoding="utf-8") as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)
        print(f"\nJSON gravado em {args.saida_json}")

    total = sum(r["totais"]["horas"] for r in resultado.values())
    print("=" * 72)
    print(f"TOTAL BRUTO DAS TELAS: {total:.1f}h  (antes de infraestrutura e fases)")


if __name__ == "__main__":
    main()
