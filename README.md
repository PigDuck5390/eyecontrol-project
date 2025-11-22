
## 설치 방법
anaconda 설치 후 ananconda prompt에서 진행

1. git clone https://github.com/PigDuck5390/eyecontrol-project.git
2. cd ../eyecontrol-project
3. bash
conda create -n env python=3.10
conda activate env
4. pip install -r requirements.txt


아래 링크에서 Vosk 한국어 모델 (v0.22) 다운로드
https://alphacephei.com/vosk/models

압축을 풀고 model/ 폴더에 넣기(model폴더 생성)
eyecontrol-project/ model/ vosk-model-small-ko-0.22/


## 실행
bash
1. conda activate eyecontrol
2. cd ../eyecontrol-project (main.py가 있는 경로로 이동)
3. python main.py
