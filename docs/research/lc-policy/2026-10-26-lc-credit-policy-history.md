# LendingClub written credit policy, 2007-2018 (from SEC filings)

**Provenance:** compiled 2026-10-26 by a research subagent of the governance owner, from EDGAR (CIK 0001409970): 424B3 supplements, 8-Ks, S-3 and 10-K. Quotes were pulled from raw EDGAR HTML. Spot-checked by the owner against the 2016-06-07 8-K (verbatim match). Criteria without a source are marked UNSOURCED. No decline-boundary analysis has been done on any data (see the pre-registration).


Compiled 2026-10-26. Read-only research. All quotes were extracted from the raw EDGAR HTML (downloaded with curl, tags stripped, whitespace collapsed). Bullets are rendered as "•". Nothing below is paraphrased inside quotation marks. "UNSOURCED" means I found no filing text for it.

**How effective dates are assigned.** A date counts as an "effective date" only when the filing says "effective X" / "as of X". When a criterion first appears in a restated base prospectus and no date is given, I record "first appears in prospectus dated X". The operational effective date for those rows is UNSOURCED.

**Coverage.** I enumerated every 424B3 / POS AM / S-1 / S-3 / 424B4 filing in the EDGAR submissions index (16,717 424B3s; all but about 100 are LC self-filed posting/sales supplements of loan listings). I downloaded the 87 printer-filed prospectus documents and extracted their criteria sections. EDGAR full-text search over 2014–2019 then found that from 2015 on, credit-criteria changes were disclosed in **8-Ks incorporated by reference into the S-3 shelf**, not in 424B3s. I did not read every 10-Q, and I did not read the 2014 IPO S-1/424B4 or the 2015-06-12 S-3ASR closely. The 2015 S-3ASR's text contains no FICO/criteria language.

---

## 1. Summary table

DTI-1 = debt-to-income excluding mortgage. DTI-2 = DTI including mortgage and the requested loan. Inq = credit inquiries in last 6 months.

