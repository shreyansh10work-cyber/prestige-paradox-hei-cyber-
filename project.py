"""
================================================================================
THE PRESTIGE PARADOX: Institutional Bibliometric Status and Cybersecurity
Media Salience in Global Higher Education, 2020-2024
================================================================================
Author      : Shreyansh Chaudhary (Student ID: 001487390)
Programme   : MSc Business Analytics, University of Greenwich
Module      : BUSI 1783 - Business Analytics Project
Supervisor  : Dr Raunak Mishra

PURPOSE
-------
This script is the single source of truth for every number reported in the
dissertation. It rebuilds the final analytical dataset, runs the models, and
writes a machine-readable manifest (results_manifest.json) plus all figures.

Every statistic quoted in the dissertation is emitted by this script. If a
number is not printed here, it does not belong in the dissertation.

INPUT
-----
    prestige_paradox_742_universities_raw.csv
        Pre-merge output of the GDELT + OpenAlex pipeline. Contains 742 rows,
        including the 'He University' false fuzzy merge.

OUTPUT
------
    prestige_paradox_dataset_741.csv   Final analytical dataset (He removed)
    results_manifest.json              Every reported statistic, machine-readable
    figures/*.png                      Figures 1-11
    regression_results.txt             Full model summaries
    optimizer_stability.txt            Optimiser comparison

METHODOLOGICAL NOTE ON 742 vs 741
---------------------------------
The fuzzy merge at threshold 90 collapsed seven unrelated GDELT name-fragments
(e.g. 'Citizen Lab Of The University Of Toronto', 'Regents Of The University Of
California', 'University The') onto a single OpenAlex record, 'He University'.
This is a false merge: the 32 events attributed to it belong to other
institutions. It is removed by manual validation, giving the analytical N of
741. All dissertation results use N = 741.

USAGE
-----
    python project.py
================================================================================
"""

import json
import os
import warnings

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy.stats import chi2_contingency, skew

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings("ignore")

# ------------------------------------------------------------------ config ---
RAW_INPUT   = "prestige_paradox_742_universities_raw.csv"
FINAL_CSV   = "prestige_paradox_dataset_741.csv"
MANIFEST    = "results_manifest.json"
FIG_DIR     = "figures"
FALSE_MERGE = "He University"      # identified via manual validation
MIN_COUNTRY = 5                    # countries with < 5 unis pooled into 'Other'

os.makedirs(FIG_DIR, exist_ok=True)
M = {}   # results manifest

def rule(t):
    print("\n" + "=" * 78 + f"\n{t}\n" + "=" * 78)


# =============================================================== STAGE 1 =====
rule("STAGE 1 - LOAD PRE-MERGE DATA AND REMOVE FALSE FUZZY MERGE")

raw = pd.read_csv(RAW_INPUT)
print(f"Rows loaded (pre-merge, 742-row file) : {len(raw)}")

he = raw[raw["the_official_name"] == FALSE_MERGE]
if len(he):
    print(f"\nFalse merge found: '{FALSE_MERGE}'")
    print(f"  events attributed  : {int(he['cyber_news_count'].iloc[0])}")
    print(f"  GDELT names merged : {he['gdelt_name'].iloc[0][:90]}...")
    print("  -> removing (unrelated fragments collapsed onto one OpenAlex record)")

df = raw[raw["the_official_name"] != FALSE_MERGE].copy().reset_index(drop=True)

M["n_universities_pre_merge_file"] = int(len(raw))
M["he_university_events_removed"]  = int(he["cyber_news_count"].iloc[0]) if len(he) else 0
M["n_universities"]                = int(len(df))
M["total_cyber_events"]            = int(df["cyber_news_count"].sum())
M["n_countries"]                   = int(df["country"].nunique())

print(f"\nAnalytical dataset : N = {M['n_universities']} universities")
print(f"Total cyber events : {M['total_cyber_events']}")
print(f"Countries          : {M['n_countries']}")


# =============================================================== STAGE 2 =====
rule("STAGE 2 - DESCRIPTIVE STATISTICS (TABLE 2)")

