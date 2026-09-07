# Information Diffusion and Market Reaction: A Historical Earnings Event Study

**Case: Meta Platforms, Inc. (META), Q4 FY2021 earnings, announced February 2, 2022**

---

## 1. Abstract

This project studies how a single, real, historical earnings announcement was incorporated into a
company's stock price. Using Meta Platforms' Q4 FY2021 earnings release — which triggered a
same-week -26.4% single-day stock decline, one of the largest market-capitalization losses by a US
company on record — we combine a standard market-model event study with a small, real news dataset
and two candidate information-diffusion curves (exponential absorption and logistic diffusion) to
characterize the speed and shape of the market's reaction. We find a statistically significant,
economically large abnormal return on the announcement-reaction day (-23.09%, t = -15.87), with
roughly 69% of the eventual ten-day cumulative abnormal return already realized by the close of
that single session. Neither diffusion curve fits the observed path well by a strict R² ≥ 0.8
standard (logistic: R² = 0.58; exponential: R² = -5.04), which is itself an informative result: at
daily granularity, this reaction looks much more like a near-instantaneous repricing than a gradual
diffusion process. All four pre-registered hypotheses and their honest results are reported in
Section 17.

## 2. Introduction

Earnings announcements are one of the most-studied information events in financial economics
because they are regular, scheduled, and produce a verifiable "surprise" (actual vs. expected)
that can be related to the resulting price change. Most classroom treatments of event studies use
either a stylized example or a large panel of many small events, which can obscure the mechanics of
any single event. This project instead goes deep on one dramatic, well-documented case, so every
step — from raw data to final statistic — can be inspected and reasoned about individually.

## 3. Research Question

*How does newly released earnings information become incorporated into a company's stock price,
and how do the timing and intensity of news coverage relate to the speed and magnitude of the
market reaction?*

This is deliberately an explanatory question about a historical event, not a predictive question
about future prices.

## 4. Hypotheses

| ID | Statement | Variables | Method |
|---|---|---|---|
| H1 | A large earnings-related surprise is associated with a large, statistically significant abnormal return on the event day. | EPS/revenue surprise (%), event-day abnormal return | Brown & Warner (1985) single-event t-test |
| H2 | Increased news intensity is associated with increased trading volume. | Daily article count, abnormal volume ratio | Pearson correlation (event window) |
| H3 | The majority of the event-related price adjustment occurs relatively soon after the earnings release. | Information absorption time (p50, p90) | Empirical interpolation on the CAR path |
| H4 | A diffusion model can approximate the observed cumulative market reaction. | Exponential vs. logistic R², RMSE, MAE | Nonlinear least squares + goodness-of-fit |

Full results are in Section 17.

## 5. Background

### 5.1 Event selection

Before committing to Meta, we considered Nvidia (May 2023 AI-guidance beat), Apple, Amazon, and
Tesla earnings events. Meta's Q4 FY2021 release was selected because it uniquely combines:

- an unambiguous, single-timestamp catalyst (after-hours release on 2022-02-02);
- an extreme, unambiguous price reaction (-26.4% the next session) that is far larger than typical
  daily noise, giving a high signal-to-noise ratio for an event study;
- a well-documented, independently verifiable set of facts (EPS miss, revenue beat, first-ever
  sequential DAU decline, weak forward guidance) reported identically across many independent
  outlets;
- dense contemporaneous news coverage suitable for a small, real, citable headline dataset; and
- full reproducibility from free, keyless data sources (Section 10).

Nvidia's 2023 AI-boom earnings were considered but rejected as the *primary* case specifically
because their popularity risked turning this into "another AI stock story" rather than a general
information-diffusion case study; Meta's event is older, more extreme in magnitude, and driven by a
richer mix of factors (earnings, guidance, and a structural user-growth signal), which better
exercises the event-study and diffusion methodology.

### 5.2 The event, in brief

Meta Platforms reported Q4 FY2021 results after market close on February 2, 2022: EPS of $3.67
(vs. a $3.84 consensus estimate — a miss), revenue of $33.67B (vs. $33.40B estimated — a narrow
beat), and the first-ever reported sequential decline in Facebook daily active users (1.93B, vs.
1.95B estimated). Management guided Q1 2022 revenue to $27–29B, well below the ~$30.15B consensus,
and cited an estimated ~$10B full-year impact from Apple's App Tracking Transparency changes plus
rising competition from TikTok. META closed at $323.00 on Feb 2 and $237.76 on Feb 3 — a one-day
return of -26.39%, wiping out on the order of $230B of market capitalization (contemporaneous
estimates range $230–251B depending on methodology and timing). See
`data/raw/earnings_facts.json` for every figure with its source citation.

