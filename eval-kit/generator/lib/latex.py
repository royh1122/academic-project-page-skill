"""LaTeX sources (paper, summary, report, short paper, poster, overview TikZ) and pdflatex driver.

Templates use <<key>> placeholders so LaTeX braces and percent signs need no escaping.
Byte-stable PDFs: \\pdfinfoomitdate, \\pdftrailerid{}, \\pdfsuppressptexinfo and SOURCE_DATE_EPOCH.
Only Latin Modern fonts are used (lmodern + T1).
"""
import shutil
from pathlib import Path

from .common import MARK, NUM, P, run, tool
from .content import LIMITATIONS, REFS, PEOPLE, names

S = NUM["setup"]
MT = NUM["main_table"]
SW = NUM["sensor_sweep"]
D = NUM["derived"]
US = NUM["user_study"]
ROWS = MT["rows"]
OURS, RBF, LITE, LIN = ROWS[3], ROWS[1], ROWS[2], ROWS[0]


def fill(tpl, **kw):
    for k, v in kw.items():
        tpl = tpl.replace(f"<<{k}>>", str(v))
    assert "<<" not in tpl, tpl[tpl.index("<<"):tpl.index("<<") + 40]
    return tpl


def tex_caption(s):
    return s.replace("256x256", r"$256\times256$").replace("%", r"\%")


# ----------------------------------------------------------------- shared blocks
def info_block(title, authors, kind):
    return fill(r"""\pdfinfoomitdate=1
\pdftrailerid{}
\pdfsuppressptexinfo=-1
\pdfinfo{/Title (<<title>>) /Author (<<authors>>) /Subject (FICTIONAL synthetic test material) /Keywords (fictional; synthetic; test fixture; CC0 1.0; <<kind>>) /Creator (Quillwave kit generator)}
""", title=title, authors="; ".join(authors), kind=kind)


FOOTER = fill(r"""\usepackage{fancyhdr}
\pagestyle{fancy}\fancyhf{}\renewcommand{\headrulewidth}{0pt}
\cfoot{\scriptsize <<mark>>}\rfoot{\small\thepage}
\fancypagestyle{plain}{\fancyhf{}\renewcommand{\headrulewidth}{0pt}\cfoot{\scriptsize <<mark>>}\rfoot{\small\thepage}}
""", mark=MARK)

PKGS = r"""\usepackage{lmodern}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{booktabs}
\usepackage{graphicx}
\usepackage{amsmath}
\usepackage{xcolor}
\usepackage{url}
\usepackage{tikz}
\usetikzlibrary{arrows.meta,calc,positioning}
"""


def table_main(label="tab:main"):
    best = [max(r[1] for r in ROWS), max(r[2] for r in ROWS), min(r[3] for r in ROWS)]
    lines = []
    for n, p, s, m in ROWS:
        cells = [f"{p:.2f}", f"{s:.3f}", f"{m:.1f}"]
        cells = [rf"\textbf{{{c}}}" if v == b else c for c, v, b in zip(cells, (p, s, m), best)]
        lines.append(f"{n} & " + " & ".join(cells) + r" \\")
    return fill(r"""\begin{table}[t]\centering\small
\caption{<<cap>>}\label{<<label>>}
\begin{tabular}{lrrr}\toprule
Method & PSNR (dB) $\uparrow$ & SSIM $\uparrow$ & Runtime (ms) $\downarrow$ \\\midrule
<<body>>
\bottomrule\end{tabular}
\end{table}
""", cap=tex_caption(MT["caption"]), label=label, body="\n".join(lines))


def table_sweep(label="tab:sweep"):
    sc = SW["sensor_counts"]
    best = [max(r[i + 1] for r in SW["psnr_rows"]) for i in range(len(sc))]
    lines = []
    for r in SW["psnr_rows"]:
        cells = [rf"\textbf{{{v:.2f}}}" if v == best[i] else f"{v:.2f}" for i, v in enumerate(r[1:])]
        lines.append(f"{r[0]} & " + " & ".join(cells) + r" \\")
    return fill(r"""\begin{table}[t]\centering\small
\caption{<<cap>>}\label{<<label>>}
\begin{tabular}{l<<cols>>}\toprule
Method & <<head>> \\\midrule
<<body>>
\bottomrule\end{tabular}
\end{table}
""", cap=tex_caption(SW["caption"]), label=label, cols="r" * len(sc),
                head=" & ".join(f"{c} sensors" for c in sc), body="\n".join(lines))