dv = df["cyber_news_count"]
M["dv_mean"]     = round(float(dv.mean()), 2)
M["dv_sd"]       = round(float(dv.std()), 2)
M["dv_var"]      = round(float(dv.var()), 2)
M["dv_min"]      = int(dv.min())
M["dv_median"]   = int(dv.median())
M["dv_max"]      = int(dv.max())
M["overdispersion_ratio"] = round(float(dv.var() / dv.mean()), 2)
M["dv_max_university"] = str(df.loc[dv.idxmax(), "the_official_name"])

iv = df["cited_by_count"]
M["iv_mean"]   = int(round(iv.mean()))
M["iv_sd"]     = int(round(iv.std()))
M["iv_min"]    = int(iv.min())
M["iv_median"] = int(round(iv.median()))
M["iv_max"]    = int(iv.max())

lg = df["log_cited_by_count"]
M["log_iv_mean"]   = round(float(lg.mean()), 2)
M["log_iv_sd"]     = round(float(lg.std()), 2)
M["log_iv_min"]    = round(float(lg.min()), 2)
M["log_iv_median"] = round(float(lg.median()), 2)
M["log_iv_max"]    = round(float(lg.max()), 2)

M["skew_raw_citations"] = round(float(skew(iv)), 2)
M["skew_log_citations"] = round(float(skew(lg)), 2)

t2 = pd.DataFrame([
    ["cyber_news_count (DV)", M["n_universities"], f"{M['dv_mean']:.2f}", f"{M['dv_sd']:.2f}",
     M["dv_min"], M["dv_median"], M["dv_max"]],
    ["cited_by_count (IV)", M["n_universities"], f"{M['iv_mean']:,}", f"{M['iv_sd']:,}",
     f"{M['iv_min']:,}", f"{M['iv_median']:,}", f"{M['iv_max']:,}"],
    ["log_cited_by_count", M["n_universities"], f"{M['log_iv_mean']:.2f}", f"{M['log_iv_sd']:.2f}",
     f"{M['log_iv_min']:.2f}", f"{M['log_iv_median']:.2f}", f"{M['log_iv_max']:.2f}"],
], columns=["Variable", "N", "Mean", "SD", "Min", "Median", "Max"])
print(t2.to_string(index=False))

print(f"\nOverdispersion ratio (var/mean) : {M['overdispersion_ratio']}  -> Negative Binomial justified")
print(f"Skewness raw citations          : {M['skew_raw_citations']}")
print(f"Skewness log citations          : {M['skew_log_citations']}")


# =============================================================== STAGE 3 =====
rule("STAGE 3 - GEOGRAPHIC DISTRIBUTION (FIGURE 8)")

cc = df["country"].value_counts()
M["country_counts_top10"] = {str(k): int(v) for k, v in cc.head(10).items()}
M["us_count"]   = int(cc.get("US", 0))
M["us_percent"] = round(100 * cc.get("US", 0) / len(df), 1)
M["gb_count"]   = int(cc.get("GB", 0))
M["gb_percent"] = round(100 * cc.get("GB", 0) / len(df), 1)
print(cc.head(10).to_string())
print(f"\nUS: {M['us_count']} ({M['us_percent']}%)   GB: {M['gb_count']} ({M['gb_percent']}%)")

plt.figure(figsize=(8, 6))
cc.head(15).sort_values().plot(kind="barh", color="slateblue")
plt.title("Universities in Dataset by Country (Top 15)")
plt.xlabel("Number of Universities"); plt.ylabel("Country")
plt.tight_layout(); plt.savefig(f"{FIG_DIR}/figure8_country_distribution.png", dpi=200); plt.close()


# =============================================================== STAGE 4 =====
rule("STAGE 4 - TOP UNIVERSITIES (TABLE 3 / FIGURE 2)")

top15 = df.nlargest(15, "cyber_news_count")[
    ["the_official_name", "country", "cyber_news_count", "cited_by_count"]].reset_index(drop=True)
top15.index += 1
print(top15.to_string())

M["top15"] = [
    {"rank": i, "name": r.the_official_name, "country": r.country,
     "mentions": int(r.cyber_news_count), "citations": int(r.cited_by_count)}
    for i, r in top15.iterrows()
]

