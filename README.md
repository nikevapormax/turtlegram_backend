# turtlegram_backend

# <0515>
1. signup() 기능
  - request.form
    - `request.form['id']`과 같이 입력한 정보의 `key` 값을 통해 `value`를 가져올 수 있음 
    - 위의 방식으로 데이터를 가져오다가 존재하지 않는 값을 요청하게 되면 error가 발생하고 이는 서버에 좋지 않은 영향을 가져옴
    - 그러므로 form 형식으로 데이터를 받아오게 되면 `request.form.get('id')`을 사용해 값이 없다면 `None` 값을 반환하는 것이 나음

    - html의 button의 type이 `submit`인 경우 form data를 받아옴
  - request.data
    -  `JSON`형식으로 입력된 데이터를 가져오며, `print(request.data)`과 같이 그대로 가져오면 `b'{\n    "id": "jeongdaegeun2",\n    "password": "12345"\n}'`이 반환됨
    -  json을 import하고 `data = json.loads(request.data)`와 같이 data를 선언한 후 다음과 같이 데이터를 가져올 수 있음
       ```python
       print(data.get('id')) # jeongdaegeun2
       print(data['password']) # 12345
       ```
   - **SOP (Same Origin Policy)**
    - 개념
        - 동일 기원 정책 / 동일 출처 정책
        - 현대 브라우저에서 지원하는 것으로 JavaScript, Documents, Media 등을 `하나의 Origin(기원)에서 다른 Origin(기원)으로 통신하지 못하도록` 막는 정책
        - `CSRF(Cross Site Request Forgery)` 나 `CST`  같은 보안상의 이슈로 인해 막는 것
    - SOP가 없다면?
        - 우리는 turtle.com에 접속해야 하는데 `turtlee.com`으로 속아 잘못 접속하게 될 수 있다. 이때 우리가 같은 브라우저에서 turtle.com에 로그인을 하거나 로그인중이라면 AJAX 요청 등을 통해 비밀리에 유저의 정보를 탈취하거나 다른 기능들을 수행할 수 있다. (CRSF)
    - Same Origin이란?
        - `같은 프로토콜, 호스트, 포트`를 사용해야 함
        - 기준 URL : http://www.turtle.com/ko/docs
        
        | 비교대상 URL | 동일? | 이유 |
        | --- | --- | --- |
        | http://www.turtle.com/ko/images | o | 같은 프로토콜, 호스트, 포트 |
        | http://www.turtle.com:500/ko/docs | x | 포트 불일치 |
        | http://w.turtle.com/ko/docs | x | 호스트 불일치 |
        | https://www.turtle.com/ko/docs | x | 프로토콜 불일치 |
        | http://turtle.com/ko/imgaes | x | 호스트 불일치 |
- **CORS(Cross-Origin Resource Sharing)**
    - 개념
        - 교차 출처 리소스 공유
        - `추가 HTTP 헤더`를 사용하여 한 출처에서 사용중인 Web Application이 `다른 출처의 선택한 자원에 접근`할 수 있는 권한을 부여하도록 브라우저에 알려주는 체제
        - 리소스가 `자신의 출처(도메인, 프로토콜, 포트)`와 다를 때 교차 출처 HTTP 요청을 실행
        - CORS 실패는 오류의 원인이지만, 보안상의 이유로 JavaScript에서는 오류의 상세 정보에 접근할 수 없으며, 알 수 있는 것은 오류가 발생한 것
            - 정확히 어떤 것이 실패했는지 알아내려면 브라우저의 콘솔 확인 필요
- **CSP (Content Securiy Policy)**
    - 개념
        - 웹 보안 정책 중 하나로, 주로 `XSS나 Data Injection, Click Jacking` 등 웹 페이지에 `악성 스크립트를 삽입하는 공격기법들을 막기 위해` 사용
        - `Header`에 CSP의 내용이 작성되며, 특정 리소스가 `어디서 왔는지`를 검사하고 `허용된 범위에 포함되었는지` 검토
    - [https://csp-evaluator.withgoogle.com/](https://csp-evaluator.withgoogle.com/) 를 통해 CSP가 걸려있는지 확인 가능
