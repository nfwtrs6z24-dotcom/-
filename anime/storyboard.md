# 台本・絵コンテ 「ころころ、みかん。」（60秒）

## 企画
| 項目 | 内容 |
|---|---|
| 尺 | 60秒（CATV スポット枠想定。30秒版は末尾参照） |
| ログライン | 段々畑から転がり落ちたみかんを追いかけた少女が、港で人と出会い、ひとつのみかんを分け合う。 |
| テーマ | 「ころがった先で、だれかとつながる。」— 山（みかん）と海（港）がつながる八幡浜の町 |
| 画面 | 1920×1080 / 29.97p / 16:9 |
| 構成 | セリフ最小限（AI動画は口パクが苦手なため、**話している口元はなるべく映さない**構成にしています） |

## 台本

```
○段々畑（朝）
  海を見下ろす石垣の段々畑。
  NA「海と山のあいだの町、八幡浜。」

  ハル、じいちゃんとみかんを収穫している。ひときわ大きなみかんを両手で掲げる。
  ハル「見て！ こんなに大きいよ！」
  じいちゃん、目を細めてうなずく。

  ハルの手からみかんがつるり。石垣の段をぽん、ぽんと跳ねて転がっていく。
  ハル「あっ！」

  ハル、みかんを追って段々畑を駆け下りる。
  ハル「まって〜！」

○港へ下る路地（昼）
  石段を転がるみかん。塀の上の猫が飛び起きる。ハルが続いて駆け抜ける。

○港・岸壁（夕方）
  網の手入れをしている漁師の足元に、みかんがコツンと当たって止まる。
  漁師、ひょいと拾い上げる。息を切らしたハルが到着。
  漁師（手渡しながら）「ええみかんじゃねえ。」

  ハル、みかんをむいて半分を差し出す。
  ハル「はんぶんこ、しよ。」
  遅れて着いたじいちゃんも加わり、三人で岸壁に腰かけて食べる。

  夕日が海に沈み、港がみかん色に染まる。三人の後ろ姿。
  NA「ころがった先で、だれかと、つながる。」

○タイトル
  「ころころ、みかん。」
  制作 八西CATV ／ 映像の一部に生成AIを使用しています
```

## 絵コンテ（カット表）

- **ファイル名**は `clips/S01.mp4` のようにカット番号で保存すると `assemble.sh` が自動で並べます。
- 尺は `shots.csv` が正です。生成クリップは**表の尺より1〜2秒長め**に作ると編集で余裕が出ます（Runway なら 5秒/10秒で生成）。
- 「動画プロンプト」は Image to Video 用です。まず「画像プロンプト」で静止画（1カット目のフレーム）を作り、その画像＋動画プロンプトで動かすと安定します。
- 全プロンプトの末尾に `characters.md` の **[共通スタイル]** を付けてください。

| # | 時間 | 尺 | 画面 | 音 |
|---|---|---|---|---|
| S01 | 0:00 | 5s | 段々畑と海の超ロング（俯瞰）。ゆっくり前進 | NA「海と山のあいだの町、八幡浜。」/ BGM入り |
| S02 | 0:05 | 5s | ハル（背中寄り）がみかんを掲げる。奥でじいちゃんが微笑む | ハル「見て！こんなに大きいよ！」 |
| S03 | 0:10 | 4s | みかんのアップ。手から滑り、石垣の段で跳ねる | ハル「あっ！」/ ぽんっSE |
| S04 | 0:14 | 6s | 段々畑の斜面を跳ねるみかん（手前）、追うハル（奥）。横移動 | ハル「まって〜！」/ 足音 |
| S05 | 0:20 | 6s | 路地の石段を転がるみかん、塀の猫が飛び起き、ハルが駆け抜ける | 猫「ニャッ」/ コロコロSE |
| S06 | 0:26 | 5s | 岸壁。網を繕う漁師の長靴にみかんが当たり止まる。拾い上げる | コツンSE / 波・カモメ |
| S07 | 0:31 | 6s | 漁師がハルにみかんを手渡す（漁師は横顔〜背中、口元を見せない） | 漁師「ええみかんじゃねえ。」 |
| S08 | 0:37 | 7s | ハルが半分を差し出す→じいちゃん合流、三人で岸壁に座って食べる | ハル「はんぶんこ、しよ。」/ 笑い声 |
| S09 | 0:44 | 8s | 夕日が沈む港、みかん色の空と海。三人の後ろ姿（逆光シルエット） | NA「ころがった先で、だれかと、つながる。」 |
| S10 | 0:52 | 8s | 夕焼けの空と海だけの静かな画（タイトルはテロップで重ねる） | BGM締め |

