# キャラクター・美術設定 「ころころ、みかん。」

AI動画は**カットごとに顔や服が変わりやすい**ため、最初に「設定画（リファレンス画像）」を1枚ずつ作り、
全カットの生成時にその画像を参照させます（Runway の References / Image to Video など）。
下の英語プロンプトをそのまま画像生成AIに入れて、気に入った1枚を `refs/` に保存してください。

## 共通スタイル（全プロンプトの末尾に必ず付ける）

```
Japanese hand-drawn 2D anime style, soft watercolor background art, warm natural light,
clean line art, gentle pastel colors with vivid mandarin orange accents, 16:9, cinematic composition,
no text, no logo, no watermark
```

> 既存アニメ作品名・スタジオ名・作家名（「〇〇風」）はプロンプトに入れないでください。放送・権利の面で安全なオリジナル画風にするためです。

---

## ハル（主人公）
- 10歳の女の子。祖父のみかん畑の手伝いが好き。元気で、ちょっとそそっかしい。
- 見た目：黒髪ショートボブ＋小さなみかん色のヘアピン、黄色のTシャツ、デニムのオーバーオール、白いスニーカー、首にタオル
- セリフ：「見て！こんなに大きいよ！」「あっ！」「まって〜！」「はんぶんこ、しよ。」

```
Character reference sheet of a 10-year-old Japanese girl named Haru, short black bob hair with a small orange hair clip,
yellow t-shirt, denim overalls, white sneakers, small towel around her neck, cheerful round eyes,
front view, side view and back view, full body, plain white background, [共通スタイル]
```

## じいちゃん（ハルの祖父）
- 70代のみかん農家。日焼けした穏やかな人。口数は少ない。
- 見た目：白髪の短髪、麦わら帽子、紺の作業着、首に手ぬぐい、腰に収穫ばさみ

```
Character reference sheet of a kind Japanese farmer in his 70s, tanned skin, short white hair, straw hat,
navy blue work clothes, tenugui towel around neck, pruning shears on belt, gentle smile,
front view, side view and back view, full body, plain white background, [共通スタイル]
```

## 漁師のおじさん
- 50代。港で網の手入れをしている。豪快だが優しい。地元ことば。
- 見た目：がっしり体型、ねじり鉢巻き、白いTシャツ、オレンジのゴム胴長（ビブパンツ）、長靴
- セリフ：「ええみかんじゃねえ。」

```
Character reference sheet of a sturdy Japanese fisherman in his 50s, twisted headband, white t-shirt,
orange rubber fishing bib overalls, black rubber boots, big friendly grin,
front view, side view and back view, full body, plain white background, [共通スタイル]
```

## みかん（もう一人の主人公）
- ひときわ大きくてツヤのある温州みかん。ヘタに葉っぱが1枚ついている。**顔は付けない**（あくまで本物のみかん）。

```
A single large glossy Japanese mandarin orange with one green leaf on the stem, close-up, product turnaround,
plain white background, [共通スタイル]
```

---

## 美術（背景）設定

| 場所 | 内容 | ポイント |
|---|---|---|
| 段々畑 | 海を見下ろす急斜面の石垣の段々畑、みかんの木、運搬用モノレール | 八幡浜らしさの核。石垣と海を必ず同じ画面に |
| 路地・石段 | 港へ下る細い坂道、古い民家、石段、猫 | 実在の特定の家・店の看板は描かない |
| 港 | 漁船が並ぶ岸壁、網、魚箱、遠くに島影 | 実在施設のロゴ・船名は入れない |
| 夕景 | 海に沈む夕日で港全体がみかん色に | ラストの見せ場。光の点滅は入れない |

```
Background art: steep terraced mandarin orange groves with old stone walls on a hillside overlooking a calm blue bay,
small fishing town below, a tiny monorail track for carrying harvest, morning light, no people, [共通スタイル]
```

```
Background art: narrow sloping alley with old stone steps leading down to a small fishing harbor,
traditional Japanese houses with tiled roofs, potted plants, a cat sleeping on a wall, afternoon, no people, [共通スタイル]
```

```
Background art: small Japanese fishing harbor quay with moored fishing boats, fishing nets and plastic fish crates,
island silhouettes far away, late afternoon, no people, [共通スタイル]
```
