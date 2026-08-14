# VidLens

[English](en.md) | [en](en.md) | [zhcn](zhcn.md) | [zhtw](zhtw.md) | [ja](ja.md) | [fr](fr.md) | [es](es.md) | [de](de.md) | [pt](pt.md)

텍스트 전용 AI 에이전트에게 이미지와 비디오를 볼 수 있는 능력을 부여합니다.

VidLens는 시각 파일을 외부 비전 모델로 라우팅하여 일반 텍스트로 반환합니다.

**이미지 분석은 종속성 제로.** Python 3 표준 라이브러리만 필요.

**모델이 네이티브로 시각을 지원하면 VidLens를 사용하지 마세요.** 텍스트 전용 모델 전용입니다.

## 빠른 시작: MCP 서버 (권장)

```bash
pip install "mcp>=1.0,<2.0" opencv-python numpy
python scripts/vidlens.py --init
python vidlens/server.py
```

## 빠른 시작: CLI (MCP 미지원 폴백)

```bash
git clone https://github.com/francis20060728-jpg/vidlens.git
cd vidlens
python scripts/vidlens.py --init
python scripts/vidlens.py --status
python scripts/vidlens.py photo.png "이미지에 무엇이 있나요?"
```

## 자동 사용 규칙

```bash
python scripts/vidlens.py --install-agents
python scripts/vidlens.py --remove-agents
```

## 라이선스

MIT. [LICENSE](LICENSE)를 참조하세요.
