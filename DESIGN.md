# LongForm FS — Web App Design

## Overview

A web application that mirrors the Massachusetts Probate & Family Court Financial Statement (Long Form, CJ-D 301 L) as an editable, persistent web form. Data is saved to a local SQLite database. PDF extraction (auto-populating fields from uploaded financial documents) is a later phase.

---

## Rendering Modes

Every section has three rendering modes:

| Mode | Editable | Description |
|---|---|---|
| **Entry form** | Yes | User-friendly input. Split fields where needed. Computed fields shown read-only. |
| **Read-only view** | No | Exact replica of the court form with Roman numeral section numbers and alphabetic line item labels. |
| **PDF export** | No | Identical to read-only view, generated as a new PDF document (not filling the original court PDF). |

Read-only view and PDF share one template. CERTIFICATION BY AFFIANT and STATEMENT BY ATTORNEY appear in the PDF only — static boilerplate, no data stored.

---

## Computed Fields

Computed in the browser in real time. Never stored. Shown in **both** entry and view/PDF as read-only.

| Computed Field | Formula |
|---|---|
| Total Gross Weekly Income | Sum of all `income` rows + sum of `income_other` rows |
| Total Weekly Deductions | Sum of all `deductions` rows + sum of `deductions_other` rows |
| **Net Weekly Income** | Total Gross Weekly Income − Total Weekly Deductions |
| Total Weekly Expenses | Sum of all `expenses` rows + `expenses_other` + `expenses_additional` rows + `expenses_additional_other` rows |
| Real estate equity (per row) | FMV − mortgage_1 − mortgage_2 |
| Vehicle equity (per row) | FMV − outstanding_loan |
| Total Assets | Sum of all account balances + real estate equities + vehicle equities + pension balances + other asset values + assets_additional balances |
| Total Liabilities | Sum of `amount_due` across all liabilities |
| Total Weekly Liability Payments | Sum of `weekly_payment` across all liabilities |

---

## Numbering in Read-only / PDF

- Sections: Roman numerals — `I.`, `II.`, `III.`, `VI.`, `VII.`, `VIII.`, `IX.`
- Line items: alphabetic — `a)`, `b)` ... `r)`, `s)` etc.
- Split fields (e.g. salary + wages + commissions + bonuses) roll up to one lettered line in the view with their combined total. Sub-fields are not individually lettered.
- Dynamic "other" rows appear between the last lettered item and the section total, listed without a letter, in `sort_order` sequence.

---

## Data Model

### Conventions applying to all tables

- Every table has `FOOTNOTE` (TEXT) and `NOTE` (TEXT) columns.
- Single-row tables use `FIELD_NAME` / `VALUE` pairs with hard-coded field names.
- Multi-row tables have one row per entity (account, vehicle, etc.).
- Computed fields are never stored.

---

### `personal_info` — Section I
Single-row table. One row per field.

| FIELD_NAME | Notes |
|---|---|
| `name` | Labeled "Plaintiff / Petitioner" in view/PDF |
| `defendant` | |
| `address_street` | |
| `address_city` | |
| `address_state` | |
| `address_zip` | |
| `tel` | |
| `ssn_last4` | |
| `dob` | |
| `children_count` | |
| `occupation` | |
| `employer` | |
| `employer_address` | |
| `employer_tel` | |
| `health_insurance` | `yes` / `no` |
| `health_provider` | |
| `case_division` | View/PDF only — not shown in entry form |
| `case_docket` | View/PDF only — not shown in entry form |

**Columns:** `FIELD_NAME`, `VALUE`, `FOOTNOTE`, `NOTE`

---

### `income` — Section II
Single-row table. One row per field.