## 6. Information Diffusion

"Information diffusion" here means the process by which new, price-relevant information becomes
reflected in a security's price over time, rather than instantaneously. Two idealized shapes are
commonly used to describe such absorption processes:

- **Exponential absorption**: a constant-hazard-rate process, `f(t) = 1 - exp(-k·t)`, appropriate
  when the market digests a fixed proportion of *remaining* unpriced information at every instant
  after t=0. This is the natural shape under semi-strong-form efficiency with fast reaction.
- **Logistic diffusion**: an S-shaped process, `f(t) = 1 / (1 + exp(-k·(t - t0)))`, appropriate when
  absorption first requires a build-up (e.g., of investor attention or trading volume) before
  accelerating and then saturating. This is the classic Bass (1969) innovation-diffusion shape
  applied to information rather than product adoption.

We do not claim either curve describes what any individual investor does; we ask only whether the
*aggregate, observable* cumulative-reaction path resembles one of these two well-known shapes
better than the other (Section 15).

## 7. Efficient Market Hypothesis

Under the semi-strong form of the Efficient Market Hypothesis (Fama, 1970), security prices should
reflect all publicly available information essentially immediately upon its release, leaving no
exploitable post-announcement drift. A finding that most of the cumulative abnormal return is
realized within the first trading session (as we find in Section 17, H3) is consistent with
semi-strong efficiency. A finding of substantial, persistent post-announcement drift would instead
be evidence *against* fast semi-strong efficiency for this event — a well-known empirical anomaly
(the "post-earnings-announcement drift" literature, e.g. Bernard & Thomas, 1989). This project does
not adjudicate the general debate; it reports what happened in this one case.

## 8. Price Discovery

"Price discovery" refers to the mechanism — order flow, trading, quote updates — by which new
information gets embedded into the traded price. Abnormal trading volume (Section 14) is used here
as a rough observable proxy for the intensity of price-discovery activity: on the event day,
volume was 9.9× the estimation-window average, consistent with unusually large information-driven
trading activity concentrated on that single session.

## 9. Event Study Methodology

We follow the single-firm event-study framework of MacKinlay (1997):

1. **Market model.** Fit `R_it = α + β·R_mt + e_it` via OLS on an estimation window that excludes
   the event, using the S&P 500 (`^GSPC`) as the market proxy.
2. **Expected return.** Predict the expected return in the event window from the fitted α, β.
3. **Abnormal return (AR).** `AR_t = R_t(actual) - R_t(expected)`.
4. **Cumulative abnormal return (CAR).** Running sum of AR across the event window.
5. **Significance.** Because this is a single event (n=1), classical cross-sectional t-tests do not
   apply. We use the Brown & Warner (1985) approach instead: divide the event-day AR by the
   *time-series* standard deviation of the market-model residuals from the estimation window, and
   compare against the standard normal/t distribution. This tests "is this reaction bigger than
   normal day-to-day noise?", which remains valid with one event.

**Estimation window:** 120 trading days, ending 10 trading days before the event window opens
(2021-08-05 to 2022-01-19, approximately). The 10-day gap prevents any pre-event drift or
information leakage from contaminating the α/β estimates.

**Event window:** `[-5, +10]` trading days around t=0. Five pre-event days let us check for
abnormal drift/leakage before the announcement; ten post-event days give enough runway to see
whether the reaction stabilizes, while staying short enough that unrelated news is unlikely to
contaminate the window.

**Event day (t=0):** 2022-02-03 — the first trading session in which the market could react, since
the release came after the 2022-02-02 close.

## 10. Dataset

All data is small, real, and checked into `data/raw/` (full detail in `data/README.md`):

| File | Content | Source |
|---|---|---|
| `meta_prices.csv` | Daily OHLCV, META, 2021-06-01 to 2022-04-15 | Yahoo Finance public chart API |
| `benchmark_prices.csv` | Daily OHLCV, S&P 500 (`^GSPC`), same range | Yahoo Finance public chart API |
| `earnings_facts.json` | EPS/revenue actual & estimate, DAU/MAU, guidance, stock reaction | Hand-transcribed from CNBC, Washington Post, Bloomberg, Forbes, Motley Fool, Wikipedia (each cited) |
| `news_headlines.csv` | 13 real headlines (title, publisher, date, URL) | Curated from the same public sources |