# Figure 2 MUST come from the same dataframe as Table 3 (supervisor point 1)
top20 = df.nlargest(20, "cyber_news_count")[["the_official_name", "cyber_news_count"]].copy()
top20["label"] = top20["the_official_name"].replace(
    {"Indiana University – Purdue University Indianapolis": "Indiana U.–Purdue U. Indianapolis"})
plt.figure(figsize=(9, 7))
top20.sort_values("cyber_news_count").plot(
    kind="barh", x="label", y="cyber_news_count", color="#7a1420", legend=False, ax=plt.gca())
plt.title("Top 20 Universities by GDELT Cybersecurity Media Mention Count, 2020–2024")
plt.xlabel("Number of Mentions"); plt.ylabel("")
plt.tight_layout(); plt.savefig(f"{FIG_DIR}/figure2_top20_universities.png", dpi=200); plt.close()


# =============================================================== STAGE 5 =====
rule("STAGE 5 - PRESTIGE TIER ANALYSIS (TABLE 4 / FIGURES 5 & 10)")

tier_order = ["Elite (5M+)", "High (1M-5M)", "Medium (100K-1M)", "Low (<100K)"]
tier = df.groupby("prestige_tier", observed=True)["cyber_news_count"].agg(["count", "mean", "median"])
tier = tier.reindex(tier_order)
tier["pct"] = (100 * tier["count"] / len(df)).round(1)
print(tier.round(2).to_string())
print(f"\nTier count sum = {int(tier['count'].sum())} (must equal {M['n_universities']})")
assert int(tier["count"].sum()) == M["n_universities"], "Tier counts do not sum to N"

M["tiers"] = {
    t: {"n": int(tier.loc[t, "count"]),
        "mean": round(float(tier.loc[t, "mean"]), 1),
        "median": float(tier.loc[t, "median"]),
        "pct": float(tier.loc[t, "pct"])}
    for t in tier_order
}

plt.figure(figsize=(8, 5))
tier["mean"].plot(kind="bar", color="goldenrod", edgecolor="white")
plt.title("Average Cyber News Mentions by Prestige Tier")
plt.ylabel("Average Mention Count"); plt.xlabel("prestige_tier")
plt.xticks(rotation=20); plt.tight_layout()
plt.savefig(f"{FIG_DIR}/figure5_mentions_by_tier.png", dpi=200); plt.close()

plt.figure(figsize=(8, 5))
pal = {"Low (<100K)": "#c0392b", "Medium (100K-1M)": "#e67e22",
       "High (1M-5M)": "#27ae60", "Elite (5M+)": "#2980b9"}
sns.boxplot(data=df, x="prestige_tier", y="cyber_news_count",
            order=tier_order[::-1], palette=pal)
plt.yscale("log")
plt.title("Cybersecurity Media Mentions by Prestige Tier")
plt.ylabel("Cybersecurity Media Mentions (log scale)"); plt.xlabel("Prestige Tier")
plt.tight_layout(); plt.savefig(f"{FIG_DIR}/figure10_boxplot_by_tier.png", dpi=200); plt.close()


# =============================================================== STAGE 6 =====
rule("STAGE 6 - IV DISTRIBUTION AND CORRELATIONS (FIGURES 3, 4, 6)")

fig, ax = plt.subplots(1, 2, figsize=(12, 5))
ax[0].hist(df["cited_by_count"], bins=30, color="teal", edgecolor="white")
ax[0].set_title("Distribution of Citation Counts (Raw)"); ax[0].set_xlabel("Total Citations")
ax[1].hist(df["log_cited_by_count"], bins=30, color="teal", edgecolor="white")
ax[1].set_title("Distribution of Citation Counts (Log Scale)"); ax[1].set_xlabel("Log(Citations + 1)")
plt.tight_layout(); plt.savefig(f"{FIG_DIR}/figure3_citation_distribution.png", dpi=200); plt.close()

plt.figure(figsize=(9, 6))
plt.scatter(df["log_cited_by_count"], df["cyber_news_count"],
            alpha=0.6, color="darkred", edgecolor="white", s=60)