def bibliography(cmd="thebibliography"):
    items = []
    for key, kind, au, title, where, year in REFS:
        items.append(rf"\bibitem{{{key}}} {au}. {title}. \emph{{{where}}}, {year}. (Fictional reference.)")
    return "\\begin{thebibliography}{9}\\small\n" + "\n".join(items) + "\n\\end{thebibliography}\n"


def limitations_tex(env="itemize"):
    return f"\\begin{{{env}}}\n" + "\n".join(rf"\item \textbf{{{t}.}} {d}" for t, d in LIMITATIONS) + f"\n\\end{{{env}}}\n"


ABSTRACT_TEX = fill(r"""Quillwave reconstructs a full $<<n>>\times<<n>>$ ripple field from <<k>> point sensors. Ripple
fields are procedurally generated sums of interfering circular waves: cheap to synthesise, but hard to
interpolate, because the wave fronts between sensors are lost by smooth interpolation. Quillwave encodes the
sensor readings into a <<ld>>-dimensional latent field code and decodes it with a coordinate-based field
decoder. On RippleBench-Synthetic, a benchmark of <<tf>> synthetic test fields generated for this work,
Quillwave reaches <<psnr>>\,dB PSNR and <<ssim>> SSIM, <<gain>>\,dB above radial-basis interpolation (the
best baseline), which is a <<mse>>\,\% lower mean squared error. It is also <<sp>>$\times$ faster than
radial-basis interpolation at inference. All results are on synthetic fields only.""",
                    n=S["field_size"], k=S["sensors"], ld=S["latent_dim"], tf=S["test_fields"],
                    psnr=f"{OURS[1]:.2f}", ssim=f"{OURS[2]:.3f}", gain=f"{D['psnr_gain_over_best_baseline_db']:.2f}",
                    mse=f"{D['relative_mse_reduction_pct']:.1f}", sp=f"{D['speedup_vs_rbf']:.2f}")

INTRO_TEX = fill(r"""Many sensing problems share one shape: a handful of point measurements, and a wish to know the
whole field between them. Smooth interpolation is the standard answer, and it works when the field is
smooth. It fails for fields made of travelling waves, where the interesting structure, the wave fronts,
lies exactly between the sensors.

We study this failure on \emph{ripple fields}: sums of damped circular waves from a few random sources,
sampled on a $<<n>>\times<<n>>$ grid. They are easy to generate in any quantity, have a known ground truth,
and carry no personal or proprietary data. We make three contributions:
\begin{itemize}
\item RippleBench-Synthetic, a procedurally generated benchmark with <<trf>> training and <<tf>> test fields;
\item Quillwave, an encoder--decoder that predicts the full field from <<k>> sensors and a per-pixel confidence;
\item an evaluation against linear and radial-basis interpolation and an ablation, Quillwave-Lite.
\end{itemize}""", n=S["field_size"], trf=S["train_fields"], tf=S["test_fields"], k=S["sensors"])

RELATED_TEX = r"""Interpolating sparse probes of wave-like fields has been studied with hand-crafted
bases~\cite{nobody2024interpolating,anyone2023radial} and, more recently, with learned
decoders~\cite{someone2025learned}. Sensor placement in toy domains is discussed
in~\cite{whoever2024placement}; we fix the layout to isolate the reconstruction step. Purely synthetic
benchmarks~\cite{nameless2025benchmarks} trade realism for control, and we follow the error measures
recommended in~\cite{anybody2025measuring}."""

