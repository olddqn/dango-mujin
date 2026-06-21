# Phase F-15: Support Execution Review

- **Status:** 実行境界監査（二鍵が揃った時、正当な Support Execution とは何かの検証）。**コード/データ/生成/登録なし。文書のみ。**
- **Date:** 2026-06-20
- **対象:** Support Execution / Resource Acceptance / Two Keys / Person Domain / Gateway Autonomy / TTFR-G / Control
- **前提:** **F-13（二鍵 Approval ∧ Gateway Consent）**, **F-14（Gateway Consent＝Resource Acceptance 層・特定・撤回可能）**, F-10（support＝Resource Acceptance 層・無表象/無割当/無推薦）, N-1.7（Execution は当事者領域）, H-16（person domain 封印）, Reality Correction（捏造禁止）

> 中心問い: **二鍵（Approval ∧ Gateway Consent）が揃った時、正当な Support Execution とは何か。**
> 結論先取り: **Support Execution ＝ gateway が consent した特定支援を、Resource Acceptance 層内で、gateway がコントロールを保ったまま行う資源の移転。それは gateway を Mujin の被管理者にせず（gateway autonomy 保持）、person domain へ漏れず、TTFR-G の時計を進めるが TTFR-P を進めない。実行は撤回に追従し（gateway がいつでも止められる）、二鍵のいずれかが欠ければ即時停止。現状 二鍵未成立ゆえ execution = 0。**

---

## 0. 二鍵成立後に開くもの・なお閉じているもの

```
Approval（系側の門）∧ Gateway Consent（gateway 側の門）   ← F-13/F-14
   ▼  開く: Resource Acceptance 層の Support Execution（gateway domain）
   ╳  なお閉: Person Domain（owner consent=0・封印）・Participation・Representation・Selection
```

- 二鍵は **gateway domain の Resource Acceptance 層のみ**を開く。person domain・参加・代弁・選定は依然封印。
- 実行が開いても、それは「gateway が受領に同意した特定支援」に厳密に限定される。

---

## 1. Q1〜Q10 の監査

### Q1. Support Execution とは何か

**gateway が consent した特定支援（資金・人手等）を、Resource Acceptance 層内で gateway へ移転する行為。** consent の範囲（F-14：特定・specific）を超えない。

### Q2. Execution は gateway を Mujin の被管理者にするか

**No（gateway autonomy 保持）。** 資源を移転しても、gateway は独立 actor のまま——Mujin は gateway を管理・指揮しない。
- 「資源を出したから口を出す」は Resource Acceptance ⊄ Participation/control の越境（F-10/F-14）。

### Q3. Execution は consent の範囲を超えられるか

**No。** gateway が consent した特定支援のみ。範囲外（別の支援・追加条件）は新たな consent を要す（F-14 specific）。

### Q4. Execution は person domain に漏れないか

**漏らしてはならない。** 実行は gateway-as-actor への資源移転に閉じ、不在 owner へ到達しない。
- 「支援を owner に届ける」「支援と引き換えに owner access」は漏れ（F-9 §5 / F-10 Q9）。

### Q5. Execution は Selection/Ranking を含むか

**No。** 複数候補から「これを実行」と選ぶのは human ＋ gateway consent の領域であって、実行自体は ranking を持たない（F-12 Q6/F-13 Q2）。実行は consent された特定支援を行うのみ。

### Q6. Execution は撤回に追従するか

**Yes。** gateway が consent を撤回すれば、進行中/将来の実行は停止（F-14 Q7・H-15 Q7）。既成の移転は遡及不能だが新たな移転は止まる（→ F-18）。

### Q7. Execution は TTFR-G を進めるか

**Yes（条件付き）。** consent された支援が gateway の self-stated bottleneck を解消へ向ければ TTFR-G が進む（F-10 Q7）。解消の尺度は gateway 自身（F-16 へ）。

### Q8. Execution は TTFR-P を進めるか

**No（最重要）。** gateway への資源移転は person relief を進めない（F-10 Q8）。**資金が動いた gateway ≠ 救われた人々。** TTFR-G を TTFR-P と混同しない。

### Q9. 二鍵のいずれかが欠けたら Execution はどうなるか

**即時停止/不開始。** Approval 取消 or Gateway Consent 撤回 or verification 失効（F-11 currently-observable の喪失）のいずれでも、実行は止まる。
- 二鍵 ∧ verified が実行の継続条件。

### Q10. 最小正当 Support Execution は何か

**gateway が consent した特定支援を、Resource Acceptance 層内で、gateway autonomy を保ち、person domain に漏らさず、撤回に追従し、TTFR-G のみ進め TTFR-P を進めず、二鍵 ∧ verified が成立する間だけ行う資源移転。**

---

## 2. 中心監査: Execution が越えてはならない境界

| 越境先 | 形 | 封鎖 |
|---|---|---|
| Control/Participation | 資源で gateway を指揮 | gateway autonomy（Q2）・⊄ Participation |
| Scope 逸脱 | consent 範囲外を実行 | specific consent（Q3） |
| Person Domain | owner へ到達/引き換え | 封印（Q4） |
| Selection/Ranking | 実行が選択/順位を含む | human＋consent 領域（Q5） |
| TTFR-P 誤認 | gateway 移転を person 救済と数える | TTFR-G≠TTFR-P（Q8） |