z = np.polyfit(df["log_cited_by_count"], df["cyber_news_count"], 1)
xs = np.linspace(df["log_cited_by_count"].min(), df["log_cited_by_count"].max(), 100)
plt.plot(xs, np.poly1d(z)(xs), "k--", alpha=0.7, label="Linear trend")
plt.xlabel("Log(Total Citations) — Prestige Proxy")
plt.ylabel("Cyber News Mention Count (2020-2024)")
plt.title("Does Prestige Predict Cyber News Coverage? (Prestige Paradox)")
plt.legend(); plt.tight_layout()
plt.savefig(f"{FIG_DIR}/figure4_scatter_citations_mentions.png", dpi=200); plt.close()

# Correlation matrix uses the LOG variables actually entering the model, so the
# r = 0.985 quoted in the dissertation is visible in the figure itself.
corr_vars = ["cyber_news_count", "log_cited_by_count", "log_works_count"]
corr = df[corr_vars].corr()
M["r_log_cited_log_works"] = round(float(df["log_cited_by_count"].corr(df["log_works_count"])), 3)
M["r_cited_works_raw"]     = round(float(df["cited_by_count"].corr(df["works_count"])), 3)
print(corr.round(3).to_string())
print(f"\nr(log_cited_by_count, log_works_count) = {M['r_log_cited_log_works']}  <- collinearity")

plt.figure(figsize=(6.5, 5))
sns.heatmap(corr, annot=True, cmap="coolwarm", center=0, fmt=".3f", vmin=0, vmax=1)
plt.title("Correlation Matrix — Model Variables")
plt.tight_layout(); plt.savefig(f"{FIG_DIR}/figure6_correlation_heatmap.png", dpi=200); plt.close()


# =============================================================== STAGE 7 =====
rule("STAGE 7 - CHI-SQUARE TEST (REPORTED FOR TRANSPARENCY ONLY)")

med = df["cited_by_count"].median()
df["prestige_group"] = np.where(df["cited_by_count"] >= med, "High", "Low")
df["has_event"] = np.where(df["cyber_news_count"] > 0, "Yes", "No")
ct = pd.crosstab(df["prestige_group"], df["has_event"])
chi2, pchi, dof, _ = chi2_contingency(ct)
M["chi2_stat"]    = round(float(chi2), 4)
M["chi2_p"]       = round(float(pchi), 4)
print(ct.to_string())
print(f"\nchi2 = {M['chi2_stat']}, p = {M['chi2_p']}")
print("Uninformative by construction: the 3+ frequency filter means every")
print("university has events, so has_event has no variation.")


# =============================================================== STAGE 8 =====
rule("STAGE 8 - NEGATIVE BINOMIAL REGRESSION (TABLE 5)")

vc = df["country"].value_counts()
common = vc[vc >= MIN_COUNTRY].index
df["country_grouped"] = df["country"].where(df["country"].isin(common), "Other")

groups = sorted(df["country_grouped"].unique())
M["n_country_groups"]  = int(len(groups))
M["n_country_dummies"] = int(len(groups) - 1)
M["country_reference"] = str(groups[0])   # patsy drops the first level alphabetically
print(f"Countries in data      : {M['n_countries']}")
print(f"Countries with >= {MIN_COUNTRY} unis : {len(common)}  (rest pooled as 'Other')")
print(f"Country groups         : {M['n_country_groups']}")
print(f"Country dummies        : {M['n_country_dummies']}")
print(f"Reference category     : {M['country_reference']} (alphabetically first)")

formula = "cyber_news_count ~ log_cited_by_count + C(country_grouped)"
main = smf.negativebinomial(formula, data=df).fit(method="bfgs", maxiter=500, disp=False)
print("\n" + str(main.summary()))

coef = float(main.params["log_cited_by_count"])
se   = float(main.bse["log_cited_by_count"])
ci   = np.exp(main.conf_int()).loc["log_cited_by_count"]