METHOD_TEX = fill(r"""Let $s\in\mathbf{R}^{<<k>>}$ be the sensor readings at known positions $p_i$ on a regular
$<<g>>\times<<g>>$ grid. The sensor encoder $E_\phi$ maps the pairs $(p_i, s_i)$ to a latent field code
$z = E_\phi(s) \in \mathbf{R}^{<<ld>>}$. The field decoder $D_\theta$ is coordinate-based: for any pixel
position $x$ it predicts a value and a confidence,
\begin{equation}
  \bigl(\hat f(x),\, c(x)\bigr) = D_\theta(x, z).
\end{equation}
Training minimises the mean squared error between $\hat f$ and the ground-truth field over all pixels,
plus a term that asks $c(x)$ to rank pixels by their error. Quillwave-Lite removes the latent code and
conditions the decoder on the raw readings directly. The full model has <<pm>>M parameters and is trained
for <<ep>> epochs.""", k=S["sensors"], g=S["sensor_grid"], ld=S["latent_dim"], pm=S["params_millions"], ep=S["epochs"])

SETUP_TEX = fill(r"""RippleBench-Synthetic fields are $<<n>>\times<<n>>$ sums of damped circular waves from up to four
sources with random positions, wavelengths and phases. We use <<trf>> training fields and <<tf>> test fields,
and <<k>> sensors unless stated otherwise. We compare against linear interpolation and radial-basis
interpolation from the same sensors, and against the Quillwave-Lite ablation. Learned models are trained
<<tr>> times with different seeds; we report the mean over the <<tr>> training runs. Runtime is per
field at inference.""", n=S["field_size"], trf=S["train_fields"], tf=S["test_fields"], k=S["sensors"], tr=S["training_runs"])

RESULTS_TEX = fill(r"""Table~\ref{tab:main} gives the main result. Quillwave reaches <<psnr>>\,dB PSNR and <<ssim>> SSIM,
<<gain>>\,dB above radial-basis interpolation, the best baseline; in terms of mean squared error this is a
<<mse>>\,\% reduction. At <<rt>>\,ms per field it is <<sp>>$\times$ faster than radial-basis interpolation
(<<rbfrt>>\,ms), though slower than linear interpolation (<<linrt>>\,ms). The ablation Quillwave-Lite reaches
<<litepsnr>>\,dB, so the latent field code accounts for part of the gain.

Table~\ref{tab:sweep} varies the number of sensors. Quillwave is the best method at every sensor count,
from <<p16>>\,dB with <<c16>> sensors to <<p128>>\,dB with <<c128>> sensors. Figure~\ref{fig:panels}
summarises these trends together with error statistics and the training curve, and
Figure~\ref{fig:qual} shows reconstructions of four test scenes.""",
                   psnr=f"{OURS[1]:.2f}", ssim=f"{OURS[2]:.3f}", gain=f"{D['psnr_gain_over_best_baseline_db']:.2f}",
                   mse=f"{D['relative_mse_reduction_pct']:.1f}", rt=f"{OURS[3]:.1f}", sp=f"{D['speedup_vs_rbf']:.2f}",
                   rbfrt=f"{RBF[3]:.1f}", linrt=f"{LIN[3]:.1f}", litepsnr=f"{LITE[1]:.2f}",
                   p16=f"{SW['psnr_rows'][3][1]:.2f}", c16=SW["sensor_counts"][0],
                   p128=f"{SW['psnr_rows'][3][4]:.2f}", c128=SW["sensor_counts"][3])

USER_TEX = fill(r"""A small user study with <<n>> participants rated the side-by-side comparison videos. Mean
ease of use was <<e>> and mean perceived quality <<q>> on a scale up to <<m>>. Raw responses are not
published.""", n=US["participants"], e=f"{US['mean_ease']:.2f}", q=f"{US['mean_quality']:.2f}", m=US["scale_max"])


ARCH_TEX = r"""\paragraph{Encoder.} Each sensor contributes a token made of its position and its reading. The tokens
pass through a small set-encoder with shared weights followed by attention pooling, so the code does not
depend on the order in which sensors are listed. The pooled vector is projected to the latent field code.

\paragraph{Decoder.} The decoder receives a pixel position, encoded with sinusoidal features, together
with the latent field code. A stack of fully connected layers with skip connections predicts two outputs:
the field value and a confidence score. Because the decoder is queried per pixel, the output resolution is
not tied to the training resolution, although every result in this document uses the benchmark resolution.

\paragraph{Confidence.} The confidence head is trained with a ranking objective: pixels with a larger
reconstruction error should receive a lower score. It is meant to show \emph{where} the reconstruction is
least reliable, not \emph{how} reliable it is; Section~\ref{sec:limits} returns to this point."""

