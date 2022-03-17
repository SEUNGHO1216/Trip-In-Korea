# TripInKorea
***
## 국내여행지 소개사이트!!
### 여행을 사진과 함께 기록하고 공유하는 웹 어플리케이션
<br>
[사이트](http://sparta-restaurant.shop/)

<br>

### 프로젝트 선정 이유
- 현 시국으로 인해 여행을 다니지 못하는 사람들에게는 간접 체험을 기회를 제공하고 해외여행이 부담스러운 사람들에게는 다른 사람이 경험한 좋은 국내여행지를 둘러볼 수 있는 사이트
- 간단한 이미지와 짧은 글로 여행지에 대한 구체적인 정보전달보다 인사이트를 주기 위함

<br>

### 개발자
22.03.07 - 22.03.10
- 백승호, 장재영, 정기현, 정현석

### 주요 기능
- JWT를 이용한 로그인, 로그아웃 기능
- JWT 토근을 활용한 서버사이드렌더링 동적페이지 구현
  - 로그인 여부에 따라 마이페이지 유무 및 로그아웃 버튼 생성  
  - 로그인 유뮤에 따라 게시물 생성 유무 차별
- 이미지 업로드 시 이미지 미리보기 기능 구현
- MongoDB를 활용한 게시물 내용 표출 및 정렬(_id기준)
- MongoDB find 조건을 활용하여 지역별 여행지 추출
- '좋아요'기능 구현(수정 필요)
- 게시물 CRUD 완성

<br>

### 사용 기술
- front) html, css, javascript, jquery, jinja2
- back) python, flask, jwt
- DB) mongoDB

### 사용시 설치해야하는 library
- Flask(2.0.3)
- Jinja2 (3.0.3)
- PyJWT (1.7.1 : PyJWT는 version을 맞춰주시기 바랍니다.)
- certifi
- dnspython
- pymongo
- pytz
- bson
- Werkzeug