| FIELD_NAME | Form label | Entry form |
|---|---|---|
| `salary` | a) Base pay — Salary | Separate input |
| `wages` | a) Base pay — Wages | Separate input |
| `commissions` | a) Commissions | Separate input |
| `bonuses` | a) Bonuses | Separate input |
| `overtime` | b) Overtime | |
| `part_time` | c) Part-time job | |
| `self_employment` | d) Self-employment | |
| `tips` | e) Tips | |
| `dividends` | f) Dividends | |
| `interest` | g) Interest | |
| `trusts` | h) Trusts | |
| `annuities` | i) Annuities | |
| `pensions` | j) Pensions | |
| `retirement_funds_1` | k) Retirement Funds — sub-field 1 | Separate input |
| `retirement_funds_2` | k) Retirement Funds — sub-field 2 | Separate input |
| `public_assistance` | l) Public Assistance | |
| `disability_1` | m) Disability — sub-field 1 | Separate input |
| `disability_2` | m) Disability — sub-field 2 | Separate input |
| `unemployment` | n) Unemployment insurance | |
| `workers_comp` | o) Worker's compensation | |
| `child_support_received` | p) Child Support | |
| `alimony_received` | q) Alimony (actually received) | |
| `royalties` | Royalties and other rights | |
| `rsu` | Restricted Stock Units | |
| `additional_schedule_total` | Total from attached additional schedule | |

**Columns:** `FIELD_NAME`, `VALUE`, `FOOTNOTE`, `NOTE`

**View/PDF:** `salary + wages + commissions + bonuses` summed and shown as `a)`. `retirement_funds_1 + retirement_funds_2` shown as `k)`. `disability_1 + disability_2` shown as `m)`.

**`r) Total Gross Weekly Income`** — computed, read-only, shown in both entry and view/PDF.

---

### `income_other`
Dynamic "other" rows for Section II. User can add/remove rows.

| Column | Type |
|---|---|
| `id` | INTEGER PK |
| `label` | TEXT |
| `amount` | REAL |
| `sort_order` | INTEGER |
| `footnote` | TEXT |
| `note` | TEXT |

Listed without a letter in view/PDF, between `q)` and `r) Total`.

---

### `deductions` — Section III
Single-row table. Same pattern as `income`.

| FIELD_NAME | Form label |
|---|---|
| `federal_tax` | a) Federal tax withholding / estimated payments |
| `state_tax` | b) State tax withholding / estimated payments |
| `fica` | c) F.I.C.A. |
| `medicare` | d) Medicare |
| `medical_insurance` | e) Medical Insurance |
| `dental_insurance` | f) Dental Insurance |
| `vision_insurance` | g) Vision Insurance |
| `life_insurance` | h) Life Insurance |
| `hsa` | i) Health Savings Account |
| `retirement` | j) Retirement |
| `union_dues` | k) Union Dues |
| `spousal_support` | l) Spousal Support |
| `child_support_paid` | m) Child Support |
| `credit_union_savings` | n) Credit Union (Savings) |
| `credit_union_loan` | o) Credit Union (Loan) |
| `deferred_comp` | p) Deferred Compensation |
| `savings` | q) Savings |
| `charitable` | r) Charitable Contributions |
| `ma_pfl` | MA Paid Family & Medical Leave |
| `federal_allowances` | Federal withholding allowances claimed |
| `state_allowances` | State withholding allowances claimed |
| `prior_year_gross` | Gross Income from Prior Year |
| `years_social_security` | Number of years paid into Social Security |

**Columns:** `FIELD_NAME`, `VALUE`, `FOOTNOTE`, `NOTE`

**`s) Total Weekly Deductions`** — computed, read-only, shown in both entry and view/PDF.

---

### `deductions_other`
Dynamic "other" rows for Section III. Identical structure to `income_other`.
Listed without a letter in view/PDF, between the last lettered item and `s) Total`.

---

### Net Weekly Income — Section IV
No table. Computed only. Shown in both entry (read-only) and view/PDF.

---

### `expenses` — Section VI
Single-row table. Same pattern as `income`.

