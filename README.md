# turtlegram_backend

# <0515>
1. signup() 기능
  - request.form
    - `request.form['id']`과 같이 입력한 정보의 `key` 값을 통해 `value`를 가져올 수 있음 
    - 위의 방식으로 데이터를 가져오다가 존재하지 않는 값을 요청하게 되면 error가 발생하고 이는 서버에 좋지 않은 영향을 가져옴
    - 그러므로 form 형식으로 데이터를 받아오게 되면 `request.form.get('id')`을 사용해 값이 없다면 `None` 값을 반환하는 것이 나음
  - request.data
    -  `JSON`형식으로 입력된 데이터를 가져오며, `print(request.data)`과 같이 그대로 가져오면 `b'{\n    "id": "jeongdaegeun2",\n    "password": "12345"\n}'`이 반환됨
    -  json을 import하고 `data = json.loads(request.data)`와 같이 data를 선언한 후 다음과 같이 데이터를 가져올 수 있음
       ```python
       print(data.get('id')) # jeongdaegeun2
       print(data['password']) # 12345
       ```