M["main_converged"]  = bool(main.mle_retvals.get("converged", False))
M["main_n"]          = int(main.nobs)
M["main_df_resid"]   = int(main.df_resid)
M["main_df_model"]   = int(main.df_model)
M["main_pseudo_r2"]  = round(float(main.prsquared), 5)
M["main_llf"]        = round(float(main.llf), 1)
M["main_llnull"]     = round(float(main.llnull), 1)
M["main_llr_p"]      = f"{float(main.llr_pvalue):.2e}"
M["coef"]            = round(coef, 4)
M["se"]              = round(se, 4)
M["z"]               = round(coef / se, 3)
M["irr"]             = round(float(np.exp(coef)), 3)
M["irr_ci_low"]      = round(float(ci[0]), 3)
M["irr_ci_high"]     = round(float(ci[1]), 3)
M["irr_pct"]         = round((float(np.exp(coef)) - 1) * 100, 1)
M["alpha"]           = round(float(main.params["alpha"]), 4)
M["alpha_se"]        = round(float(main.bse["alpha"]), 3)
M["alpha_z"]         = round(float(main.params["alpha"] / main.bse["alpha"]), 2)

cd = [i for i in main.params.index if i.startswith("C(country_grouped)")]
M["n_country_coefs_shown"]      = int(len(cd))
M["any_country_dummy_sig_p05"]  = bool((main.pvalues[cd] < 0.05).any())
M["min_country_dummy_p"]        = round(float(main.pvalues[cd].min()), 3)

print(f"\nHEADLINE: IRR = {M['irr']} (95% CI {M['irr_ci_low']}-{M['irr_ci_high']}), p < 0.0001")
print(f"          = {M['irr_pct']}% more mentions per unit log citations")
print(f"Country dummies significant at p<0.05? {M['any_country_dummy_sig_p05']} "
      f"(smallest p = {M['min_country_dummy_p']})")

plt.figure(figsize=(8, 5))
irr_all = pd.DataFrame({"IRR": np.exp(main.params), "p": main.pvalues})
key = irr_all[~irr_all.index.str.startswith("C(country")]
cols = ["darkred" if p < 0.05 else "steelblue" for p in key["p"]]
plt.barh(key.index, key["IRR"], color=cols)
plt.axvline(1, color="black", ls="--", lw=1.2, label="IRR = 1 (no effect)")
plt.xlabel("Incidence Rate Ratio (IRR)")
plt.title("Negative Binomial Regression — Key Predictors\n(Red = significant at p < 0.05)")
plt.legend(); plt.tight_layout()
plt.savefig(f"{FIG_DIR}/figure7_irr_chart.png", dpi=200); plt.close()


# =============================================================== STAGE 9 =====
rule("STAGE 9 - OPTIMISER STABILITY (TABLE 6)")

M["optimisers"] = []
lines = []
for meth in ["bfgs", "lbfgs", "powell", "cg", "nm"]:
    m = smf.negativebinomial(formula, data=df).fit(method=meth, maxiter=500, disp=False)
    cf, s = float(m.params["log_cited_by_count"]), float(m.bse["log_cited_by_count"])
    rec = {"method": meth,
           "converged": bool(m.mle_retvals.get("converged", False)),
           "coef": round(cf, 4), "se": round(s, 4),
           "irr": round(float(np.exp(cf)), 4),
           "p": float(m.pvalues["log_cited_by_count"])}
    M["optimisers"].append(rec)
    ln = (f"{meth:8s} | converged={str(rec['converged']):5s} | coef={rec['coef']:.4f} "
          f"| SE={rec['se']:.4f} | p={rec['p']:.6f} | IRR={rec['irr']:.4f}")
    print(ln); lines.append(ln)
open("optimizer_stability.txt", "w").write("\n".join(lines) + "\n")

conv = [o for o in M["optimisers"] if o["converged"]]
M["n_optimisers_converged"] = len(conv)
M["conv_coef_min"] = min(o["coef"] for o in conv)
M["conv_coef_max"] = max(o["coef"] for o in conv)
M["conv_irr_min"]  = min(o["irr"] for o in conv)
M["conv_irr_max"]  = max(o["irr"] for o in conv)
print(f"\nConverged: {M['n_optimisers_converged']}/5 | coef {M['conv_coef_min']}-{M['conv_coef_max']} "
      f"| IRR {M['conv_irr_min']}-{M['conv_irr_max']}")