| FIELD_NAME | Form label |
|---|---|
| `rent` | Rent |
| `mortgage` | Mortgage (Principal, Interest — Taxes & Insurance) |
| `condo_fees` | Condominium Fees |
| `homeowner_insurance` | Homeowner / Tenant Insurance |
| `maintenance` | Maintenance Fees |
| `electricity` | Electricity |
| `propane` | Propane |
| `natural_gas` | Natural Gas |
| `cable` | Cable TV / Internet |
| `water` | Water |
| `sewer` | Sewer |
| `heat` | Heat |
| `food` | Food & Restaurants |
| `clothing` | Clothing |
| `laundry` | Laundry |
| `dry_cleaning` | Dry Cleaning |
| `house_supplies` | House Supplies |
| `uninsured_medical` | Uninsured Medical |
| `uninsured_dental` | Uninsured Dental |
| `medical_insurance` | Medical Insurance |
| `dental_insurance` | Dental Insurance |
| `vision_insurance` | Vision Insurance |
| `life_insurance` | Life Insurance |
| `vehicle_expenses` | Motor Vehicle Expenses |
| `fuel` | Fuel |
| `vehicle_insurance` | Vehicle Insurance |
| `vehicle_loan` | Vehicle Loan payment(s) |
| `vehicle_maintenance` | Vehicle Maintenance Fees |
| `property_taxes` | Property taxes and assessments |
| `entertainment` | Entertainment |
| `daycare` | Child(ren)'s Day Care Expense |
| `child_support` | Child Support |
| `children_education` | Child(ren)'s Education |
| `vacation` | Vacation |
| `cell_phone` | Cell Phone |
| `education_self` | Education (self) |
| `lottery` | Lottery Tickets |
| `uniforms` | Uniforms |
| `travel` | Travel |
| `continuing_education` | Required continuing education |
| `employment_expenses` | Employment related expenses (unreimbursed) |

**Columns:** `FIELD_NAME`, `VALUE`, `FOOTNOTE`, `NOTE`

**Deferred (revisit later):** "Total Weekly Payment for Liabilities from Page 8" and "Total Weekly Expenses from Attached Additional Schedule."

---

### `expenses_other`
Dynamic "other" rows for Section VI. Identical structure to `income_other`.

---

### `expenses_additional` — Additional Weekly Expenses (page 11)
Separate single-row table. Same `FIELD_NAME` / `VALUE` pattern as `expenses`.

| FIELD_NAME | Form label |
|---|---|
| `transportation` | Other Transportation: Tolls, Parking, Public Trans, Taxis |
| `personal_care` | Personal Care: Hair, Toiletries, Sports/Hobbies |
| `gifts` | Gifts |
| `wife_water` | Wife's Water (Town of Chelmsford) |
| `child_allowance` | Child's Allowance |
| `child_extracurricular` | Child's Extracurricular Activities |
| `child_entertainment` | Child's Miscellaneous / Entertainment |
| `child_vacation` | Child's Vacation |
| `wife_homeowner_insurance` | Wife's Home Owner's Insurance |
| `wife_cable` | Wife's Cable TV / Internet |
| `child_transportation` | Child's Transportation |
| `child_education` | Child's Education: Supplies, Transportation, Coaching |
| `house_cleaning` | House Cleaning |
| `college_savings` | Child's College Savings |
| `wife_mortgage` | Wife's Mortgage |
| `wife_real_estate_taxes` | Wife's Real Estate Taxes |
| `wife_condo_fee` | Wife's Condo Fee |
| `child_clothing` | Child's Clothing |
| `legal_accounting` | Legal & Accounting Fees |
| `subscriptions` | Subscriptions / Books / Software |
| `child_medical` | Child's Out-of-Pocket Medical |
| `wife_electric` | Wife's Electric |

**Columns:** `FIELD_NAME`, `VALUE`, `FOOTNOTE`, `NOTE`

---

### `expenses_additional_other`
Dynamic "other" rows for the additional expenses section. Identical structure to `income_other`.

---

### `counsel_fees` — Section VII
Single-row table. Same `FIELD_NAME` / `VALUE` pattern.

| FIELD_NAME | Form label |
|---|---|
| `retainer_paid` | Retainer amount(s) paid to your attorney(s) |
| `fees_incurred` | Legal fees incurred to date against retainer(s) |
| `anticipated_from` | Anticipated total legal expense (from $) |
| `anticipated_to` | Anticipated total legal expense (to $) |

**Columns:** `FIELD_NAME`, `VALUE`, `FOOTNOTE`, `NOTE`

---

### `real_estate` — Section VIII A/B
Multi-row table. One row per property.

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | |
| `property_type` | TEXT | `primary` / `vacation` |
| `address_street` | TEXT | |
| `address_city` | TEXT | |
| `address_state` | TEXT | |
| `title_holder` | TEXT | |
| `purchase_price` | REAL | |
| `purchase_year` | TEXT | |
| `assessed_value` | REAL | |
| `assessment_date` | TEXT | |
| `fair_market_value` | REAL | |
| `mortgage_1` | REAL | Outstanding 1st mortgage |
| `mortgage_2` | REAL | Outstanding 2nd mortgage / home equity loan |
| `footnote` | TEXT | |
| `note` | TEXT | |

