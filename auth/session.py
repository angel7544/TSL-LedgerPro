class Session:
    _instance = None
    user = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = Session()
        return cls._instance

    def set_user(self, user_data):
        self.user = user_data

    def get_user(self):
        return self.user

    def clear(self):
        self.user = None
