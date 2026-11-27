# 보고서 그림·표 목록 (core 담당, 2026-11-26)

모든 그림은 `report/figures/`에 **아래 파일 이름 그대로** 저장합니다. PNG, 300dpi, 가로 6.5인치(약 16.5cm), 한글 글꼴(Mac은 AppleGothic, Colab은 `fonts-nanum` 설치 후 NanumGothic).
표는 `report/tables/`에 csv로 저장합니다(보고서에서 core 담당이 표로 옮김). 각자 결과 메모(3~5문장)는 `report/memos/이름.md`.

판정에 쓰는 값은 모두 같은 SR 정의(with_treasury: MIRR 초과수익률, 동일가중, 거절=0)입니다.

## 본문 표

| 번호 | 파일 | 내용 | 담당 | 상태 |
|---|---|---|---|---|
| 표 1 | `eda_audit/table_1_censoring.csv` | 만기·발행월별 미종결 비율 (만기 컷오프 근거) | core 담당 | 완료 |
| 표 2 | `eda_audit/table_2a~2c_*.csv` | 상태·등급·만기별 수익률 (MIRR, 초과수익률, HPR) | core 담당 | 완료 |
| 표 3 | `eda_audit/table_3a_screening_funnel.csv`, `table_3b_feature_spec.csv` | 변수 선별 깔때기 141→37, 변수 목록·VIF·부호 | core 담당 | 완료 |
| 표 4 | `tables/t4_validation_summary.csv` | Dev OOB(B=100) 세 모형의 a* 중앙값·범위, SR*, AUC, Brier | logit 담당 (①②③ outputs 집계) | 대기 |
| 표 5 | `tables/t5_test_6a.csv` | Test 판별력·보정 (AUC, KS, Brier, LogLoss, PoM) | eval 담당 | 대기 |
| 표 6 | `tables/t6_test_6b.csv` | Test ΔSR(②−③, ②−①), 95% 구간, 97.5% 분위수 대 δ, 비열등 판정 | eval 담당 | 대기 |
| 표 7 | `tables/t7_robustness.csv` | 견고성 3개(금액가중, HPR, 승인율 0.35~0.63)의 ΔSR과 부호 일치 여부 | 함수: logit 담당 / Test 적용: eval 담당 | 대기 |
| 표 8 | `tables/t8_test_6c.csv` | 단조성 위반율, Top-3 거절 사유 Jaccard (①②③) | eval 담당 | 대기 |
| 표 9 | `tables/t9_sensitivity_core16.csv` | 민감도 A(Core 16개)의 Test SR·ΔSR | logit 담당(①), xgb 담당(②③) 모형 / eval 담당 평가 | 대기 |

## 본문 그림

| 번호 | 파일 | 내용 | 담당 |
|---|---|---|---|
| 그림 1 | `fig1_censoring.png` | 표 1의 막대그래프 (36·60개월, 발행월별 미종결 비율, 컷오프 선) | core 담당 |
| 그림 2 | `fig2_oob_sr_curves.png` | 세 모형의 승인율별 OOB SR 평균 ±1SD, a* 점선 (Figure A를 한 장에) | logit 담당 |
| 그림 3 | `fig3_astar_dist.png` | 회차별 a*_b 분포 (세 모형) (Figure B) | logit 담당 |
| 그림 4 | `fig4_oob_dsr.png` | 회차별 ΔSR_b 곡선 (②−③, ②−①) (Figure C) | logit 담당 |
| 그림 5 | `fig5_test_dsr_boot.png` | Test paired bootstrap ΔSR 분포, 97.5% 분위수와 δ 선 | eval 담당 |
| 그림 6 | `fig6_test_dsr_band.png` | Test 승인율별 ΔSR 곡선 (0.10~0.90, 0.35~0.63 음영) | eval 담당 |
| 그림 7 | `fig7_violation_jaccard.png` | 위반율과 Jaccard 비교 (①②③) | eval 담당 |
| 그림 8 | `fig8_boundary_cases.png` | 경계 사례 3명의 세 모형 Top-3 거절 사유 (Waterfall) | eval 담당 |

## 부록

| 번호 | 파일 | 내용 | 담당 |
|---|---|---|---|
| 부록 A | `report/sign_check.csv` | 부호 점검 (단변량 10분위, ① β, ② PDP) | core 담당 (완료) |
| 부록 B | `figA1_tuning_history.png`, `tables/tA1_tuning_trials.csv` | 튜닝 시도별 logloss, 최종 파라미터 | xgb 담당 |
| 부록 C | `figA2_pdp.png` | ② PDP (부호 ±1 변수) | xgb 담당 |
| 부록 D | `tables/tA2_vif.csv` | ① 설계행렬 VIF | logit 담당 (02_logit 6절) |
| 부록 E | `figA3_oob_sr_approved_only.png` | 승인 대출만 기준 SR 곡선 (a*가 하한에 붙는 이유 설명용) | logit 담당 |

## 메모 양식 (`report/memos/이름.md`)

1. 무엇을 돌렸나 (config·lib_prep 해시, B, 실행 날짜)
2. 핵심 수치 2~3개
3. 예상과 다른 점, 한계 한 줄
