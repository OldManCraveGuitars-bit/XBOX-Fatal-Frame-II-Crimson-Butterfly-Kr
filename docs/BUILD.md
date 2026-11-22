# Windows EXE 패처 빌드

Windows 64비트 / Python 3.13 기준입니다. 배포 사용자는 Python이 필요하지 않습니다.

```powershell
python -m pip install -r requirements-build.txt
```

`vendor/xdelta3/README.md`에 명시한 xdelta3 3.2.1 Windows x86-64를 준비합니다.
원본과 검증된 v0.81 결과 XISO는 README의 해시와 같아야 합니다. ISO는 저장소와 릴리스에 포함하지 않습니다.

```powershell
python tools/build_public_patch.py --source "D:\Games\Fatal Frame II - Crimson Butterfly (Japan).iso" --target "D:\Games\Fatal-Frame-II-Crimson-Butterfly-Kr-v0.81.xiso.iso" --xdelta vendor/xdelta3/xdelta3.exe --output patches/Fatal-Frame-II-Crimson-Butterfly-Kr-v0.81.ffpatch
python -m pytest tests -q
python tools/build_windows_release.py
```

차분은 변경 파일 99개의 VCDIFF와 XDVDFS 디렉터리 정보입니다. 나머지 파일은 사용자의 원본에서 복사합니다.
빌더는 설정된 원본/결과 해시와 원본 XBE 보존을 확인합니다. 생성한 차분 해시는 `patcher/release-config.json`과 같아야 합니다.
다른 xdelta 빌드나 ZIP 생성 환경에서는 차분 바이트가 달라질 수 있습니다.

```powershell
release/XBOX-Fatal-Frame-II-Crimson-Butterfly-Kr-v0.81-Patcher.exe --inspect --report build/inspect.json
release/XBOX-Fatal-Frame-II-Crimson-Butterfly-Kr-v0.81-Patcher.exe --source "D:\Games\original.iso" --output "D:\Games\Korean.iso" --report build/exe-roundtrip.json
release/XBOX-Fatal-Frame-II-Crimson-Butterfly-Kr-v0.81-Patcher.exe --ui-smoke --report build/exe-ui-smoke.json
python tools/package_release.py
```

완성 EXE를 검사한 뒤 패키징합니다. `--ui-smoke`는 위젯 배치 검사이며 게임 GPU 검증이 아닙니다.
빌드 임시 경로는 `FFII_BUILD_WORK`, 배포 출력은 `FFII_RELEASE_DIR`, PyInstaller 캐시는 `PYINSTALLER_CONFIG_DIR`, 일반 임시 파일은 `TEMP/TMP`로 별도 드라이브를 지정할 수 있습니다.
`patches/*.ffpatch`, `build/`, `release/`와 디코더 바이너리는 Git에서 제외합니다.