No paid API, API key, or authentication is required to reproduce any of this. See Section 22 for
why intraday data was not used.

## 11. Data Collection

Market data was pulled from Yahoo Finance's public, unauthenticated chart endpoint
(`https://query1.finance.yahoo.com/v8/finance/chart/<symbol>`) — the same source the popular
`yfinance` library wraps — via `scripts/fetch_market_data.py`. Earnings facts and news headlines
were collected by web research against primary/major-outlet sources and manually transcribed into
structured files with an explicit source citation on every fact (see the `sources` field in
`earnings_facts.json` and the `url` column in `news_headlines.csv`). No article body text is
reproduced — only publicly stated headline text and metadata.

## 12. Data Cleaning

`src/signalflow/data.py` validates every input before it can enter the pipeline: required columns
must be present, prices must be strictly positive, volumes non-negative, dates unique and sortable,
and company/benchmark price series are inner-joined on date so a market-model regression can never
pair a return with a missing counterpart. Any violation raises a `DataValidationError` rather than
silently producing a wrong number (see `tests/test_data.py`).

## 13. NLP Methodology

Headline sentiment is scored with VADER (Valence Aware Dictionary and sEntiment Reasoner; Hutto &
Gilbert, 2014), chosen deliberately over a heavier model such as FinBERT:

- The input is a small set of **short headlines** (metadata), not full articles — VADER is designed
  for exactly this kind of short, informal text.
- It requires **no training data, GPU, or model download**, keeping the project's "no paid
  services, works offline" guarantee intact.
- Its output (a single interpretable compound score) is easy to reason about and explain, which
  matters more here than squeezing out marginal accuracy on 13 headlines — a sample far too small
  for a transformer's extra capacity to matter statistically.

A small finance-domain lexicon adjustment (`src/signalflow/sentiment.py`) corrects a handful of
words VADER's general-purpose lexicon under- or mis-scores in a financial-news context (e.g.
"plummets", "wipeout", "beat"), following the pattern VADER's own documentation recommends for
domain adaptation.

## 14. Market Reaction Methodology

Beyond AR/CAR (Section 9), we compute:

- **Volatility**: standard deviation of daily returns, separately for the pre-event window
  (relative days < 0), post-event window (> 0), and the estimation window, to see whether
  volatility elevated after the event and whether it appears to be reverting.
- **Abnormal volume**: each day's volume divided by the mean estimation-window volume, expressed as
  a multiple (e.g. "9.9×" on the event day).
- **Maximum reaction / time to peak**: the event-window day with the largest `|AR|` and `|CAR|`.

## 15. Diffusion Models

Both candidate curves (Section 6) are fit with `scipy.optimize.curve_fit` (nonlinear least squares)
to the **absorption fraction** path: `CAR(t) / CAR(t_end)` for each post-event trading day
`t = 0, 1, …, 10`, where `t_end = +10` is the last observed day. This normalizes the (negative, in
this case) cumulative abnormal return onto a 0→1 scale representing "fraction of the eventual move
realized so far." Models are compared by RMSE, MAE, and R² (Section 18).

## 16. Experimental Design

This is a single-event, observational (not experimental) study: there is no control group and no
manipulated treatment. The "control" for isolating the company-specific reaction is the market
model itself (Section 9), which nets out the contemporaneous market-wide return. All four
hypotheses (Section 4) are tested using only the real dataset described in Section 10 — no
simulated or synthetic data is used anywhere in this project.

## 17. Results

**Event study (Section 9):**
- Market model: α = -0.0011, β = 1.31, R² = 0.36, n = 120 (estimation window)
- Event-day (t=0) abnormal return: **-23.09%** (t = -15.87, p < 0.0001)
- Cumulative abnormal return, full `[-5, +10]` window: **-29.44%**
- Event-day abnormal volume: **9.9×** the estimation-window average
- Pre-event volatility: 1.41% · Post-event volatility: 3.04% · Estimation-window (baseline)
  volatility: 1.81% — volatility roughly doubled after the event relative to baseline and had not
  fully reverted by day +10.

**Diffusion models (Section 15):**
- Exponential: k = 1.126, RMSE = 0.228, MAE = 0.134, **R² = -5.04** (worse than the mean — a poor
  fit, because it forces the curve through 0% absorption at t=0, which does not match reality)
