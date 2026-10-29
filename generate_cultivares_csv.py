#!/usr/bin/env python3
"""
Gera cultivares_embrapa_2013.csv com os 16 cultivares de soja do
Catálogo Embrapa/Fundação Meridional Centro-Sul 2013.

Fonte:
  https://www.infoteca.cnptia.embrapa.br/infoteca/bitstream/doc/976493/1/CATALOGOSojaCentrosul2013.pdf

Convenções:
  - res_*  True  somente quando nota == R (Resistente).
  - MR, MS, S, AT, Tolerante → False.
  - regioes  campo com separador "|"  (e.g. "101|102|201").
  - meses_semeadura  campo com separador "|"  (e.g. "OUT|NOV").

Nota sobre dimensão do catálogo:
  Este catálogo Centro-Sul 2013 contém exclusivamente cultivares
  desenvolvidas pela Embrapa em parceria com a Fundação Meridional.
  O total nacional de cultivares registradas no MAPA (~130) inclui
  dezenas de obtentoras (Syngenta, Pioneer, Nidera, etc.) e cobre
  todas as cinco Macrorregiões Sojícolas do Brasil.
"""

import csv
import os

# ---------------------------------------------------------------------------
# Dados extraídos individualmente de cada página do PDF
# (região via mapa colorido + cabeçalhos de coluna nas tabelas de densidade;
#  doenças via seção "Reação a doenças" de cada ficha)
# ---------------------------------------------------------------------------