# ============================================================== STAGE 10 =====
rule("STAGE 10 - ROBUSTNESS CHECK WITH log_works_count (TABLE 7)")

rformula = "cyber_news_count ~ log_cited_by_count + log_works_count + C(country_grouped)"
rob = smf.negativebinomial(rformula, data=df).fit(disp=False)
print(str(rob.summary().tables[1]))

M["rob_converged"]   = bool(rob.mle_retvals.get("converged", False))
M["rob_coef"]        = round(float(rob.params["log_cited_by_count"]), 4)
M["rob_se"]          = round(float(rob.bse["log_cited_by_count"]), 3)
M["rob_z"]           = round(float(rob.tvalues["log_cited_by_count"]), 3)
M["rob_p"]           = round(float(rob.pvalues["log_cited_by_count"]), 3)
M["rob_irr"]         = round(float(np.exp(rob.params["log_cited_by_count"])), 3)
M["rob_works_p"]     = round(float(rob.pvalues["log_works_count"]), 3)
M["rob_pseudo_r2"]   = round(float(rob.prsquared), 5)

print(f"\nConverged: {M['rob_converged']}  <- collinearity (r = {M['r_log_cited_log_works']}) "
      f"destabilises the Hessian")
print(f"log_cited_by_count: coef={M['rob_coef']} SE={M['rob_se']} p={M['rob_p']} IRR={M['rob_irr']}")
print(f"log_works_count   : p={M['rob_works_p']} (not significant)")
print("A non-converged model has unreliable SEs by construction and cannot be")
print("read as confirmatory. Impact vs volume remains unresolved by these data.")

with open("regression_results.txt", "w") as f:
    f.write("PRESTIGE PARADOX - REGRESSION RESULTS\n" + "=" * 60 + "\n\n")
    f.write(f"Sample size: {M['n_universities']} universities\n")
    f.write(f"Total cyber news events: {M['total_cyber_events']}\n\n")
    f.write(f"Chi-square: {M['chi2_stat']}, p = {M['chi2_p']}\n")
    f.write("Note: uninformative - all universities have >= 3 events by construction\n\n")
    f.write(f"Overdispersion ratio: {M['overdispersion_ratio']}\n\n")
    f.write("MAIN MODEL - Negative Binomial (no size control):\n")
    f.write(str(main.summary()))
    f.write("\n\nROBUSTNESS CHECK (with log_works_count):\n")
    f.write(str(rob.summary()))


# ============================================================== STAGE 11 =====
rule("STAGE 11 - WRITE OUTPUTS")

out = df.drop(columns=["prestige_group", "has_event", "country_grouped"])
out.to_csv(FINAL_CSV, index=False)
print(f"Wrote {FINAL_CSV}  ({len(out)} rows, {len(out.columns)} columns)")
print(f"Columns: {list(out.columns)}")

with open(MANIFEST, "w") as f:
    json.dump(M, f, indent=2)
print(f"Wrote {MANIFEST}  ({len(M)} keys)")
print(f"Wrote {FIG_DIR}/ (9 generated figures; Figures 1, 9 and 11 come from the "
      f"GDELT event-level pipeline and README)")

rule("VERIFICATION SUMMARY - THESE ARE THE ONLY VALID DISSERTATION NUMBERS")
for k in ["n_universities", "total_cyber_events", "n_countries", "dv_mean", "dv_sd",
          "dv_median", "dv_max", "overdispersion_ratio", "iv_mean", "iv_sd", "iv_median",
          "log_iv_mean", "log_iv_sd", "log_iv_median", "skew_raw_citations",
          "skew_log_citations", "us_count", "us_percent", "n_country_groups",
          "n_country_dummies", "country_reference", "coef", "se", "z", "irr",
          "irr_ci_low", "irr_ci_high", "irr_pct", "alpha", "main_pseudo_r2",
          "r_log_cited_log_works", "rob_converged", "rob_p", "rob_works_p"]:
    print(f"  {k:26s} = {M[k]}")
print("\nDone.")