- Logistic: k = 0.209, t0 = -4.77, RMSE = 0.060, MAE = 0.050, **R² = 0.58** (moderate fit — the best
  of the two, but short of a strong fit)
- Better-fitting model: **logistic**
- Information absorption time: 50% of the eventual move was absorbed within **0.00 trading days**
  (i.e., already true by the close of the announcement-reaction session), 90% within **2.26 trading
  days**.

**Hypotheses:**

| ID | Result | Key statistic |
|---|---|---|
| H1 | **Supported** | t = -15.87, p < 0.0001 |
| H2 | **Supported** (descriptively; see caveat in Section 18) | Pearson r = 0.67, p = 0.004, n = 16 |
| H3 | **Supported** | 50% absorbed by day 0; 90% by day 2.26 |
| H4 | **Not supported** | Best R² = 0.58 (logistic), below the pre-registered 0.8 bar |

Full conclusion text for each hypothesis, including caveats, is served at
`/api/results/hypotheses` and shown in the dashboard's Results tab.

## 18. Statistical Analysis

The H1 t-test is a legitimate single-event significance test in the Brown & Warner (1985)
tradition — it establishes that the reaction is far larger than normal daily noise, not that
"bigger surprises cause proportionally bigger reactions" (which would need a cross-sectional sample
of many events). The H2 correlation (r = 0.67) is statistically notable on its own terms (p = 0.004)
but rests on only 16 trading days, only 5 of which carry a curated headline in our small dataset;
we report it transparently while flagging that it describes this one event's timeline rather than
a generalizable news-volume relationship. H3's absorption-time statistics are simple, well-defined
interpolations on real data, not model outputs. H4's R² values come directly from the nonlinear
least-squares fits in Section 15.

## 19. Model Comparison

The logistic model outperforms the exponential model on every metric (RMSE 0.060 vs. 0.228; MAE
0.050 vs. 0.134; R² 0.58 vs. -5.04). This makes structural sense: the exponential model is
constrained to start at 0% absorption at t=0, but empirically **69%** of the eventual move was
already realized by the close of the event day itself (`absorption_fraction[0] = 0.6895`) — the
exponential's zero-intercept assumption is simply wrong for this event. The logistic model's free
horizontal-shift parameter (`t0 = -4.77`) lets it "start" its S-curve before t=0, effectively
treating day 0 as already partway up the curve, which fits much better but is still a modest fit
overall (R² = 0.58, short of our pre-registered 0.8 "approximates well" bar).

## 20. Discussion

The dominant pattern in this event is **not gradual diffusion but a near-instantaneous repricing**:
roughly seven-tenths of the ten-day cumulative reaction happened within the first single trading
session, with the remainder unfolding as a noisy, partial continuation/reversion over the following
two trading days before stabilizing. This is consistent with a market that is highly efficient with
respect to large, unambiguous, well-covered news at daily granularity — there simply is not much
"diffusion" left to model once the announcement day itself is priced in. The magnitude of the
event-day abnormal return (-23%) also vastly exceeds what the EPS surprise alone (-4.4%) or revenue
surprise (+0.8%) would suggest, supporting the widely reported narrative that guidance and the
DAU-decline signal — not the reported quarter's numbers — drove the reaction.

## 21. Limitations

(Also served live at `/api/results/limitations` and shown in the dashboard.)

1. **Single-event study** — every statistic describes this one event; it is not a validated general
   model of "how markets react to earnings."
2. **Daily, not intraday, granularity** — free, keyless intraday data is not available this far
   back, so within-day absorption dynamics (e.g. the first five minutes of after-hours trading)
   cannot be resolved.
3. **Market model, not a full risk model** — no size/value/momentum/sector factors are controlled
   for beyond the single S&P 500 factor.
4. **Small, curated news sample** — 13 real headlines, not a comprehensive news feed; H2's
   correlation is descriptive, not a powered general test.
5. **Diffusion curves are descriptive fits, not causal mechanisms** — a good fit shows the *shape*
   of the reaction is consistent with a curve, not that investors literally follow it.
6. **No forward-looking claims** — this project does not predict future prices and is not intended
   for trading use.

## 22. Threats to Validity

