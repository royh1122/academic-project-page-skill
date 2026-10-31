"""The v1.0 paper (LaTeX). Byte-stable settings as in the Quillwave generator; Latin Modern only."""
from .common import INST, MARK, NUM, P, fmt
from .content import ABSTRACT, LIMITATIONS

V10 = NUM["splits"]["v1_0"]
AN = NUM["annotators"]


def fill(tpl, **kw):
    for k, v in kw.items():
        tpl = tpl.replace(f"<<{k}>>", str(v))
    assert "<<" not in tpl, tpl[tpl.index("<<"):tpl.index("<<") + 40]
    return tpl


def tex(s):
    return s.replace("%", r"\%").replace("&", r"\&")


def author_block():
    keys = list(INST)
    marks = []
    for p in NUM["people"]:
        sup = ",".join(str(keys.index(i) + 1) for i in p["inst"])
        extra = (r"$^{*}$" if p.get("equal") else "") + (r"$^{\dagger}$" if p["key"] == P["corresponding"] else "")
        marks.append(rf"{p['name']}$^{{{sup}}}${extra}")
    insts = r" \quad ".join(rf"$^{{{n + 1}}}${INST[k]}" for n, k in enumerate(keys))
    corr = next(p for p in NUM["people"] if p["key"] == P["corresponding"])
    return (", ".join(marks) + r"\\[4pt]" + rf"{{\small {insts}}}\\[2pt]"
            + rf"{{\small $^{{*}}$Equal contribution. $^{{\dagger}}$Corresponding author: \texttt{{{corr['email']}}}}}")


def results_table():
    rows = [r for r in NUM["leaderboard"]["rows"] if r[1] == "v1.0" and r[3] <= NUM["dates"]["v1_0"]]
    body = "\n".join(rf"{m} & {f:.1f} \\" for m, _, f, _ in rows)
    return body


PAPER = r"""\documentclass[10pt,a4paper,twocolumn]{article}
\usepackage[margin=1.8cm]{geometry}
\usepackage{lmodern}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{booktabs}
\usepackage{graphicx}
\usepackage{url}
\usepackage{fancyhdr}
\pagestyle{fancy}\fancyhf{}\renewcommand{\headrulewidth}{0pt}
\cfoot{\scriptsize <<mark>>}\rfoot{\small\thepage}
\fancypagestyle{plain}{\fancyhf{}\renewcommand{\headrulewidth}{0pt}\cfoot{\scriptsize <<mark>>}\rfoot{\small\thepage}}
\pdfinfoomitdate=1
\pdftrailerid{}
\pdfsuppressptexinfo=-1
\pdfinfo{/Title (<<title_plain>>) /Author (<<authors_plain>>) /Subject (FICTIONAL synthetic test material) /Keywords (fictional; synthetic; test fixture; CC0 1.0; paper) /Creator (Paperwren kit generator)}
\graphicspath{{figures/}}
\begin{document}
\twocolumn[{\begin{center}
{\LARGE\bfseries <<title>>\par}\vspace{10pt}
<<authors>>\\[6pt]
{\small <<venue>>}
\end{center}\vspace{6pt}}]
\begin{abstract}
<<abstract>>
\end{abstract}
\section{Introduction}
Forms are still filled in by hand in clinics, libraries and field stations, and reading them is hard for machines:
values are crossed out, squeezed into boxes, or written across lines. Paperwren gives a controlled test of this. The
layouts and values are synthetic, so nothing private is written on the forms, but the handwriting is real.
\begin{figure}[t]\centering
\includegraphics[width=\linewidth]{overview.png}
\caption{From layout to benchmark.}\label{fig:overview}
\end{figure}
\section{The dataset}
Paperwren v1.0 has <<total>> forms in <<families>> layout families (Table~\ref{tab:splits}). <<annot>> paid
annotators in <<countries>> countries filled them in by hand; every form was labelled field by field and checked
by a second annotator.
\begin{table}[t]\centering\small
\caption{Splits in release v1.0.}\label{tab:splits}
\begin{tabular}{lr}\toprule
Split & Forms \\\midrule
Train & <<train>> \\
Validation & <<val>> \\
Test & <<test>> \\\midrule
Total & <<total>> \\\bottomrule
\end{tabular}
\end{table}
\section{Benchmark}
Models return every field's value as text. We score field-level F1 on the held-out test split; test labels are not
released. Table~\ref{tab:results} gives the results at submission time.
\begin{table}[t]\centering\small
\caption{Field-level F1 (\%) on the v1.0 test split.}\label{tab:results}
\begin{tabular}{lr}\toprule
Model & F1 \\\midrule
<<results>>
\bottomrule
\end{tabular}
\end{table}
\begin{figure}[t]\centering
\includegraphics[width=\linewidth]{sample_forms.png}
\caption{Four sample forms.}
\end{figure}
\section{Access and ethics}
The forms are shared on request under a data-use agreement that forbids identifying annotators from their
handwriting. Annotators were paid and gave consent for research use of their handwriting.
\section{Limitations}
\begin{itemize}
<<lims>>
\end{itemize}
\end{document}
"""


def paper_tex():
    names = [p["name"] for p in NUM["people"]]
    return fill(PAPER, mark=MARK, title=P["title"], title_plain=P["title"],
                authors_plain="; ".join(n.replace("ü", "ue").replace("í", "i").replace("ê", "e") for n in names),
                authors=author_block(), venue=f"{P['venue']['full']} ({P['venue']['short']})",
                abstract=tex(ABSTRACT), total=fmt(V10["total"]), families=len(NUM["families"]),
                annot=AN["count"], countries=AN["countries"], train=fmt(V10["train"]), val=fmt(V10["val"]),
                test=fmt(V10["test"]), results=results_table(),
                lims="\n".join(rf"\item \textbf{{{t}.}} {d}" for t, d in LIMITATIONS))