| # | Effective | Source filing | FICO min | DTI-1 | DTI-2 | Credit history | Inq (6 mo) | Delinq / public records / collections | Revolving util. | Other account reqs |
|---|---|---|---|---|---|---|---|---|---|---|
| V0 | inception (May 2007) – Oct 12, 2008 | 2008-10-14 424B3 (retrospective) | 640 | below 30% | not stated | UNSOURCED (none listed) | UNSOURCED (none listed) | no current delinquencies, recent bankruptcy, collections or open tax liens | UNSOURCED (none listed) | none listed |
| V1 | Oct 13, 2008 (stated in 2009-06-17 10-K wrapper) | 2008-10-14 424B3 base prospectus dated Oct 13, 2008 | 640 | below 25% | not stated | ≥12 months | ≤10 | no current delinquencies, recent bankruptcy, collections or open tax liens | ≤100% | ≥4 ever opened, ≥3 currently open |
| V2 | **Nov 25, 2008** (stated) | 2008-11-24 424B3 supplement (POS AM 1/2) | **660** | below 25% | – | 12 mo | ≤10 | as V1 | ≤100% | as V1 |
| V3 | first appears in prospectus dated Jul 30, 2009 | 2009-07-30 424B3 (POS AM 3) | 660 | below 25% | – | **≥36 months** | ≤10 | **"…tax liens or non-medical related collections opened within the last 12 months"** | ≤100% | ≥4 ever / ≥3 open |
| V4 | first appears in prospectus dated May 7, 2010 | 2010-05-07 424B3 (POS AM 5) | 660 | below 25% | – | 36 mo | **≤8** | as V3 | ≤100% | **≥3 ever / ≥2 open; revolving balance < $150,000** |
| V5 | prospectus dated Jan 6, 2011 (POS AM 9 says "effective January _____, 2011") | 2011-01-06 424B3 | 660 | **below 25%, or 30% if score ≥720** | – | 36 mo | **≤8, or ≤3 if score below 740** (detail section says "740 or less") | as V3 | ≤100% | as V4 |
| V6 | first appears in prospectus dated Apr 10, 2012 | 2012-04-10 424B3 (new S-1 333-177230) | 660 | 25% (660–719) / 30% (≥720) | – | 36 mo | as V5 | as V3 | **≤98%** | ≥2 open, <$150,000 revolving (detail section drops "ever opened"; Q&A keeps "at least three accounts ever opened") |
| V7 | **Jun 1, 2012** (stated "As of June 1, 2012") | 2012-05-31 424B3 supplement | 660 | **below 35%** | – | 36 mo | as V5 | as V3 | ≤98% | as V6 |
| V8 | first appears in prospectus dated Nov 28, 2012 (POS AM 2 "to provide revisions to the credit policy") | 2012-11-28 424B3 | 660 | below 35% | – | 36 mo | **≤6 (all scores)** | **no longer listed**; grading model "allows borrowers to have delinquencies and public records" | **no longer listed** | **≥2 revolving trade accounts** |
| V9 | disclosed in supplement dated Sep 10, 2013 (that supplement's "Effective September 10, 2013" covers its fee changes; it does not date when the DTI-2 rule began, so the rule's start date is UNSOURCED) | 2013-09-10 424B3 | 660 | below 35% | **"may not be greater than pre-determined percentage levels based on certain borrower member attributes"** (levels UNSOURCED) | 36 mo | ≤6 | as V8 | – | as V8 |
| V10 | in FY2013 10-K wrapper (424B3 filed 2014-04-03) and prospectus dated Apr 30, 2014 | 2014-04-03 424B3; 2014-05-01 424B3 | 660 | below 35% | "acceptable" (levels UNSOURCED) | 36 mo | "6 or fewer inquiries (or recently opened accounts)" | as V8 | – | ≥2 revolving accounts currently open |
| V11 | **Jul 25, 2014** (stated) | 2014-07-25 424B3 supplement | 660 | **below 40%** | acceptable | 36 mo | ≤6 (or recently opened accts) | as V8 | – | as V10 |
| V12 | **Aug 20, 2014** (stated) | 2014-08-21 424B3 supplement; restated in S-3ASR prospectus dated Aug 22, 2014 | 660 | below 40% | acceptable | 36 mo | **"5 or fewer inquiries (or recently opened accounts) in the last six months, excluding mortgage or auto loan inquiries"** | as V8 | – | as V10 |
| V13 | **as of Dec 28, 2015** (stated) | 8-K filed 2015-12-22 (Item 8.01) | 660 | below 40%; **50% direct-pay; 35% joint** (these two measured excl. mortgage *and* requested loan) | acceptable | 36 mo | ≤5 (excl. mortgages and auto loans) | as V8 | – | ≥2 revolving accounts |
| V14 | **April 2016** (month only) | 2016-10-14 8-K investor letter; FY2016 10-K | 660 | 40% | – | – | – | tightening on unnamed "populations"; thresholds UNSOURCED | – | – |
| V15 | **Jun 7, 2016** (stated) | 8-K filed 2016-06-07 | 660 | **below 35%** (excl. mortgage and requested loan) | "within an acceptable limit" | 36 mo | ≤5 (excl. mortgages and auto) | as V8 | – | ≥2 revolving accounts |
| V16 | **October 2016, January 2017** (month only) | FY2016 10-K | – | – | – | – | – | combination-of-risk-factor tightening; thresholds UNSOURCED | – | – |
| V17 | **Mar 9, 2017** (stated) | 8-K filed 2017-03-09 | 660 (primary); **540 secondary joint borrower** | below 35% | acceptable limit | 36 mo | ≤5; **secondary ≤6** | as V8 | – | ≥2 revolving accounts |
| V18 | in S-3 prospectus filed May 22, 2017 (date of change from 35% back to 40% UNSOURCED) | 2017-05-22 S-3 / S-3ASR | 660 / 540 secondary | **below 40%** | within an acceptable limit | 36 mo | ≤5 / ≤6 secondary | as V8 | – | ≥2 revolving accounts |
| – | 2018 | FY2017 & FY2018 10-Ks: generic only. 2019-08-09 S-3ASR restates V18 unchanged | no written change found for 2018 | | | | | | | |

