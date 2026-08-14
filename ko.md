# VidLens

[English](README.md) | [简体中文](zhcn.md) | [繁體中文](zhtw.md) | [日本語](ja.md) | [Français](fr.md) | [Español](es.md) | [Deutsch](de.md) | [Português](pt.md)

---

텍스트 전용 AI 에이전트에게 이미지와 비디오를 볼 수 있는 능력을 부여합니다.

VidLens는 시각 파일을 외부 비전 모델로 라우팅하여 일반 텍스트로 반환합니다.

> **모델이 네이티브로 시각을 지원하면 VidLens를 사용하지 마세요.** 텍스트 전용 모델 전용입니다.

## 작동 방식

```
이미지/비디오 -> base64 인코딩 -> 비전 API -> 일반 텍스트 결과
```

## 원클릭 배포 (AI 에이전트에게 지시)

에이전트에게 말하세요:

> Install vidlens from https://github.com/francis20060728-jpg/vidlens and configure it for me.

에이전트가 저장소를 클론하고, --init을 실행하며, config.yaml 작성을 도와줍니다.

## 필수 조건

- [Python 3](https://python.org) (3.7+)
- OpenAI 호환 비전 API 키
- (선택) [ffmpeg](https://ffmpeg.org)

## 빠른 시작: MCP 서버 (권장)

MCP는 VidLens를 사용하는 가장 빠른 방법입니다.

```bash
# 1. 설치
git clone https://github.com/francis20060728-jpg/vidlens.git
cd vidlens
pip install "mcp>=1.0,<2.0" opencv-python numpy
# 2. 설정
python scripts/vidlens.py --init
# 3. MCP 서버 실행
python vidlens/server.py
```

MCP 클라이언트에 등록:

```json
{
  "mcpServers": {
    "vidlens": {
      "command": "python",
      "args": ["/abs/path/to/vidlens/vidlens/server.py"]
    }
  }
}
```

### MCP 도구

| 도구 | 설명 | 주요 인수 |
|------|------|------|
| `look` | 비전 모델로 단일 이미지 또는 비디오 파일을 분석합니다. 비디오는 자동으로 레이블이 지정된 콩택트 시트로 샘플링됩니다. | `media_path` (required), `prompt` (optional), `prompt_name` (optional), `frame_count` (optional, default 9) |
| `list_media` | 디렉토리에서 이미지 및 비디오 파일을 찾습니다. 재귀적으로 검색하고 파일명 키워드로 필터링합니다. 이미지 우선으로 정렬된 절대 경로를 반환합니다. | `directory` (optional, default cwd), `keyword` (optional), `max_results` (optional, default 20) |
| `find_and_look` | 키워드로 디렉토리를 검색한 후 한 번의 호출로 최적 일치 항목을 분석합니다. list_media + look의 편리한 조합입니다. | `directory` (required), `keyword` (required), `prompt` (optional), `prompt_name` (optional), `frame_count` (optional) |

예: `look(media_path="chart.png", prompt="이 이미지는 무엇을 보여주나요?")`


## 빠른 시작: CLI (MCP 미지원 폴백)

결과는 stdout에 직접 출력됩니다.

```bash
git clone https://github.com/francis20060728-jpg/vidlens.git
cd vidlens
python scripts/vidlens.py --init
python scripts/vidlens.py --status
python scripts/vidlens.py photo.png "이미지에 무엇이 있나요?"
```

## 자동 사용 규칙 (Codex)

```bash
python scripts/vidlens.py --install-agents
python scripts/vidlens.py --remove-agents
python scripts/vidlens.py --status
```

네이티브 시각을 먼저 확인: 모델이 이미지를 볼 수 있으면 VidLens를 건너뜁니다.

## 기능

- **이미지 종속성 제로**
- **MCP 서버 모드**
- **프로바이더 페일오버** (최대 9개)
- **추론 모델 지원**
- **로컬 OCR 폴백**
- **비디오 지원** (ffmpeg / opencv)
- **커스텀 프롬프트 템플릿**
- **멀티 프로바이더**

## 설정

| 키 | 기본값 | 용도 |
|-----|-----|-----|
| `api_url` | `""` | 비전 API URL |
| `api_key` | `""` | API 키 |
| `model_name` | `""` | 모델 이름 |
| `response_tokens` | `4000` | 최대 토큰 |
| `is_reasoning_model` | `false` | 추론 모델은 true |

## 문제 해결

| 문제 | 해결책 |
|---------|---------|
| `NEEDS CONFIG` | `--init` 실행 후 config.yaml 편집 |
| 비디오 실패 | ffmpeg 또는 `pip install opencv-python numpy` |

## 피드백

질문이나 제안이 있으신가요? **francis20060728@gmail.com**로 이메일을 보내주시면 신속히 처리하겠습니다.
## 문서

- [설치 가이드](docs/SETUP.md)
- [고급 기능](docs/ADVANCED.md)
- [문제 해결](docs/TROUBLESHOOTING.md)
- [변경 로그](CHANGELOG.md)

## 라이선스

MIT. [LICENSE](LICENSE)를 참조하세요.
