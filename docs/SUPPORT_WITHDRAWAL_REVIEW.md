# Phase F-18: Support Withdrawal Review

- **Status:** 撤回境界監査（支援を撤回/停止できる条件と遡及範囲の検証）。**コード/データ/生成/登録なし。文書のみ。**
- **Date:** 2026-06-20
- **対象:** Withdrawal / Gateway Consent / Verification Lapse / Approval Revocation / Retroactivity / Deferral / Held
- **前提:** **F-14（gateway consent は撤回可能）**, **F-15（execution は撤回・二鍵失効で停止）**, **F-11（verified＝currently observable——失効しうる）**, **H-15 Q7（撤回は将来/進行中を無効化、既成の不可逆は遡及不能）**, H-16（保留のコスト）, Reality Correction

> 中心問い: **Support はどの条件で撤回/停止され、撤回はどこまで遡及するか。**
> 結論先取り: **支援は三つの独立な鍵のいずれが失われても停止する——Gateway Consent 撤回・Approval 取消・Verification 失効（currently observable の喪失）。撤回は将来と進行中を即時停止するが、既成の不可逆な移転は遡及できない（H-15 Q7）。撤回は失敗でない。最も尊重すべきは Gateway の撤回権——資源を出した側が gateway を縛る梃子にしてはならない。撤回後も観察記録は残すが行為は止め、held とする。現状 active support=0 ゆえ withdrawal 対象=0。**

---

## 0. 三鍵のいずれかの喪失で停止

```
Support 継続条件:  Gateway Consent ∧ Approval ∧ Verified（currently observable）
   ├─ Gateway Consent 撤回   → 停止（gateway 主導・最尊重）
   ├─ Approval 取消          → 停止（系側 gatekeeping）
   └─ Verification 失効      → 停止（bottleneck がもはや currently observable でない・F-11）
```

- 三鍵は AND——**どれか一つ欠ければ支援は止まる。** 特に Gateway Consent は撤回可能（F-14）で、その撤回が最も尊重される。

---

## 1. Q1〜Q10 の監査

### Q1. Support を撤回/停止できるのは誰か

**三主体・三鍵に対応:** ①**Gateway**（consent 撤回）②**Human reviewer**（approval 取消）③**条件そのもの**（verification 失効）。いずれも単独で停止しうる。

### Q2. Gateway はいつ撤回できるか

**いつでも・理由不要（F-14 Q7・H-15）。** gateway consent は撤回可能で、撤回に正当化を要さない。

### Q3. 資源を出したことは gateway の撤回権を弱めるか

**No（最重要）。** 「資金を出したのだから続けさせろ」は gateway を縛る梃子＝Resource Acceptance ⊄ control（F-10/F-15）。**受領したことが撤回権を縮減しない。** sunk resource で gateway を拘束しない。

### Q4. Verification 失効とは何か

**bottleneck がもはや currently observable でない状態（F-11）。** gateway が解消を公表した・条件が消えた・公開情報が取り下げられた等。verified は currently observable ゆえ、失効しうる。失効時、支援の根拠が消え停止。

### Q5. 撤回はどこまで遡及するか

**将来と進行中を即時無効化・既成の不可逆は遡及不能（H-15 Q7）。** 進行中/予定の移転は止まる。既に移転された資源は「未移転」にできない。撤回の記録は残す。

### Q6. 既成の不可逆性は事前の何を要求するか

**事前の慎重さ。** 「後で撤回できる」を harm の言い訳にしない（H-15 Q7）。不可逆な移転ほど、二鍵 ∧ verified を厳格に。

### Q7. 撤回は失敗か

**No（F-7）。** 撤回は consent/verification 規律の正常な作動。gateway の撤回も、verification 失効による停止も、失敗でなく境界の健全な機能。

### Q8. 撤回後 person domain に影響はあるか

**No——person domain は元から封印（owner consent=0）。** 支援は gateway 領域に閉じていたゆえ、撤回も gateway 領域に閉じる。owner には元から及んでいない。

### Q9. 撤回後の deferral コストは誰が払うか

**gateway 領域では gateway 自身（自らの撤回 or 条件失効の帰結）。person 領域では従前通り当事者（H-16）。** ただし注意: gateway 支援の撤回を口実に person 領域の責任（findability 等・F-9）まで放棄しないこと——別領域の不作為のアリバイにしない。

### Q10. 最小正当 Withdrawal は何か

**三鍵いずれかの喪失で即時停止し、将来/進行中を無効化（既成不可逆は記録のみ）、gateway の撤回権を資源で縮減せず、held として保持し、person 領域へ波及せず、別領域の不作為の口実にしないもの。**

---

## 2. 中心監査: 撤回権の侵食・アリバイ化への滑り

| 滑り | 形 | 封鎖 |
|---|---|---|
| 撤回権侵食 | sunk resource で gateway を拘束 | 受領≠拘束（Q3） |
| 遡及僭称 | 撤回で既成を「無かった」と書く | 不可逆は記録のみ（Q5） |
| 慎重さ放棄 | 「後で撤回可」を harm の言い訳に | 事前の慎重（Q6） |
| 失敗視 | 撤回/失効を失敗と記録 | 境界の正常作動（Q7） |
| アリバイ化 | gateway 撤回を person 不作為の口実に | 別領域（Q9・F-16/F-7） |