Income verification, every version: DTI uses "the income reported by the borrower member, which is not verified unless we display an icon in the loan listing indicating otherwise" (V0 exception below). There is no written income-verification *threshold* in any version, so that criterion is UNSOURCED.

Not stated in any version I read, so UNSOURCED: maximum DTI-2 levels (V9 onward), loan-amount caps as an eligibility criterion (these are grading "guidance" amounts, not eligibility), minimum income, and employment-length requirements.

---

## 2. Verbatim criteria, by version

### V0: inception to Oct 13, 2008 (retrospective)
Source: 424B3 filed 2008-10-14, prospectus dated October 13, 2008. https://www.sec.gov/Archives/edgar/data/1409970/000095013408017934/f41480b3e424b3.htm
> "In addition, from our inception until the date of this prospectus, our credit criteria and loan grading criteria differed from the credit criteria and loan grading criteria described elsewhere in this prospectus. During this period, under our minimum borrower member criteria, our prospective borrower members needed to have: • a minimum FICO score of 640 (as reported by a consumer reporting agency); • a debt-to-income ratio (excluding mortgage) below 30%, as calculated by Lending Club based on (i) the borrower member's debt reported by a consumer reporting agency; and (ii) the income reported by the borrower member, which we verified for approximately 25% of loan requests that proceeded past the initial credit check stage and were posted on the website; and • a credit profile (as reported by a consumer reporting agency) without any current delinquencies, recent bankruptcy, collections or open tax liens."

