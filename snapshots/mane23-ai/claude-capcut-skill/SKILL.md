---
name: capcut
description: |
  CapCut/JianYing 프로젝트 자동 편집. 타임코드 컷, 내용 기반 장면 찾기(자막+비전),
  토킹헤드 무음·NG 제거, 롱폼->쇼츠 변환, 자막 생성/스타일/번역, 프로젝트 검사/롤백.
  백엔드: capcut-cli 단독. 트리거: 키워드 자동 감지 + /capcut 명시 호출.
  CapCut 프로젝트(draft 폴더)가 입력일 때만 발화. 일반 mp4 편집은 video 스킬로 위임.
version: 0.2.0
compatible_cli: ">=0.9.0"
context_requires:
  must: []
  optional:
    - references/cli-cheatsheet.md
    - references/project-paths.md
    - references/skill-routing.md
---

# CapCut Skill

Claude Code에서 자연어로 CapCut/JianYing 프로젝트를 편집. 모든 변경은 `capcut-cli`를 통한 비파괴(자동 백업) 편집.

---

## 1. 트리거 조건

### 자동 키워드 감지 (1차)
다음 키워드 중 1개 이상 감지 시 후보가 됨:
- 한국어: `캡컷`, `켑컷`, `캡컷프로`, `컷편집`, `영상편집`, `자막`, `무음제거`, `쇼츠`, `NG`, `토킹헤드`, `하이라이트 추출`
- 영어: `capcut`, `jianying`, `video edit`, `silence cut`, `subtitle`, `shorts`, `talking head`
- 명시 호출: `/capcut`, `/capcut <intent>` (예: `/capcut doctor`, `/capcut smart-cut`)

### 컨텍스트 조건 (2차, AND)
다음 중 **최소 1개** 충족 시 발화:
- CapCut/JianYing/capcut/켑컷/캡컷 단어 명시
- `draft_content.json` 또는 CapCut 프로젝트 폴더 언급
- `/capcut` 명시 호출
- 영상 파일(.mp4/.mov) + CapCut 컨텍스트 동시 존재

### Negative patterns (3차, 거짓 양성 차단)
- "캡쳐(screenshot)" -> 비활성
- "쇼츠(쇼핑/단축)" 단독 -> 영상 컨텍스트 없으면 비활성
- 일반 ffmpeg 작업 -> `skills/video/`로 위임

상세: [references/intent-keywords.md](references/intent-keywords.md), [references/skill-routing.md](references/skill-routing.md)

---

## 2. 사전 검증 게이트 (순서 고정)

스킬 활성화 시 다음 순서를 **반드시** 실행:

1. **CapCut 프로세스 검사** — `node scripts/lock-check.mjs`
   - 실행 중이면 "CapCut을 종료해 주세요. 계속 진행하면 변경이 덮어쓰일 수 있습니다." 경고
   - 사용자 강제 승인 시에만 진행
2. **환경 검증** — `node scripts/doctor.mjs`
   - Node / capcut-cli / FFmpeg / Whisper(선택) / CapCut Desktop / Draft 경로 6단계 체크
   - 필수 항목 실패 시 설치 가이드 출력 후 종료
3. **프로젝트 경로 확정** — `node scripts/locate-project.mjs`
   - OS별 draft 폴더 자동 검색
   - Desktop 미설치 + Web 흔적 감지 시 "CapCut Web은 미지원. Desktop 설치 후 재시도" 안내

---

## 3. 다른 스킬 충돌 체크

| 입력 유형 | 우선 스킬 |
|-----------|-----------|
| CapCut draft 폴더 또는 캡컷 명시 | **capcut** (본 스킬) |
| 일반 mp4 컷/인코딩 (CapCut 무관) | `video` |
| Remotion 코드형 영상 생성 | `video` |
| 화면 디자인/UI | `frontend-design` |
| 모션 그래픽 단독 | `game-dev` |

CapCut 컨텍스트가 없으면 즉시 "video 스킬을 사용하세요" 등 위임 메시지 출력 후 종료.

상세: [references/skill-routing.md](references/skill-routing.md)

---

## 4. 인텐트 분류 결정 트리

| 감지 패턴 | 워크플로우 |
|-----------|-----------|
| 시간 패턴 (`\d+:\d+`, `\d분`, `\d초`) + 컷/트림/속도 동사 | [01-timecode-edit](workflows/01-timecode-edit.md) |
| "찾아서/그 장면/···하는 부분" + 컷 동사 | [02-content-search](workflows/02-content-search.md) |
| "무음/NG/스마트컷/정리" | [03-talking-head](workflows/03-talking-head.md) |
| "쇼츠/세로/숏폼/9:16/하이라이트" | [04-long-to-shorts](workflows/04-long-to-shorts.md) |
| "자막/캡션/번역" | [05-subtitle-styling](workflows/05-subtitle-styling.md) |
| "보여줘/검사/되돌려/롤백/백업" | [06-inspect-maintain](workflows/06-inspect-maintain.md) |
| "템플릿/저장/적용" | [07-template-reuse](workflows/07-template-reuse.md) |
| "모자이크/얼굴 가려/번호판/프라이버시" | [08-mosaic-privacy](workflows/08-mosaic-privacy.md) |
| "배경 블러/크로마키/필터/트랜지션/블렌딩/말풍선" | [09-effects-styling](workflows/09-effects-styling.md) |
| "따라다니게/추적/모션 트래킹" | [10-motion-tracking](workflows/10-motion-tracking.md) |
| "색보정/LUT/시네마틱/빈티지/흑백/톤" | [11-color-grading](workflows/11-color-grading.md) |
| "안정화/손떨림/잡음 제거/노이즈" | [12-stabilize-denoise](workflows/12-stabilize-denoise.md) |
| "켄 번스/줌/팬/애니메이션/페이드/타이핑" | [13-animation](workflows/13-animation.md) |
| "다국어 자막/동시 자막/···어 같이" | [14-multi-language-captions](workflows/14-multi-language-captions.md) |