FAIL_TEX = r"""\paragraph{Failure cases.} Quillwave is least accurate where two wave sources lie close together
between the same group of sensors: the interference pattern then varies faster than the sensor spacing,
and the decoder tends to merge the two sources into one. Radial-basis interpolation fails in the same
places, but more smoothly. Near the border of the field, where sensors are present only on one side, all
methods lose accuracy; Quillwave keeps the wave fronts but sometimes shifts their phase."""

DISC_TEX = r"""The results suggest that the main benefit of a learned latent code is a prior over plausible wave
patterns: with few sensors, the decoder fills the gaps with wave fronts that are consistent with the
readings, where interpolation fills them with a smooth surface. This prior is also the main risk. Because
RippleBench-Synthetic is generated by the same family of processes used for training, the benchmark
rewards exactly this prior, and it says little about fields from other processes. A fair comparison on
real measurements would need baselines with access to the same training data and the same compute budget,
and a separate check of whether the confidence scores match observed errors."""

CONCL_TEX = r"""Quillwave shows that a learned latent field code recovers wave fronts that smooth interpolation
misses, at a lower runtime than radial-basis interpolation. Whether this carries over to real
measurements is open; the limitations above apply to every number in this document."""

FIG_OVERVIEW = r"""\begin{figure}[t]\centering
\resizebox{\linewidth}{!}{\input{overview_tikz.tex}}
\caption{Quillwave pipeline: sensor readings are encoded into a latent field code, which a coordinate-based
decoder turns into the full field.}\label{fig:overview}
\end{figure}
"""

FIG_PANELS = r"""\begin{figure}[t]\centering
\includegraphics[width=\linewidth]{<<p>>results_panels.png}
\caption{Results on RippleBench-Synthetic. (a) PSNR and (b) SSIM against the number of sensors; (c) runtime;
(d) absolute error histogram; (e) per-scene PSNR, Quillwave against radial-basis interpolation;
(f) validation PSNR during training.}\label{fig:panels}
\end{figure}
"""

FIG_QUAL = r"""\begin{figure}[t]\centering
\includegraphics[width=\linewidth]{<<p>>qualitative_grid.jpg}
\caption{Four test scenes: sensor map, linear interpolation, radial-basis interpolation, Quillwave, and
ground truth.}\label{fig:qual}
\end{figure}
"""


def author_block(keys, with_mail=True):
    a = " \\quad ".join(rf"{PEOPLE[k]['name']}$^{{1}}$" for k in keys)
    mails = ", ".join(rf"\texttt{{{PEOPLE[k]['email']}}}" for k in keys)
    return fill(r"""{\large <<a>>\par}\vspace{4pt}
{\small $^{1}$<<aff>>\par}<<mail>>""", a=a, aff=P["affiliation"],
                mail=(r"\vspace{2pt}{\small " + mails + r"\par}") if with_mail else "")