The transition is dated in the FY2009 10-K wrapped as 424B3 filed 2009-06-17 (https://www.sec.gov/Archives/edgar/data/1409970/000095012309014517/c86931e424b3.htm):
> "Effective October 13, 2008, we changed our minimum borrower member criteria to the criteria reflected elsewhere in this document, except that the minimum FICO score remained 640." / "Effective November 25, 2008, we raised the minimum FICO score to 660."

### V1: Oct 13, 2008 base prospectus
Source: same 2008-10-14 424B3. Detailed section ("Minimum Credit Criteria and Underwriting"):
> "Under the credit policy, prospective borrower members must have: • a minimum FICO score of 640 (as reported by a consumer reporting agency); • a debt-to-income ratio (excluding mortgage) below 25%, as calculated by Lending Club based on (i) the debt (excluding mortgage) reported by a consumer reporting agency; and (ii) the income reported by the borrower member, which is not verified unless we display an icon in the loan listing indicating otherwise; and • a credit profile (as reported by a consumer reporting agency) without any current delinquencies, recent bankruptcy, collections or open tax liens and reflecting: • at least four accounts ever opened; • at least three accounts currently open; • no more than 10 credit inquiries in the past six months; • utilization of credit limit not exceeding 100%; and • a minimum credit history of 12 months."

Definitions, same filing, carried essentially unchanged through 2012:
> "“debt-to-income ratio” means the borrower's aggregate monthly payment in respect of debt obligations appearing on the borrower's credit report, other than those secured by real estate, divided by the borrower's monthly income, as reported by the borrower;" … "“current delinquency” means a payment obligation of the borrower appearing on the borrower's credit report that is 30 or more days late at the time the borrower applies for a member loan on the Lending Club platform;" … "“recent bankruptcy” means a bankruptcy, as indicated by a credit report, that occurred less than seven years before the date the borrower applies for a member loan on the Lending Club platform;" … "“utilization of credit limit” means the ratio obtained by dividing the outstanding indebtedness of a borrower by the total indebtedness authorized under all of the borrower's open credit lines, as reported on the borrower's credit report." … "“credit history” means the time elapsed since the borrower first opened a credit account, as reported on the borrower's credit report."

The same filing defines the score: "A FICO score is a numeric rating that ranges between 300 and 850…" and "We currently obtain consumer credit information from a single consumer reporting agency".

### V2: FICO 660, effective Nov 25, 2008
Source: 424B3 supplement filed 2008-11-24 (https://www.sec.gov/Archives/edgar/data/1409970/000095013408021116/f50667b3e424b3.htm); also POS AM No. 1 filed 2008-11-20 (https://www.sec.gov/Archives/edgar/data/1409970/000095013408020994/f50667a1posam.htm).
> "A. Minimum Borrower Member FICO Score Increased to 660 Effective November 25, 2008, the minimum FICO score that prospective borrower members are required to have will be raised from 640 to 660."

The POS AM adds: "for member loans initially posted on or after November 25, 2008".

### V3: prospectus dated July 30, 2009
Source: https://www.sec.gov/Archives/edgar/data/1409970/000095012309027114/f53045b3e424b3.htm
> "Under the current credit policy, prospective borrower members must have: • a minimum FICO score of 660 (as reported by a consumer reporting agency); • a debt-to-income ratio (excluding mortgage) below 25%, as calculated by LendingClub based on (i) the debt (excluding mortgage) reported by a consumer reporting agency; and (ii) the income reported by the borrower member, which is not verified unless we display an icon in the loan listing indicating otherwise; and • a credit profile (as reported by a consumer reporting agency) without any current delinquencies, recent bankruptcy, tax liens or non-medical related collections opened within the last 12 months, and reflecting: • at least four accounts ever opened; • at least three accounts currently open; • no more than 10 credit inquiries in the past six months; • utilization of credit limit not exceeding 100%; and • a minimum credit history of 36 months."

### V4: prospectus dated May 7, 2010
Source: https://www.sec.gov/Archives/edgar/data/1409970/000095012310045706/c00530e424b3.htm
> "• a credit profile (as reported by a consumer reporting agency) without any current delinquencies, recent bankruptcy, tax liens or non-medical related collections opened within the last 12 months, and reflecting: • at least three accounts ever opened; • at least two accounts currently open; • no more than 8 credit inquiries in the past six months; • a revolving credit balance of less than $150,000; • utilization of credit limit not exceeding 100%; and • a minimum credit history of 36 months."

FICO 660 and DTI-1 "below 25%" are unchanged. Side note: POS AM No. 9 filed 2010-10-27 (https://www.sec.gov/Archives/edgar/data/1409970/000095012310096204/c07243posam.htm) adds criteria for *secured* loans only: "• a minimum FICO score of 714; • No less than 3 and no more than 15 currently opened accounts; • No delinquencies in the last 12 months; and • No charge-offs in the last 36 months."

### V5: prospectus dated January 6, 2011
Source: https://www.sec.gov/Archives/edgar/data/1409970/000095012311001009/c10659e424b3.htm. Purpose statement in POS AM filed 2011-01-04 (https://www.sec.gov/Archives/edgar/data/1409970/000095012311000301/c10458posam.htm): "to reflect, effective January _____, 2011, the changes set forth below: … • Automatically deny applications with the following characteristics: • FICO score of < 740 and more than three (3) credit inquires in the prior six (6) months. All other borrowers would be allowed eight (8) or fewer inquiries in the prior six (6) months. … • For borrowers with a credit score equal to or greater than 720 increase DTI-1 to 30% from 25%."

Q&A summary:
> "• a debt-to-income ratio (excluding mortgage) below 25% (or 30% if the borrower's credit score is 720 or higher) … no more than 8 credit inquiries in the past six months, or no more than 3 credit inquiries if their credit score is below 740, utilization of credit limit not exceeding 100%, revolving credit balance of less than $150,000 and a minimum credit history of 36 months."

Detailed section, whose wording differs at the boundary:
> "• a debt-to-income ratio below 25%, or 30% for borrowers with credit scores of 720 or more … • no more than 8 credit inquiries in the past six months, or no more than 3 credit inquiries for borrowers with credit scores of 740 or less;"

### V6: prospectus dated April 10, 2012
Source: https://www.sec.gov/Archives/edgar/data/1409970/000119312512156944/d306143d424b3.htm
> "Under the current credit policy, prospective borrower members must have among other elements: • a minimum FICO score of 660 (as reported by a consumer reporting agency); • for borrowers with a credit score between 660-719, they will need a debt-to-income ratio (excluding mortgage) below 25%; for borrowers with a credit score of 720 or higher, they will need a debt-to-income ratio (excluding mortgage) below 30%; • a credit report (as reported by a consumer reporting agency) without any current delinquencies, recent bankruptcy, tax liens or non-medical related collections opened within the last 12 months, and reflecting: • at least two accounts currently open; • for credit credits 740 and higher, no more than 8 credit inquiries on the credit report in the past six months and for credit scores below 740, no more than 3 inquiries on the credit report in the past six months; • a revolving credit balance of less than $150,000; • utilization of credit limit not exceeding 98%; and • a minimum credit history of 36 months."

"among other elements" first appears here. It is an explicit statement that the list is not exhaustive.

### V7: DTI-1 35%, as of June 1, 2012
Source: 424B3 filed 2012-05-31. https://www.sec.gov/Archives/edgar/data/1409970/000119312512255710/d361695d424b3.htm
> "As of June 1, 2012, the following references (and any other similar reference in the prospectus): Page 8 “a debt-to-income ratio (excluding mortgage) below 25% (or 30% if the borrower's credit score is 720 or higher)” … are amended to read as follows: “…a debt-to-income ratio (excluding mortgage) below 35%...”"

Restated in the prospectus dated July 31, 2012 (https://www.sec.gov/Archives/edgar/data/1409970/000119312512325943/d353028d424b3.htm): "• a debt-to-income ratio (excluding mortgage) below 35%;". The other V6 elements are unchanged.

### V8: prospectus dated November 28, 2012 ("revisions to the credit policy")
Source: https://www.sec.gov/Archives/edgar/data/1409970/000119312512483918/d445714d424b3.htm (POS AM: https://www.sec.gov/Archives/edgar/data/1409970/000119312512468147/d432052dposam.htm)
> "Under the current credit policy, prospective borrower members must have among other elements: • a minimum FICO score of 660 (as reported by a consumer reporting agency); • a debt-to-income ratio (excluding mortgage) below 35%; • minimum credit history of 36 months; • 6 or less inquiries in the last 6 months; and • at least 2 revolving trade accounts"

Same filing:
> "• our proprietary scoring model which takes into account many of the attributes previously used by us and also allows borrowers to have delinquencies and public records;"

The prospectus dated April 30, 2013 (https://www.sec.gov/Archives/edgar/data/1409970/000119312513187963/d523128d424b3.htm) is unchanged on criteria.

### V9: DTI including mortgage, disclosed Sept 10, 2013
Source: https://www.sec.gov/Archives/edgar/data/1409970/000119312513362879/d596018d424b3.htm
> "2. Throughout the Prospectus the Company refers to certain minimum requirements required of a borrower member. One such requirement is that a borrower member must have a debt-to-income ratio (excluding mortgage) that is less than 35%. In addition to this requirement, the credit policy requires that a borrower member's debt-to-income-ratio that includes their mortgage (if any) and the requested loan through the platform may not be greater than pre-determined percentage levels based on certain borrower member attributes."

The "pre-determined percentage levels" are never published, so they are UNSOURCED.

### V10: FY2013 10-K wrapper (424B3 filed 2014-04-03) / prospectus dated April 30, 2014
Sources: https://www.sec.gov/Archives/edgar/data/1409970/000119312514128328/d703491d424b3.htm ; https://www.sec.gov/Archives/edgar/data/1409970/000119312514173269/d719822d424b3.htm
> "Under the current Public Credit Policy, borrower requirements include the following: • minimum FICO score of 660 (as reported by a consumer reporting agency); • debt-to-income ratio (excluding mortgage) below 35%; • acceptable debt-to-income ratio (including mortgage and the requested Public Policy Loan amount); and • credit report (as reported by a consumer reporting agency) reflecting: • at least two revolving accounts currently open; • 6 or fewer inquiries (or recently opened accounts) in the last 6 months; and • a minimum credit history of 36 months."

### V11: DTI-1 40%, effective July 25, 2014
Source: https://www.sec.gov/Archives/edgar/data/1409970/000119312514280480/d762161d424b3.htm
> "Effective July 25, 2014, one element of the minimum credit criteria has been modified. 1. All references to a “debt-to-income ratio (excluding mortgage) below 35%,” or any such similar reference, is now replaced with the following or a similar reference as the context requires to replace 35% with 40%: “debt-to-income ratio (excluding mortgage) below 40%”"

### V12: inquiries 5, effective August 20, 2014
Source: https://www.sec.gov/Archives/edgar/data/1409970/000119312514316001/d778113d424b3.htm
> "Effective August 20, 2014, one element of the minimum credit criteria has been modified. 1. All references to a “6 or fewer inquiries (or recently opened accounts) in the last six months,” or any such similar reference is now replaced with the following or a similar reference as the context requires: “5 or fewer inquiries (or recently opened accounts) in the last six months, excluding mortgage or auto loan inquiries”"

Restated in the S-3ASR prospectus (filed 2014-08-25, dated Aug 22, 2014; https://www.sec.gov/Archives/edgar/data/1409970/000119312514319072/d775378ds3asr.htm): "• minimum FICO score of 660 (as reported by a consumer reporting agency); • debt-to-income ratio (excluding mortgage) below 40%; • acceptable debt-to-income ratio (including mortgage and the requested Standard Program Loan amount); and • credit report (as reported by a consumer reporting agency) reflecting: • at least two revolving accounts currently open; • 5 or fewer inquiries (or recently opened accounts) in the last 6 months; and • a minimum credit history of 36 months." This restatement omits the mortgage/auto exclusion.

### V13: as of December 28, 2015
Source: 8-K filed 2015-12-22, Item 8.01. https://www.sec.gov/Archives/edgar/data/1409970/000140997015001494/form8-kfiledon122215credit.htm
> "As of December 28, 2015, the minimum credit criteria for borrowers to obtain a standard program loan include: • minimum FICO score of 660 (as reported by a consumer reporting agency); • debt-to-income ratio (excluding mortgage) of below 40%, except in the following circumstances where the debt-to-income ratio (excluding mortgage and the requested standard program loan amount) must be below: ◦ 50% in the case of the direct pay program (described below); and ◦ 35% in the case of joint application loans (described below) if joint income is considered • acceptable debt-to-income ratio (including mortgage and the requested standard program loan amount); and • credit report (as reported by a consumer reporting agency) reflecting: ◦ at least two revolving accounts; ◦ 5 or fewer inquiries in the last 6 months (excluding mortgages and auto loans); and ◦ a minimum credit history of 36 months"

### V14 / V16: unquantified tightenings (April 2016, October 2016, January 2017)
Source: 8-K investor letter filed 2016-10-14 (https://www.sec.gov/Archives/edgar/data/1409970/000140997016002805/investorletter101416.htm):
> "The credit policy was tightened in April 2016 to remove populations primarily characterized by borrowers with high indebtedness, an increased propensity to accumulate debt, and lower credit scores. In June, the maximum debt-to-income (DTI) threshold (excluding mortgage and the requested program loan amount) across the prime loan program was further reduced to 35% (from 40%)."

FY2016 10-K (https://www.sec.gov/Archives/edgar/data/1409970/000140997017000255/a201610-k.htm):
> "These changes included implementing changes to tighten credit criteria based on a unique combination of risk factors, such as number of recent installment loans, revolving utilization, and higher risk scores on our proprietary scorecard. The actions taken in April, June and October 2016 eliminated approximately 11% of total loan volume on an annualized basis from specific risk segments that would have otherwise been approved. Additional action taken in January 2017 eliminated approximately 5% of total loan volume on an annualized basis."

The thresholds for the April 2016, October 2016 and January 2017 actions are UNSOURCED.

### V15: effective June 7, 2016
Source: 8-K filed 2016-06-07. https://www.sec.gov/Archives/edgar/data/1409970/000140997016002239/form8-kon6716interestrate.htm
> "Effective June 7, 2016, debt to income (DTI) criteria (excluding mortgage and the requested program loan amount) is being reduced to 35% (from 40%) across the standard loan program. … Effective June 7, 2016, the minimum credit criteria for borrowers to obtain a standard program loan include: • minimum FICO score of 660 (as reported by a consumer reporting agency); • debt-to-income ratio (excluding mortgage and the requested program loan amount) of below 35%; • debt-to-income ratio (including mortgage and the requested standard program loan amount) within an acceptable limit; and • credit report (as reported by a consumer reporting agency) reflecting: ◦ at least two revolving accounts; ◦ 5 or fewer inquiries in the last 6 months (excluding mortgages and auto loans); and ◦ a minimum credit history of 36 months."

### V17: effective March 9, 2017 (joint applications)
Source: 8-K filed 2017-03-09. https://www.sec.gov/Archives/edgar/data/1409970/000140997017000295/form8-kfiledon3917.htm
> "To be approved for an individual standard program loan on the platform, the borrower applicant must continue to satisfy the following minimum credit criteria for standard program loans: • minimum FICO score of 660 (as reported by a consumer reporting agency); • debt-to-income ratio (excluding mortgage and the requested program loan amount) of below 35%; … Additionally, effective March 9, 2017, … the secondary borrower must now also satisfy additional credit criteria, including a minimum FICO score of 540 and 6 or fewer inquiries in the last 6 months (excluding mortgages and auto loans)."

### V18: S-3 filed May 22, 2017 (DTI-1 back to 40%)
Source: https://www.sec.gov/Archives/edgar/data/1409970/000140997017000632/forms-3filedon52217.htm
> "To be approved for an individual Standard Program Loan, the borrower applicant must satisfy at least the following minimum credit criteria: • minimum FICO score of 660 (as reported by a consumer reporting agency); • debt-to-income ratio (excluding mortgage and the requested program loan amount) of below 40%; • debt-to-income ratio (including mortgage and the requested standard program loan amount) within an acceptable limit; and • credit report (as reported by a consumer reporting agency) reflecting: • at least two revolving accounts • five or fewer credit inquiries in the last 6 months (excluding mortgages and auto loans); and • a minimum credit history of 36 months."

Same filing: "WebBank operates a variety of credit policies through our platform, most of which create loans that are not publically available."

**Gap:** I found no filing that dates the 35%→40% reversion. It happened between 2017-03-09 (35%) and 2017-05-22 (40%). Full-text searches for "40%" + "debt-to-income" + "standard program" from 2017-03-10 to 2019-01 return only this S-3 and the FY2017 10-K. The FY2017 10-K uses generic wording only: "a FICO score of at least 660, satisfactory debt-to-income ratios, 36 months of credit history and a limited number of credit inquiries in the previous six months". The reversion date is therefore UNSOURCED.

### 2018
The FY2017 10-K (https://www.sec.gov/Archives/edgar/data/1409970/000140997018000231/a201710-k.htm) and FY2018 10-K (https://www.sec.gov/Archives/edgar/data/1409970/000140997019000222/a201810-k.htm) give only the generic sentence above. The next notes prospectus, the S-3ASR filed 2019-08-09 (https://www.sec.gov/Archives/edgar/data/1409970/000140997019000988/forms-3asrfiledon8919.htm), restates V18: "• debt-to-income ratio (excluding mortgage and the requested loan amount) of below 40%". I found no written criteria change dated in 2018.

---

## 3. Public rejects file: descriptive profile only (no model, no boundary analysis)

File: `/home/tony/projects/governance/data/rejected_2007_to_2018Q4.csv`, 1.78 GB. 27,648,741 data rows. Columns as given. No missing Application Date. Earliest date 2007-05-26.

| Year | Rows | Risk_Score missing | % missing | Risk_Score min–max (non-missing) | Risk_Score == 0 | Risk_Score > 850 |
|---|---|---|---|---|---|---|
| 2007 | 5,274 | 104 | 1.97 | 0–811 | 223 | 0 |
| 2008 | 25,596 | 2,506 | 9.79 | 0–821 | 1,028 | 0 |
| 2009 | 56,991 | 6,226 | 10.92 | 0–828 | 3,324 | 0 |
| 2010 | 112,561 | 7,977 | 7.09 | 0–849 | 9,525 | 0 |
| 2011 | 217,792 | 2,778 | 1.28 | 0–832 | 19,655 | 0 |
| 2012 | 337,277 | 4,338 | 1.29 | 0–850 | 18,759 | 0 |
| 2013 | 760,942 | 23,822 | 3.13 | 0–990 | 34,240 | 578 |
| 2014 | 1,933,700 | 254,523 | 13.16 | 300–990 | 0 | 5,537 |
| 2015 | 2,859,379 | 2,348,928 | 82.15 | 300–990 | 0 | 1,454 |
| 2016 | 4,769,874 | 3,751,577 | 78.65 | 300–990 | 0 | 3,412 |
| 2017 | 7,072,573 | 3,246,249 | 45.90 | 300–990 | 0 | 15,802 |
| 2018 | 9,496,782 | 8,848,602 | 93.17 | 300–990 | 0 | 2,218 |
| **All** | **27,648,741** | **18,497,630** | **66.90** | | | |

**DTI format.** DTI is a string with a percent sign. There are no blanks. Patterns: `N.N%` (e.g. "38.64%") 23,459,590 rows; integer `N%` (e.g. "10%") 2,986,088; negative `-N%` (e.g. "-1%") 1,203,063. Negative values by year: 2008 1,789; 2009 4,399; 2010 3,597; 2011 5,822; 2012 4,226; 2013 12,073; 2014 233,500; 2015 230,819; 2016 297,766; 2017 343,193; 2018 65,879. I found no source documenting "-1%". Its meaning (most likely a missing or zero-income sentinel) is UNSOURCED. The secondary dictionary below defines DTI as excluding mortgage *and the requested LC loan*. That matches the 2015+ written criterion (DTI-1), not the pre-2015 "excluding mortgage" wording.

**Policy Code.** Values present: "0.0" 27,559,694; "2.0" 88,129 (first appears 2014: 6,241 rows in 2014, 9,207 in 2015, 15,256 in 2016, 17,727 in 2017, 39,698 in 2018); blank 918 (all 2017). There is **no "1"**. The secondary dictionary says "publicly available policy_code=1 / new products not publicly available policy_code=2". So the file's "0" does not match the dictionary. Whether 0 means "public/standard program" is UNSOURCED.

**Risk_Score definition change (FICO to Vantage).** A secondary source reproduces the RejectStats dictionary entry, dated 2017-04-11 and with no LendingClub citation (https://luke.lol/blog/uncategorized/lending-club-folio-investing-note-rejection-definitions/):
> "For applications prior to November 5, 2013 the risk score is the borrower's FICO score." / "For applications after November 5, 2013 the risk score is the borrower's Vantage score."

I could not retrieve LendingClub's own LCDataDictionary.xlsx to confirm this. The data agrees with it. Through 2013-11-05 the non-missing max per day is ≤850 and no value exceeds 850. The first values above 850 appear on 2013-11-06 (5 rows, daily max 980), and the annual max is 990 from 2013 on. 501–990 is the VantageScore 1.0/2.0 scale; that fact is not from a filing. Also, value 0 appears only through 2013, and the minimum is 300 from 2014. On 2013-11-06 non-missing scores drop to 452 of 2,899 rows. **Implication:** Risk_Score is not one scale across the file, and the written FICO 660 floor cannot be applied directly to post-2013-11-05 rows. I did not do any boundary analysis.

---

## 4. Caveats
1. From 2012-04 on, the prospectus lists are qualified "among other elements" / "at least the following". The written criteria are stated as a floor, not the whole policy. From 2014 on, LC also says WebBank runs other, non-public credit policies (custom program).
2. In several versions the Q&A summary and the detailed section word the same rule differently: V5 "below 740" vs "740 or less"; V6 "accounts ever opened" kept vs dropped. Both are quoted above.
3. The pre-Nov-2008 "Effective October 13, 2008" date comes from a 10-K wrapper, not a 424B3 supplement.
4. V3, V4, V6 and V8 are dated by prospectus date only.