CULTIVARES: list[dict] = [
    # ── CULTIVARES CONVENCIONAIS (Tabela 2, p. 32) ─────────────────────────
    {
        "nome": "BRS 184",
        "tipo": "Convencional",
        # Mapa p. 14: RECs 201, 202, 203, 204, 302
        "regioes": "201|202|203|204|302",
        "meses_semeadura": "OUT|NOV|DEZ",
        # Página 14-15: R / R / MS / S / MR / R / Tol / S / S / S
        "res_cancro_haste": True,
        "res_mancha_olho_ra": True,
        "res_oidio": False,
        "res_podridao_parda_haste": False,
        "res_podridao_fitoftora": False,     # Moderadamente Resistente → False
        "res_mosaico_comum": True,
        "res_virus_necrose_haste": False,    # Tolerante → False
        "res_nema_incognita": False,
        "res_nema_javanica": False,
        "res_nema_cisto": False,
    },
    {
        "nome": "BRS 232",
        "tipo": "Convencional",
        # Mapa p. 16: RECs 102, 103, 201, 202, 203, 204, 302
        "regioes": "102|103|201|202|203|204|302",
        "meses_semeadura": "OUT|NOV|DEZ",
        # Página 16-17: R / R / MS / R / S / R / S / MR / S / S
        "res_cancro_haste": True,
        "res_mancha_olho_ra": True,
        "res_oidio": False,
        "res_podridao_parda_haste": True,
        "res_podridao_fitoftora": False,
        "res_mosaico_comum": True,
        "res_virus_necrose_haste": False,
        "res_nema_incognita": False,         # Moderadamente Resistente → False
        "res_nema_javanica": False,
        "res_nema_cisto": False,
    },
    {
        "nome": "BRS 257",
        "tipo": "Convencional",
        # Mapa p. 18: RECs 102, 103, 201, 202, 203
        "regioes": "102|103|201|202|203",
        "meses_semeadura": "OUT|NOV|DEZ",
        # Página 18-19: R / R / MS / MR / R / R / S / MR / MR / S
        "res_cancro_haste": True,
        "res_mancha_olho_ra": True,
        "res_oidio": False,
        "res_podridao_parda_haste": False,   # Moderadamente Resistente
        "res_podridao_fitoftora": True,
        "res_mosaico_comum": True,
        "res_virus_necrose_haste": False,
        "res_nema_incognita": False,         # MR → False
        "res_nema_javanica": False,          # MR → False
        "res_nema_cisto": False,
    },
    {
        "nome": "BRS 262",
        "tipo": "Convencional",
        # Mapa p. 20: RECs 301, 302, 303
        "regioes": "301|302|303",
        "meses_semeadura": "OUT|NOV",
        # Página 20-21: R / R / MS / S / R / S / S / S / S / R (cisto raças 1 e 3)
        "res_cancro_haste": True,
        "res_mancha_olho_ra": True,
        "res_oidio": False,
        "res_podridao_parda_haste": False,
        "res_podridao_fitoftora": True,
        "res_mosaico_comum": False,
        "res_virus_necrose_haste": False,
        "res_nema_incognita": False,
        "res_nema_javanica": False,
        "res_nema_cisto": True,
    },
    {
        "nome": "BRS 282",
        "tipo": "Convencional",
        # Mapa p. 22: RECs 201, 202, 203, 204, 302
        "regioes": "201|202|203|204|302",
        "meses_semeadura": "OUT|NOV|DEZ",
        # Página 22-23: R / R / MS / R / S / S / S / R / R / S
        "res_cancro_haste": True,
        "res_mancha_olho_ra": True,
        "res_oidio": False,
        "res_podridao_parda_haste": True,
        "res_podridao_fitoftora": False,
        "res_mosaico_comum": False,
        "res_virus_necrose_haste": False,
        "res_nema_incognita": True,
        "res_nema_javanica": True,
        "res_nema_cisto": False,
    },
    {
        "nome": "BRS 283",
        "tipo": "Convencional",
        # Mapa p. 24: RECs 103, 201, 202, 203, 204, 301, 302, 303
        "regioes": "103|201|202|203|204|301|302|303",
        "meses_semeadura": "OUT|NOV|DEZ",
        # Página 24-25: R / R / MS / MR / MR* / S / MdmTol / S / MR / S
        # (*moderada resistência de campo)
        "res_cancro_haste": True,
        "res_mancha_olho_ra": True,
        "res_oidio": False,
        "res_podridao_parda_haste": False,   # MR
        "res_podridao_fitoftora": False,     # MR (resistência de campo)
        "res_mosaico_comum": False,
        "res_virus_necrose_haste": False,    # Moderadamente Tolerante
        "res_nema_incognita": False,
        "res_nema_javanica": False,          # MR
        "res_nema_cisto": False,
    },
    {
        "nome": "BRS 284",
        "tipo": "Convencional",
        # Mapa p. 26: RECs 103, 201, 202, 203, 204, 301, 302, 303
        "regioes": "103|201|202|203|204|301|302|303",
        "meses_semeadura": "OUT|NOV|DEZ",
        # Página 26-27: R / R / MS / R / S* / S / S / S / MR / S
        "res_cancro_haste": True,
        "res_mancha_olho_ra": True,
        "res_oidio": False,
        "res_podridao_parda_haste": True,
        "res_podridao_fitoftora": False,     # S* (moderada resistência de campo)
        "res_mosaico_comum": False,
        "res_virus_necrose_haste": False,
        "res_nema_incognita": False,
        "res_nema_javanica": False,          # MR
        "res_nema_cisto": False,
    },
    {
        "nome": "BRS 317",
        "tipo": "Convencional",
        # Mapa p. 28: RECs 201, 202, 203, 204, 302
        "regioes": "201|202|203|204|302",
        "meses_semeadura": "OUT|NOV|DEZ",
        # Página 28-29: R / R / MR / MR / S* / R / S / R / S / S
        "res_cancro_haste": True,
        "res_mancha_olho_ra": True,
        "res_oidio": False,                  # MR
        "res_podridao_parda_haste": False,   # MR
        "res_podridao_fitoftora": False,     # S*
        "res_mosaico_comum": True,
        "res_virus_necrose_haste": False,
        "res_nema_incognita": True,
        "res_nema_javanica": False,
        "res_nema_cisto": False,
    },
    {
        "nome": "BRS 361",
        "tipo": "Convencional",
        # Mapa p. 30: RECs 301, 302, 303
        "regioes": "301|302|303",
        "meses_semeadura": "OUT|NOV",
        # Página 30-31: R / R / MR / MS / R / R / Tol / S / S / S
        "res_cancro_haste": True,
        "res_mancha_olho_ra": True,
        "res_oidio": False,                  # MR
        "res_podridao_parda_haste": False,   # MS
        "res_podridao_fitoftora": True,
        "res_mosaico_comum": True,
        "res_virus_necrose_haste": False,    # Tolerante
        "res_nema_incognita": False,
        "res_nema_javanica": False,
        "res_nema_cisto": False,
    },
    # ── CULTIVARES TRANSGÊNICAS RR (Tabela 3, p. 48) ───────────────────────
    {
        "nome": "BRS 245 RR",
        "tipo": "RR",
        # Mapa p. 34: RECs 301, 302, 303
        "regioes": "301|302|303",
        "meses_semeadura": "OUT|NOV",
        # Página 34-35: R / R / MS / S / 1S / R / Tol / S / S / S
        # (nota 1: fitóftora — evitar solos compactados)
        "res_cancro_haste": True,
        "res_mancha_olho_ra": True,
        "res_oidio": False,
        "res_podridao_parda_haste": False,
        "res_podridao_fitoftora": False,
        "res_mosaico_comum": True,
        "res_virus_necrose_haste": False,    # Tolerante
        "res_nema_incognita": False,
        "res_nema_javanica": False,
        "res_nema_cisto": False,
    },
    {
        "nome": "BRS 295 RR",
        "tipo": "RR",
        # Mapa p. 36: RECs 201, 202, 203, 204, 302
        "regioes": "201|202|203|204|302",
        "meses_semeadura": "OUT|NOV|DEZ",
        # Página 36-37: R / R / MR / S / R / S / MdmTol / S / S / R(cisto raças 1 e 3)
        "res_cancro_haste": True,
        "res_mancha_olho_ra": True,
        "res_oidio": False,                  # MR
        "res_podridao_parda_haste": False,
        "res_podridao_fitoftora": True,
        "res_mosaico_comum": False,
        "res_virus_necrose_haste": False,    # Moderadamente Tolerante
        "res_nema_incognita": False,
        "res_nema_javanica": False,
        "res_nema_cisto": True,
    },
    {
        "nome": "BRS 316 RR",
        "tipo": "RR",
        # Mapa p. 38: RECs 201, 202, 203, 204, 302
        "regioes": "201|202|203|204|302",
        "meses_semeadura": "OUT|NOV|DEZ",
        # Página 38-39: R / R / MS / R / R / R / MdmTol / MR / R / S
        "res_cancro_haste": True,
        "res_mancha_olho_ra": True,
        "res_oidio": False,
        "res_podridao_parda_haste": True,
        "res_podridao_fitoftora": True,
        "res_mosaico_comum": True,
        "res_virus_necrose_haste": False,    # Moderadamente Tolerante
        "res_nema_incognita": False,         # MR
        "res_nema_javanica": True,
        "res_nema_cisto": False,
    },
    {
        "nome": "BRS 334 RR",
        "tipo": "RR",
        # Mapa p. 40: RECs 301, 302, 303
        "regioes": "301|302|303",
        "meses_semeadura": "OUT|NOV",
        # Página 40-41: R / R / (oidio não listado) / MR / S / R / Tol / S / S / S
        "res_cancro_haste": True,
        "res_mancha_olho_ra": True,
        "res_oidio": False,
        "res_podridao_parda_haste": False,   # MR
        "res_podridao_fitoftora": False,
        "res_mosaico_comum": True,
        "res_virus_necrose_haste": False,    # Tolerante
        "res_nema_incognita": False,
        "res_nema_javanica": False,
        "res_nema_cisto": False,
    },
    {
        "nome": "BRS 359 RR",
        "tipo": "RR",
        # Mapa p. 42 e tabela de densidade: RECs 201, 202, 203, 204
        "regioes": "201|202|203|204",
        "meses_semeadura": "SET|OUT|NOV",
        # Página 42-43: R / MR / MR / R / R / R / Tol / MR / S / R(Rotylenchulus, não cisto)
        "res_cancro_haste": True,
        "res_mancha_olho_ra": False,         # MR
        "res_oidio": False,                  # MR
        "res_podridao_parda_haste": True,
        "res_podridao_fitoftora": True,
        "res_mosaico_comum": True,
        "res_virus_necrose_haste": False,    # Tolerante
        "res_nema_incognita": False,         # MR
        "res_nema_javanica": False,
        "res_nema_cisto": False,             # R Rotylenchulus reniformis (≠ nema-cisto)
    },
    {
        "nome": "BRS 360 RR",
        "tipo": "RR",
        # Mapa p. 44 e tabela de densidade: RECs 201, 202, 203, 204
        "regioes": "201|202|203|204",
        "meses_semeadura": "SET|OUT|NOV",
        # Página 44-45: R / MR / MR / R / R / R / Tol / MR / S / R(Rotylenchulus)
        "res_cancro_haste": True,
        "res_mancha_olho_ra": False,         # MR
        "res_oidio": False,                  # MR
        "res_podridao_parda_haste": True,
        "res_podridao_fitoftora": True,
        "res_mosaico_comum": True,
        "res_virus_necrose_haste": False,    # Tolerante
        "res_nema_incognita": False,         # MR
        "res_nema_javanica": False,
        "res_nema_cisto": False,
    },
    {
        "nome": "BRS 378 RR",
        "tipo": "RR",
        # Mapa p. 46 e tabela de densidade: RECs 102 e 103
        "regioes": "102|103",
        # Página 47: Set. 30 é vermelho (Não indicada); Out, Nov e Dez têm faixas Tolerada/Preferencial
        "meses_semeadura": "OUT|NOV|DEZ",
        # Página 46-47: R / MR / (Pústula bacteriana R) / S / MR / R / Tol / S / S / (sem cisto)
        "res_cancro_haste": True,
        "res_mancha_olho_ra": False,         # MR
        "res_oidio": False,
        "res_podridao_parda_haste": False,
        "res_podridao_fitoftora": False,     # MR
        "res_mosaico_comum": True,
        "res_virus_necrose_haste": False,    # Tolerante
        "res_nema_incognita": False,
        "res_nema_javanica": False,
        "res_nema_cisto": False,
    },
]

# ---------------------------------------------------------------------------
# Gera o CSV
# ---------------------------------------------------------------------------

FIELDNAMES = [
    "nome", "tipo", "regioes", "meses_semeadura",
    "res_cancro_haste", "res_mancha_olho_ra", "res_oidio",
    "res_podridao_parda_haste", "res_podridao_fitoftora",
    "res_mosaico_comum", "res_virus_necrose_haste",
    "res_nema_incognita", "res_nema_javanica", "res_nema_cisto",
]

out_path = os.path.join(os.path.dirname(__file__), "cultivares_embrapa_2013.csv")

with open(out_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
    writer.writeheader()
    for c in CULTIVARES:
        writer.writerow({k: c[k] for k in FIELDNAMES})

print(f"Wrote {len(CULTIVARES)} cultivares → {out_path}")
print()
print("Resumo:")
for c in CULTIVARES:
    print(f"  {c['nome']:20s} ({c['tipo']:12s}): {c['regioes']}")