# ----------------------------------------------------------------- overview TikZ
OVERVIEW_TIKZ = r"""% Quillwave overview diagram (FICTIONAL synthetic test material). Same file is used
% for figures/overview.png (standalone) and inside the paper.
\begin{tikzpicture}[x=1cm,y=1cm,font=\sffamily,
  box/.style={draw=black!65, line width=0.9pt, rounded corners=4pt, align=center,
              minimum height=2.6cm, minimum width=3.0cm, font=\sffamily\large},
  arr/.style={-{Stealth[length=3.2mm,width=2.6mm]}, line width=1.2pt, black!70}]
\useasboundingbox (0,0) rectangle (20.32,7.62);
% sensors
\node[box, fill=blue!4, minimum width=3.6cm, minimum height=3.6cm] (s) at (2.3,4.2) {};
\foreach \i in {0,...,7}{\foreach \j in {0,...,7}{
  \fill[blue!55!black] ($(s.south west)+({0.33+\i*0.42}, {0.33+\j*0.42})$) circle (2.1pt);}}
\node[font=\sffamily\large, below=3mm of s] {64 point sensors};
% encoder, latent, decoder
\node[box, fill=orange!12] (e) at (6.5,4.2) {Sensor\\encoder};
\node[box, fill=teal!12, minimum width=2.6cm] (z) at (10.1,4.2) {Latent field\\code\\(128-d)};
\node[box, fill=orange!12] (d) at (13.7,4.2) {Field\\decoder};
% output field: concentric ripples clipped to a square
\node[box, fill=white, minimum width=3.6cm, minimum height=3.6cm] (o) at (17.9,4.2) {};
\begin{scope}
\clip[rounded corners=4pt] (o.south west) rectangle (o.north east);
\foreach \r in {0.2,0.5,...,3.2}{\draw[blue!60!teal, line width=2.2pt, opacity=0.55] ($(o.center)+(-0.6,-0.4)$) circle (\r);}
\foreach \r in {0.3,0.65,...,3.0}{\draw[teal!70!black, line width=1.6pt, opacity=0.45] ($(o.center)+(0.9,0.8)$) circle (\r);}
\end{scope}
\draw[black!65, line width=0.9pt, rounded corners=4pt] (o.south west) rectangle (o.north east);
\node[font=\sffamily\large, below=3mm of o] {$256\times256$ field};
% query coordinate
\node[font=\sffamily\large] (q) at (13.7,7.0) {pixel position $x$};
\draw[arr] (q) -- (d);
\node[font=\sffamily, text=black!70] at (13.7,2.45) {value and confidence};
\draw[arr] (s) -- (e); \draw[arr] (e) -- (z); \draw[arr] (z) -- (d); \draw[arr] (d) -- (o);
\end{tikzpicture}
"""

OVERVIEW_STANDALONE = r"""\documentclass[border=0pt]{standalone}
\usepackage{lmodern}
\usepackage[T1]{fontenc}
\usepackage{tikz}
\usetikzlibrary{arrows.meta,calc,positioning}
<<info>>
\begin{document}
\input{overview_tikz.tex}
\end{document}
"""


def overview_standalone():
    return fill(OVERVIEW_STANDALONE, info=info_block("Quillwave overview", ["Quillwave kit generator"], "figure"))


# ----------------------------------------------------------------- paper
PAPER = r"""\documentclass[11pt,a4paper]{article}
\usepackage[margin=2.4cm]{geometry}
<<pkgs>>
<<footer>>
<<info>>
\graphicspath{{../../figures/}}
\begin{document}
\begin{center}
{\LARGE\bfseries <<title>>\par}\vspace{10pt}
<<authors>>
\vspace{4pt}{\small Accepted at <<venue>> (<<venuefull>>).\par}
\end{center}
\begin{abstract}
<<abstract>>
\end{abstract}

\section{Introduction}
<<intro>>

\section{Related work}
<<related>>

\section{Method}
<<fig_overview>>
<<method>>
<<arch>>

\section{Experiments}
\subsection{Setup}
<<setup>>
<<table_main>>
<<table_sweep>>
\subsection{Results}
<<results>>
<<fig_panels>>
<<fig_qual>>
<<fail>>
\subsection{User study}
<<user>>

\section{Discussion}
<<disc>>

\section{Limitations}\label{sec:limits}
<<limitations>>

\section{Conclusion}
<<conclusion>>

<<bib>>
\end{document}
"""


def paper_tex(authors):
    return fill(PAPER, pkgs=PKGS, footer=FOOTER,
                info=info_block(P["title"], names(authors), "paper"),
                title=P["title"], authors=author_block(authors), venue=P["venue"]["short"],
                venuefull=P["venue"]["full"], abstract=ABSTRACT_TEX, intro=INTRO_TEX, related=RELATED_TEX,
                fig_overview=FIG_OVERVIEW, method=METHOD_TEX, setup=SETUP_TEX, table_main=table_main(),
                table_sweep=table_sweep(), results=RESULTS_TEX, fig_panels=fill(FIG_PANELS, p=""),
                fig_qual=fill(FIG_QUAL, p=""), user=USER_TEX, limitations=limitations_tex(),
                conclusion=CONCL_TEX, bib=bibliography(), arch=ARCH_TEX, fail=FAIL_TEX, disc=DISC_TEX)