### カット別 生成プロンプト

**S01 段々畑の俯瞰**
- 画像：`Wide aerial view of steep terraced mandarin orange groves with stone walls on a hillside, calm blue bay and a small fishing town below, early morning sunlight, no people`
- 動画：`Slow cinematic push-in toward the bay, leaves gently swaying in the breeze, soft morning light, calm`

**S02 みかんを掲げるハル**（参照：ハル・じいちゃん設定画）
- 画像：`Haru, a 10-year-old girl in yellow t-shirt and denim overalls, holding up a large mandarin orange with both hands toward the sky, seen from behind over her shoulder, her grandfather in a straw hat smiling in the background among orange trees, terraced grove, sea in the distance`
- 動画：`The girl lifts the orange up proudly and bounces happily, grandfather nods gently, static camera`

**S03 みかんが滑る**
- 画像：`Close-up of a child's hands holding a large glossy mandarin orange with a leaf, stone wall of a terraced grove below`
- 動画：`The orange slips out of the hands, falls and bounces once on the stone step, then rolls away downhill, shallow depth of field`

**S04 段々畑を転がる**（参照：ハル・みかん）
- 画像：`A mandarin orange bouncing down terraced stone steps in the foreground, girl Haru running down the slope after it in the background, orange trees, blue sea`
- 動画：`Camera pans sideways following the bouncing orange, the girl runs after it with arms out, energetic, playful`

**S05 路地の石段**（参照：ハル・みかん・路地背景）
- 画像：`Low angle view of narrow old stone steps in a seaside Japanese town, a mandarin orange rolling down, a cat on a wall`
- 動画：`The orange rolls down the stone steps toward the camera, the cat jumps up surprised, then a girl in overalls runs past, low tracking shot`

**S06 漁師が拾う**（参照：漁師・港背景）
- 画像：`Fishing harbor quay, a sturdy fisherman in orange bib overalls and black rubber boots sitting and mending a net, a mandarin orange rolling toward his boot`
- 動画：`The orange taps against the boot and stops, the fisherman notices and picks it up with a big grin, seagulls in the sky`

**S07 手渡し**（参照：ハル・漁師）
- 画像：`Over-the-shoulder shot from behind the fisherman, handing a mandarin orange to an out-of-breath girl Haru, harbor and boats behind, late afternoon light`
- 動画：`The fisherman gently hands the orange to the girl, she takes it with both hands and smiles, subtle movement, static camera`

**S08 はんぶんこ**（参照：ハル・漁師・じいちゃん）
- 画像：`Girl Haru, a fisherman and her grandfather in a straw hat sitting side by side on the edge of a harbor quay, sharing a peeled mandarin orange, warm sunset light`
- 動画：`The girl splits the orange and offers half, they eat and laugh together, legs dangling over the quay, slow push-in`

**S09 みかん色の夕日**
- 画像：`Silhouettes of three people (a girl, an old man in a straw hat, a fisherman) sitting on a harbor quay from behind, huge orange sunset over the sea, whole harbor glowing mandarin orange`
- 動画：`The sun slowly sets into the sea, gentle waves sparkle softly, very slow pull-back, peaceful` ※**キラキラの強い点滅は避ける**

**S10 タイトル背景**
- 画像：`Empty calm sea and sky at dusk, gradient from mandarin orange to deep blue, a few soft clouds, lots of negative space in the center, no people`
- 動画：`Clouds drift very slowly, almost still`

## 音
| 種類 | 内容 | 作り方の例 |
|---|---|---|
| ナレーション | 落ち着いた女性 or 地元の方の声 | **地元の方・局アナウンサーの実声を推奨**（地域性・権利の両面で安心） |
| セリフ | ハル／漁師（2行のみ） | 実声収録、または商用・放送利用可の音声合成（利用規約を確認） |
| BGM | ピアノ＋アコースティックギターの温かい曲 60秒 | 放送利用可のライセンス曲 or 音楽生成AI（放送利用可の有料プラン） |
| SE | ぽんっ、コロコロ、コツン、波、カモメ、猫 | 局の効果音ライブラリ |

`audio/voice.wav` に 60秒のタイムラインでセリフとNAを並べ（上表の時間に合わせる）、`audio/bgm.wav` を置くと自動でミックス＆ −24 LKFS に整えます。

## 30秒版を作る場合
S01（3s）→ S03（3s）→ S04（4s）→ S06（4s）→ S08（6s）→ S09（5s）→ S10（5s）。
NAは「ころがった先で、だれかと、つながる。」のみ、セリフは「あっ！」「はんぶんこ、しよ。」の2つに絞る。
