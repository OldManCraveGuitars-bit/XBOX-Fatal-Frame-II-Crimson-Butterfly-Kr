# Windows EXE 패처 빌드

Windows 64비트 / Python 3.13 기준입니다. 배포 사용자는 이 빌드 과정이나 Python이 필요하지 않습니다.

```powershell
python -m pip install -r requirements-build.txt
```

`vendor/xdelta3/README.md`에 명시한 xdelta3 3.2.1 Windows x86-64를 준비합니다.
원본과 검증된 v0.75 결과 XISO는 README의 해시와 같아야 합니다. ISO는 Git과 릴리스에 포함하지 않습니다.

```powershell
python tools/build_public_patch.py --source "D:\Games\Fatal Frame II - Crimson Butterfly (Japan).iso" --target "D:\Games\Fatal-Frame-II-Crimson-Butterfly-Kr-v0.75.xiso.iso" --xdelta vendor/xdelta3/xdelta3.exe --output patches/Fatal-Frame-II-Crimson-Butterfly-Kr-v0.75.ffpatch
python -m pytest tests -q
python tools/build_windows_release.py
```

차분은 변경 파일 100개의 VCDIFF와 새 XDVDFS 디렉터리 정보를 담습니다. 나머지 파일은 사용자의 원본에서 복사합니다.
생성한 차분·디코더 해시는 `patcher/release-config.json`과 일치해야 합니다. 다른 xdelta 빌드는 차분 바이트가 달라질 수 있습니다.

```powershell
python patcher/app.py --inspect --report build/inspect.json
python patcher/app.py --source "D:\Games\original.iso" --output "D:\Games\Korean.iso" --report build/patch-result.json
```

EXE도 같은 명령행 옵션을 지원합니다. 완성 EXE의 `--source/--output` 전체 왕복과 `--ui-smoke` 검사를 마친 뒤
`build/exe-roundtrip.json`, `build/exe-ui-smoke.json`을 두고 `python tools/package_release.py`로 ZIP을 만듭니다.
UI smoke 검사는 위젯 배치를 확인하는 검사이며 실제 게임 GPU 검증은 아닙니다.

저장소의 `patches/*.ffpatch`, `build/`, `release/`와 디코더 바이너리는 Git에서 제외합니다.
텍스트/이미지 편집과 한글화 제작 프로젝트는 이 배포용 최소 패처 소스와 별도입니다.
