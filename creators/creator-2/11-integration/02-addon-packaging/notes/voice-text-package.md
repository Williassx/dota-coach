# Source-пакет local text preview

[Подпункт](../README.md) · [Recipe](../voice-text-manifest.json).

Из корня проверено, output каждый раз новый:

```bash
python3 - <<'PY'
import json, subprocess
base = 'creators/creator-2/01-foundation/02-panorama-capability/tools/'
manifest = 'creators/creator-2/11-integration/02-addon-packaging/voice-text-manifest.json'
result = subprocess.run(['python3', base + 'build_probe_bundle.py', '--manifest', manifest], check=True, capture_output=True, text=True)
output = json.loads(result.stdout)['output']
subprocess.run(['python3', base + 'verify_probe_bundle.py', '--manifest', manifest, '--bundle', output], check=True)
PY
```

Kind panorama_source_voice_text содержит6 byte-copy resources/5references: canonical
Hud manifest, layout/CSS и Roster→VoiceText→Panel. Ровно один context, disabled empty
TextEntry, две disabled кнопки и plain labels; explicit bind по
[инструкции панели](../../../06-voice/03-voice-feedback/notes/text-preview.md).
Новое TextEntry разрешено только dedicated policy этого kind; старые defaults
сохранены. Verifier сверяет байты с current source и полную достижимость ресурсов.

Пакет альтернативный: общий custom_ui_manifest с другими экранами автоматически
не объединяется. Он не устанавливается/не компилируется в Tools. UI показывает
local предложение, не голосовое распознавание или исполненный приказ. Микрофон/
ASR/native geometry/hittest/transport/C1authority/эффект/второй владелец открыты.