**Equity** = FMV − mortgage_1 − mortgage_2 — computed, shown in both entry (read-only) and view/PDF.

---

### `vehicles` — Section VIII
Multi-row table. One row per vehicle.

| Column | Type |
|---|---|
| `id` | INTEGER PK |
| `vehicle_type` | TEXT |
| `make` | TEXT |
| `model` | TEXT |
| `purchase_year` | TEXT |
| `fair_market_value` | REAL |
| `purchase_price` | REAL |
| `outstanding_loan` | REAL |
| `footnote` | TEXT |
| `note` | TEXT |

**Equity** = FMV − outstanding_loan — computed, shown in both entry (read-only) and view/PDF.

---

### `pensions` — Section VIII C
Multi-row table. One row per plan.

| Column | Type |
|---|---|
| `id` | INTEGER PK |
| `plan_type` | TEXT — `defined_contribution` / `defined_benefit` |
| `plan_name` | TEXT |
| `institution` | TEXT |
| `account_number` | TEXT |
| `beneficiary` | TEXT |
| `balance` | REAL |
| `outstanding_loan` | REAL |
| `as_of_date` | TEXT |
| `footnote` | TEXT |
| `note` | TEXT |

---

### `accounts` — Section VIII D
Multi-row table. One row per financial account.

| Column | Type |
|---|---|
| `id` | INTEGER PK |
| `account_type` | TEXT — see type list below |
| `institution` | TEXT |
| `account_number` | TEXT |
| `beneficiary` | TEXT |
| `balance` | REAL |
| `as_of_date` | TEXT |
| `footnote` | TEXT |
| `note` | TEXT |

**`account_type` values:** `savings`, `checking`, `money_market`, `cd`, `credit_union`, `investment`, `stocks`, `ira`, `roth_ira`, `hsa`, `hsa_investment`, `529_education`, `retirement_other`, `deferred_comp`, `life_insurance`, `annuity`, `us_savings_bond`, `profit_sharing`, `reit`, `crypto`, `custodial`, `legacy`, `other`

---

### `other_assets` — Section VIII D (tangible)
Multi-row table. One row per asset.

| Column | Type |
|---|---|
| `id` | INTEGER PK |
| `asset_type` | TEXT — `jewelry`, `home_furnishings`, `collections`, `firearms`, `tools`, `crops`, `judgments`, `other` |
| `description` | TEXT |
| `value` | REAL |
| `footnote` | TEXT |
| `note` | TEXT |

---

### `assets_additional` — Additional Assets (page 10)
Separate multi-row table. Same structure as `accounts`. One row per additional financial account.

| Column | Type |
|---|---|
| `id` | INTEGER PK |
| `account_type` | TEXT — same type list as `accounts` |
| `institution` | TEXT |
| `account_number` | TEXT |
| `beneficiary` | TEXT |
| `balance` | REAL |
| `as_of_date` | TEXT |
| `footnote` | TEXT |
| `note` | TEXT |

---

### `liabilities` — Section IX
Multi-row table. One row per liability.

| Column | Type |
|---|---|
| `id` | INTEGER PK |
| `creditor` | TEXT |
| `nature_of_debt` | TEXT |
| `date_incurred` | TEXT |
| `amount_due` | REAL |
| `weekly_payment` | REAL |
| `footnote` | TEXT |
| `note` | TEXT |

**Total Liabilities** and **Total Weekly Liability Payments** — computed, read-only, shown in both entry and view/PDF.

---

## PDF Notes

- Generated as a new document from the read-only template (WeasyPrint or equivalent)
- Not filling the original court PDF file
- Numbered exactly as the court form: Roman numeral sections, alphabetic line items
- CERTIFICATION BY AFFIANT and STATEMENT BY ATTORNEY appear as static boilerplate in PDF only — no entry form, no table

---

## Out of Scope for v1

- PDF upload and field auto-population from financial documents (Phase 2)
- Authentication / multi-user support
- Multiple cases / case switching
- "Total Weekly Payment for Liabilities from Page 8" and "Total Weekly Expenses from Attached Additional Schedule" (deferred)