- **Internal validity**: the market-model estimation window (Aug 2021–Jan 2022) could itself
  contain confounding company-specific news that biases β; we mitigate this only by using a
  reasonably long (120-day) window, not by explicitly screening for confounders.
- **Construct validity**: "information absorption" is operationalized as a fraction of the
  end-of-window CAR, which depends on the arbitrary choice of a 10-day window end; a different
  window length would shift the absorption-time estimates somewhat (Section 15 documents the exact
  definition used).
- **External validity**: because this is one event for one company in one regime, none of these
  findings should be extrapolated to other companies, sectors, or market conditions without new
  data.

## 23. Future Work

- Extend the same pipeline to a small panel of comparable large-cap earnings surprises (e.g. 5–10
  events) to enable genuine cross-sectional testing of H1's "larger surprise → larger reaction"
  claim.
- If licensed intraday data becomes available, re-run the diffusion analysis at minute-level
  granularity to actually resolve within-day absorption dynamics.
- Add a size/value/momentum multi-factor model as a robustness check on the abnormal-return
  estimates.

## 24. Conclusion

For Meta Platforms' Q4 FY2021 earnings event, the market's reaction was large, statistically
significant, and overwhelmingly realized within a single trading session — a pattern more
consistent with fast semi-strong-form efficiency than with a gradual, multi-day diffusion process.
Of the two candidate diffusion curves tested, the logistic model fit better but still fell short of
a strong fit, and the exponential model fit poorly — an honest, informative negative result rather
than a forced conclusion. The earnings/revenue surprise alone cannot explain the magnitude of the
reaction; forward guidance and the first-ever DAU decline appear to have been the dominant drivers,
consistent with contemporaneous reporting.

## 25. References

- Ball, R., & Brown, P. (1968). An Empirical Evaluation of Accounting Income Numbers. *Journal of
  Accounting Research*, 6(2), 159–178.
- Bass, F. M. (1969). A New Product Growth Model for Consumer Durables. *Management Science*,
  15(5), 215–227.
- Bernard, V. L., & Thomas, J. K. (1989). Post-Earnings-Announcement Drift: Delayed Price Response
  or Risk Premium? *Journal of Accounting Research*, 27, 1–36.
- Brown, S. J., & Warner, J. B. (1985). Using Daily Stock Returns: The Case of Event Studies.
  *Journal of Financial Economics*, 14(1), 3–31.
- Fama, E. F. (1970). Efficient Capital Markets: A Review of Theory and Empirical Work. *Journal of
  Finance*, 25(2), 383–417.
- Hutto, C. J., & Gilbert, E. (2014). VADER: A Parsimonious Rule-based Model for Sentiment Analysis
  of Social Media Text. *Proceedings of the ICWSM*.
- MacKinlay, A. C. (1997). Event Studies in Economics and Finance. *Journal of Economic
  Literature*, 35(1), 13–39.
- CNBC. (2022, Feb 2). [Facebook-parent Meta (FB) Q4 2021 earnings](https://www.cnbc.com/2022/02/02/facebook-parent-meta-fb-q4-2021-earnings.html)
- CNBC. (2022, Feb 3). [Facebook stock plummets 26% in its biggest one-day drop ever](https://www.cnbc.com/2022/02/03/facebook-shares-plummet-22percent-after-reporting-weak-guidance.html)
- The Washington Post. (2022, Feb 2). [Facebook loses users for first time in history](https://www.washingtonpost.com/technology/2022/02/02/facebook-earnings-meta/)
- Bloomberg. (2022, Feb 3). [Meta (FB) Set for $200 Billion Wipeout, Among Worst in History](https://www.bloomberg.com/news/articles/2022-02-03/meta-set-for-200-billion-wipeout-among-worst-in-market-history)
- Forbes. (2022, Feb 3). [Facebook Loses Daily Active Users For The First Time](https://www.forbes.com/sites/roberthart/2022/02/03/facebook-loses-daily-active-users-for-the-first-time--heres-where-theyre-going/)
- The Motley Fool. (2022, Feb 3). [Meta Platforms (FB) Q4 2021 Earnings Call Transcript](https://www.fool.com/earnings/call-transcripts/2022/02/03/facebook-fb-q4-2021-earnings-call-transcript/)
- Wikipedia. [Meta Platforms](https://en.wikipedia.org/wiki/Meta_Platforms) (accessed 2026-09-07).

Full source list with every individual fact citation: `data/raw/earnings_facts.json` and
`data/raw/news_headlines.csv`.
