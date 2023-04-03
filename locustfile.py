from locust import HttpUser, task, between

class ApiUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):

        self.client.headers.update({"Authorization": f"Bearer 8c9c3671beb2c7baed28c003aba23b1d44450b21e7956c7342d32d90f54c59be342ebb2bb11d20e68c5793d8039c60d3730d05deb0465d40d7183f824c9eed485796d9e7b587a661560b44e1c43abad0f72ff2935555de2bb58a4cc314dc3ba4a79a7117f8299a8d3edd8c726690e1164936364df51193bd2c52a2ce29d7cb63b10bc9dd777acb8e6c7b34fdfc85fa6f7c855804cb47dcf6a941860c41781e395731aef7c9a2cab7e1e6cb981fa1083104f3d2057689785b9c5514f4fbb811e9e5b519b67d50f2f2728fa3730baf13427de206d0307e892135f611a17034495d0988d04e6f3903e56705efbd8ad7330565241e616cffc7c90bec"})


    @task
    def items_task(self):
        self.client.get("/items")

    @task
    def important_dates_task(self):
        self.client.get("/important_dates")

    @task
    def rules_task(self):
        self.client.get("/rules")

    # @task
    # def regsiter_task(self):
    #     data = {
    #       "user": {
    #         "username": "1",
    #         "email": "amir@sadeghi.me",
    #         "first_name": "Amir",
    #         "last_name": "Sadeghi",
    #         "password": "Amiir@1234"
    #       },
    #       "telephone_number": "5149804356"
    #     }
    #     self.client.post("/registerEndPoint", json=data)