- **判定: 実行を Resource Acceptance 層・consent 範囲・gateway autonomy・person 封印・撤回追従・TTFR-G 限定に固定すれば、5越境すべて防げる。**

---

## 3. 監査仮説 H1〜H5 の判定

| 仮説 | 判定 | 根拠 |
|---|---|---|
| **H1** Execution は gateway を被管理者にしない | **支持** | Q2（autonomy） |
| **H2** Execution は consent 範囲を超えない | **支持** | Q3（specific） |
| **H3** Execution は person domain に漏れない | **支持** | Q4 |
| **H4** Execution は TTFR-G を進め TTFR-P を進めない | **支持** | Q7/Q8 |
| **H5** Execution は撤回・二鍵失効で停止する | **支持** | Q6/Q9 |

---

## 4. Support Execution の不変条件（F-15 確定）

```
execution_within_consented_scope     : true   # Q1/Q3
execution_preserves_gateway_autonomy : true   # Q2
execution_no_control_over_gateway    : true   # Q2
execution_sealed_from_person_domain  : true   # Q4
execution_has_no_selection_or_ranking : true  # Q5
execution_follows_withdrawal         : true   # Q6
execution_advances_ttfr_g_only       : true   # Q7
execution_does_not_advance_ttfr_p    : true   # Q8
execution_requires_two_keys_and_verified : true # Q9
execution_stops_if_any_key_or_verification_lost : true # Q9
```

---

## 5. Reality Correction

```
voice-006 owner consent = 0
verified bottleneck = held   support candidate = 0   approval = 0   gateway consent = 0
support execution = 0
```

- 二鍵（Approval ∧ Gateway Consent）のいずれも未成立、かつ verification=held ゆえ **support execution = 0 が正しい。**
- これは連鎖的に正しい data-driven 帰結（held → candidate 0 → approval 0 / gateway consent 0 → execution 0）。ゼロは失敗でない。
- 実行を二鍵なしに起こすこと（無から resource を動かす）は越境・捏造＝違反。
- honest 注記: raw seed は実在エンティティでない。実 Voice は voice-006 の 1 件。

---

## 6. 推奨ステータス（honest）

- **Support Execution モデルの設計整合性: strongly_aligned**（F-13/F-14 の二鍵を実行に翻訳・F-10 Resource Acceptance/gateway autonomy と一貫・TTFR-G/TTFR-P 区別・person 封印維持）。実 execution ゼロゆえ経験的裏付けは無い。
- **推奨: support_execution_defined / resource-acceptance-only / two-keys-gated。**
- **いま実装しない:** 実行コード。二鍵 ∧ verified が揃うまで execution=0 が正しい。
- **方向: 実行は consent 範囲の Resource Acceptance 層・gateway autonomy 保持・person 封印・撤回追従・TTFR-G 限定。逆向き（gateway 管理、scope 逸脱、owner 到達、TTFR-P 誤認、二鍵なし実行）は不採用。**

---

## 7. 成功条件の確認

- ✅ 生成なし / 登録なし / 文書のみ・コード/データ無変更。
- ✅ Execution が gateway autonomy 保持・consent 範囲・person 封印・撤回追従・TTFR-G 限定であることを確定。5越境を監査。H1〜H5 全支持。
- ✅ Reality Correction: 二鍵未成立ゆえ execution=0 が正しいこと、二鍵なし実行が違反であることを honest に記録。

---

*本文書は二鍵成立後の正当な Support Execution の境界監査であり、何も生成しない。Support Execution ＝ gateway が consent した特定支援を Resource Acceptance 層内で gateway へ移転する行為であり、gateway を Mujin の被管理者にせず（gateway autonomy 保持）、consent の特定範囲を超えず、person domain へ漏れず、selection/ranking を含まず、撤回に追従し、TTFR-G の時計を進めるが TTFR-P を進めず（資金が動いた gateway は救われた人々ではない）、二鍵 ∧ verified が成立する間だけ継続し、いずれかが失効すれば即時停止する。現状 Approval も Gateway Consent も未成立で verification=held ゆえ support execution=0 が正しく、これは連鎖的に正しい data-driven 帰結であってゼロは失敗でなく、二鍵なしに資源を動かすことは越境・捏造＝違反である。本監査は execution ゼロの設計監査であり、二鍵 ∧ verified が揃うまで execution=0 が正しい。Reach Gap・実価値は未解決であり、本文書もその解決を主張しない。*

---

## NEXT_RECOMMENDED_PHASE

**F-16: Support Reality Feedback Review** — （仮に）実行された支援が gateway の self-stated bottleneck を実際に解消したかを、捏造せず gateway 自身の尺度で観察する方法。TTFR-G completion の honest な確認・Jammy House/D.R.A. 教訓の適用・gateway relief と person relief の峻別を監査する。