# ----------------------------------------------------------------- summary (V2)
SUMMARY = r"""\documentclass[11pt,a4paper]{article}
\usepackage[margin=2.2cm]{geometry}
<<pkgs>>
<<footer>>
<<info>>
\graphicspath{{figures/}}
\begin{document}
\begin{center}
{\Large\bfseries <<title>>\par}\vspace{8pt}
<<authors>>
\vspace{4pt}{\small Project summary. Research in preparation; not peer reviewed.\par}
\end{center}
\section*{Abstract}
<<abstract>>
<<table_main>>
<<table_sweep>>
\section*{Results}
<<results>>
<<fig_panels>>
\section*{Limitations}
<<limitations>>
\end{document}
"""


def summary_tex(authors):
    res = RESULTS_TEX.split("Figure~")[0].rstrip().rstrip(".") + "."
    res = res.replace(" Figure~\\ref{fig:panels}", "")
    res += r" Figure~\ref{fig:panels} summarises these trends."
    return fill(SUMMARY, pkgs=PKGS, footer=FOOTER, info=info_block(P["title"] + " (summary)", names(authors), "summary"),
                title=P["title"], authors=author_block(authors), abstract=ABSTRACT_TEX,
                table_main=table_main(), table_sweep=table_sweep(), results=res,
                fig_panels=fill(FIG_PANELS, p=""), limitations=limitations_tex())


# ----------------------------------------------------------------- FYP report (V3)
REPORT = r"""\documentclass[11pt,a4paper,oneside]{report}
\usepackage[margin=2.5cm]{geometry}
<<pkgs>>
<<footer>>
<<info>>
\graphicspath{{images/}}
\begin{document}
\begin{titlepage}\centering
\vspace*{2cm}
{\large Final Year Project 2025--2026\par}\vspace{1.2cm}
{\LARGE\bfseries <<title>>\par}\vspace{1.5cm}
{\large <<authors>>\par}\vspace{1cm}
{\large Supervisor: <<supervisor>>\par}\vspace{2cm}
{<<aff>>\par}\vfill
{\small <<mark>>\par}
\end{titlepage}

\chapter*{Acknowledgements}
We thank our supervisor, <<supervisor>>, for weekly guidance, and the (fictional) Department of Imaginary
Sciences for computing time. We also thank the <<np>> participants of our user study.

\chapter*{Abstract}
<<abstract>>

\tableofcontents

\chapter{Introduction}
<<intro>>

\chapter{Background}
<<related>>

\chapter{System design}
The project has two parts: a training and evaluation system, and a web dashboard that shows live
reconstructions from a simulated sensor array. The dashboard streams a new synthetic field every few
seconds, samples it at the sensor positions, and shows the reconstruction next to the ground truth.
\begin{figure}[h]\centering
\includegraphics[width=0.8\linewidth]{dashboard_01.png}
\caption{Dashboard main view: live field, sensor layout and reconstruction.}
\end{figure}
\begin{figure}[h]\centering
\includegraphics[width=0.8\linewidth]{dashboard_02.png}
\caption{Dashboard sensor view: per-sensor readings over time.}
\end{figure}
\begin{figure}[h]\centering
\includegraphics[width=0.8\linewidth]{dashboard_03.png}
\caption{Dashboard metrics view: PSNR and SSIM of the live reconstruction.}
\end{figure}
\begin{figure}[h]\centering
\includegraphics[width=0.8\linewidth]{dashboard_04.png}
\caption{Dashboard settings view: sensor count and decoder options.}
\end{figure}

\chapter{Method}
<<fig_overview>>
<<method>>
<<arch>>

\chapter{Experiments}
\section{Setup}
<<setup>>
<<table_main>>
<<table_sweep>>
\section{Results}
<<results>>
<<fig_panels>>
<<fig_qual>>
<<fail>>
\section{User study}
<<user>>

\chapter{Discussion}
<<disc>>

\chapter{Limitations and future work}\label{sec:limits}
<<limitations>>
Future work includes testing on real sensor data and calibrating the confidence map.

\chapter{Conclusion}
<<conclusion>>

<<bib>>
\end{document}
"""


