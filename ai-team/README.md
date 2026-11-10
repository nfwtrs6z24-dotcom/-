# AIチーム：500円note 制作・販売準備

統括責任者（Claude）が3人のAI社員を順番に動かし、成果物を次の社員へ引き継ぎます。

| ファイル | 役割 |
|---|---|
| [agents/00_director.md](agents/00_director.md) | 統括責任者（作業順序・引き継ぎ・最終チェック） |
| [agents/01_researcher.md](agents/01_researcher.md) | 社員①　市場調査担当 |
| [agents/02_writer.md](agents/02_writer.md) | 社員②　記事制作担当 |
| [agents/03_marketer.md](agents/03_marketer.md) | 社員③　マーケティング担当 |
| [brief.md](brief.md) | 依頼者から受け取る初期情報（統括が記入） |
| outputs/ | 各社員の成果物の保存先 |

## 作業フロー

```
brief.md（依頼者の回答）
   ↓
社員① 市場調査 → outputs/01_research_10themes.md（テーマ10案）
              → outputs/01b_theme_scoring.md（採点・1案に選定）
   ↓  統括チェック①
社員② 記事制作 → outputs/note_draft.md（タイトル10案・有料ライン設計・本文）
   ↓  ★ 人間が【本人が追記】に自分の経験を書き足す
   ↓  統括チェック②
社員③ マーケティング → outputs/03_x_posts.md
   ↓  統括チェック③
outputs/00_final_report.md（最終報告・販売前チェックリスト）
```

過去の成果物は `outputs/archive/` にあります（v1：帰りの車での声かけ）。
