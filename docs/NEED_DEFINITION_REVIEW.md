# Need Definition Review — voice-006 candidates A–E

- **Status:** 観察レビュー（Need Candidate の**推測の起点**の記録）。Need を作成・承認・却下しない。新機能・新データ・新 ADR・新 Layer なし。
- **Date:** 2026-06-13
- **観測対象:** [`docs/HUMAN_NEED_CANDIDATE_REVIEW.md`](HUMAN_NEED_CANDIDATE_REVIEW.md)（X-3）の候補 A–E
- **前提:** `voice-006` は Gateway Voice。Need Owner（当事者個人）は Voice 内に不在。Gateway の活動内容から個人 Need を推測する行為は Saiyan Scouter 問題の再発リスクを持つ。

> このフェーズは Need を決めない。**人間がどこから推測を始めたのかを記録する**だけ。
> ここに書く record は観測記録であり、`need_candidates.jsonl` 等のデータには一切書き込まない（文書のみ）。

---

## レビュー観点（5軸）

1. **直接観測** — voice-006 に明示されているか
2. **仲介推論** — JAR の活動内容から推測しているか
3. **Need Owner 不在** — 当事者本人の Voice が存在するか
4. **距離** — Gateway Need か Individual Need か
5. **Saiyan Scouter Risk** — 問題定義権力が発生しているか

---

## レビュー記録（A–E）

> `review_type` ∈ {direct_observation, inferred, speculative}。
> `need_owner_present` = 「この Need の主体が voice-006 に存在するか」（A/B は JAR 自身が主体＝発話者なので present。C/D/E は当事者個人が主体＝不在）。

### candidate A — 資金
```json
{
  "candidate_id": "A",
  "label": "資金支援の不足",
  "review_type": "direct_observation",
  "need_owner_present": true,
  "gateway_need": true,
  "individual_need": false,
  "distance_from_voice": "0 (gateway resource need, stated)",
  "scouter_risk": "none",
  "human_comment": "公開要請に寄付募集が明示。JAR 自身の資源 Need であり、発話者＝主体。推測なし。"
}
```

### candidate B — 人手
```json
{
  "candidate_id": "B",
  "label": "ボランティア(人手)の不足",
  "review_type": "direct_observation",
  "need_owner_present": true,
  "gateway_need": true,
  "individual_need": false,
  "distance_from_voice": "0 (gateway resource need, stated)",
  "scouter_risk": "none",
  "human_comment": "公開要請にボランティア募集が明示。JAR 自身の資源 Need。推測なし。"
}
```

### candidate C — 翻訳
```json
{
  "candidate_id": "C",
  "label": "翻訳/言語支援の不足",
  "review_type": "inferred",
  "need_owner_present": false,
  "gateway_need": false,
  "individual_need": true,
  "distance_from_voice": "2-layer (behind gap-1, individual)",
  "scouter_risk": "medium",
  "human_comment": "活動分野(言語支援)＋obs-006のキーワードから推測。当事者個人の Need を声から推測しており、Need Owner 不在。"
}
```

### candidate D — 法的
```json
{
  "candidate_id": "D",
  "label": "法的支援の不足",
  "review_type": "inferred",
  "need_owner_present": false,
  "gateway_need": false,
  "individual_need": true,
  "distance_from_voice": "2-layer (behind gap-1, individual)",
  "scouter_risk": "high",
  "human_comment": "活動分野(法的支援)からの推測。不足量・個別事案は gap-1 の奥で未観測。個人 Need の外部定義に最も近い。"
}
```

### candidate E — 就労
```json
{
  "candidate_id": "E",
  "label": "就労支援の不足",
  "review_type": "speculative",
  "need_owner_present": false,
  "gateway_need": false,
  "individual_need": true,
  "distance_from_voice": "2-layer (behind gap-1, individual)",
  "scouter_risk": "high",
  "human_comment": "活動分野はあるが、これが現在のボトルネックか自体が不明。活動領域の存在を Need 不足と読む飛躍が最大。"
}
```

---

## 集約テーブル

| candidate | review_type | need_owner_present | gateway_need | individual_need | distance | scouter_risk |
|---|---|---|---|---|---|---|
| A 資金 | direct_observation | true | ✅ | — | 0 | none |
| B 人手 | direct_observation | true | ✅ | — | 0 | none |
| C 翻訳 | inferred | false | — | ✅ | 2-layer | medium |
| D 法的 | inferred | false | — | ✅ | 2-layer | high |
| E 就労 | speculative | false | — | ✅ | 2-layer | high |

---

## この5軸が明らかにしたこと（観測結果）

**5つの観点が、すべて同じ一本の線で割れる。**

```
        direct_observation │ inferred / speculative
        need_owner present  │ need_owner ABSENT
        gateway_need        │ individual_need
        distance 0          │ distance 2-layer (gap-1)
        scouter_risk none   │ scouter_risk medium→high
        ───────────────────┼───────────────────────
              A · B         │       C · D · E
```

- **推測の起点は「JAR の活動分野」である。** 人間が C/D/E を考え始めた瞬間は、voice-006 の明示（資金・人手募集）ではなく、JAR が掲げる活動領域（翻訳・法的・就労）を読んだ時。
- **Saiyan Scouter Risk は、この線を越えた瞬間に発生する。** A/B（JAR 自身の stated need）には問題定義権力がない。C/D/E（不在の個人の need を活動分野から推測）に入った瞬間、外部が当事者の Need を著者化し始める。
- **review_type の段階（direct → inferred → speculative）は、距離と risk に単調に対応する。** speculative(E) は「それが Need か」自体が推測。

---

## 結論（確定しない）

- **A・B は Gateway Need の直接観測**であり、個人 Need を定義しない範囲で扱える（最も安全）。
- **C・D・E は Individual Need の推測**であり、当事者本人の Voice が現れるまで**確定しない**。仲介者の活動分野を当事者の Need と読み替えないこと。
- 本レビューは、人間の推測の起点が「活動分野の読み替え」にあることを記録した。これは欠陥ではなく、**Gateway Voice から出発する限り不可避な推測**であり、だからこそ Need を確定しない保留が要る。

---

*本文書は Need 定義の推測起点の観測記録であり、Need を作成・承認・却下せず、Need Candidate を自動生成・自動修正せず、Task/Gateway/資源配分を生成しない。個人 Need（C/D/E）は当事者の Voice が現れるまで確定しない。Reach Gap は未解決であり、本文書もその解決を主張しない。*