def report_tex(authors, supervisor):
    return fill(REPORT, pkgs=PKGS, footer=FOOTER,
                info=info_block(P["title"] + " (Final Year Project report)", names(authors), "report"),
                title=P["title"], authors=" \\quad ".join(names(authors)), supervisor=PEOPLE[supervisor]["name"],
                aff=P["affiliation"], mark=MARK, np=US["participants"], abstract=ABSTRACT_TEX, intro=INTRO_TEX,
                related=RELATED_TEX, fig_overview=fill(FIG_OVERVIEW.replace(r"\input{overview_tikz.tex}",
                                                                            r"\includegraphics[width=\linewidth]{overview.png}")),
                method=METHOD_TEX, setup=SETUP_TEX, table_main=table_main(), table_sweep=table_sweep(),
                results=RESULTS_TEX, fig_panels=fill(FIG_PANELS, p=""), fig_qual=fill(FIG_QUAL, p=""),
                user=USER_TEX, limitations=limitations_tex(), conclusion=CONCL_TEX, bib=bibliography(),
                arch=ARCH_TEX, fail=FAIL_TEX, disc=DISC_TEX)


# ----------------------------------------------------------------- competition short paper (V3, T14)
SHORT = r"""\documentclass[10pt,a4paper,twocolumn]{article}
\usepackage[margin=1.8cm]{geometry}
<<pkgs>>
<<footer>>
<<info>>
\graphicspath{{figures/}}
\begin{document}
\twocolumn[\begin{center}
{\Large\bfseries Quillwave: Sharp Ripple Fields from <<k>> Sensors\par}\vspace{6pt}
<<authors>>
\vspace{4pt}{\small Short paper, <<comp>>\par}
\vspace{2pt}{\small This short paper was selected as a finalist (one of <<nf>>) in the <<comp>>.\par}
\vspace{10pt}\end{center}]
\section*{Abstract}
<<abstract>>
\section{Method}
<<method>>
\begin{figure}[t]\centering
\includegraphics[width=\linewidth]{overview.png}
\caption{Quillwave pipeline.}
\end{figure}
\section{Results}
<<setup>>
<<table_main>>
<<results>>
\section{Limitations}
<<limitations>>
<<bib>>
\end{document}
"""


def short_paper_tex(authors):
    comp = P["competition"]
    res = RESULTS_TEX.split("Table~\\ref{tab:sweep}")[0].strip()
    return fill(SHORT, pkgs=PKGS, footer=FOOTER, info=info_block("Quillwave short paper", names(authors), "short paper"),
                k=S["sensors"], authors=author_block(authors, with_mail=False), comp=comp["name"],
                nf=comp["finalists"], abstract=ABSTRACT_TEX, method=METHOD_TEX, setup=SETUP_TEX,
                table_main=table_main().replace(r"\begin{table}[t]", r"\begin{table}[h]"),
                results=res, limitations=limitations_tex(), bib=bibliography())