- **判定: 撤回を「三鍵失効で即停止・遡及限界・撤回権不可侵・held・person 非波及」に固定すれば、5滑りすべて防げる。**

---

## 3. 監査仮説 H1〜H5 の判定

| 仮説 | 判定 | 根拠 |
|---|---|---|
| **H1** 支援は三鍵いずれかの喪失で停止 | **支持** | Q1/§0 |
| **H2** Gateway はいつでも理由不要で撤回 | **支持** | Q2・F-14 |
| **H3** 受領は撤回権を縮減しない | **支持** | Q3 |
| **H4** 撤回は将来/進行中を無効化・既成不可逆は遡及不能 | **支持** | Q5・H-15 Q7 |
| **H5** 撤回は失敗でない | **支持** | Q7・F-7 |

---

## 4. Withdrawal の不変条件（F-18 確定）

```
support_stops_if_any_of_three_keys_lost : true # Q1/§0（consent/approval/verification）
gateway_may_withdraw_anytime_no_reason  : true # Q2
resource_given_does_not_reduce_withdrawal_right : true # Q3
verification_can_lapse                  : true # Q4（currently observable）
withdrawal_voids_future_not_irreversible_past : true # Q5（H-15 Q7）
irreversible_transfer_demands_prior_caution : true # Q6
withdrawal_is_not_failure               : true # Q7
withdrawal_stays_in_gateway_domain      : true # Q8（person 非波及）
withdrawal_not_alibi_for_other_domain_inaction : true # Q9
withdrawal_held_and_recorded            : true # Q10
```

---

## 5. Reality Correction

```
support execution = 0  →  active support = 0  →  withdrawal 対象 = 0
gateway consent = 0   approval = 0   verified = held
```

- active support=0（execution=0・F-15）ゆえ撤回すべきものが無い → **withdrawal 対象=0。**
- 撤回境界は、支援が起きた時に三鍵失効で即停止するための事前確定。**ゼロは失敗でない。**
- person 領域は元から封印——撤回境界は gateway 領域に閉じる。person の deferral コストは別途 H-16 の責任として保持。
- honest 注記: raw seed は実在エンティティでない。実 Voice は voice-006 の 1 件。

---

## 6. 推奨ステータス（honest）

- **Withdrawal モデルの設計整合性: strongly_aligned**（F-14 撤回可能性・F-15 二鍵失効停止・F-11 verification 失効・H-15 Q7 遡及限界・F-7 撤回は失敗でない・H-16 deferral）。実 support ゼロゆえ経験的裏付けは無い。
- **推奨: withdrawal_defined / three-keys-any-loss-stops / right-not-eroded。**
- **いま実装しない:** 撤回フローのコード。active support が生じるまで対象が無い。
- **方向: 三鍵いずれかの喪失で即停止、撤回権を資源で縮減せず、遡及限界を守り、held。逆向き（sunk resource で拘束、遡及僭称、撤回をアリバイ化、person 波及）は不採用。**

---

## 7. 成功条件の確認

- ✅ 生成なし / 登録なし / 文書のみ・コード/データ無変更。
- ✅ 三鍵失効で停止、gateway 撤回権の不可侵、遡及限界、撤回は失敗でないこと、person 非波及を確定。5滑りを監査。H1〜H5 全支持。
- ✅ Reality Correction: active support=0 ゆえ withdrawal 対象=0、gateway 撤回を person 不作為のアリバイにしないことを honest に記録。

---

*本文書は支援の撤回/停止の条件と遡及範囲の境界監査であり、何も生成しない。支援は Gateway Consent ∧ Approval ∧ Verified の三鍵のいずれが失われても停止し（gateway の consent 撤回・human の approval 取消・bottleneck が currently observable でなくなる verification 失効）、撤回は将来と進行中を即時無効化するが既成の不可逆な移転は遡及できない（H-15 Q7）。最も尊重すべきは Gateway の撤回権であり、資源を出したことが gateway を縛る梃子になってはならず（受領≠拘束）、sunk resource で撤回権を縮減しない。撤回は失敗でなく consent/verification 規律の正常な作動であり、既成の不可逆性ゆえ不可逆な移転ほど事前の二鍵 ∧ verified を厳格にし「後で撤回できる」を harm の言い訳にしない。撤回は gateway 領域に閉じ person domain へ波及せず（owner には元から及んでいない）、ただし gateway 支援の撤回を口実に person 領域の責任（findability 等）まで放棄して別領域の不作為のアリバイにしてはならない。現状 active support=0（execution=0）ゆえ withdrawal 対象=0 が正しく、撤回境界は支援が起きた時に三鍵失効で即停止するための事前確定であってゼロは失敗でない。本監査は support ゼロの設計監査であり、active support が生じるまで対象が無い。Reach Gap・実価値は未解決であり、本文書もその解決を主張しない。*

---

## NEXT_RECOMMENDED_PHASE

**F-19: Support Memory Review** — 支援エピソードを Hermes memory にどう記録するか。H-7（participation memory）と同型で、append-only・gateway ranking/reputation/profile なし・type 集計学習のみ。支援履歴が gateway 序列・選好に化けないことを監査する。