중첩 인텐트: 사용자 확인 -> 순차 실행 (예: 04 추출 -> 05 자막).

---

## 5. 인터뷰 모드 (의도 불명 또는 `/capcut help`)

3-5문 짧은 인터뷰로 워크플로우 자동 매핑:

```
Q1. 어떤 영상을 다루세요? (CapCut 프로젝트 / 신규 영상 파일 / 둘 다)
Q2. 결과물 목적? (편집 마무리 / 쇼츠 제작 / 자막 작업 / 자동 정리)
Q3. 길이? (30초 미만 / 1-5분 / 5분 이상)
Q4. 자막 필요? (이미 있음 / 새로 생성 / 번역 / 불필요)
Q5. (필요 시) 특정 장면 시간 알고 있나요? (예/아니오)
```
답변 조합 -> 7개 워크플로우 중 1-2개 추천 -> 사용자 확정 -> 실행.

---

## 6. 워크플로우 위임

인텐트 매칭 후 해당 `workflows/*.md`의 절차를 따른다.

| # | 파일 | 핵심 |
|---|------|------|
| 01 | [01-timecode-edit.md](workflows/01-timecode-edit.md) | 타임코드 직접 컷/트림/속도 |
| 02 | [02-content-search.md](workflows/02-content-search.md) | 자막+비전 하이브리드 매칭 |
| 03 | [03-talking-head.md](workflows/03-talking-head.md) | 무음/NG 자동 제거 |
| 04 | [04-long-to-shorts.md](workflows/04-long-to-shorts.md) | 다중 신호 하이라이트 + 쇼츠 |
| 05 | [05-subtitle-styling.md](workflows/05-subtitle-styling.md) | 자막 생성/스타일/번역 |
| 06 | [06-inspect-maintain.md](workflows/06-inspect-maintain.md) | 검사/롤백/백업 |
| 07 | [07-template-reuse.md](workflows/07-template-reuse.md) | 템플릿 저장/적용 |
| 08 | [08-mosaic-privacy.md](workflows/08-mosaic-privacy.md) | 모자이크 (정적/추적) |
| 09 | [09-effects-styling.md](workflows/09-effects-styling.md) | bg-blur, chroma, filter, transition |
| 10 | [10-motion-tracking.md](workflows/10-motion-tracking.md) | 오브젝트 추적 자막/효과 |
| 11 | [11-color-grading.md](workflows/11-color-grading.md) | 색보정·LUT |
| 12 | [12-stabilize-denoise.md](workflows/12-stabilize-denoise.md) | 안정화·잡음 제거 |
| 13 | [13-animation.md](workflows/13-animation.md) | 켄 번스/텍스트 애니/키프레임 |
| 14 | [14-multi-language-captions.md](workflows/14-multi-language-captions.md) | 다국어 동시 자막 |

---

## 7. 공통 후처리

모든 워크플로우는 다음 후처리를 거친다:

1. **dry-run 우선**: `--dry-run`으로 변경 미리보기 출력
2. **사용자 승인**: 명시적 OK 받기 전 실제 변경 금지
3. **실행**: 승인 시 실제 명령 호출
4. **검증**: `capcut info` diff 자동 출력
5. **실패 시**: `capcut restore --backup <id>` 자동 안내
6. **로깅**: 모든 단계 [scripts/logger.mjs](scripts/logger.mjs)로 `logs/YYYY-MM-DD.jsonl` 기록

---

## 8. 비용 통제

- Whisper 모델: 영상 길이별 자동 선택 (<30s tiny, <5min base, <30min medium, 이상 large-v3)
- Vision 호출: 자막 매칭 신뢰도 >= 0.8이면 스킵, 비전 필요 시 후보 ±5초 키프레임만, 3x3 그리드로 합성
- 번역: 호출 전 길이/토큰 추정 표시 -> 사용자 승인

상세: [references/token-budget.md](references/token-budget.md)

---

## 9. 안전 정책 (요약)

| 정책 | 메커니즘 |
|------|----------|
| 동시 실행 방지 | lock-check.mjs (CapCut 프로세스 감지) |
| 모든 쓰기 검토 | --dry-run 강제 우선 |
| 자동 백업 | capcut-cli 자체 + 7일 보존 (~/.claude/skills/capcut/backups/) |
| 변경 가시화 | capcut info diff |
| 실패 복구 | capcut restore 안내 + 자동 옵션 |

상세: [references/known-issues.md](references/known-issues.md)