# ----------------------------------------------------------------- poster (A1 portrait)
POSTER = r"""\documentclass{article}
\usepackage[paperwidth=594mm,paperheight=841mm,margin=28mm]{geometry}
<<pkgs>>
\usepackage{fancyhdr}
\pagestyle{fancy}\fancyhf{}\renewcommand{\headrulewidth}{0pt}\cfoot{\fontsize{16}{20}\selectfont <<mark>>}
\setlength{\footskip}{18mm}
<<info>>
\graphicspath{{../figures/}}
\setlength{\parindent}{0pt}
\newcommand{\blocktitle}[1]{{\fontsize{36}{44}\selectfont\bfseries\color{blue!55!black}#1\par}\vspace{5mm}}
\begin{document}
\fontsize{22}{28}\selectfont
\begin{center}
{\fontsize{72}{84}\selectfont\bfseries Quillwave\par}\vspace{6mm}
{\fontsize{44}{54}\selectfont Sparse-Sensor Reconstruction of Synthetic Ripple Fields\par}\vspace{14mm}
{\fontsize{32}{40}\selectfont <<authors>>\par}\vspace{4mm}
{\fontsize{26}{32}\selectfont <<aff>>\par}\vspace{4mm}
{\fontsize{26}{32}\selectfont <<venue>>\par}
\end{center}
\vspace{8mm}
\blocktitle{Overview}
\begin{center}\includegraphics[width=0.72\linewidth]{overview.png}\end{center}\vspace{2mm}
\begin{minipage}[t]{0.47\linewidth}
\blocktitle{Problem}
Recover a full $<<n>>\times<<n>>$ ripple field from <<k>> point sensors. Smooth interpolation loses
the wave fronts between sensors.\par\vspace{8mm}
\blocktitle{Method}
A sensor encoder maps the readings to a <<ld>>-dimensional latent field code; a coordinate-based field
decoder predicts the value and a confidence at every pixel.\par\vspace{8mm}
\blocktitle{Main result}
{\fontsize{22}{28}\selectfont
\begin{tabular}{lrrr}\toprule
Method & PSNR (dB) & SSIM & Runtime (ms)\\\midrule
<<rows>>
\bottomrule\end{tabular}\par}
\vspace{8mm}
+<<gain>>\,dB over radial-basis interpolation (<<mse>>\,\% lower MSE), <<sp>>$\times$ faster.\par\vspace{8mm}
\blocktitle{Qualitative comparison}
\includegraphics[width=\linewidth]{qualitative_grid.jpg}
\end{minipage}\hfill
\begin{minipage}[t]{0.49\linewidth}
\blocktitle{Results}
\includegraphics[width=\linewidth]{results_panels.png}\par\vspace{10mm}
\blocktitle{Limitations}
\begin{itemize}\setlength{\itemsep}{4mm}
<<lims>>
\end{itemize}
\vspace{8mm}
\blocktitle{Links}
\begin{tikzpicture}\draw[black!60, line width=1.2pt, dashed] (0,0) rectangle (9cm,9cm);
\node[align=center, text width=8cm] at (4.5,4.5) {QR code placeholder\\(no target)};\end{tikzpicture}
\hfill\begin{minipage}[b]{0.5\linewidth}\raggedright Project page:\\\texttt{\fontsize{20}{26}\selectfont <<url>>}\end{minipage}
\end{minipage}
\end{document}
"""


def poster_tex(authors):
    best = [max(r[1] for r in ROWS), max(r[2] for r in ROWS), min(r[3] for r in ROWS)]
    rows = []
    for n, p, s, m in ROWS:
        cells = [f"{p:.2f}", f"{s:.3f}", f"{m:.1f}"]
        cells = [rf"\textbf{{{c}}}" if v == b else c for c, v, b in zip(cells, (p, s, m), best)]
        rows.append(f"{n} & " + " & ".join(cells) + r" \\")
    return fill(POSTER, pkgs=PKGS, mark=MARK, info=info_block(P["title"] + " (poster)", names(authors), "poster"),
                authors=", ".join(names(authors)), aff=P["affiliation"],
                venue=f"{P['venue']['short']} ({P['venue']['full']})", n=S["field_size"], k=S["sensors"],
                ld=S["latent_dim"], rows="\n".join(rows), gain=f"{D['psnr_gain_over_best_baseline_db']:.2f}",
                mse=f"{D['relative_mse_reduction_pct']:.1f}", sp=f"{D['speedup_vs_rbf']:.2f}",
                lims="\n".join(rf"\item \textbf{{{t}.}} {d}" for t, d in LIMITATIONS),
                url=P["urls"]["project"])


# ----------------------------------------------------------------- driver
def compile_tex(tex_path, outdir, runs=2):
    """Compile tex_path (cwd = its folder, so relative \\graphicspath works); PDF lands in outdir."""
    tex_path = Path(tex_path)
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    pdflatex = tool("pdflatex")
    for _ in range(runs):
        run([pdflatex, "-interaction=nonstopmode", "-halt-on-error", f"-output-directory={outdir}", tex_path.name],
            cwd=tex_path.parent, what=f"pdflatex {tex_path.name}")
    return outdir / (tex_path.stem + ".pdf")


def pdf_to_png(pdf, png_stem, dpi=None, scale_x=None):
    args = [tool("pdftoppm"), "-png", "-singlefile"]
    args += ["-r", str(dpi)] if dpi else ["-scale-to-x", str(scale_x), "-scale-to-y", "-1"]
    run(args + [pdf, png_stem], what="pdftoppm")
    return Path(str(png_stem) + ".png")
